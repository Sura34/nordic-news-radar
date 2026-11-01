let articles=[],category='All';
const $=id=>document.getElementById(id);
const cats=['All','Local','Sweden','Ethiopia','World'];
const STORE='nordic-radar-read-v1';
let readIds=new Set();
try{const saved=JSON.parse(localStorage.getItem(STORE)||'[]');if(Array.isArray(saved))readIds=new Set(saved.filter(x=>typeof x==='string').slice(-1000))}catch(e){}
function storyId(a){return String(a.link||a.title||'').split('?')[0].replace(/\/$/,'')}
function saveRead(){try{localStorage.setItem(STORE,JSON.stringify([...readIds].slice(-1000)))}catch(e){}}
function markRead(a){readIds.add(storyId(a));saveRead();render()}
function render(){
 const q=$('search').value.toLocaleLowerCase();
 $('filters').replaceChildren(...cats.map(c=>{
  const b=document.createElement('button');
  const group=articles.filter(a=>c==='All'||a.category===c);
  const unread=group.filter(a=>!readIds.has(storyId(a))).length;
  b.textContent=c+(unread?' · '+unread:'');
  b.setAttribute('aria-label',c+', '+unread+' unread stories');
  b.className=c===category?'active':'';
  b.setAttribute('aria-current',c===category?'page':'false');
  b.onclick=()=>{category=c;render()};
  return b
 }));
 const items=articles.filter(a=>(category==='All'||a.category===category)&&(!$('impact').checked||a.impact)&&((a.title+' '+a.description+' '+a.source).toLocaleLowerCase().includes(q)));
 $('articles').replaceChildren(...items.slice(0,24).map((a,i)=>{
  const unread=!readIds.has(storyId(a));
  const card=document.createElement('article');card.className='article'+(i===0?' lead':'')+(unread?' unread':' read');
  const meta=document.createElement('div');meta.className='meta';
  if(unread){const dot=document.createElement('span');dot.className='unread-dot';dot.setAttribute('aria-label','Unread');dot.title='Unread story';meta.append(dot)}
  const metadata=document.createElement('span');metadata.textContent=a.source+' · '+(a.published?new Date(a.published).toLocaleString('en-GB',{dateStyle:'medium',timeStyle:'short'}):'Date unavailable');meta.append(metadata);
  const link=document.createElement('a');link.href=a.link;link.target='_blank';link.rel='noopener noreferrer';link.textContent=a.title;
  link.addEventListener('click',()=>markRead(a));
  const desc=document.createElement('p');desc.textContent=a.description||'';
  const tag=document.createElement('span');tag.className='tag';tag.textContent=a.category+(a.impact?' · Daily-life impact':'');
  card.append(meta,link,desc,tag);return card
 }));
 if(!items.length){const p=document.createElement('p');p.className='empty';p.textContent='No stories match this view. Try another section or clear the search.';$('articles').append(p)}
}
async function load(){try{
 const res=await fetch('data/news.json?ts='+Date.now(),{cache:'no-store'});if(!res.ok)throw Error('HTTP '+res.status);
 const data=await res.json();articles=(data.articles||[]).filter(a=>a.category!=='Nordics'&&!String(a.source||'').startsWith('NRK '));
 $('status').textContent=articles.length+' headlines · '+articles.filter(a=>!readIds.has(storyId(a))).length+' unread · Feed last checked: '+(data.updatedAt?new Date(data.updatedAt).toLocaleString('en-GB'):'not yet')+(data.feedErrors?.length?' · Some feeds unavailable':'');render()
}catch(e){$('status').textContent='Unable to load headlines: '+e.message}}
$('search').oninput=render;$('impact').onchange=render;$('refresh').onclick=load;load();
