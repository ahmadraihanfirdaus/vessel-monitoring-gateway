'use strict';
// Unit boundary tests only; does not launch Chrome, TLS or Laravel.
const test=require('node:test');
const assert=require('node:assert/strict');
const {admit}=require('./browser_monitoring_probe.js');
process.env.VG_BROWSER_AGENT='synthetic-owned-agent';
const origin='http://localhost:12345';
const form={host:'localhost:12345','user-agent':'synthetic-owned-agent',origin:'null','sec-fetch-site':'same-origin','sec-fetch-mode':'navigate','sec-fetch-dest':'document'};
const request=(headers=form,url='/login',method='POST')=>({headers,url,method});
test('only same-origin owned form null tuple or exact origin admitted',()=>{
  assert.equal(admit(request(),origin).pathname,'/login');
  assert.equal(admit(request({...form,origin}),origin).pathname,'/login');
  for(const key of ['sec-fetch-site','sec-fetch-mode','sec-fetch-dest'])for(const value of [undefined,'cross-site','no-cors','empty'])
    assert.throws(()=>admit(request({...form,[key]:value}),origin));
  for(const value of [undefined,'','http://foreign.invalid','http://localhost:12346'])assert.throws(()=>admit(request({...form,origin:value}),origin));
});
test('foreign host, agent and absolute request targets refused',()=>{
  for(const key of ['host','user-agent'])assert.throws(()=>admit(request({...form,[key]:'foreign'}),origin));
  for(const url of ['https://foreign.invalid/login','//foreign.invalid/login','login'])assert.throws(()=>admit(request(form,url),origin));
});
test('no telemetry API, arbitrary asset, path, method or state changing device UI',()=>{
  for(const url of ['/api/v1/telemetry','/api/v1/devices','/assets/other.js','/monitoring/other','/.env','/../.env'])assert.throws(()=>admit(request(form,url,'GET'),origin));
  for(const method of ['PUT','DELETE','OPTIONS','PATCH'])assert.throws(()=>admit(request(form,'/login',method),origin));
  assert.throws(()=>admit(request(form,'/monitoring','POST'),origin));
  assert.throws(()=>admit(request(form,'/assets/monitoring-freshness.js','POST'),origin));
});
test('fixed UI paths admit read only with owned host and agent',()=>{
  const headers={host:form.host,'user-agent':form['user-agent']};
  for(const url of ['/','/login','/monitoring','/monitoring/runtime%3Ademo','/assets/monitoring-freshness.js?v=publichash'])
    for(const method of ['GET','HEAD'])assert(admit(request(headers,url,method),origin));
});
