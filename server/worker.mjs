import {DurableObject} from 'cloudflare:workers';
import articles from './articles.json';
import {moderate} from './moderation.mjs';
import {handleOrders, initOrders, routeOrders} from './orders.mjs';
const enc=new TextEncoder();const now=()=>Date.now();const day=86400000;
const json=(v,status=200,headers={})=>Response.json(v,{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff',...headers}});
const clean=(v,n=100)=>typeof v==='string'?v.trim().slice(0,n):'';
const token=()=>Array.from(crypto.getRandomValues(new Uint8Array(32)),x=>x.toString(16).padStart(2,'0')).join('');
const hash=async s=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',enc.encode(s))),x=>x.toString(16).padStart(2,'0')).join('');
const cookie=(name,value,max=2592000)=>`${name}=${value}; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=${max}`;
const cookies=req=>Object.fromEntries((req.headers.get('Cookie')||'').split(';').map(x=>x.trim().split('=')));
const fail=(message,status=400)=>{throw Object.assign(new Error(message),{status});};
async function passwordHash(password,salt){const key=await crypto.subtle.importKey('raw',enc.encode(password),'PBKDF2',false,['deriveBits']);return Array.from(new Uint8Array(await crypto.subtle.deriveBits({name:'PBKDF2',hash:'SHA-512',iterations:100000,salt:enc.encode(salt)},key,512)),x=>x.toString(16).padStart(2,'0')).join('');}
const equal=(a,b)=>{let x=a.length^b.length;for(let i=0;i<Math.max(a.length,b.length);i++)x|=(a.charCodeAt(i)||0)^(b.charCodeAt(i)||0);return x===0;};
export default {async fetch(req,env){
  const u=new URL(req.url);
  if (['elboussairimateriaux.com', 'www.elboussairimateriaux.com'].includes(u.hostname)) {
    return new Response(null, {
      status: 404,
      headers: {'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex'}
    });
  }
  if(u.pathname==='/api/orders'||u.pathname.startsWith('/api/orders/'))return handleOrders(req,env);
  if(!u.pathname.startsWith('/api/zi/'))return env.ASSETS.fetch(req);
  try{
    if(u.pathname.startsWith('/api/zi/internal/'))return json({error:'Route introuvable'},404);
    if(u.pathname==='/api/zi/config')return json({google:!!(env.GOOGLE_CLIENT_ID&&env.GOOGLE_CLIENT_SECRET),membership:true});
    if(!['GET','POST'].includes(req.method))return json({error:'Méthode refusée'},405);
    if(req.method==='POST'&&req.headers.get('Origin')!==u.origin)return json({error:'Origine refusée'},403);
    if(req.method==='POST'&&!req.headers.get('Content-Type')?.startsWith('application/json'))return json({error:'JSON requis'},415);
    if(Number(req.headers.get('Content-Length')||0)>12000)return json({error:'Requête trop longue'},413);
    if(!env.JOURNAL)return json({error:'Espace lecteur temporairement indisponible'},503);
    const store=env.JOURNAL.get(env.JOURNAL.idFromName('zone-industrielle-v1'));
    if(u.pathname==='/api/zi/google/start'){
      if(!env.GOOGLE_CLIENT_ID||!env.GOOGLE_CLIENT_SECRET)return json({error:'Connexion Google non configurée'},503);
      const state=token();const g=new URL('https://accounts.google.com/o/oauth2/v2/auth');
      Object.entries({client_id:env.GOOGLE_CLIENT_ID,redirect_uri:u.origin+'/api/zi/google/callback',response_type:'code',scope:'openid email profile',state,prompt:'select_account'}).forEach(([k,v])=>g.searchParams.set(k,v));
      return new Response(null,{status:302,headers:{Location:g.href,'Set-Cookie':cookie('zi_oauth',state,600),'Cache-Control':'no-store'}});
    }
    if(u.pathname==='/api/zi/google/callback'){
      if(!env.GOOGLE_CLIENT_SECRET||!u.searchParams.get('state')||!equal(u.searchParams.get('state'),cookies(req).zi_oauth||''))fail('Session Google invalide',403);
      const tr=await fetch('https://oauth2.googleapis.com/token',{method:'POST',body:new URLSearchParams({code:u.searchParams.get('code')||'',client_id:env.GOOGLE_CLIENT_ID,client_secret:env.GOOGLE_CLIENT_SECRET,redirect_uri:u.origin+'/api/zi/google/callback',grant_type:'authorization_code'})});const t=await tr.json();if(!tr.ok||!t.access_token)fail('Connexion Google refusée',401);
      const pr=await fetch('https://openidconnect.googleapis.com/v1/userinfo',{headers:{Authorization:'Bearer '+t.access_token}});const p=await pr.json();if(!pr.ok||!p.email_verified||!p.sub)fail('Email Google non vérifié',401);
      const rr=await store.fetch(new Request(u.origin+'/internal/google',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sub:p.sub,email:p.email,name:p.name})}));if(!rr.ok)return rr;
      const headers=new Headers({Location:'/actualites/?connexion=ok','Cache-Control':'no-store'});headers.append('Set-Cookie',rr.headers.get('Set-Cookie'));headers.append('Set-Cookie',cookie('zi_oauth','',0));return new Response(null,{status:302,headers});
    }
    const h=new Headers(req.headers);h.delete('X-ZI-Admin');h.set('X-ZI-Rate',await hash((req.headers.get('CF-Connecting-IP')||'unknown')+':'+Math.floor(now()/day)));
    if(env.JOURNAL_ADMIN_TOKEN&&equal(req.headers.get('Authorization')||'','Bearer '+env.JOURNAL_ADMIN_TOKEN))h.set('X-ZI-Admin','yes');
    return await store.fetch(new Request(req,{headers:h}));
  }catch(e){return json({error:e.status?e.message:'Service temporairement indisponible'},e.status||503);}
}};
export class JournalStore extends DurableObject {
  constructor(ctx,env){super(ctx,env);this.ctx=ctx;this.env=env;this.sql=ctx.storage.sql;
    initOrders(this.sql);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS members(id TEXT PRIMARY KEY,email TEXT UNIQUE,name TEXT NOT NULL,salt TEXT,password TEXT,google_sub TEXT UNIQUE,profile TEXT NOT NULL,marketing INTEGER DEFAULT 0,created INTEGER NOT NULL)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS sessions(hash TEXT PRIMARY KEY,member TEXT NOT NULL,expires INTEGER NOT NULL)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS comments(id TEXT PRIMARY KEY,article TEXT NOT NULL,member TEXT NOT NULL,body TEXT NOT NULL,status TEXT NOT NULL,reason TEXT,created INTEGER NOT NULL)`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS likes(article TEXT,member TEXT,PRIMARY KEY(article,member))`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS metrics(day TEXT,product TEXT,angle TEXT,stage TEXT,event TEXT,count INTEGER DEFAULT 0,PRIMARY KEY(day,product,angle,stage,event))`);
    this.sql.exec(`CREATE TABLE IF NOT EXISTS limits(key TEXT PRIMARY KEY,count INTEGER,expires INTEGER)`);
  }
  rows(q,...p){return [...this.sql.exec(q,...p)];}
  async rate(key,max,window=day){const k=key+':'+Math.floor(now()/window);const r=this.rows('SELECT count FROM limits WHERE key=?',k)[0];if(r?.count>=max)fail('Trop de tentatives. Réessayez plus tard.',429);this.sql.exec('INSERT INTO limits VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=count+1',k,now()+window);if(!await this.ctx.storage.getAlarm())await this.ctx.storage.setAlarm(now()+day);}
  async alarm(){this.sql.exec('DELETE FROM sessions WHERE expires<?',now());this.sql.exec('DELETE FROM limits WHERE expires<?',now());this.sql.exec('DELETE FROM metrics WHERE day<?',new Date(now()-90*day).toISOString().slice(0,10));await this.ctx.storage.setAlarm(now()+day);}
  async user(req){const t=cookies(req).zi_session;if(!t)return null;return this.rows('SELECT m.* FROM members m JOIN sessions s ON s.member=m.id WHERE s.hash=? AND s.expires>?',await hash(t),now())[0]||null;}
  async session(id){const t=token();this.sql.exec('INSERT INTO sessions VALUES(?,?,?)',await hash(t),id,now()+30*day);return json({ok:true},200,{'Set-Cookie':cookie('zi_session',t)});}
  profile(u){return {name:u.name,email:u.email,profile:JSON.parse(u.profile),marketing:!!u.marketing,google:!!u.google_sub};}
  async fetch(req){try{return await this.route(req);}catch(e){return json({error:e.status?e.message:'Service temporairement indisponible'},e.status||503);}}
  async route(req){
    if(new URL(req.url).pathname==='/api/orders'||new URL(req.url).pathname.startsWith('/api/orders/'))return routeOrders(req,this);
    const u=new URL(req.url),path=u.pathname.replace('/api/zi','');
    if(req.method==='POST')await this.rate('request:'+req.headers.get('X-ZI-Rate'),100,3600000);
    const raw=req.method==='POST'?await req.text():'';if(raw.length>12000)fail('Requête trop longue',413);let b={};try{b=raw?JSON.parse(raw):{};}catch{fail('JSON invalide');}
    if(!b||typeof b!=='object'||Array.isArray(b))fail('Objet requis');
    if(path==='/internal/google'){
      let m=this.rows('SELECT * FROM members WHERE google_sub=?',b.sub)[0];
      if(!m){if(this.rows('SELECT id FROM members WHERE email=?',b.email)[0])fail('Un compte existe déjà avec cet email. Connectez-vous avec votre mot de passe.',409);const id=crypto.randomUUID();this.sql.exec('INSERT INTO members(id,email,name,google_sub,profile,created) VALUES(?,?,?,?,?,?)',id,clean(b.email,254).toLowerCase(),clean(b.name,60),b.sub,'{}',now());m={id};}
      return this.session(m.id);
    }
    if(path==='/register'&&req.method==='POST'){
      await this.rate('register:'+req.headers.get('X-ZI-Rate'),5);
      const email=clean(b.email,254).toLowerCase(),name=clean(b.name,60),pw=b.password;
      if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)||name.length<2||typeof pw!=='string'||pw.length<12||pw.length>128||b.terms!==true)fail('Pseudonyme, email, mot de passe de 12 caractères et accord requis.');
      if(this.rows('SELECT id FROM members WHERE email=?',email)[0])fail('Inscription impossible avec cet email. Essayez de vous connecter.',409);
      const salt=token(),ph=await passwordHash(pw,salt),id=crypto.randomUUID();const profile={company:clean(b.company),role:clean(b.role),city:clean(b.city),phone:clean(b.phone,30),interests:clean(b.interests,200),consented_at:new Date().toISOString(),policy:'2026-11-02'};
      this.sql.exec('INSERT INTO members(id,email,name,salt,password,profile,marketing,created) VALUES(?,?,?,?,?,?,?,?)',id,email,name,salt,ph,JSON.stringify(profile),b.marketing===true?1:0,now());return this.session(id);
    }
    if(path==='/login'&&req.method==='POST'){
      await this.rate('login:'+req.headers.get('X-ZI-Rate'),10,900000);const email=clean(b.email,254).toLowerCase();await this.rate('login-email:'+await hash(email),15,900000);const m=this.rows('SELECT * FROM members WHERE email=?',email)[0];const pw=typeof b.password==='string'?b.password:'';if(pw.length>128)fail('Identifiants incorrects',401);
      const ph=await passwordHash(pw,m?.salt||'invalid-account-constant-salt');if(!m?.password||!equal(ph,m.password))fail('Identifiants incorrects',401);return this.session(m.id);
    }
    if(path==='/logout'&&req.method==='POST'){const t=cookies(req).zi_session||'';this.sql.exec('DELETE FROM sessions WHERE hash=?',await hash(t));return json({ok:true},200,{'Set-Cookie':cookie('zi_session','',0)});}
    const member=await this.user(req);
    if(path==='/me'&&req.method==='GET')return json({member:member?this.profile(member):null});
    if(path==='/export'&&req.method==='GET'){if(!member)fail('Connexion requise',401);return json({member:this.profile(member),comments:this.rows('SELECT article,body,status,created FROM comments WHERE member=?',member.id),likes:this.rows('SELECT article FROM likes WHERE member=?',member.id)});}
    if(path==='/delete-account'&&req.method==='POST'){if(!member)fail('Connexion requise',401);if(b.confirm!==true)fail('Confirmation requise');this.ctx.storage.transactionSync(()=>{for(const table of ['comments','likes','sessions'])this.sql.exec(`DELETE FROM ${table} WHERE member=?`,member.id);this.sql.exec('DELETE FROM members WHERE id=?',member.id);});return json({ok:true},200,{'Set-Cookie':cookie('zi_session','',0)});}
    if(path==='/stats'&&req.method==='GET')return json({metrics:this.rows("SELECT product,angle,SUM(CASE WHEN event='impression' THEN count ELSE 0 END) impressions,SUM(CASE WHEN event='click' THEN count ELSE 0 END) clicks FROM metrics GROUP BY product,angle")});
    if(path==='/event'&&req.method==='POST'){
      if(b.consent!==true)fail('Accord de mesure requis');if(!['impression','click','continue'].includes(b.event)||!['budget','logistics','technical','direct'].includes(b.angle)||!['intro','middle','end'].includes(b.stage)||!['ciments','fer-a-beton','panneaux-muraux','agglos','agregats','madriers','materiaux'].includes(b.product))fail('Événement invalide');
      await this.rate('metrics:'+req.headers.get('X-ZI-Rate'),150,3600000);const d=new Date().toISOString().slice(0,10);this.sql.exec('INSERT INTO metrics VALUES(?,?,?,?,?,1) ON CONFLICT(day,product,angle,stage,event) DO UPDATE SET count=count+1',d,b.product,b.angle,b.stage,b.event);return json({ok:true});
    }
    if(path==='/admin'&&req.method==='GET'){if(req.headers.get('X-ZI-Admin')!=='yes')fail('Accès refusé',403);return json({members:this.rows('SELECT email,name,profile,marketing,created FROM members'),pending:this.rows("SELECT id,article,body,reason,created FROM comments WHERE status='pending' ORDER BY created DESC LIMIT 100"),metrics:this.rows('SELECT * FROM metrics ORDER BY day DESC LIMIT 500')});}
    if(path==='/admin/moderate'&&req.method==='POST'){if(req.headers.get('X-ZI-Admin')!=='yes')fail('Accès refusé',403);if(b.decision==='remove')this.sql.exec('DELETE FROM comments WHERE id=?',clean(b.id));else if(b.decision==='publish')this.sql.exec("UPDATE comments SET status='published',reason='editor_review' WHERE id=?",clean(b.id));else fail('Décision invalide');return json({ok:true});}
    const article=clean(u.searchParams.get('article')||b.article,120);if(!articles.includes(article))fail('Article introuvable',404);
    if(path==='/community'&&req.method==='GET')return json({likes:this.rows('SELECT count(*) n FROM likes WHERE article=?',article)[0].n,liked:!!(member&&this.rows('SELECT 1 FROM likes WHERE article=? AND member=?',article,member.id).length),comments:this.rows("SELECT c.id,c.body,c.created,m.name FROM comments c JOIN members m ON m.id=c.member WHERE c.article=? AND c.status='published' ORDER BY c.created DESC LIMIT 50",article)});
    if(!member)fail('Connectez-vous pour participer.',401);
    if(path==='/like'&&req.method==='POST'){if(b.liked===true)this.sql.exec('INSERT OR IGNORE INTO likes VALUES(?,?)',article,member.id);else this.sql.exec('DELETE FROM likes WHERE article=? AND member=?',article,member.id);return json({ok:true});}
    if(path==='/comment'&&req.method==='POST'){
      await this.rate('comment:'+member.id,8,3600000);const text=clean(b.text,1501);if(text.length<3||text.length>1500)fail('Commentaire : 3 à 1500 caractères.');const id=crypto.randomUUID();this.sql.exec('INSERT INTO comments VALUES(?,?,?,?,?,?,?)',id,article,member.id,text,'pending','checking',now());
      let verdict;try{await this.rate('ai-global',100);verdict=await moderate(text,this.env.AI);}catch{verdict={status:'pending',reason:'daily_limit'};}
      if(verdict.status==='blocked')this.sql.exec('DELETE FROM comments WHERE id=?',id);else this.sql.exec('UPDATE comments SET status=?,reason=? WHERE id=?',verdict.status,verdict.reason,id);
      return json({status:verdict.status,message:{published:'Commentaire publié.',blocked:'Commentaire refusé et supprimé : langage contraire à la charte.',pending:'Commentaire reçu, en attente de vérification.'}[verdict.status]});
    }
    return json({error:'Route introuvable'},404);
  }
}
