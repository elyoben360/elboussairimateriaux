import {DatabaseSync} from 'node:sqlite';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import catalogue from '../content/catalogue.json' with {type: 'json'};
import * as orderModule from '../server/orders.mjs';
globalThis.testOrders = orderModule;
const code = (await fs.readFile(new URL('../server/worker.mjs', import.meta.url), 'utf8'))
  .replace("import {DurableObject} from 'cloudflare:workers';", 'class DurableObject {constructor(){}}')
  .replace("import articles from './articles.json';", 'const articles=[];')
  .replace("import {moderate} from './moderation.mjs';", 'const moderate=()=>{};')
  .replace("import {handleOrders, initOrders, routeOrders} from './orders.mjs';", 'const {handleOrders,initOrders,routeOrders}=globalThis.testOrders;');
const {JournalStore, default: worker} = await import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'));
const db = new DatabaseSync(':memory:'); let syncFailure = false, writeFailure = false, syncs = 0;
const storage = {
  sql: {exec(sql, ...params) { if (writeFailure && sql.startsWith('INSERT INTO orders')) throw Error('simulated private storage error'); const query = db.prepare(sql); if (query.columns().length) return query.all(...params); query.run(...params); return []; }},
  getAlarm: async () => 1, setAlarm: async () => {},
  sync: async () => { if (syncFailure) throw Error('simulated disk sync error'); syncs++; },
  transactionSync(fn) { db.exec('BEGIN'); try { fn(); db.exec('COMMIT'); } catch (e) { db.exec('ROLLBACK'); throw e; } }
};
const store = new JournalStore({storage}, {}), origin = 'https://bananamateriaux.ma';
const env = {ORDERS_ENABLED: 'true', JOURNAL: {idFromName(name) { assert.equal(name, 'zone-industrielle-v1'); return name; }, get() { return store; }}, JOURNAL_ADMIN_TOKEN: 'test-only-not-real-secret'};
const input = {client: 'Client fictif', phone: '+212 600 000 000', site: 'Chantier de test', date: '2026-12-10', notes: 'Données fictives', confirmed: true, items: [{product: 'ciments', variant: 'ciments-v01', qty: 2.5, unit: 'tonne', delivery: 'delivery', vehicle: 'À étudier', spec: 'Test'}]};
let ip = 0;
function request(body = input, {path = '/api/orders', method = 'POST', key = crypto.randomUUID(), headers = {}, raw, environment = env} = {}) {
  const h = {Origin: origin, 'Content-Type': 'application/json', 'Idempotency-Key': key, 'CF-Connecting-IP': `192.0.2.${++ip}`, ...headers};
  return worker.fetch(new Request(origin + path, {method, headers: h, body: method === 'POST' ? (raw ?? JSON.stringify(body)) : undefined}), environment);
}
// Closed by default: no body read and no Durable Object lookup before explicit activation.
for (const configuration of [{}, {ORDERS_ENABLED: true, JOURNAL_ADMIN_TOKEN: 'test-only'}, {ORDERS_ENABLED: 'false', JOURNAL_ADMIN_TOKEN: 'test-only'}, {JOURNAL_ADMIN_TOKEN: 'test-only'}, {ORDERS_ENABLED: 'true'}, {ORDERS_ENABLED: 'true', JOURNAL_ADMIN_TOKEN: ''}]) {
  let bodyRead = false, forwarded = false;
  const blockedRequest = {url: origin + '/api/orders', method: 'POST', headers: new Headers({Origin: origin, 'Content-Type': 'application/json'}), get body() { bodyRead = true; throw Error('Body must not be read'); }};
  const blockedResponse = await orderModule.handleOrders(blockedRequest, {...configuration, JOURNAL: {idFromName() { forwarded = true; throw Error('Must not forward'); }}});
  assert.equal(blockedResponse.status, 503); assert.equal((await blockedResponse.json()).rejectedBeforeInsert, undefined); assert.equal(bodyRead, false); assert.equal(forwarded, false); assert.equal(db.prepare('SELECT count(*) n FROM orders').get().n, 0);
}
const key = crypto.randomUUID();
let response = await request(input, {key}); assert.equal(response.status, 201);
const receipt = await response.json(); assert.deepEqual(Object.keys(receipt).sort(), ['ok', 'reference', 'status']); assert.equal(receipt.status, 'received'); assert.match(receipt.reference, /^BM-[A-F0-9]{32}$/); assert.equal(syncs, 1);
// Stable catalogue ids are explicit, unique and cover every variant.
const variantIds = catalogue.flatMap(product => product.variants.map(variant => { assert.match(variant.id, new RegExp('^' + product.slug + '-v[0-9]{2,}$')); return variant.id; }));
assert.equal(variantIds.length, 58); assert.equal(new Set(variantIds).size, 58);
assert.equal(db.prepare('SELECT count(*) n FROM orders').get().n, 1);
assert.equal(JSON.parse(db.prepare('SELECT payload FROM orders').get().payload).phone, input.phone);
response = await request(input, {key}); assert.equal(response.status, 200); assert.deepEqual(await response.json(), receipt); assert.equal(db.prepare('SELECT count(*) n FROM orders').get().n, 1);
// Replays survive renamed, reordered and even removed catalogue references.
const cement = catalogue.find(product => product.slug === 'ciments'), savedVariants = structuredClone(cement.variants);
cement.variants[0].name = 'Nouveau libellé'; cement.variants[0].dimension = 'Nouvelle dimension'; cement.variants.reverse();
assert.equal(orderModule.validateOrder(input).items[0].title, 'Nouveau libellé');
response = await request(input, {key}); assert.equal(response.status, 200); assert.deepEqual(await response.json(), receipt);
cement.variants.length = 0;
response = await request(input, {key}); assert.equal(response.status, 200); assert.deepEqual(await response.json(), receipt);
assert.equal((await request(input)).status, 400); // A new order must still validate against the current catalogue.
assert.equal((await request({...input, notes: 'Changed'}, {key})).status, 409);
cement.variants.push(...savedVariants);
assert.equal(JSON.parse(db.prepare('SELECT payload FROM orders WHERE reference=?').get(receipt.reference).payload).items[0].title, savedVariants[0].name);
response = await request({...input, notes: 'Changed'}, {key}); assert.equal(response.status, 409);
for (const body of [null, [], {...input, confirmed: false}, {...input, items: []}, {...input, client: 'x'.repeat(121)}, {...input, phone: 'no'}, {...input, date: '2026-02-30'}, {...input, items: [{...input.items[0], product: 'unknown'}]}, {...input, items: [{...input.items[0], variant: 999}]}, {...input, items: [{...input.items[0], qty: '2'}]}, {...input, items: [{...input.items[0], qty: 0}]}, {...input, items: [{...input.items[0], qty: 1.001}]}, {...input, items: [{...input.items[0], unit: 'invalid'}]}, {...input, items: Array(51).fill(input.items[0])}]) {
  assert.equal((await request(body)).status, 400);
}
assert.equal((await request(input, {raw: '{'})).status, 400);
assert.equal((await request(input, {key: 'not-a-key'})).status, 400);
assert.equal((await request(input, {raw: 'x'.repeat(24001)})).status, 413);
assert.equal((await request(input, {headers: {Origin: 'https://evil.test'}})).status, 403);
assert.equal((await request(input, {headers: {Origin: ''}})).status, 403);
assert.equal((await request(input, {headers: {'Sec-Fetch-Site': 'cross-site'}})).status, 403);
assert.equal((await request(input, {headers: {'Content-Type': 'text/plain'}})).status, 415);
assert.equal((await request(input, {headers: {'Content-Type': 'application/json-evil'}})).status, 415);
assert.equal((await request(input, {environment: {}})).status, 503);
assert.equal((await request(input, {method: 'GET'})).status, 405);
const privatePath = '/api/orders/private?reference=' + receipt.reference;
for (const headers of [{}, {'X-Order-Admin': 'yes'}, {Authorization: 'Bearer wrong'}]) assert.equal((await request(null, {path: privatePath, method: 'GET', headers})).status, 403);
assert.equal((await request(null, {path: privatePath, method: 'GET', headers: {Authorization: 'Bearer undefined'}, environment: {JOURNAL: env.JOURNAL}})).status, 403);
response = await request(null, {path: privatePath, method: 'GET', headers: {Authorization: 'Bearer ' + env.JOURNAL_ADMIN_TOKEN}}); assert.equal(response.status, 200); assert.equal((await response.json()).order.phone, input.phone);
response = await request(null, {path: '/api/orders/private', method: 'GET', headers: {Authorization: 'Bearer ' + env.JOURNAL_ADMIN_TOKEN}}); assert.equal(response.status, 200); assert.equal((await response.json()).orders.length, 1);
assert.equal((await request(null, {path: '/api/orders/private', method: 'GET'})).status, 403);
assert.equal((await request(null, {path: '/api/orders/private', method: 'GET', headers: {Authorization: 'Bearer undefined'}, environment: {JOURNAL: env.JOURNAL}})).status, 403);
assert.equal((await request(null, {path: '/api/orders/' + receipt.reference, method: 'GET'})).status, 404);
writeFailure = true; response = await request(); assert.equal(response.status, 503); assert.deepEqual(await response.json(), {error: 'Réception des commandes temporairement indisponible.'}); writeFailure = false;
assert.equal(db.prepare('SELECT count(*) n FROM orders').get().n, 1);
syncFailure = true; const uncertainKey = crypto.randomUUID(); response = await request(input, {key: uncertainKey}); assert.equal(response.status, 503); assert.equal((await response.json()).ok, undefined); syncFailure = false;
response = await request(input, {key: uncertainKey}); assert.equal(response.status, 200); assert.equal(db.prepare('SELECT count(*) n FROM orders').get().n, 2);
// Concurrent retries cannot create two records even across an async read/hash boundary.
const simultaneousKey = crypto.randomUUID(); const pair = await Promise.all([request(input, {key: simultaneousKey}), request(input, {key: simultaneousKey})]); assert.deepEqual(pair.map(r => r.status).sort(), [200, 201]); assert.equal((await pair[0].json()).reference, (await pair[1].json()).reference);
for (let i = 0; i < 30; i++) assert.equal((await request(input, {raw: '{', headers: {'CF-Connecting-IP': '198.51.100.1'}})).status, 400);
assert.equal((await request(input, {headers: {'CF-Connecting-IP': '198.51.100.1'}})).status, 429);
// New order setup is additive and leaves the existing journal data intact.
db.prepare('INSERT INTO members(id,email,name,profile,created) VALUES(?,?,?,?,?)').run('existing-test', 'test@example.test', 'Existing', '{}', 1);
new JournalStore({storage}, {}); assert.equal(db.prepare('SELECT name FROM members WHERE id=?').get('existing-test').name, 'Existing');
for (const host of ['elboussairimateriaux.com', 'www.elboussairimateriaux.com']) assert.equal((await worker.fetch(new Request('https://' + host + '/api/orders', {method: 'POST'}), env)).status, 404);
// Explicit rejection means no insertion in this request, not in a previous attempt.
const countBeforeRejection = db.prepare('SELECT count(*) n FROM orders').get().n;
for (const [body, options, status] of [
  [{...input, confirmed: false}, {}, 400],
  [input, {raw: 'x'.repeat(24001)}, 413],
  [input, {headers: {'Content-Type': 'text/plain'}}, 415],
  [input, {headers: {'CF-Connecting-IP': '198.51.100.1'}}, 429]
]) {
  response = await request(body, options); assert.equal(response.status, status); assert.equal((await response.json()).rejectedBeforeInsert, true);
  assert.equal(db.prepare('SELECT count(*) n FROM orders').get().n, countBeforeRejection);
}
response = await request({...input, notes: 'Changed again'}, {key}); assert.equal(response.status, 409); assert.equal((await response.json()).rejectedBeforeInsert, undefined);
writeFailure = true; response = await request(); assert.equal(response.status, 503); assert.equal((await response.json()).rejectedBeforeInsert, undefined); writeFailure = false;
syncFailure = true; response = await request(input, {key}); assert.equal(response.status, 503); assert.equal((await response.json()).rejectedBeforeInsert, undefined); syncFailure = false;
// A marked rejection on a retry must NEVER be interpreted as no prior order.
response = await request(input, {key, headers: {'Content-Type': 'text/plain'}}); assert.equal(response.status, 415); assert.equal((await response.json()).rejectedBeforeInsert, true);
assert.equal(db.prepare('SELECT count(*) n FROM orders WHERE reference=?').get(receipt.reference).n, 1);
response = await request(input, {key}); assert.equal(response.status, 200); assert.deepEqual(await response.json(), receipt);
// Operator inbox is bounded and sorted, exposing no telephone/address/notes.
// All 45 seeds share one timestamp, spanning three pages and exercising the tie-breaker.
for (let i = 0; i < 45; i++) db.prepare('INSERT INTO orders VALUES(?,?,?,?,?,?)').run('BM-' + String(i).padStart(32, '0'), 'seed-' + i, 'hash-' + i, JSON.stringify({client: 'Fictif ' + i, phone: 'private'}), 'received', 2000000000000);
const adminHeaders = {Authorization: 'Bearer ' + env.JOURNAL_ADMIN_TOKEN};
const list = async (query = '') => request(null, {path: '/api/orders/private' + query, method: 'GET', headers: adminHeaders});
response = await list(); assert.equal(response.status, 200);
const firstPage = await response.json(), inbox = firstPage.orders;
assert.equal(inbox.length, 20); assert.equal(inbox[0].client, 'Fictif 44'); assert.equal(inbox.at(-1).client, 'Fictif 25'); assert.deepEqual(Object.keys(inbox[0]).sort(), ['client', 'receivedAt', 'reference', 'status']);
assert.equal(firstPage.nextCursor, '2000000000000:BM-' + String(25).padStart(32, '0'));
// A newer arrival after the first page must not shift or duplicate the next page.
db.prepare('INSERT INTO orders VALUES(?,?,?,?,?,?)').run('BM-' + 'F'.repeat(32), 'new-arrival', 'new-hash', JSON.stringify({client: 'New arrival'}), 'received', 2000000000001);
const secondPage = await (await list('?cursor=' + encodeURIComponent(firstPage.nextCursor))).json();
assert.equal(secondPage.orders.length, 20); assert.equal(secondPage.orders[0].client, 'Fictif 24'); assert.equal(secondPage.orders.at(-1).client, 'Fictif 5');
const lastPage = await (await list('?cursor=' + encodeURIComponent(secondPage.nextCursor))).json();
assert.equal(lastPage.orders.length, 8); assert.equal(lastPage.orders[0].client, 'Fictif 4'); assert.equal(lastPage.nextCursor, null);
const seen = [...firstPage.orders, ...secondPage.orders, ...lastPage.orders].map(row => row.reference);
assert.equal(new Set(seen).size, 48); assert.equal(seen.length, 48);
const expected = db.prepare('SELECT reference FROM orders WHERE reference != ? ORDER BY created DESC,reference DESC').all('BM-' + 'F'.repeat(32)).map(row => row.reference); assert.deepEqual(seen, expected);
const finalRow = lastPage.orders.at(-1), endCursor = Date.parse(finalRow.receivedAt) + ':' + finalRow.reference;
assert.deepEqual(await (await list('?cursor=' + encodeURIComponent(endCursor))).json(), {orders: [], nextCursor: null});
for (const cursor of ['', 'garbage', '-1:BM-' + 'A'.repeat(32), '01:BM-' + 'A'.repeat(32), '1.5:BM-' + 'A'.repeat(32), '1e3:BM-' + 'A'.repeat(32), '8640000000000001:BM-' + 'A'.repeat(32), '9007199254740992:BM-' + 'A'.repeat(32), '1000:BM-' + 'a'.repeat(32), '1000:BM-ABC', firstPage.nextCursor + ':extra', 'x'.repeat(1000)]) assert.equal((await list('?cursor=' + encodeURIComponent(cursor))).status, 400);
for (const query of ['?cursor=' + encodeURIComponent(firstPage.nextCursor) + '&cursor=' + encodeURIComponent(firstPage.nextCursor), '?reference=' + receipt.reference + '&cursor=' + encodeURIComponent(firstPage.nextCursor), '?limit=1000', '?reference=' + receipt.reference + '&reference=' + receipt.reference]) assert.equal((await list(query)).status, 400);
for (const query of ['?cursor=' + encodeURIComponent(firstPage.nextCursor), '?cursor=invalid']) {
  for (const headers of [{}, {'X-Order-Admin': 'yes'}, {Authorization: 'Bearer wrong'}]) assert.equal((await request(null, {path: '/api/orders/private' + query, method: 'GET', headers})).status, 403);
  assert.equal((await request(null, {path: '/api/orders/private' + query, method: 'GET', headers: adminHeaders, environment: {JOURNAL: env.JOURNAL}})).status, 403);
}
console.log('Orders backend: persistence, duplicate/concurrent retries, validation, bounded input, CSRF, rate limit, private access, stable pagination, closed storage failures, additive schema and old-domain guards passed.');
