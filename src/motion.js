(()=>{'use strict';
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
function cycle(root,delay,advance,button){
 let paused=false,visible=true,timer;
 function sync(){clearInterval(timer);if(!paused&&!reduce.matches&&!document.hidden&&visible&&!root.classList.contains('news-filtered')&&(!root.contains(document.activeElement)||root.hasAttribute('data-image-rotation')))timer=setInterval(advance,delay);root.classList.toggle('motion-stopped',paused||reduce.matches||document.hidden||!visible);}
 button?.addEventListener('click',()=>{paused=!paused;button.textContent=paused?'Reprendre':'Pause';button.setAttribute('aria-pressed',String(paused));if(root.hasAttribute('data-image-rotation'))button.setAttribute('aria-label',paused?'Reprendre le diaporama':'Mettre le diaporama en pause');sync()});
 ['focusin','focusout'].forEach(type=>root.addEventListener(type,()=>requestAnimationFrame(sync)));
 root.addEventListener('newsfilter',sync);document.addEventListener('visibilitychange',sync);reduce.addEventListener('change',sync);
 if('IntersectionObserver'in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync()}).observe(root);sync();
}
document.querySelectorAll('[data-image-rotation]').forEach(root=>{
 const slides=[...root.querySelectorAll('.hero-slide')],caption=root.querySelector('[data-rotation-caption]'),credit=root.querySelector('[data-rotation-credit]');let index=0;
 if(slides.length<2){root.querySelector('.hero-controls')?.remove();return;}
 function show(i){index=(i+slides.length)%slides.length;slides.forEach((s,n)=>s.classList.toggle('is-active',n===index));const current=slides[index];if(caption){caption.textContent=current.dataset.caption;caption.href=current.dataset.url;}if(credit)credit.textContent=current.dataset.credit;const progress=root.querySelector('.rotation-progress span');if(progress){progress.style.animation='none';requestAnimationFrame(()=>{progress.style.animation='';});}}
 cycle(root,6500,()=>show(index+1),root.querySelector('[data-rotation-pause]'));
});
document.querySelectorAll('[data-news-carousel]').forEach(root=>{const track=root.querySelector('[data-news-track]');if(!track)return;
 function step(direction){const cards=[...track.children].filter(c=>!c.hidden),next=cards.findIndex(c=>c.offsetLeft-track.offsetLeft>=track.scrollLeft+10),end=track.scrollLeft+track.clientWidth>=track.scrollWidth-8;let x;if(direction>0)x=end?0:(cards[next]?.offsetLeft||0)-track.offsetLeft;else x=track.scrollLeft<=8?track.scrollWidth:Math.max(0,track.scrollLeft-(cards[0]?.offsetWidth||300)-24);track.scrollTo({left:x,behavior:reduce.matches?'instant':'smooth'});}
 root.querySelector('[data-news-prev]')?.addEventListener('click',()=>step(-1));root.querySelector('[data-news-next]')?.addEventListener('click',()=>step(1));cycle(root,root.closest('.latest-news')?4800:7500,()=>step(1),root.querySelector('[data-news-pause]'));
});
document.querySelectorAll('[data-ticker]').forEach(root=>{const line=root.querySelector('.ticker-line'),set=root.querySelector('.ticker-set');if(!set)return;const clone=set.cloneNode(true);clone.setAttribute('aria-hidden','true');clone.querySelectorAll('a').forEach(a=>a.tabIndex=-1);line.append(clone);cycle(root,60000,()=>{},root.querySelector('[data-ticker-pause]'));});
})();

/* Deux couches par carte, un ordonnanceur et chargement des cartes visibles. */
(()=>{'use strict';if(!('IntersectionObserver'in window))return;const albums=window.EBM_ALBUMS||{},reduced=matchMedia('(prefers-reduced-motion: reduce)'),items=new Map();
const observer=new IntersectionObserver(entries=>entries.forEach(e=>{const s=items.get(e.target);if(s)s.visible=e.isIntersecting;}));
function discover(root){const selectors='.depot-card>.media-visual,.product-card>.media-visual,.reference-card .owned-photo,.catalogue-product-photo';const nodes=[...(root.matches?.(selectors)?[root]:[]),...(root.querySelectorAll?.(selectors)||[])];for(const node of nodes){const img=node.tagName==='IMG'?node:node.querySelector('img');if(!img)continue;const album=albums[img.getAttribute('src')];if(!album||album.length<2)continue;const box=node.tagName==='IMG'?node.parentElement:node;if(items.has(box))continue;box.classList.add('card-image-rotator');const first=img.cloneNode(false),second=img.cloneNode(false);for(const layer of [first,second]){layer.removeAttribute('srcset');layer.removeAttribute('sizes');layer.removeAttribute('id');layer.className='card-slide';layer.alt='';layer.setAttribute('aria-hidden','true');box.append(layer);}first.classList.add('is-active');img.style.opacity='0';const state={box,img,layers:[first,second],album,index:0,layer:0,visible:false,pending:false};items.set(box,state);observer.observe(box);}}
function advance(s){if(s.pending||!s.visible||s.box.closest('[hidden]')||s.box.contains(document.activeElement))return;s.pending=true;const index=(s.index+1)%s.album.length,next=s.album[index],layer=s.layers[1-s.layer];layer.onload=()=>{if(!s.box.isConnected)return;s.layers[s.layer].classList.remove('is-active');layer.classList.add('is-active');s.img.alt=next.alt;s.index=index;s.layer=1-s.layer;s.pending=false;if(s.box.matches('[data-zoom]'))s.box.dataset.photoIndex=String(index);};layer.onerror=()=>{s.pending=false;};layer.src=next.src;}
discover(document.body);new MutationObserver(records=>{for(const r of records)for(const n of r.addedNodes)if(n.nodeType===1)discover(n);for(const [box] of items)if(!box.isConnected){observer.unobserve(box);items.delete(box);}}).observe(document.body,{childList:true,subtree:true});setInterval(()=>{if(document.hidden||reduced.matches)return;items.forEach(advance);},4800);
})();
