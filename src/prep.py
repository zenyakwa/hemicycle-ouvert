import gzip,json,re,collections,os,sys,importlib.util
SRC=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(SRC)
sys.path.insert(0,SRC)
from slug import assign_slugs
def _load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
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

def clean_aut(a):
    if not a: return None
    a=re.sub(r'^(MM\.|Mmes|M\.|Mme)\s+','',a).strip(' ,')
    return a
def auto_resume(expo):
    """Extrait automatique, coupé à 280 caractères."""
    pick=auto_phrase(expo)
    if pick and len(pick)>280:
        pick=pick[:280].rsplit(' ',1)[0].rstrip(',;:')+'…'
    return pick


def resume_inutilisable(extrait, longueur_origine):
    """Raison pour laquelle un extrait automatique ne doit pas être affiché, ou None."""
    if not extrait: return None
    e=extrait.strip()
    if re.match(r'(?i)article\b', e): return 'commence par ARTICLE'
    if len(re.findall(r'(?i)\barticle\s+(\d+|premier|liminaire)', e))>=2: return "liste d'articles"
    if longueur_origine>280: return 'trop long'
    return None


def auto_phrase(expo):
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
    return pick.strip()


def classify_votes(d, log=print):
    for v in d['votes']:
        v['cat']=cat(v); v['k']=kind(v)
        m=re.search(r'\(([^()]*(lecture|paritaire|définitive)[^()]*)\)',v['t']); v['lec']=m.group(1) if m else None
    log(collections.Counter(v['cat'] for v in d['votes']))
    for v in d['votes']:
        if v['cat']=='autres': log('AUTRE',v['t'][:140])


def loyalty(d):
    """Vote avec son groupe (part des votes clés où le député a voté comme la majorité de son groupe) et présence aux votes clés."""
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


def build_resumes(out, X, res):
    num2k={n:k for k,ns in X['map'].items() for n in ns}
    dos={}
    # drapeau source : 0 = rédigé d'après l'intitulé, 1 = rédigé d'après l'exposé des motifs, 2 = extrait automatique
    for k in X.get('map',{}):
        v=X['dos'].get(k) or {}
        if k in res.R:
            dos[k]=[res.R[k], clean_aut(v.get('auteur')), v.get('promu'), 1 if v.get('expo') else 0]
        else:
            raw=auto_phrase(v.get('expo'))
            if not (raw or v.get('auteur') or v.get('promu')): continue
            why=resume_inutilisable(raw, len(raw or '')) if raw else "pas d'extrait de l'exposé des motifs"
            if why:  # 3 = résumé à venir (raison en 5e position, pour le rapport)
                dos[k]=[None, clean_aut(v.get('auteur')), v.get('promu'), 3, why]
            else:
                dos[k]=[auto_resume(v.get('expo')), clean_aut(v.get('auteur')), v.get('promu'), 2]
    for v in out['votes']:
        k=num2k.get(v['n'])
        if k in dos: v['dk']=k
    out['dos']=dos


def build_quiz(out, X, qz, log=print):
    byn={v['n']:v for v in out['votes']}
    quiz=[]
    for item in qz.QUIZ:
        n,q,th=item[:3]; fixed=item[3] if len(item)>3 else None
        v=byn.get(n)
        if not v: log('quiz : scrutin',n,'introuvable, question ignorée'); continue
        k=v.get('dk'); info=X['dos'].get(k) or {}
        flat=re.sub(r'\s+',' ',info.get('expo') or '')
        if fixed and re.sub(r'\s+',' ',fixed) in flat: quote=fixed
        else:
            if fixed: log('quiz : citation introuvable dans l\'exposé du scrutin',n,'— extrait automatique utilisé')
            quote=auto_resume(info.get('expo'))
        if v['k']=='Projet de loi': src='Exposé des motifs du projet de loi (Gouvernement)'
        elif info.get('auteur'): src='Exposé des motifs, texte déposé par '+clean_aut(info['auteur'])
        else: src='Exposé des motifs du texte'
        quiz.append({'n':n,'q':q,'th':th,'qt':quote,'qs':src if quote else None})
    out['quiz']=quiz
    log('quiz',len(quiz),'questions,',sum(1 for x in quiz if x['qt']),'avec citation')


