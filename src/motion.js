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
 root.querySelector('[data-news-prev]')?.addEventListener('click',()=>step(-1));root.querySelector('[data-news-next]')?.addEventListener('click',()=>step(1));cycle(root,7500,()=>step(1),root.querySelector('[data-news-pause]'));
});
document.querySelectorAll('[data-ticker]').forEach(root=>{const line=root.querySelector('.ticker-line'),set=root.querySelector('.ticker-set');if(!set)return;const clone=set.cloneNode(true);clone.setAttribute('aria-hidden','true');clone.querySelectorAll('a').forEach(a=>a.tabIndex=-1);line.append(clone);cycle(root,60000,()=>{},root.querySelector('[data-ticker-pause]'));});
})();
