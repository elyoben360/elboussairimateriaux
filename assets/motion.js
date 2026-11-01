(()=>{'use strict';
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
function cycle(root,delay,advance,button){
 let paused=false,visible=true,timer;
 function sync(){clearInterval(timer);if(!paused&&!reduce.matches&&!document.hidden&&visible&&!root.matches(':hover')&&!root.contains(document.activeElement))timer=setInterval(advance,delay);root.classList.toggle('motion-stopped',paused||reduce.matches||document.hidden||!visible);}
 button?.addEventListener('click',()=>{paused=!paused;button.textContent=paused?'Reprendre':'Pause';button.setAttribute('aria-pressed',String(paused));sync()});
 ['mouseenter','mouseleave','focusin','focusout'].forEach(type=>root.addEventListener(type,()=>requestAnimationFrame(sync)));
 document.addEventListener('visibilitychange',sync);reduce.addEventListener('change',sync);
 if('IntersectionObserver'in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync()}).observe(root);sync();
}
const hero=document.querySelector('[data-hero]');
if(hero){const slides=[...hero.querySelectorAll('.hero-slide')],dots=[...hero.querySelectorAll('[data-hero-dot]')],caption=hero.querySelector('[data-hero-caption]');let index=0;
 function show(i){index=(i+slides.length)%slides.length;slides.forEach((s,n)=>s.classList.toggle('is-active',n===index));dots.forEach((d,n)=>d.setAttribute('aria-pressed',String(n===index)));caption.textContent='© El Boussairi Matériaux · '+dots[index].dataset.caption+' ↗';caption.href=dots[index].dataset.url;}
 hero.querySelector('[data-hero-prev]').onclick=()=>show(index-1);hero.querySelector('[data-hero-next]').onclick=()=>show(index+1);dots.forEach((d,i)=>d.onclick=()=>show(i));cycle(hero,6500,()=>show(index+1),hero.querySelector('[data-hero-pause]'));
}
document.querySelectorAll('[data-news-carousel]').forEach(root=>{const track=root.querySelector('[data-news-track]');if(!track)return;
 function step(direction){const cards=[...track.children],next=cards.findIndex(c=>c.offsetLeft-track.offsetLeft>=track.scrollLeft+10),end=track.scrollLeft+track.clientWidth>=track.scrollWidth-8;let x;if(direction>0)x=end?0:(cards[next]?.offsetLeft||0)-track.offsetLeft;else x=track.scrollLeft<=8?track.scrollWidth:Math.max(0,track.scrollLeft-(cards[0]?.offsetWidth||300)-24);track.scrollTo({left:x,behavior:reduce.matches?'instant':'smooth'});}
 root.querySelector('[data-news-prev]')?.addEventListener('click',()=>step(-1));root.querySelector('[data-news-next]')?.addEventListener('click',()=>step(1));cycle(root,7500,()=>step(1),root.querySelector('[data-news-pause]'));
});
document.querySelectorAll('[data-ticker]').forEach(root=>{const line=root.querySelector('.ticker-line'),set=root.querySelector('.ticker-set');if(!set)return;const clone=set.cloneNode(true);clone.setAttribute('aria-hidden','true');clone.querySelectorAll('a').forEach(a=>a.tabIndex=-1);line.append(clone);cycle(root,60000,()=>{},root.querySelector('[data-ticker-pause]'));});
})();