def build_transparence(out, TP, log=print):
    dep_by={}
    if os.path.exists(TP):
        for k,v in sorted(json.load(open(TP,encoding='utf-8'))['deports'].items(), reverse=True):
            dep_by.setdefault(v['pa'],[]).append([v['date'],v['cible'],v['portee'],v.get('motif','')])
    for d in out['deputes']:
        h=d.pop('hatvp',None)
        if h and 'pages_nominatives/' in h: d['hv']=h.split('pages_nominatives/')[1]
        if d['id'] in dep_by: d['dp']=dep_by[d['id']]
        if not d.get('cm'): d.pop('cm',None)
    log('déports', sum(len(v) for v in dep_by.values()))


def build_logos(root):
    """Logos présents dans logos/ et crédits lus dans logos/SOURCES.md : {sigle: [chemin, page Commons, licence, auteur]}."""
    d=os.path.join(root,'logos'); out={}
    if not os.path.isdir(d): return out
    src={}
    sp=os.path.join(d,'SOURCES.md')
    if os.path.exists(sp):
        for line in open(sp,encoding='utf-8'):
            c=[x.strip() for x in line.strip().strip('|').split('|')]
            if len(c)==6 and c[0] and c[0]!='Sigle' and not c[0].startswith('-'):
                m=re.search(r'\((https?://[^)]+)\)',c[3]); src[c[0]]=[m.group(1) if m else '',c[5],c[4]]
    for f in sorted(os.listdir(d)):
        k,_,ext=f.rpartition('.')
        if ext in ('svg','png','webp') and k in src: out[k]=['/logos/'+f]+src[k]
    return out


def build_data(root=ROOT, log=lambda *a: None):
    """Construit le dictionnaire des données du site (sans rien écrire sur le disque)."""
    P=lambda *a: os.path.join(root,*a)
    d=json.load(gzip.open(P('data','an-data.json.gz'),'rt',encoding='utf-8'))
    classify_votes(d, log)
    loyalty(d)
    out={'cats':[[k,l] for k,l,_ in CATS if l]+[['autres','Autres sujets']],**d}
    log(collections.Counter(v['k'] for v in d['votes']))
    log(set(g[1] for v in d['votes'] for g in v['gv']))
    X=json.load(open(P('data','an-dossiers.json'),encoding='utf-8'))
    build_resumes(out, X, _load('res',P('src','resumes.py')))
    build_quiz(out, X, _load('quiz',P('src','quiz.py')), log)
    build_transparence(out, P('data','an-transparence.json'), log)
    assign_slugs(out['deputes'])
    out['logos']=build_logos(root)
    lx=_load('lexique',P('src','lexique.py'))
    out['lex']=[[t['id'],t['terme'],t['definition'],t['formes']] for t in lx.TERMES]
    log('résumés',len(out['dos']),'votes avec résumé',sum(1 for v in out['votes'] if v.get('dk')))
    return out


