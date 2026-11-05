(()=>{'use strict';
const galleries=[...document.querySelectorAll('[data-gallery]')];
for(const gallery of galleries){
 const cards=[...gallery.querySelectorAll('.depot-card')],filter=gallery.querySelector('[data-photo-filter]'),more=gallery.querySelector('[data-photo-more]'),status=gallery.querySelector('[data-photo-status]');
 if(!filter||!more)continue;
 let limit=6;
 const matches=()=>cards.filter(c=>!filter.value||c.dataset.photoGroup===filter.value);
 function render(){const selected=matches();cards.forEach(c=>c.hidden=!selected.includes(c)||selected.indexOf(c)>=limit);more.hidden=limit>=selected.length;more.textContent='Voir plus de galeries ('+Math.max(0,selected.length-limit)+')';status.textContent=Math.min(limit,selected.length)+' / '+selected.length+' galeries';}
 filter.addEventListener('change',()=>{limit=6;render()});
 more.addEventListener('click',()=>{const selected=matches(),first=selected[limit];limit+=6;render();first?.querySelector('a')?.focus({preventScroll:true})});render();
}
const links=[...document.querySelectorAll('[data-zoom]')];if(!links.length)return;
const dialog=document.createElement('dialog');dialog.className='media-viewer';dialog.setAttribute('aria-labelledby','media-caption');
const top=document.createElement('div');top.className='dialog-top';const credit=document.createElement('span');credit.textContent='© Banana Matériaux';const close=document.createElement('button');close.type='button';close.className='dialog-close';close.textContent='Fermer ×';top.append(credit,close);
const imageWrap=document.createElement('div');imageWrap.className='media-full';const img=document.createElement('img');const watermark=document.createElement('span');watermark.className='photo-credit';watermark.textContent='© Banana Matériaux';imageWrap.append(img,watermark);
const bottom=document.createElement('div');bottom.className='dialog-bottom';const prev=document.createElement('button'),next=document.createElement('button'),caption=document.createElement('p');prev.type=next.type='button';prev.className=next.className='gallery-arrow';prev.textContent='‹';next.textContent='›';prev.setAttribute('aria-label','Photo précédente');next.setAttribute('aria-label','Photo suivante');caption.id='media-caption';caption.setAttribute('aria-live','polite');bottom.append(prev,caption,next);dialog.append(top,imageWrap,bottom);document.body.append(dialog);
img.addEventListener('load',()=>imageWrap.setAttribute('aria-busy','false'));img.addEventListener('error',()=>{imageWrap.setAttribute('aria-busy','false');caption.textContent='Cette image ne peut pas être chargée.'});let active=[],index=0,opener=null,priorOverflow='';
function show(i){index=(i+active.length)%active.length;const a=active[index];imageWrap.setAttribute('aria-busy','true');img.src=a.src;img.alt=a.alt;caption.textContent=(index+1)+' / '+active.length+' · '+img.alt;prev.hidden=next.hidden=active.length<2;}
links.forEach(a=>a.addEventListener('click',e=>{if(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();opener=a;let pics;try{pics=JSON.parse(a.dataset.photoImages||'null')}catch(error){}active=Array.isArray(pics)?pics.filter(p=>typeof p.src==='string'&&p.src.startsWith('/assets/')&&typeof p.alt==='string'):[{src:a.getAttribute('href'),alt:a.querySelector('img').alt}];if(!active.length)return;show(Number(a.dataset.photoIndex)||0);priorOverflow=document.body.style.overflow;document.body.style.overflow='hidden';dialog.showModal();close.focus()}));
close.onclick=()=>dialog.close();prev.onclick=()=>show(index-1);next.onclick=()=>show(index+1);dialog.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();show(index+(e.key==='ArrowRight'?1:-1))}});dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});dialog.addEventListener('close',()=>{img.removeAttribute('src');document.body.style.overflow=priorOverflow;opener?.focus({preventScroll:true})});
let startX=0,startY=0;imageWrap.addEventListener('touchstart',e=>{startX=e.changedTouches[0].clientX;startY=e.changedTouches[0].clientY},{passive:true});imageWrap.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-startX,dy=e.changedTouches[0].clientY-startY;if(Math.abs(dx)>65&&Math.abs(dx)>Math.abs(dy)*1.5)show(index+(dx<0?1:-1))},{passive:true});
})();
