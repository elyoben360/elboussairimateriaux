import catalogue from '../content/catalogue.json' with {type: 'json'};

const MAX_BYTES = 24000;
const json = (value, status = 200) => Response.json(value, {status, headers: {'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', 'X-Robots-Tag': 'noindex'}});
const fail = (message, status = 400) => { throw Object.assign(new Error(message), {status}); };
const digest = async value => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value))), x => x.toString(16).padStart(2, '0')).join('');
const equal = (a, b) => { let result = a.length ^ b.length; for (let i = 0; i < Math.max(a.length, b.length); i++) result |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0); return result === 0; };
const field = (value, max, required = false) => {
  if (value === undefined && !required) return '';
  if (typeof value !== 'string' || value.length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value)) fail('Champ invalide ou trop long.');
  const text = value.trim(); if (required && !text) fail('Complétez les champs obligatoires.'); return text;
};
function units(p) {
  const s = (p.product + ' ' + p.family).toLowerCase();
  if (p.units) return p.units;
  if (/madrier/.test(s)) return ['mètre linéaire'];
  if (/polystyrène/.test(s)) return ['m³'];
  if (/agrégat|sable|granulat/.test(s)) return ['m³', 'voyage', 'sac', 'tonne'];
  if (/fer à béton/.test(s)) return ['kg', 'tonne', 'barre'];
  if (/panneaux muraux/.test(s)) return ['panneau', 'm²'];
  if (/treillis/.test(s)) return ['unité', 'panneau'];
  if (/ciment|colle|emufal/.test(s)) return ['sac', 'tonne', 'palette'];
  if (/agglo|brique|hourdis/.test(s)) return ['unité', 'palette'];
  if (/poutrelle|madrier|baguette/.test(s)) return ['unité', 'mètre linéaire'];
  if (/membrane|film|polystyrène/.test(s)) return ['m²', 'rouleau', 'unité'];
  return ['unité', 'kg', 'mètre linéaire'];
}
function normalizeOrder(b) {
  if (!b || typeof b !== 'object' || Array.isArray(b) || b.confirmed !== true) fail('Confirmez le récapitulatif de votre commande.');
  if (!Array.isArray(b.items) || b.items.length < 1 || b.items.length > 50) fail('La commande doit contenir entre 1 et 50 lignes.');
  const client = field(b.client, 120, true), phone = field(b.phone, 30, true), site = field(b.site, 300, true);
  if (client.length < 2 || !/^[+\d ().-]{6,30}$/.test(phone) || phone.replace(/\D/g, '').length < 6) fail('Vérifiez votre nom et votre téléphone.');
  const date = field(b.date, 10), notes = field(b.notes, 2000);
  if (date && (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !Number.isFinite(Date.parse(date)) || new Date(date).toISOString().slice(0, 10) !== date)) fail('Date invalide.');
  const items = b.items.map(item => {
    if (!item || typeof item !== 'object' || Array.isArray(item)) fail('Ligne invalide.');
    const product = field(item.product, 100, true), variant = field(item.variant, 120, true), unit = field(item.unit, 30, true);
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(product) || !/^[a-z0-9]+(?:-[a-z0-9]+)*-v[0-9]{2,}$/.test(variant)) fail('Identifiant de référence invalide.');
    if (typeof item.qty !== 'number' || !Number.isFinite(item.qty) || item.qty < 0.01 || item.qty > 1000000 || Math.abs(item.qty * 100 - Math.round(item.qty * 100)) > 0.000001) fail('Quantité invalide (0,01 à 1 000 000, deux décimales maximum).');
    if (!['pickup', 'delivery'].includes(item.delivery)) fail('Unité ou mode de fourniture invalide.');
    return {product, variant, qty: item.qty, unit, spec: field(item.spec, 300), delivery: item.delivery, vehicle: item.delivery === 'delivery' ? field(item.vehicle, 100) : ''};
  });
  return {client, phone, site, date, notes, confirmed: true, items};
}
export function validateOrder(b) {
  const normalized = normalizeOrder(b);
  return {...normalized, items: normalized.items.map(item => {
    const product = catalogue.find(p => p.slug === item.product);
    const variant = product?.variants.find(v => v.id === item.variant);
    if (!variant) fail('Référence absente du catalogue.');
    if (!units(product).includes(item.unit)) fail('Unité invalide.');
    return {...item, title: variant.name, dimension: variant.dimension};
  })};
}
async function readBody(req) {
  if (Number(req.headers.get('Content-Length') || 0) > MAX_BYTES) fail('Requête trop longue.', 413);
  const reader = req.body?.getReader(); if (!reader) fail('Commande requise.');
  let length = 0; const chunks = [];
  while (true) { const {done, value} = await reader.read(); if (done) break; length += value.byteLength; if (length > MAX_BYTES) { await reader.cancel(); fail('Requête trop longue.', 413); } chunks.push(value); }
  const bytes = new Uint8Array(length); let offset = 0; for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  try { return JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(bytes)); } catch { fail('JSON invalide.'); }
}
export async function handleOrders(req, env) {
  try {
    const u = new URL(req.url);
    const privateRoute = u.pathname === '/api/orders/private';
    if (u.pathname !== '/api/orders' && !privateRoute) return json({error: 'Route introuvable'}, 404);
    // Always closed without the existing server secret. Never trust client admin headers.
    if (privateRoute && (!env.JOURNAL_ADMIN_TOKEN || !equal(req.headers.get('Authorization') || '', 'Bearer ' + env.JOURNAL_ADMIN_TOKEN))) return json({error: 'Accès refusé'}, 403);
    if (req.method !== (privateRoute ? 'GET' : 'POST')) return json({error: 'Méthode refusée'}, 405);
    // Intake stays closed until explicitly enabled and private operator access is configured.
    if (!privateRoute && (env.ORDERS_ENABLED !== 'true' || !env.JOURNAL_ADMIN_TOKEN)) return json({error: 'Réception des commandes temporairement indisponible.'}, 503);
    if (!privateRoute && (req.headers.get('Origin') !== u.origin || ['cross-site', 'same-site'].includes(req.headers.get('Sec-Fetch-Site')))) return json({error: 'Origine refusée'}, 403);
    if (!privateRoute && req.headers.get('Content-Type')?.split(';')[0].trim().toLowerCase() !== 'application/json') return json({error: 'JSON requis', rejectedBeforeInsert: true}, 415);
    if (!env.JOURNAL) return json({error: 'Réception des commandes temporairement indisponible.'}, 503);
    const headers = new Headers(req.headers); headers.delete('X-Order-Admin'); headers.delete('Authorization');
    headers.set('X-Order-Rate', await digest((req.headers.get('CF-Connecting-IP') || 'unknown') + ':' + Math.floor(Date.now() / 86400000)));
    if (privateRoute) headers.set('X-Order-Admin', 'yes');
    return await env.JOURNAL.get(env.JOURNAL.idFromName('zone-industrielle-v1')).fetch(new Request(req, {headers}));
  } catch (e) { return json({error: e.status ? e.message : 'Réception des commandes temporairement indisponible.'}, e.status || 503); }
}
export function initOrders(sql) {
  sql.exec(`CREATE TABLE IF NOT EXISTS orders(reference TEXT PRIMARY KEY, idempotency_hash TEXT UNIQUE NOT NULL, payload_hash TEXT NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL, created INTEGER NOT NULL)`);
  sql.exec('CREATE INDEX IF NOT EXISTS orders_created ON orders(created)');
  sql.exec('CREATE INDEX IF NOT EXISTS orders_created_reference ON orders(created DESC,reference DESC)');
}
export async function routeOrders(req, store) {
  let insertionAttempted = false;
  try {
    const u = new URL(req.url);
    if (u.pathname === '/api/orders/private' && req.method === 'GET') {
      if (req.headers.get('X-Order-Admin') !== 'yes') fail('Accès refusé', 403);
      // Small private operator inbox; all paths require server-verified authorization.
      const reference = u.searchParams.get('reference'), cursor = u.searchParams.get('cursor');
      if ([...u.searchParams.keys()].some(key => !['reference', 'cursor'].includes(key)) || u.searchParams.getAll('reference').length > 1 || u.searchParams.getAll('cursor').length > 1 || (reference !== null && cursor !== null)) fail('Paramètres de consultation invalides.');
      if (reference === null) {
        let boundary = null;
        if (cursor !== null) {
          const match = /^(0|[1-9][0-9]{0,15}):(BM-[A-F0-9]{32})$/.exec(cursor);
          if (!match || !Number.isSafeInteger(Number(match[1])) || Number(match[1]) > 8640000000000000) fail('Curseur invalide.');
          boundary = {created: Number(match[1]), reference: match[2]};
        }
        // Keyset pagination preserves timestamp ties and avoids offset drift on new arrivals.
        const select = "SELECT reference,status,created,json_extract(payload,'$.client') AS client FROM orders";
        const rows = boundary
          ? store.rows(select + ' WHERE created < ? OR (created = ? AND reference < ?) ORDER BY created DESC,reference DESC LIMIT 21', boundary.created, boundary.created, boundary.reference)
          : store.rows(select + ' ORDER BY created DESC,reference DESC LIMIT 21');
        const page = rows.slice(0, 20), last = page.at(-1);
        return json({orders: page.map(row => ({reference: row.reference, status: row.status, receivedAt: new Date(row.created).toISOString(), client: row.client})), nextCursor: rows.length > 20 ? `${last.created}:${last.reference}` : null});
      }
      if (!/^BM-[A-F0-9]{32}$/.test(reference || '')) fail('Référence invalide.');
      const row = store.rows('SELECT reference,payload,status,created FROM orders WHERE reference=?', reference)[0];
      if (!row) fail('Commande introuvable.', 404);
      return json({reference: row.reference, status: row.status, receivedAt: new Date(row.created).toISOString(), order: JSON.parse(row.payload)});
    }
    if (u.pathname !== '/api/orders' || req.method !== 'POST') fail('Route introuvable', 404);
    await store.rate('orders-attempt:' + req.headers.get('X-Order-Rate'), 30, 3600000);
    const key = req.headers.get('Idempotency-Key') || '';
    if (!/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(key)) fail('Identifiant de commande invalide.');
    const normalized = normalizeOrder(await readBody(req));
    // Hash only stable client intent, never mutable catalogue labels or dimensions.
    const idempotencyHash = await digest(key.toLowerCase()), payloadHash = await digest(JSON.stringify(normalized));
    let reference, replay = false;
    // No await inside the transaction: uniqueness check and insert are atomic.
    store.ctx.storage.transactionSync(() => {
      const existing = store.rows('SELECT reference,payload_hash FROM orders WHERE idempotency_hash=?', idempotencyHash)[0];
      if (existing) {
        if (existing.payload_hash !== payloadHash) fail('Ce récapitulatif a changé. Préparez une nouvelle confirmation.', 409);
        reference = existing.reference; replay = true; return;
      }
      // A retry is resolved above before checking the current catalogue.
      const payload = JSON.stringify(validateOrder(normalized));
      reference = 'BM-' + crypto.randomUUID().replaceAll('-', '').toUpperCase();
      insertionAttempted = true;
      store.sql.exec('INSERT INTO orders(reference,idempotency_hash,payload_hash,payload,status,created) VALUES(?,?,?,?,?,?)', reference, idempotencyHash, payloadHash, payload, 'received', Date.now());
    });
    // Explicitly wait for durable persistence; never acknowledge a failed write.
    await store.ctx.storage.sync();
    return json({ok: true, status: 'received', reference}, replay ? 200 : 201);
  } catch (e) {
    // This certifies only this request, not earlier attempts with the same key.
    // Clients may release their pending guard only on their very first transmission.
    const rejectedBeforeInsert = !insertionAttempted && req.method === 'POST' && new URL(req.url).pathname === '/api/orders' && [400, 413, 415, 429].includes(e.status);
    return json({error: e.status ? e.message : 'Réception des commandes temporairement indisponible.', ...(rejectedBeforeInsert ? {rejectedBeforeInsert: true} : {})}, e.status || 503);
  }
}
