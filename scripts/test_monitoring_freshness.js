'use strict';
// Deterministic policy/DOM-adapter unit tests, not browser or hardware evidence.
const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname,'../backend/laravel/public/assets/monitoring-freshness.js'),'utf8');
const policyModule={exports:{}};
vm.runInNewContext(source,{module:policyModule},{timeout:1000});
const {integer,status,navigationStart} = policyModule.exports;
const live = {label:'LIVE',reason:'SERVER RECEIPT AGE',ageMs:'0',staleMs:'2000',offlineMs:'4000'};
test('zero and exact conservative expiry boundaries',()=>{
    for(const [elapsed,expected] of [[0,'LIVE'],[1999,'LIVE'],[1999.1,'STALE'],[2000,'STALE'],[3999,'STALE'],[3999.1,'OFFLINE'],[4000,'OFFLINE'],[99999,'OFFLINE']])
        assert.equal(status(live,elapsed),expected);
});
test('malformed and unsafe integers never become live',()=>{
    for(const value of ['',null,undefined,0,1.1,'-1','01','1e3',' 0','Infinity','9007199254740992']) {
        assert.equal(integer(value),null);
        for(const field of ['ageMs','staleMs','offlineMs']) assert.equal(status({...live,[field]:value},0),'UNKNOWN');
    }
    assert.equal(integer('0'),0);assert.equal(integer('9007199254740991'),Number.MAX_SAFE_INTEGER);
});
test('invalid policy, elapsed and integer overflow fail closed',()=>{
    for(const elapsed of [NaN,Infinity,-1,-0.1,undefined,'0'])assert.equal(status(live,elapsed),'UNKNOWN');
    for(const pair of [['0','1'],['2','2'],['3','2']])assert.equal(status({...live,staleMs:pair[0],offlineMs:pair[1]},0),'UNKNOWN');
    assert.equal(status({...live,ageMs:'9007199254740991'},1),'UNKNOWN');
    for(const label of ['UNKNOWN','constructor','__proto__','live',''])assert.equal(status({...live,label},0),'UNKNOWN');
});
test('server expired label is a lower bound, missing receipt never live',()=>{
    assert.equal(status({...live,label:'STALE'},0),'STALE');assert.equal(status({...live,label:'OFFLINE'},0),'OFFLINE');
    assert.equal(status({label:'OFFLINE',reason:'NO RECEIPT'},0),'OFFLINE');
    assert.equal(status({label:'OFFLINE',reason:'NO RECEIPT'},NaN),'UNKNOWN');
});
test('request timing admits zero, rejects cached or inconsistent navigation',()=>{
    const entry={type:'navigate',requestStart:0,responseStart:0};
    const p=value=>({getEntriesByType:()=>value});
    assert.equal(navigationStart(p([entry])),0);
    assert.equal(navigationStart(p([{...entry,type:'reload',requestStart:2,responseStart:3}])),2);
    for(const value of [[],[entry,entry],[{...entry,type:'back_forward'}],[{...entry,requestStart:-1}],[{...entry,requestStart:2,responseStart:1}],[{...entry,responseStart:NaN}]])
        assert.equal(navigationStart(p(value)),null);
});
function dom(options={}) {
    let clock=0, interval;const events={},docEvents={};
    const nodes=Array.from({length:4},()=>({dataset:{vgLabel:'LIVE',vgReason:'SERVER RECEIPT AGE',vgAgeMs:'0',vgStaleMs:'2000',vgOfflineMs:'4000'},textContent:'SNAPSHOT: LIVE',classes:new Set(['badge','SNAPSHOT'])}));
    for(const node of nodes)node.classList={remove:(...names)=>names.forEach(n=>node.classes.delete(n)),add:n=>node.classes.add(n)};
    const document={hidden:false,querySelectorAll:()=>nodes,addEventListener:(name,fn)=>docEvents[name]=fn};
    const context={document,performance:{now:()=>clock,getEntriesByType:()=>options.noTiming?[]:[{type:'navigate',requestStart:0,responseStart:0}]},setInterval:fn=>interval=fn,addEventListener:(name,fn)=>events[name]=fn};
    vm.runInNewContext(source,context,{timeout:1000});
    return {nodes,events,docEvents,document,tick(value){clock=value;interval();}};
}
test('all duplicate DOM labels age together without touching values or fetching',()=>{
    const d=dom();for(const n of d.nodes)assert.equal(n.textContent,'LIVE');
    d.tick(2000);for(const n of d.nodes)assert.equal(n.textContent,'STALE');
    d.tick(4000);for(const n of d.nodes){assert.equal(n.textContent,'OFFLINE');assert(!n.classes.has('LIVE'));}
});
test('rewound time remains unknown even when timing later recovers',()=>{
    const d=dom();d.tick(2100);d.tick(2000);d.tick(10000);for(const n of d.nodes)assert.equal(n.textContent,'UNKNOWN');
});
test('missing timing, cached restore, freeze, hide and pagehide fail closed',()=>{
    for(const action of [d=>d.events.pageshow({persisted:true}),d=>d.events.pagehide(),d=>d.docEvents.freeze(),d=>{d.document.hidden=true;d.docEvents.visibilitychange();}]){
        const d=dom();action(d);d.tick(10);for(const n of d.nodes)assert.equal(n.textContent,'UNKNOWN');
    }
    for(const n of dom({noTiming:true}).nodes)assert.equal(n.textContent,'UNKNOWN');
});
test('mutable DOM attributes cannot revive expired captured descriptors',()=>{
    const d=dom();d.tick(4000);for(const n of d.nodes){n.dataset.vgAgeMs='0';n.dataset.vgOfflineMs='999999';}
    d.tick(4100);for(const n of d.nodes)assert.equal(n.textContent,'OFFLINE');
});
