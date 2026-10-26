'use strict';
// Actual Chrome + actual private PHP backend. No certificate-ignore options.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const http = require('node:http');
const https = require('node:https');
const {spawn} = require('node:child_process');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
class ProbeError extends Error { constructor(code) { super(code); this.code = code; } }
const demand = (condition, code) => { if (!condition) throw new ProbeError(code); };

function prerequisites() {
  demand(typeof WebSocket === 'function', 'NODE_WEBSOCKET_UNAVAILABLE');
  demand(!process.env.NODE_OPTIONS && !process.env.NODE_TLS_REJECT_UNAUTHORIZED, 'NODE_OVERRIDE_REFUSED');
  const binary = process.env.VG_BROWSER_BINARY;
  demand(typeof binary === 'string' && path.isAbsolute(binary) && fs.statSync(binary).isFile(), 'BROWSER_BINARY_REQUIRED');
}

function admit(req, origin) {
  demand(req.headers.host===new URL(origin).host && req.headers['user-agent']===process.env.VG_BROWSER_AGENT,'FOREIGN_BROWSER_REQUEST');
  demand(typeof req.url==='string' && req.url.startsWith('/') && !req.url.startsWith('//'),'ABSOLUTE_PROXY_REFUSED');
  const url=new URL(req.url,origin);
  const permitted=new Set(['/','/login','/logout','/monitoring','/monitoring/runtime:demo','/monitoring/runtime%3Ademo','/assets/monitoring-freshness.js']);
  demand(permitted.has(url.pathname),'UNSUPPORTED_UI_PATH');
  demand(['GET','HEAD','POST'].includes(req.method),'UNSUPPORTED_UI_METHOD');
  demand(req.method!=='POST' || ['/login','/logout'].includes(url.pathname),'READ_ONLY_UI_ONLY');
  const privateForm=req.headers.origin==='null' && req.headers['sec-fetch-site']==='same-origin'
    && req.headers['sec-fetch-mode']==='navigate' && req.headers['sec-fetch-dest']==='document';
  demand(!req.headers.origin || req.headers.origin===origin || privateForm,'FOREIGN_BROWSER_ORIGIN');
  if(req.method==='POST')demand(req.headers.origin===origin || privateForm,'POST_ORIGIN_REQUIRED');
  return url;
}

class Cdp {
  constructor(socket) {
    this.socket = socket; this.next = 1; this.pending = new Map();
    socket.addEventListener('close',()=>this.cancel());
    socket.addEventListener('message', event => {
      const value = JSON.parse(event.data);
      const waiting = this.pending.get(value.id);
      if (!waiting) return;
      clearTimeout(waiting.timer); this.pending.delete(value.id);
      if (value.error) waiting.reject(new ProbeError('CDP_COMMAND_REFUSED'));
      else waiting.resolve(value.result || {});
    });
  }
  cancel() {
    for(const waiting of this.pending.values()) {clearTimeout(waiting.timer);waiting.reject(new ProbeError('CDP_CLOSED'));}
    this.pending.clear();
  }
  static async open(url) {
    const socket = new WebSocket(url);
    await new Promise((resolve, reject) => {
      const timer=setTimeout(()=>{socket.close();reject(new ProbeError('CDP_CONNECT_TIMEOUT'));},8000);
      socket.addEventListener('open', ()=>{clearTimeout(timer);resolve();}, {once:true});
      socket.addEventListener('error', () => {clearTimeout(timer);reject(new ProbeError('CDP_CONNECT_FAILED'));}, {once:true});
    });
    return new Cdp(socket);
  }
  send(method, params = {}, sessionId) {
    if(this.socket.readyState!==WebSocket.OPEN)return Promise.reject(new ProbeError('CDP_CLOSED'));
    const id = this.next++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {this.pending.delete(id); reject(new ProbeError('CDP_TIMEOUT'));}, 8000);
      this.pending.set(id, {resolve,reject,timer});
      this.socket.send(JSON.stringify({id,method,params,...(sessionId ? {sessionId} : {})}));
    });
  }
  async value(expression, session) {
    const result = await this.send('Runtime.evaluate', {expression,returnByValue:true,awaitPromise:true}, session);
    if(result.exceptionDetails) {const kind=result.exceptionDetails.exception?.className;throw new ProbeError('BROWSER_EXPRESSION_FAILED_'+(['SyntaxError','TypeError','ReferenceError'].includes(kind)?kind:'OTHER'));}
    return result.result.value;
  }
}

