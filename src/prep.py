import gzip,json,re,collections,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=lambda *a: os.path.join(ROOT,*a)
d=json.load(gzip.open(P('data','an-data.json.gz')))
CATS=[
("censure","Censure",["motion de censure"]),
("societe0",None,None),
("immigration","Immigration",["immigration","étranger","asile","rétention administrative","maintien en rétention","nationalité","séjour","intégration"]),
("defense","Armées & défense",["militaire","défense nationale","armée","armées","ukraine","otan"]),
("finances","Budget & finances",["loi de finances","finances","budget","fiscal","impôt","taxe","comptes","dette","gestion des finances","approbation des comptes","fin de gestion","opérateurs de l'etat","financement de la sécurité sociale"]),
("sante","Santé",["santé","soins","médic","hôpital","fin de vie","aide à mourir","cancer","maladie","cardio","psychiatr","pharma","soignant","infirmi","palliatif","hospitalier","médecin","mortalité","orthophonist","vapotage","tabac"]),
("education","Éducation & jeunesse",["école","éducation","enseignement","étudiant","bourses","mineurs","enfant","jeunesse","universit","scolaire"]),
("justice","Sécurité & justice",["sécurité","justice","pénal","criminel","police","ordre public","légitime défense","narcotrafic","prison","victimes","terror","attentat","délinquance","juridiction","magistrat","saisis","procureur","criminalité","homicide","routière","détenues","fraude","nullités","pompiers"]),
("ecologie","Écologie & énergie",["énergie","environnement","climat","hydroélectr","nucléaire","textile","eau","biodiversité","pollution","renouvelable","plastique","pfas","zéro artificialisation","électricité","perfluoro","frelon"]),
("agriculture","Agriculture",["agricol","agricult","montagne","pêche","alimentation","élevage","paysan","apicole","vigne"]),
("social","Travail & social",["retraite","travail","emploi","chômage","salari","solidarité","pauvre","handicap","social","sociale","minima","précarité","professionnalisation"]),
("territoires","Logement & territoires",["logement","territoire","collectivit","commune","outre-mer","martinique","corse","calédonie","guadeloupe","mayotte","guyane","réunion","polynésie","ruralité","élus locaux","élu local","maire","locatif","meublés","ascen","débits de boissons","indivis","succession"]),
("economie","Économie & numérique",["économi","entreprise","numérique","réseaux sociaux","industrie","nationalisation","commerce","simplification","consommat","banque","intelligence artificielle","transport","patrimoine immobilier","commerci","bancaire","restaurant","intérêt public majeur"]),
("institutions","Institutions & Europe",["constitution","élection","électoral","institution","parlement","résolution","européen","europe","déclaration du gouvernement","référendum","scrutin","vote par correspondance","candidats"]),
("societe","Société & droits",["code noir","homosexualité","devoir conjugal","violences sexuelles","sexiste","discrimination","égalité","laïcité","racisme","ivg","avortement","mariage"]),
("culture","Culture & sport",["sport","culture","patrimoine","audiovisuel","presse","jeux olympiques","musée","langue"]),
]
def cat(v):
    txt=((v['dos'] or '')+' '+v['t']).lower()
    if v['ty']=='MOC': return 'censure'
    order=[c for c in CATS if c[0]=="societe"]+[c for c in CATS if c[0]=="sante"]+[c for c in CATS[1:] if c[0] not in ("societe","societe0","sante")]
    for k,_,kw in order:
        if any(w in txt for w in kw): return k
    return 'autres'
def kind(v):
    t=v['t'].lower()
    if v['ty']=='MOC' or 'motion de censure' in t: return 'Motion de censure'
    if 'motion de rejet' in t: return 'Motion de rejet'
    if 'déclaration du gouvernement' in t: return 'Déclaration du Gouvernement'
    if 'proposition de résolution' in t: return 'Résolution'
    if 'projet de loi' in t: return 'Projet de loi'
    if 'proposition de loi' in t: return 'Proposition de loi'
    return 'Autre'
for v in d['votes']:
    v['cat']=cat(v); v['k']=kind(v)
    m=re.search(r'\(([^()]*(lecture|paritaire|définitive)[^()]*)\)',v['t']); v['lec']=m.group(1) if m else None
print(collections.Counter(v['cat'] for v in d['votes']))
for v in d['votes']:
    if v['cat']=='autres': print('AUTRE',v['t'][:140])
