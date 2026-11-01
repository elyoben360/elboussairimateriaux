from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
p=root/'src/catalogue.js';s=p.read_text();data=json.loads((root/'content/catalogue.json').read_text());s=re.sub(r'const DATA=.*?;\nconst VEHICLES=',lambda m:'const DATA='+json.dumps(data,ensure_ascii=False)+';\nconst VEHICLES=',s,count=1,flags=re.S);p.write_text(s);print('Catalogue synchronisé:',len(data),'gammes')
