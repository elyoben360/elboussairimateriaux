// Runs the actual frontend guard without a browser; the server simulator commits before losing its response.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const {webcrypto}=require('node:crypto');
const source=fs.readFileSync('src/catalogue.js','utf8');
const code=source.slice(source.indexOf('class OrderSubmissionGuard {'),source.indexOf('let orderStep=1;'));
const Guard=vm.runInNewContext(code+'\nOrderSubmissionGuard',{TextEncoder});
(async()=>{
 const disk=new Map();const storage={getItem:k=>disk.get(k)||null,setItem:(k,v)=>disk.set(k,v)};
 let client=new Guard(storage,webcrypto);const payload=JSON.stringify({client:'Private Test Person',phone:'0600123456',site:'Private Test Address',items:[{qty:2}]});const modified=payload.replace('"qty":2','"qty":3');
 const db=new Map();let calls=0;
 function server(attempt,body,loseResponse=false){calls++;const existing=db.get(attempt.key);if(existing)assert.equal(existing.body,body);else db.set(attempt.key,{body,reference:'BM-RECOVERED'});if(loseResponse)throw new Error('Response lost after persistence');return db.get(attempt.key).reference}
 const first=await client.prepare(payload);assert.throws(()=>server(first,payload,true),/Response lost/);assert.equal(db.size,1);
 await assert.rejects(()=>client.prepare(modified),/transmission précédente/);assert.equal(calls,1);
 // Reload constructs a new guard with only stored digest/key, not the private form body.
 client=new Guard(storage,webcrypto);await assert.rejects(()=>client.prepare(modified),/transmission précédente/);
 const retry=await client.prepare(payload);assert.equal(retry.key,first.key);const reference=server(retry,payload);client.confirm(retry,reference);assert.equal(db.size,1);assert.equal(calls,2);
 client=new Guard(storage,webcrypto);const receipt=await client.prepare(payload);assert.equal(receipt.reference,'BM-RECOVERED');assert.equal(calls,2);
 const next=await client.prepare(modified);assert.notEqual(next.key,first.key);assert.equal(db.size,1);
 const saved=JSON.stringify([...disk.values()]);for(const privateValue of ['Private Test Person','0600123456','Private Test Address','"qty"'])assert(!saved.includes(privateValue));
 const refused=new Guard({getItem:()=>null,setItem:()=>{throw Error('Storage unavailable')}},webcrypto);await assert.rejects(()=>refused.prepare(payload),/Storage unavailable/);
 const silent=new Guard({getItem:()=>null,setItem:()=>{}},webcrypto);await assert.rejects(()=>silent.prepare(payload),/conserver/);
 const broken=new Guard({getItem:()=>'{broken',setItem:()=>{}},webcrypto);await assert.rejects(()=>broken.prepare(payload));
 // Definitive rejection frees only the exact first attempt, never an uncertain retry.
 const fresh=()=>{const m=new Map();return new Guard({getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,v)},webcrypto)};
 for(const status of [400,413,415,429]){const g=fresh();const a=await g.prepare(payload);assert.equal(a.isFirstTransmission,true);assert.equal(g.reject({...a,key:'wrong'},status,{error:'Rejected',rejectedBeforeInsert:true}),false);assert.equal(g.reject(a,status,{error:'Rejected',rejectedBeforeInsert:true}),true);assert.notEqual((await g.prepare(modified)).key,a.key)}
 for(const [status,data] of [[400,{error:'Rejected'}],[409,{error:'Conflict',rejectedBeforeInsert:true}],[503,{error:'Down',rejectedBeforeInsert:true}],[429,null],[400,{error:'Rejected',rejectedBeforeInsert:'true'}]]){const g=fresh();const a=await g.prepare(payload);assert.equal(g.reject(a,status,data),false);await assert.rejects(()=>g.prepare(modified),/transmission précédente/)}
 for(const status of [400,429]){const g=fresh();const a=await g.prepare(payload);server(a,payload); // committed, response unseen by guard
 const reloaded=new Guard(g.storage,webcrypto);const replay=await reloaded.prepare(payload);assert.equal(replay.isFirstTransmission,false);assert.equal(g.reject(replay,status,{error:'Rejected',rejectedBeforeInsert:true}),false);await assert.rejects(()=>g.prepare(modified),/transmission précédente/)}
 const dated=fresh();const datedPayload=JSON.stringify({date:'2026-11-05',client:'Private Test Person'});const beforeMidnight=await dated.prepare(datedPayload,{date:'2026-11-05',today:'2026-11-05'});const datedReload=new Guard(dated.storage,webcrypto);const afterMidnight=await datedReload.prepare(datedPayload,{date:'2026-11-05',today:'2026-11-06'});assert.equal(afterMidnight.key,beforeMidnight.key);assert.equal(afterMidnight.isFirstTransmission,false);
 const newPast=fresh();await assert.rejects(()=>newPast.prepare(datedPayload,{date:'2026-11-05',today:'2026-11-06'}),/aujourd’hui/);assert.equal(newPast.read().pending,null);
 console.log('Order recovery: persisted/lost response, modified-payload block, exact retry, reload reconciliation, receipt replay, no PII storage, fail-closed storage, definitive first rejection, uncertain retry rejection and midnight replay passed.');
})().catch(e=>{console.error(e);process.exit(1)});