gid={g['id']:g for g in d['groups']}
# loyalty & key participation
for i,dep in enumerate(d['deputes']):
    same=tot=kp=ke=0
    for v in d['votes']:
        if v['dt']<dep['d']: continue
        ke+=1; c=v['v'][i]
        if c not in 'pca': continue
        kp+=1
        gm=next((g for g in v['gv'] if g[0]==dep['g']),None)
        if gm and gm[1] in ('pour','contre','abstention'):
            tot+=1; same+= ({'p':'pour','c':'contre','a':'abstention'}[c]==gm[1])
    dep['loy']=round(100*same/tot) if tot else None; dep['kp']=kp; dep['ke']=ke
json.dump({'cats':[[k,l] for k,l,_ in CATS if l]+[['autres','Autres sujets']],**d},open(P('data','data.json'),'w'),ensure_ascii=False,separators=(',',':'))
print(collections.Counter(v['k'] for v in d['votes']))
print(set(g[1] for v in d['votes'] for g in v['gv']))

# ---- résumés des textes ----
import importlib.util,os
spec=importlib.util.spec_from_file_location('res',os.path.join(os.path.dirname(os.path.abspath(__file__)),'resumes.py')); res=importlib.util.module_from_spec(spec); spec.loader.exec_module(res)
X=json.load(open(P('data','an-dossiers.json')))
num2k={n:k for k,ns in X['map'].items() for n in ns}
out=json.load(open(P('data','data.json')))
def clean_aut(a):
    if not a: return None
    a=re.sub(r'^(MM\.|Mmes|M\.|Mme)\s+','',a).strip(' ,')
    return a
dos={}
def auto_resume(expo):
    """Extrait automatique : la phrase de l'exposé des motifs qui annonce l'objet du texte."""
    if not expo: return None
    e=re.sub(r'^\s*(Mesdames,?\s*)?Messieurs,?\s*','',expo)
    e=re.sub(r'\(\[?\d+\]?\)|\[\d+\]','',e)
    phrases=re.split(r'(?<=[.!?])\s+(?=[A-ZÉÈÀÂÎ«])',e)
    VERB=r'\b(vise|visent|a pour objet|a pour objectif|propose|proposons|prévoit|entend)\b'
    TXT=r'(proposition|projet) de (loi|résolution)|ce texte|le présent'
    pick=next((ph for ph in phrases if re.search(VERB,ph,re.I) and re.search(TXT,ph,re.I) and 40<len(ph)<600),None)
    pick=pick or next((ph for ph in phrases if re.search(VERB,ph,re.I) and 40<len(ph)<600),None)
    pick=pick or (phrases[0] if phrases and len(phrases[0])>40 else None)
    if not pick: return None
    pick=pick.strip()
    if len(pick)>280:
        pick=pick[:280].rsplit(' ',1)[0].rstrip(',;:')+'…'
    return pick
# drapeau source : 0 = rédigé d'après l'intitulé, 1 = rédigé d'après l'exposé des motifs, 2 = extrait automatique
for k in X.get('map',{}):
    v=X['dos'].get(k) or {}
    if k in res.R:
        dos[k]=[res.R[k], clean_aut(v.get('auteur')), v.get('promu'), 1 if v.get('expo') else 0]
    else:
        a=auto_resume(v.get('expo'))
        if a or v.get('auteur') or v.get('promu'):
            dos[k]=[a, clean_aut(v.get('auteur')), v.get('promu'), 2]
for v in out['votes']:
    k=num2k.get(v['n'])
    if k in dos: v['dk']=k
out['dos']=dos
json.dump(out,open(P('data','data.json'),'w'),ensure_ascii=False,separators=(',',':'))
print('résumés',len(dos),'votes avec résumé',sum(1 for v in out['votes'] if v.get('dk')))

# ---- construit index.html ----
t=open(P('src','template.html'),encoding='utf-8').read()
d=open(P('data','data.json'),encoding='utf-8').read().replace('</','<\\/')
body=t.replace('__DATA__',d)
i=body.index('</style>')+len('</style>')
HEAD=open(P('src','head.html'),encoding='utf-8').read()
open(P('index.html'),'w',encoding='utf-8').write(HEAD+body[:i]+'\n</head>\n<body>\n'+body[i:]+'\n</body>\n</html>\n')
print('index.html regénéré')