def write_rapport(data, path):
    """data/resumes-a-ecrire.md : dossiers sans résumé utilisable, à compléter dans src/resumes.py."""
    par_dos={}
    for v in data['votes']:
        if v.get('dk'): par_dos.setdefault(v['dk'],[]).append(v)
    def ligne(k,why):
        vs=sorted(par_dos.get(k,[]),key=lambda v:v['dt'],reverse=True)
        titre=(vs[0].get('dos') or vs[0]['t']) if vs else k
        dr=next((v['dr'] for v in vs if v.get('dr')),None)
        lien=f"[dossier](https://www.assemblee-nationale.fr/dyn/17/dossiers/{dr})" if dr else ''
        nums=', '.join(f"[{v['n']}](https://www.assemblee-nationale.fr/dyn/17/scrutins/{v['n']})" for v in vs)
        return (vs[0]['dt'] if vs else ''), f"| `{k}` | {titre.replace('|','/')} | {vs[0]['dt'] if vs else ''} | {nums} | {lien} | {why} |"
    a=[ligne(k,d[4]) for k,d in data['dos'].items() if d[3]==3]
    b=[ligne(k,'extrait automatique affiché') for k,d in data['dos'].items() if d[3]==2]
    # votes sur un texte sans aucune donnée de dossier (ni extrait, ni auteur)
    for v in data['votes']:
        if not v.get('dk') and v.get('dr') and v['k'] not in ('Motion de censure',):
            k=v['dr'].replace('DLR5L','')
            par_dos.setdefault(k,[]).append(v)
    c=[ligne(k,"aucune donnée du dossier") for k in sorted({v['dr'].replace('DLR5L','') for v in data['votes'] if not v.get('dk') and v.get('dr') and v['k']!='Motion de censure'})]
    head="| Clé | Texte | Dernier vote | Scrutins | Lien officiel | Raison |\n|---|---|---|---|---|---|"
    out=["# Résumés « En bref » à écrire","",
         "Fichier régénéré à chaque passage de `src/prep.py`. Pour ajouter un résumé, ajouter une ligne dans `src/resumes.py` avec la clé du dossier (ex. `\"17N55223\": \"…\"`), puis relancer `python src/prep.py`.","",
         f"## Affichés « Résumé à venir » ({len(a)})","",head]+[x for _,x in sorted(a,reverse=True)]+["",
         f"## Extraits automatiques affichés, à relire ({len(b)})","",head]+[x for _,x in sorted(b,reverse=True)]+["",
         f"## Votes sans aucun résumé ni donnée de dossier ({len(c)})","",head]+[x for _,x in sorted(c,reverse=True)]
    with open(path,'w',encoding='utf-8') as f: f.write('\n'.join(out)+'\n')


UI_CSS=['base.css','layout.css','votes.css','fiche.css','jeux.css','pages.css','home.css','scrutin.css','mobile.css']
UI_JS=['core.js','lexique.js','popups.js','hemicycle.js','groupes.js','recherche.js','composants.js','home.js','fiche.js','votes.js','jeux.js','scrutin.js','router.js','start.js']


def ui_bundle(root, names):
    return ''.join(open(os.path.join(root,'src','ui',n),encoding='utf-8').read() for n in names)


def data_json(data):
    return json.dumps(data,ensure_ascii=False,separators=(',',':'))


def render_index(data, root=ROOT):
    P=lambda *a: os.path.join(root,*a)
    t=open(P('src','template.html'),encoding='utf-8').read()
    t=t.replace('__CSS__',ui_bundle(root,UI_CSS).rstrip('\n'))
    t=t.replace('__JS__','(function(){\n'+ui_bundle(root,UI_JS)+'})();')
    body=t.replace('__DATA__',data_json(data).replace('</','<\\/'))
    i=body.index('</style>')+len('</style>')
    HEAD=open(P('src','head.html'),encoding='utf-8').read()
    return HEAD+body[:i]+'\n</head>\n<body>\n'+body[i:]+'\n</body>\n</html>\n'


def main():
    data=build_data(ROOT, print)
    with open(os.path.join(ROOT,'data','data.json'),'w',encoding='utf-8') as f: f.write(data_json(data))
    with open(os.path.join(ROOT,'index.html'),'w',encoding='utf-8') as f: f.write(render_index(data))
    write_rapport(data, os.path.join(ROOT,'data','resumes-a-ecrire.md'))
    print('index.html regénéré')


if __name__=='__main__':
    main()
