import json,re,html,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
ROOT=Path(__file__).resolve().parents[1]
FEEDS=[('SVT Väst','https://www.svt.se/nyheter/lokalt/vast/rss.xml','Local'),('SVT Sverige','https://www.svt.se/nyheter/inrikes/rss.xml','Sweden'),('SVT Utrikes','https://www.svt.se/nyheter/utrikes/rss.xml','World'),('P4 Göteborg','https://api.sr.se/api/rss/program/104','Local'),('Ekot','https://api.sr.se/api/rss/program/83','Sweden'),('Google News Ale','https://news.google.com/rss/search?q=Ale+kommun+OR+%C3%84lv%C3%A4ngen&hl=sv&gl=SE&ceid=SE:sv','Local'),('Google News Göteborg','https://news.google.com/rss/search?q=G%C3%B6teborg&hl=sv&gl=SE&ceid=SE:sv','Local'),('Google News Sverige','https://news.google.com/rss/headlines/section/geo/SE?hl=sv&gl=SE&ceid=SE:sv','Sweden'),('Sweden Regional','https://news.google.com/rss/search?q=lokala+nyheter+Sverige+kommun+region+when:7d&hl=sv&gl=SE&ceid=SE:sv','Sweden'),('Sweden Regional English','https://news.google.com/rss/search?q=Sweden+regional+local+news+municipalities+when:7d&hl=en&gl=SE&ceid=SE:en','Sweden'),('Sweden English','https://news.google.com/rss/search?q=Sweden+politics+economy+technology+when:7d&hl=en&gl=SE&ceid=SE:en','Sweden'),('World English','https://news.google.com/rss/search?q=international+breaking+news+economy+security+when:7d&hl=en&gl=US&ceid=US:en','World')]
LOCAL=re.compile(r'älvängen|ale kommun|nödinge|surte|bohus|göteborg|västra götaland|kungälv',re.I)
IMPACT=re.compile(r'trafik|tåg|väg|skola|förskola|sjukvård|sjukhus|ränta|bolån|elpris|skatt|västtrafik|olycka|varning|störning|buss|arbete|inflation',re.I)
def clean(s):return re.sub(r'\s+',' ',re.sub(r'<[^>]*>',' ',html.unescape(s or ''))).strip()[:500]
def get(n,*names):
 for name in names:
  t=n.findtext(name)
  if t:return t
 return ''
def collect(name,url,category):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 NordicNewsRadar/1.0'})
 with urllib.request.urlopen(req,timeout=20) as r:root=ET.fromstring(r.read(3000000))
 nodes=root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry');out=[]
 for node in nodes[:40]:
  title=clean(get(node,'title','{http://www.w3.org/2005/Atom}title'))
  link=get(node,'link')
  if not link:
   for el in node.findall('{http://www.w3.org/2005/Atom}link'):
    if el.get('href'):link=el.get('href');break
  if not title or not link.startswith(('https://','http://')):continue
  desc=clean(get(node,'description','{http://www.w3.org/2005/Atom}summary'))
  date=get(node,'pubDate','{http://www.w3.org/2005/Atom}published','{http://www.w3.org/2005/Atom}updated')
  try:dt=parsedate_to_datetime(date)
  except Exception:
   try:dt=datetime.fromisoformat(date.replace('Z','+00:00'))
   except Exception:dt=None
  local=bool(LOCAL.search(title+' '+desc))
  out.append(dict(title=title,description=desc,link=link,source=name,category='Local' if local else category,published=dt.astimezone(timezone.utc).isoformat() if dt else None,impact=bool(IMPACT.search(title+' '+desc))))
 return out
def main():
 path=ROOT/'data/news.json'
 try:old=json.loads(path.read_text()).get('articles',[])
 except Exception:old=[]
 found=[];errors=[]
 for name,url,cat in FEEDS:
  try:found.extend(collect(name,url,cat))
  except Exception as exc:errors.append(f'{name}: {type(exc).__name__}: {exc}')
 seen=set();items=[]
 for a in found+old:
  if a.get('category')=='Nordics' or a.get('source','').startswith('NRK '):continue
  key=a['link'].split('?')[0].rstrip('/')
  if key not in seen:seen.add(key);items.append(a)
 items.sort(key=lambda a:a.get('published') or '',reverse=True)
 cutoff=datetime.now(timezone.utc).timestamp()-7*86400
 items=[a for a in items if not a.get('published') or datetime.fromisoformat(a['published'].replace('Z','+00:00')).timestamp()>=cutoff]
 if not items:raise SystemExit('No feeds returned articles; preserving prior data')
 path.write_text(json.dumps(dict(updatedAt=datetime.now(timezone.utc).isoformat(),articles=items[:250],feedErrors=errors),ensure_ascii=False,indent=2)+'\n')
 print(f'Collected {len(items)} headlines; {len(errors)} feed errors')
 for err in errors:print(err)
if __name__=='__main__':main()
