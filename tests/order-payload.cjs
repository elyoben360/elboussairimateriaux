const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/catalogue.js','utf8');
const DATA=JSON.parse(fs.readFileSync('content/catalogue.json','utf8'));
const fields={client:{value:' Test client '},phone:{value:'+212600000000'},site:{value:' Test address '},date:{value:''},notes:{value:'Accès test'}};
const context=vm.createContext({DATA,cart:[],$:id=>fields[id]});
for(const name of ['cleanDimension','variantTitle','orderPayload','message']){const start=source.indexOf('function '+name+'(');const end=source.indexOf('\n',start);vm.runInContext(source.slice(start,end),context)}
let count=0;for(const p of DATA){for(let i=0;i<p.variants.length;i++){context.cart=[{kind:'mat',product:p.slug,variant:p.variants[i].id,title:vm.runInContext(`variantTitle(DATA.find(p=>p.slug===${JSON.stringify(p.slug)}).variants[${i}],' — ')`,context),qty:2.5,unit:p.units?.[0]||'unité',delivery:'Avec livraison — transport à organiser',vehicle:'Camion-grue',spec:'Test'}];const payload=vm.runInContext('orderPayload()',context);assert.equal(payload.items[0].product,p.slug);assert.equal(payload.items[0].variant,p.variants[i].id);assert.equal(payload.items[0].delivery,'delivery');assert.equal(payload.client,'Test client');assert.match(vm.runInContext('message()',context),/COMMANDE — BANANA MATÉRIAUX/);count++}}

// Durable identity survives catalogue reorder/renaming; legacy index is never trusted.
const first=DATA[0],variant=first.variants[0];context.cart=[{product:first.slug,variant:variant.id,title:'Previous display label',qty:1,unit:'sac',delivery:'Sans livraison'}];first.variants.reverse();assert.equal(vm.runInContext('orderPayload()',context).items[0].variant,variant.id);
context.cart=[{product:first.slug,variant:999,title:vm.runInContext(`variantTitle(DATA[0].variants[0],' — ')`,context),qty:1,unit:'sac',delivery:'Sans livraison'}];assert.equal(vm.runInContext('orderPayload()',context).items[0].variant,first.variants[0].id);
// Removed stable IDs must never be remapped to a new catalogue item with the same title.
const stableLine={product:first.slug,variant:variant.id,title:vm.runInContext(`variantTitle(DATA[0].variants[0],' — ')`,context),qty:1,unit:'sac',delivery:'Sans livraison'};context.cart=[stableLine];const beforeRemoval=JSON.stringify(vm.runInContext('orderPayload()',context));first.variants=first.variants.filter(v=>v.id!==variant.id);assert.equal(JSON.stringify(vm.runInContext('orderPayload()',context)),beforeRemoval);DATA.splice(DATA.indexOf(first),1);assert.equal(JSON.stringify(vm.runInContext('orderPayload()',context)),beforeRemoval);
context.cart=[{title:'Unknown former product',qty:1,delivery:'Sans livraison'}];assert.throws(()=>vm.runInContext('orderPayload()',context),/ancienne référence/);
assert(!/paiement|règlement/i.test(fs.readFileSync('src/home.html','utf8')));
console.log(`Order payload: ${count} catalogue variants, contact trimming, delivery mapping, message and unresolved legacy reference passed.`);