async function run() {
  prerequisites();
  const root = fs.realpathSync(process.env.VG_BROWSER_ROOT || '');
  demand(path.dirname(root) === fs.realpathSync(os.tmpdir()) && path.basename(root).startsWith('vg-live-http-'), 'OWNED_ROOT_REQUIRED');
  const profile = path.join(root, 'browser-profile');
  demand(!fs.existsSync(profile), 'FRESH_BROWSER_PROFILE_REQUIRED');
  fs.mkdirSync(profile);
  fs.mkdirSync(path.join(profile, 'Default'));
  fs.writeFileSync(path.join(profile, 'Default/Preferences'), JSON.stringify({credentials_enable_service:false,profile:{password_manager_enabled:false}}));
  const upstream = new URL(process.env.VG_BROWSER_UPSTREAM);
  demand(upstream.protocol === 'https:' && upstream.hostname === '127.0.0.1' && upstream.port, 'PRIVATE_TLS_REQUIRED');
  const agentName = process.env.VG_BROWSER_AGENT;
  demand(/^vg-live\/[a-f0-9]{32}$/.test(agentName || ''), 'OWNED_AGENT_REQUIRED');
  const tls = new https.Agent({ca:fs.readFileSync(path.join(root,'ca.pem')),rejectUnauthorized:true,minVersion:'TLSv1.2'});
  let front, child, cdp, origin, session, outcome = 3, requests = 0;
  const record = {browser:null,upstream_tls_verified:false,cookie_attributes:null,initial:null,middle:null,
    expired:null,refreshed:null,no_data_polling:false,failure:null,profile_closed:false,fallbacks:{},
    observations:{stage:'startup',ui_statuses:[],adapter_refusal:[]}};
  async function request(target, method='GET', headers={}, body=Buffer.alloc(0)) {
    return new Promise((resolve,reject) => {
      const req = https.request(new URL(target,upstream), {method,agent:tls,headers:{...headers,host:upstream.host,'user-agent':agentName,'content-length':body.length}}, response => {
        const chunks=[]; let size=0;
        response.on('data',chunk => {size+=chunk.length; if(size>1048576) response.destroy(); else chunks.push(chunk);});
        response.on('end',() => {record.upstream_tls_verified=true;resolve({status:response.statusCode,headers:response.headers,body:Buffer.concat(chunks)});});
        response.on('error',() => reject(new ProbeError('TLS_RESPONSE_FAILED')));
      });
      req.on('error',() => reject(new ProbeError('STRICT_TLS_UPSTREAM_FAILED')));
      req.setTimeout(10000,() => req.destroy()); req.end(body);
    });
  }
  // Own-process deadline; tear down owned connections so normal finally closes
  // the browser before Python's outer safety timeout. Never kill by image name.
  let timedOut=false;
  const deadline=setTimeout(()=>{timedOut=true;if(cdp)cdp.cancel();tls.destroy();if(front)front.closeAllConnections();},45000);
  try {
    front = http.createServer({maxHeaderSize:16384}, async (req,res) => {
      try {
        // Chrome can serialize a same-origin form's Origin as null under the
        // actual no-referrer policy. Admit only its browser-owned fetch tuple;
        // exact Host/UA plus Laravel's real session/CSRF checks still apply.
        const url=admit(req,origin);
        const chunks=[];let size=0;
        for await (const chunk of req) {size+=chunk.length;demand(size<=8192,'BROWSER_BODY_CAP');chunks.push(chunk);}
        const headers={...req.headers};
        for (const key of Object.keys(headers)) if (key.startsWith('x-forwarded-') || ['connection','transfer-encoding','content-length','host'].includes(key)) delete headers[key];
        if(headers.origin===origin) headers.origin=upstream.origin;
        const response=await request(url.pathname+url.search,req.method,headers,Buffer.concat(chunks));requests++;
        record.observations.ui_statuses.push([req.method,url.pathname,response.status]);
        const output={...response.headers};delete output['content-length'];delete output.connection;delete output['transfer-encoding'];
        if(output.location) {demand(output.location.startsWith(upstream.origin+'/'),'FOREIGN_REDIRECT');output.location=origin+output.location.slice(upstream.origin.length);}
        let body=response.body;
        if((output['content-type']||'').startsWith('text/html')) body=Buffer.from(body.toString('utf8').split(upstream.origin).join(origin));
        // Secure/HttpOnly/SameSite cookies are deliberately forwarded unchanged.
        res.writeHead(response.status,{...output,'content-length':body.length});res.end(req.method==='HEAD'?undefined:body);
      } catch(error) {if(record.observations.adapter_refusal.length<20)record.observations.adapter_refusal.push(error instanceof ProbeError?error.code:'ADAPTER_INTERNAL_ERROR');res.writeHead(403,{'cache-control':'no-store'});res.end('Private browser adapter refused.');}
    });
    await new Promise(resolve => front.listen(0,'127.0.0.1',resolve));origin='http://localhost:'+front.address().port;
    const args=['--headless=new','--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',
      '--user-data-dir='+profile,'--enable-automation','--no-first-run','--no-default-browser-check',
      '--disable-background-networking','--disable-component-update','--disable-sync','--disable-breakpad','--disable-gpu','about:blank'];
    child=spawn(process.env.VG_BROWSER_BINARY,args,{stdio:'ignore',windowsHide:true});
    let spawnFailed=false;child.on('error',()=>{spawnFailed=true;});
    let started=false;
    for(let i=0;i<100;i++) {if(spawnFailed||child.exitCode!==null)break;if(fs.existsSync(path.join(profile,'DevToolsActivePort'))) {started=true;break;} await delay(100);}
    demand(started,'BROWSER_START_FAILED');
    const endpoint=fs.readFileSync(path.join(profile,'DevToolsActivePort'),'utf8').trim().split(/\r?\n/);
    demand(/^\d{1,5}$/.test(endpoint[0]) && /^\/devtools\/browser\/[a-f0-9-]+$/.test(endpoint[1]),'OWNED_CDP_ENDPOINT_REQUIRED');
    cdp=await Cdp.open('ws://127.0.0.1:'+endpoint[0]+endpoint[1]);
    const command=await cdp.send('Browser.getBrowserCommandLine');demand(command.arguments.includes('--user-data-dir='+profile),'BROWSER_PROFILE_MISMATCH');
    record.browser=(await cdp.send('Browser.getVersion')).product;
    const target=await cdp.send('Target.createTarget',{url:'about:blank'});
    session=(await cdp.send('Target.attachToTarget',{targetId:target.targetId,flatten:true})).sessionId;
    await cdp.send('Page.enable',{},session);await cdp.send('Runtime.enable',{},session);
    await cdp.send('Network.enable',{},session);await cdp.send('Network.setUserAgentOverride',{userAgent:agentName},session);
    async function until(expression) {for(let i=0;i<100;i++) {demand(!timedOut,'OWNED_BROWSER_DEADLINE');if(await cdp.value(expression,session))return;await delay(50);}throw new ProbeError('BROWSER_PAGE_TIMEOUT');}
    await cdp.send('Page.navigate',{url:origin+'/login'},session);
    record.observations.stage='login_form';
    await until('Boolean(document.querySelector("input[name=_token]"))');
    record.observations.form=await cdp.value('(()=>{const u=new URL(document.querySelector("form").action);window.__vgPolicy=null;document.addEventListener("securitypolicyviolation",e=>{window.__vgPolicy=e.violatedDirective});return {same_origin:u.origin===location.origin,protocol:u.protocol,path_is_login:u.pathname==="/login"}})()',session);
    await cdp.value('(()=>{document.querySelector("input[name=email]").value='+JSON.stringify(process.env.VG_BROWSER_EMAIL)+';document.querySelector("input[name=password]").value='+JSON.stringify(process.env.VG_BROWSER_LOGIN)+';document.querySelector("form").submit();return true})()',session);
    record.observations.stage='login_redirect';
    await until('location.pathname==="/monitoring" && document.readyState==="complete"');
    const cookies=(await cdp.send('Network.getCookies',{urls:[origin]},session)).cookies;
    const cookie=cookies.find(c=>c.name===process.env.VG_BROWSER_COOKIE);
    demand(cookie && cookie.secure && cookie.httpOnly && cookie.sameSite==='Lax','BROWSER_SECURE_SESSION_NOT_PRESERVED');
    record.cookie_attributes={secure:cookie.secure,http_only:cookie.httpOnly,same_site:cookie.sameSite};
    record.observations.stage='native_seed';
    const lines=fs.readFileSync(path.join(root,'browser-native-seed.jsonl'),'utf8').trim().split(/\r?\n/);
    const seed=Buffer.from(lines[0]);
    const accepted=await request('/api/v1/telemetry','POST',{'content-type':'application/json','accept':'application/json',authorization:'Bearer '+process.env.VG_BROWSER_DEVICE_TOKEN},seed);
    demand(accepted.status===201,'NATIVE_BROWSER_SEED_NOT_CREATED');
    record.observations.stage='device_page';
    await cdp.send('Page.navigate',{url:origin+'/monitoring/runtime%3Ademo'},session);
    await until('Boolean(document.querySelector("section[aria-label=\\\"Status data aktual\\\"]")) && document.readyState==="complete"');
    const snapshot='(()=>{const root=document.querySelector("section[aria-label=\\\"Status data aktual\\\"]");const ps=root.querySelectorAll("p");const sample=root.querySelector("[data-vg-freshness-scope=sample]")||ps[0].querySelector(".badge");const transport=root.querySelector("[data-vg-freshness-scope=transport]")||ps[2].querySelector(".badge");const visible=e=>e.getBoundingClientRect().height>0&&getComputedStyle(e).visibility!=="hidden";return {sample:sample.textContent.trim(),transport:transport.textContent.trim(),sample_class:sample.className,visible:visible(sample)&&visible(transport),simulation:root.textContent.includes("SIMULATION"),secure_context:isSecureContext}})()';
    record.initial=await cdp.value(snapshot,session);const count=requests;
    await delay(2200);record.middle=await cdp.value(snapshot,session);
    await delay(2300);record.expired=await cdp.value(snapshot,session);record.no_data_polling=requests===count;
    const previousNavigation=await cdp.value('performance.timeOrigin',session);
    await cdp.send('Page.reload',{},session);
    await until('performance.timeOrigin!=='+JSON.stringify(previousNavigation)+' && Boolean(document.querySelector("section[aria-label=\\\"Status data aktual\\\"]")) && document.readyState==="complete"');
    record.refreshed=await cdp.value(snapshot,session);
    demand(record.initial.sample==='LIVE' && record.initial.visible && record.initial.simulation,'INITIAL_FRESH_VIEW_REQUIRED');
    demand(record.middle.sample==='STALE','OPEN_PAGE_DID_NOT_BECOME_STALE');
    demand(record.expired.sample==='OFFLINE' && record.expired.transport==='OFFLINE','OPEN_PAGE_DID_NOT_EXPIRE');
    demand(record.refreshed.sample.includes('OFFLINE') && record.no_data_polling,'MANUAL_REFRESH_OR_NO_POLLING_CONTRACT');
    async function seedNext(index) {
      const reply=await request('/api/v1/telemetry','POST',{'content-type':'application/json','accept':'application/json',authorization:'Bearer '+process.env.VG_BROWSER_DEVICE_TOKEN},Buffer.from(lines[index]));
      demand(reply.status===201,'FALLBACK_FRESH_NATIVE_SEED_REQUIRED');
    }
    async function newDeviceView() {
      const before=await cdp.value('performance.timeOrigin',session);
      await cdp.send('Page.navigate',{url:origin+'/monitoring/runtime%3Ademo'},session);
      await until('performance.timeOrigin!=='+JSON.stringify(before)+' && document.readyState==="complete" && Boolean(document.querySelector("[data-vg-freshness-scope]"))');
    }
    await seedNext(1);
    await cdp.send('Emulation.setScriptExecutionDisabled',{value:true},session);
    await newDeviceView();record.fallbacks.no_script=await cdp.value(snapshot,session);
    demand(record.fallbacks.no_script.sample==='SNAPSHOT: LIVE' && !record.fallbacks.no_script.sample_class.split(' ').includes('LIVE'),'NO_SCRIPT_NEUTRAL_SNAPSHOT_REQUIRED');
    await cdp.send('Emulation.setScriptExecutionDisabled',{value:false},session);
    await cdp.send('Network.setBlockedURLs',{urls:['*monitoring-freshness.js*']},session);
    await newDeviceView();record.fallbacks.blocked_asset=await cdp.value(snapshot,session);
    demand(record.fallbacks.blocked_asset.sample==='SNAPSHOT: LIVE','MISSING_ASSET_SNAPSHOT_REQUIRED');
    await cdp.send('Network.setBlockedURLs',{urls:[]},session);
    const broken=await cdp.send('Page.addScriptToEvaluateOnNewDocument',{source:'Object.defineProperty(performance,"getEntriesByType",{value:()=>[]})'},session);
    await newDeviceView();record.fallbacks.missing_timing=await cdp.value(snapshot,session);
    demand(record.fallbacks.missing_timing.sample==='UNKNOWN','MISSING_TIMING_UNKNOWN_REQUIRED');
    await cdp.send('Page.removeScriptToEvaluateOnNewDocument',{identifier:broken.identifier},session);
    record.fallbacks.all_labels=await cdp.value('Array.from(document.querySelectorAll("[data-vg-freshness-scope]")).map(n=>n.textContent.trim())',session);
    demand(record.fallbacks.all_labels.length===4 && record.fallbacks.all_labels.every(v=>v==='UNKNOWN'),'DUPLICATE_LABELS_DISAGREE');
    demand(!timedOut,'OWNED_BROWSER_DEADLINE');
    outcome=0;
  } catch(error) {
    if(cdp&&session)try{record.observations.page=await cdp.value('({at_monitoring:location.pathname==="/monitoring",at_login:location.pathname==="/login",policy:window.__vgPolicy||null,has_form:!!document.querySelector("form")})',session);}catch{}
    record.failure=error instanceof ProbeError?error.code:'UNEXPECTED_'+error.name;outcome=error instanceof ProbeError?1:3;
  }
  finally {
    clearTimeout(deadline);
    if(cdp) {
      try {await cdp.send('Browser.close');} catch {}
      cdp.socket.close();
    }
    if(child) {
      for(let i=0;i<50&&child.exitCode===null;i++)await delay(100);
      if(child.exitCode===null)child.kill();
      for(let i=0;i<20&&child.exitCode===null;i++)await delay(100);
      record.profile_closed=child.exitCode!==null;
    }
    if(front) {front.closeAllConnections();await new Promise(resolve=>front.close(resolve));}tls.destroy();
    if(!record.profile_closed){record.failure='BROWSER_OWNED_PROFILE_NOT_CLOSED';outcome=3;}
  }
  process.stdout.write('BROWSER_MONITORING_RECORD='+JSON.stringify(record)+'\n');
  process.stdout.write('BROWSER_MONITORING_GATE='+(outcome===0?'PASS_COMPONENT_ONLY_DEPLOYED_TLS_NOT_RUN':outcome===1?'FAIL_DISPLAY_LIFETIME':'BLOCKED_ENVIRONMENT')+'\n');
  return outcome;
}

if(require.main!==module)module.exports={admit};
else (async()=>{
  if(process.argv[2]==='--check') {prerequisites();process.stdout.write('BROWSER_PREREQUISITE=PASS_NO_LAUNCH\n');return;}
  demand(process.argv.length===3&&process.argv[2]==='--execute','EXPLICIT_EXECUTION_REQUIRED');
  process.exitCode=await run();
})().catch(()=>{process.stdout.write('BROWSER_PREREQUISITE=BLOCKED_NO_DIAGNOSTIC_VALUES\n');process.exitCode=3;});
