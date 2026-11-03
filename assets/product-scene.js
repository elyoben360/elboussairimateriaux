(()=>{'use strict';
const root=document.getElementById('catalogue');if(!root)return;
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
const bg=document.createElement('div');bg.className='product-scene';bg.setAttribute('aria-hidden','true');
const layers=[document.createElement('img'),document.createElement('img')];
layers.forEach(im=>{im.alt='';im.decoding='async';bg.append(im)});root.prepend(bg);
let active=0,index=0,key='',photos=[],timer=null,loading=false,generation=0,visible=true;
const special={
 ciments:['/assets/depot/stock-ciment-holcim.webp','/assets/references/bouznika/05.webp','/assets/references/bouznika/06.webp'],
 'tubes-pvc':['/assets/depot/tubes-gaines-stock.webp','/assets/depot/gaines-couronnes-stock.webp'],
 'gaines-reseaux':['/assets/depot/gaines-couronnes-stock.webp','/assets/depot/tubes-gaines-stock.webp'],
 'briques-rouges':['/assets/references/ain-diab/05.webp','/assets/references/ain-diab/03.webp']
};
const familyPhotos={
 'Blocs, briques et hourdis':['/assets/depot/agglos-palettes-ensemble.webp','/assets/depot/stock-exterieur-blocs-palettes.webp'],
 'Acier et armatures':['/assets/depot/arrivage-fer-beton-sonasid.webp','/assets/depot/couronnes-fil-acier.webp','/assets/depot/treillis-soudes-stock.webp'],
 'Planchers et poutrelles':['/assets/references/accompagnement/08.webp','/assets/references/accompagnement/10.webp'],
 'Étanchéité':['/assets/depot/bitume-rouleaux-etancheite.webp','/assets/references/accompagnement/08.webp'],
 'Colles et accessoires':['/assets/depot/grillage-grtt-rouleaux.webp','/assets/depot/bostik-tradicem-x-mortier-colle.webp']
};
function stop(){clearInterval(timer);timer=null}
function next(){if(loading||photos.length<2||document.hidden||!visible||reduced.matches)return;loading=true;const token=generation,n=(index+1)%photos.length,other=1-active,im=layers[other];
 im.onload=()=>{if(token!==generation)return;layers[active].classList.remove('is-active');im.classList.add('is-active');active=other;index=n;loading=false};im.onerror=()=>{if(token===generation)loading=false};im.src=photos[n];
}
function sync(){stop();if(photos.length>1&&!reduced.matches&&!document.hidden&&visible)timer=setInterval(next,12000)}
window.EBM_PRODUCT_SCENE={show(p){
 const nextKey=p?String(p.product)+'|'+String(p.image):'';if(nextKey===key)return;key=nextKey;generation++;loading=false;stop();photos=[];
 if(!p){root.classList.remove('has-product-scene');layers.forEach(im=>{im.onload=null;im.removeAttribute('src');im.classList.remove('is-active')});return}
 const album=window.EBM_ALBUMS?.[p.image]||[];photos=[...new Set(special[p.slug]||album.map(x=>x.full||x.src))];if(!photos.length&&p.image)photos=[p.image.replace('-560.webp','.webp')];if(!photos.length)photos=familyPhotos[p.family]||[];
 root.classList.toggle('has-product-scene',photos.length>0);if(!photos.length)return;
 index=0;active=0;layers.forEach(im=>{im.onload=null;im.classList.remove('is-active')});layers[0].src=photos[0];layers[0].classList.add('is-active');sync();
}};
document.addEventListener('visibilitychange',sync);reduced.addEventListener('change',sync);
if('IntersectionObserver'in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync()},{rootMargin:'80px'}).observe(root);
})();
