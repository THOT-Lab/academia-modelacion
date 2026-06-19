# -*- coding: utf-8 -*-
"""
Assemble la page autonome "Academia y modelacion".

- Extrait depuis ../centre-modelation-page/index.html :
    * le bloc <style> complet (parite visuelle)
    * les 4 panneaux academie (Bogota x2 -> colombie, modelisation x2 -> monde)
    * le dictionnaire textES (toutes les traductions ES existantes)
- Ajoute un nouvel en-tete, 3 sous-onglets, le panneau France (papiers + chercheurs),
  les traductions ES du panneau France et un JS simplifie (langue + sous-onglets).
"""
import re, pathlib

SRC = pathlib.Path(__file__).resolve().parent.parent / "centre-modelation-page" / "index.html"
OUT = pathlib.Path(__file__).resolve().parent / "index.html"
html = SRC.read_text(encoding="utf-8")

# --- 1. CSS complet + styles de la bande de logos ---------------------------
css = html[html.index("<style>") + len("<style>"): html.index("</style>")]
css += """
    /* Bande de logos partenaires (compacte) */
    .partner-band {
      display: inline-block;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 4px 9px;
      box-shadow: var(--soft-shadow);
      margin-bottom: 12px;
      max-width: 100%;
    }
    .partner-band img {
      height: 22px;
      width: auto;
      max-width: 100%;
      display: block;
    }
    @media (max-width: 720px) {
      .partner-band { padding: 3px 7px; }
      .partner-band img { height: 17px; }
    }

    /* En-tete non fixe (defile avec la page) */
    header {
      position: static;
      backdrop-filter: none;
    }
    /* Titre : typographie soignee */
    #page-title {
      font-family: "Fraunces", Georgia, "Times New Roman", serif;
      font-size: 44px;
      font-weight: 600;
      line-height: 1.02;
      letter-spacing: -0.015em;
      color: var(--navy);
      margin: 0 0 4px;
    }
    /* Bande de logos + langues empilees a droite */
    .toolbar {
      flex-direction: column;
      align-items: flex-end;
      gap: 10px;
    }
    .partner-band { margin-bottom: 0; }
    @media (max-width: 720px) {
      .toolbar { align-items: flex-start; }
      #page-title { font-size: 34px; }
    }

    /* Pastilles de filtrage par type de risque */
    .filter-host.academia-panel { padding: 0; }
    .filter-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin: 0 0 16px;
    }
    .filter-pill {
      min-height: 30px;
      padding: 5px 13px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--white);
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .01em;
    }
    .filter-pill:hover { color: var(--navy); border-color: #c2ccdb; }
    .filter-pill.active {
      background: var(--navy);
      color: #fff;
      border-color: var(--navy);
      box-shadow: var(--soft-shadow);
    }
"""

# --- 2. Panneaux Colombie + Monde ------------------------------------------
panel_start = '<section class="diagram-board academia-panel active" data-academia-panel-id="bogota">'
panel_end_marker = '\n        </div>\n      </section>\n    </main>'
i0 = html.index(panel_start)
i1 = html.index(panel_end_marker)
panels = html[i0:i1].rstrip()
panels = panels.replace('data-academia-panel-id="bogota"', 'data-academia-panel-id="colombie"')
panels = panels.replace('data-academia-panel-id="monde"', 'data-academia-panel-id="monde"')
panels = panels.replace('data-academia-panel-id="modelisation"', 'data-academia-panel-id="monde"')
assert 'panel-id="colombie"' in panels and 'panel-id="monde"' in panels, "rename panneaux KO"
# Retrait des pastilles (tag-row) des cartes de resultats
panels = re.sub(r'\s*<div class="tag-row">.*?</div>', '', panels)
assert 'tag-row' not in panels, "tag-row Colombie/Monde non retires"

# --- Classement des cartes par type de risque (data-risk) ------------------
# Resolution PAR ONGLET : la couleur d'accent fixe le type, avec quelques
# surcharges par tag (les memes tags/couleurs ne signifient pas la meme chose
# entre Colombie et Monde).
COL_ACCENT = {'red':'seisme','blue':'inondation','green':'mouvement',
              'violet':'gouvernance','cyan':'sante','amber':'urgence'}
COL_TAG = {'incendie':'feu','insar':'mouvement','telecom':'infrastructure'}
MON_ACCENT = {'red':'seisme','blue':'inondation','green':'mouvement',
              'violet':'multirisque','cyan':'infrastructure','amber':'climat'}
MON_TAG = {'volcan / systemique':'volcan'}
FAM2RISK = {'hydrologie':'inondation','seisme':'seisme','inondation':'inondation',
            'crue eclair':'inondation','avalanche':'avalanche','secheresse':'climat',
            'assurance':'gouvernance','volcan':'volcan','cotier':'inondation',
            'submersion':'inondation','glissement':'mouvement','feu de foret':'feu',
            'retrait-gonflement':'mouvement','mortalite':'gouvernance','gouvernance':'gouvernance',
            'canicule':'climat','tsunami':'tsunami','tempete':'climat','NaTech':'multirisque',
            'ilot de chaleur':'climat','eau urbaine':'inondation'}

def _resolve(accent, tag, accent_map, tag_map):
    a = accent.replace('var(', '').replace(')', '').replace('--', '').strip()
    t = tag.strip().lower()
    if t in tag_map:
        return tag_map[t]
    return accent_map.get(a, 'multirisque')

_CARD_RE = re.compile(
    r'<li class="paper-card" style="--accent:var\((--\w+)\)"><div class="paper-meta"><span>([^<]*)</span><span>([^<]*)</span>')

def inject_risk(html_frag, accent_map, tag_map):
    def repl(m):
        accent, year, tag = m.group(1), m.group(2), m.group(3)
        slug = _resolve(accent, tag, accent_map, tag_map)
        return (f'<li class="paper-card" data-risk="{slug}" style="--accent:var({accent})">'
                f'<div class="paper-meta"><span>{year}</span><span>{tag}</span>')
    return _CARD_RE.sub(repl, html_frag)

# Separer les panneaux Colombie (debut) et Monde (a partir du 1er panneau monde)
_mon_marker = '<section class="diagram-board academia-panel" data-academia-panel-id="monde">'
_mi = panels.index(_mon_marker)
panels = (inject_risk(panels[:_mi], COL_ACCENT, COL_TAG)
          + inject_risk(panels[_mi:], MON_ACCENT, MON_TAG))
assert 'data-risk=' in panels, "data-risk Colombie/Monde non injectes"

# --- Classement des CHERCHEURS par mots-cles (pour filtrer les auteurs) -----
import unicodedata
RISK_ORDER_PY = ['seisme','inondation','mouvement','climat','avalanche','feu',
                 'volcan','tsunami','gouvernance','infrastructure','urgence','sante','multirisque']
RISK_KEYWORDS = {
 'seisme':['sismi','seismic','seism','microzon','gmpe','earthquake','sismo','pushover','lignes vitales','ponts'],
 'inondation':['inondation','flood','crue','suds','drainage','eau urbain','cote','coast','submersion',
               'sea level','niveau marin','hydrolog','pluvi','littoral','surge','surcote','runoff','river',
               'marine flooding','aiga','nappe','plages'],
 'mouvement':['glissement','landslide','remocion','debris flow','debris-flow','mouvements de terrain',
              'movimiento en masa','susceptibilit','laves torrentielles','subsidence','retrait-gonflement',
              'insar','slope','estancia','geotechnolog'],
 'climat':['climat','climate','compound','compose','secheresse','sequia','drought','adaptation','extreme','ecoclimat'],
 'avalanche':['avalanche','avalancha','neige','snow'],
 'feu':['feu de foret','feux','wildfire','incendi','forest fire','allumage'],
 'volcan':['volcan','soufri','volcanic','eruptiv'],
 'tsunami':['tsunami','raz-de-maree','raz de maree','submarine landslide'],
 'gouvernance':['gouvernance','gouvernement','governance','politique','relogement','reasent','vulnerabilit',
                'citoyen','gobernanza','assurance','insurance','reassurance','catnat','economie','mortalit',
                'justice','arraigo','genre','pro-poor','secteur prive','social','haut risque'],
 'infrastructure':['infrastructure','reseaux','road','railway','network','telecom','bridge'],
 'urgence':['urgence','emergenc','evacuation','reponse','respuesta','logistique','early warning','alerte'],
 'sante':['sante','salud','health','pandemic','covid','pathogen','medical','sanitaire'],
 'multirisque':['multi-risque','multirriesgo','multi-hazard','multi-alea','riskscape','tomorrow',
                'exposition','exposure','impact model','cascad','metamodel','incertitude','natech',
                'apprentissage automatique','machine learning','deep learning','intelligence artificielle'],
}
def _norm(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()
def classify(text):
    t = _norm(text)
    return ' '.join(s for s in RISK_ORDER_PY
                    if any(k in t for k in RISK_KEYWORDS[s]))

def _tag_row(m):
    inner = m.group(1)
    text = re.sub(r'<[^>]+>', ' ', inner)
    return f'<tr data-risk="{classify(text)}">{inner}</tr>'
panels = re.sub(r'<tr>(<td>.*?</td>)</tr>', _tag_row, panels)
assert '<tr data-risk=' in panels, "data-risk chercheurs Colombie/Monde non injectes"

# --- 3. Dictionnaire textES existant ---------------------------------------
t0 = html.index("const textES = {")
t1 = html.index("const $ = (selector", t0)
text_es_block = html[t0:t1].rstrip()
assert text_es_block.startswith("const textES"), "extraction textES KO"

# ---------------------------------------------------------------------------
# 4. PANNEAU FRANCE : papiers
# (annee, accent, fam_fr, fam_es, titre, href, label, desc_fr, desc_es, auteurs)
# ---------------------------------------------------------------------------
papers = [
 ("2003","var(--blue)","hydrologie","hidrologia",
  "Improvement of a parsimonious model for streamflow simulation (GR4J)",
  "https://doi.org/10.1016/S0022-1694(03)00225-7","DOI",
  "Modele pluie-debit parcimonieux GR4J, socle de la modelisation hydrologique operationnelle francaise et de la prevision des debits.",
  "Modelo lluvia-caudal parsimonioso GR4J, base de la modelacion hidrologica operacional francesa y del pronostico de caudales.",
  "Charles Perrin; Claude Michel; Vazken Andreassian"),
 ("2007","var(--red)","seisme","sismo",
  "A simplified approach for vulnerability assessment in moderate-to-low seismic hazard regions: Grenoble",
  "https://doi.org/10.1007/s10518-007-9036-3","DOI",
  "Methode simplifiee de vulnerabilite sismique du bati pour les regions a sismicite moderee, appliquee a Grenoble.",
  "Metodo simplificado de vulnerabilidad sismica del edificado para regiones de sismicidad moderada, aplicado a Grenoble.",
  "Philippe Gueguen; Clotaire Michel; L. LeCorre"),
 ("2008","var(--blue)","inondation","inundacion",
  "Geographical analysis of damage due to flash floods in southern France (1999 and 2002)",
  "https://www.sciencedirect.com/science/article/abs/pii/S0143622808000179","ScienceDirect",
  "Analyse geographique des dommages des crues eclair mediterraneennes de 1999 et 2002, fondatrice pour l'etude du risque en France.",
  "Analisis geografico de los danos de las crecidas relampago mediterraneas de 1999 y 2002, fundacional para el estudio del riesgo en Francia.",
  "Freddy Vinet"),
 ("2009","var(--blue)","crue eclair","crecida relampago",
  "A compilation of data on European flash floods",
  "https://doi.org/10.1016/j.jhydrol.2008.12.028","DOI",
  "Inventaire de plus de 550 crues eclair europeennes, base de reference pour caracteriser l'alea et calibrer les modeles.",
  "Inventario de mas de 550 crecidas relampago europeas, base de referencia para caracterizar la amenaza y calibrar los modelos.",
  "Eric Gaume; Valerie Bain; Pietro Bernardara; et al."),
 ("2010","var(--cyan)","avalanche","avalancha",
  "A spatio-temporal modelling framework for assessing avalanche occurrence under climate change (northern French Alps)",
  "https://doi.org/10.1007/s10584-009-9718-8","DOI",
  "Cadre spatio-temporel bayesien reliant 60 ans d'avalanches des Alpes du Nord aux fluctuations climatiques.",
  "Marco espacio-temporal bayesiano que relaciona 60 anos de avalanchas de los Alpes del Norte con las fluctuaciones climaticas.",
  "Nicolas Eckert; Eric Parent; Richard Kies; Hans Baya"),
 ("2010","var(--blue)","crue eclair","crecida relampago",
  "Flash flood warning at ungauged locations using radar rainfall and antecedent soil moisture estimations",
  "https://doi.org/10.1016/j.jhydrol.2010.03.032","DOI",
  "Methode AIGA : seuils de debit sur bassins non jauges a partir de pluie radar, coeur du dispositif national d'alerte aux crues.",
  "Metodo AIGA: umbrales de caudal en cuencas no aforadas a partir de lluvia radar, nucleo del dispositivo nacional de alerta de crecidas.",
  "Pierre Javelle; Catherine Fouchier; Patrick Arnaud; Jacques Lavabre"),
 ("2010","var(--red)","seisme","sismo",
  "Comparison between seismic vulnerability models and experimental dynamic properties of existing buildings in France",
  "https://doi.org/10.1007/s10518-010-9185-7","DOI",
  "Confronte les modeles de vulnerabilite aux proprietes dynamiques mesurees in situ sur le bati existant francais.",
  "Confronta los modelos de vulnerabilidad con las propiedades dinamicas medidas in situ en el edificado existente frances.",
  "Clotaire Michel; Philippe Gueguen; Pierino Lestuzzi; et al."),
 ("2012","var(--cyan)","avalanche","avalancha",
  "Quantitative risk and optimal design approaches in the snow avalanche field: review and extensions",
  "https://hal.science/hal-01004165","HAL",
  "Revue et extensions des approches de risque quantitatif et de dimensionnement optimal des ouvrages paravalanches.",
  "Revision y extensiones de los enfoques de riesgo cuantitativo y de dimensionamiento optimo de las obras paravalanchas.",
  "Nicolas Eckert; Mohamed Naaim; Eric Parent; et al."),
 ("2012","var(--blue)","secheresse","sequia",
  "Meteorological, agricultural and hydrological drought projections over France for the 21st century",
  "https://hal.inrae.fr/hal-02596930","HAL",
  "Projections de secheresses meteorologiques, agricoles et hydrologiques sur la France au XXIe siecle.",
  "Proyecciones de sequias meteorologicas, agricolas e hidrologicas sobre Francia para el siglo XXI.",
  "Jean-Philippe Vidal; Eric Martin; N. Kitova; J.-M. Soubeyroux; Christian Page"),
 ("2014","var(--violet)","assurance","seguro",
  "Analysis of the French insurance market exposure to floods: a stochastic model combining river overflow and surface runoff",
  "https://doi.org/10.5194/nhess-14-2469-2014","DOI",
  "Modele stochastique CCR couplant debordement et ruissellement pour estimer l'exposition assurantielle francaise aux inondations.",
  "Modelo estocastico CCR que acopla desbordamiento y escorrentia para estimar la exposicion aseguradora francesa a las inundaciones.",
  "David Moncoulon; et al."),
 ("2014","var(--amber)","volcan","volcan",
  "Retrospective analysis of uncertain eruption precursors at La Soufriere, Guadeloupe (1975-77): a Bayesian Belief Network approach",
  "https://doi.org/10.1186/2191-5040-3-3","DOI",
  "Reseau bayesien pour quantifier l'incertitude des precurseurs eruptifs de La Soufriere de Guadeloupe.",
  "Red bayesiana para cuantificar la incertidumbre de los precursores eruptivos de La Soufriere de Guadalupe.",
  "Susanna Hincks; Jean-Christophe Komorowski; Steve Sparks; Willy Aspinall"),
 ("2014","var(--blue)","crue eclair","crecida relampago",
  "Evaluating flash-flood warnings at ungauged locations using post-event surveys: the AIGA system",
  "https://doi.org/10.1080/02626667.2014.923970","DOI",
  "Evalue les alertes AIGA sur bassins non jauges a partir d'enquetes post-evenement dans le sud de la France.",
  "Evalua las alertas AIGA en cuencas no aforadas a partir de encuestas post-evento en el sur de Francia.",
  "Pierre Javelle; Julie Demargne; D. Defrance; J. Pansu; Patrick Arnaud"),
 ("2015","var(--blue)","cotier","costero",
  "Evaluating uncertainties of future marine flooding occurrence as sea-level rises",
  "https://www.sciencedirect.com/science/article/pii/S1364815215300268","ScienceDirect",
  "Hierarchise les incertitudes (processus cotiers vs elevation marine) sur l'occurrence future de submersions sur un site mediterraneen.",
  "Jerarquiza las incertidumbres (procesos costeros vs ascenso del mar) sobre la ocurrencia futura de sumersiones en un sitio mediterraneo.",
  "Goneri Le Cozannet; Jeremy Rohmer; Anny Cazenave; Deborah Idier; et al."),
 ("2015","var(--blue)","submersion","sumersion",
  "The use of a micro-scale index to identify potential death risk areas due to coastal flood surges: storm Xynthia",
  "https://doi.org/10.1007/s11069-015-1669-y","DOI",
  "Indice micro-echelle de zones a risque mortel issu du retour d'experience de la tempete Xynthia (2010).",
  "Indice de micro-escala de zonas con riesgo mortal derivado de la experiencia de la tormenta Xynthia (2010).",
  "Axel Creach; Sophie Pardo; Patrick Guillotreau; Denis Mercier"),
 ("2016","var(--blue)","submersion","sumersion",
  "Estimation of insurance-related losses resulting from coastal flooding in France",
  "https://doi.org/10.5194/nhess-16-195-2016","DOI",
  "Modele CCR de pertes assurantielles par submersion marine combinant alea, niveaux marins extremes et exposition.",
  "Modelo CCR de perdidas aseguradoras por sumersion marina que combina amenaza, niveles marinos extremos y exposicion.",
  "Jean-Philippe Naulin; David Moncoulon; et al."),
 ("2016","var(--blue)","crue eclair","crecida relampago",
  "Flash flood-related mortality in southern France: first results from a new database",
  "https://doi.org/10.1051/e3sconf/20160706001","DOI",
  "Premiere base de donnees des deces par crue eclair dans le sud de la France (244 victimes recensees).",
  "Primera base de datos de fallecidos por crecida relampago en el sur de Francia (244 victimas registradas).",
  "Freddy Vinet; Laurent Boissier; Clotilde Saint-Martin"),
 ("2017","var(--red)","seisme","sismo",
  "Probabilistic seismic hazard assessment for South-Eastern France",
  "https://doi.org/10.1007/s10518-017-0249-9","DOI",
  "Evaluation probabiliste de l'alea sismique du Sud-Est de la France, avec arbres logiques et traitement des incertitudes.",
  "Evaluacion probabilista de la amenaza sismica del Sureste de Francia, con arboles logicos y tratamiento de incertidumbres.",
  "Caroline Beauval; et al."),
 ("2018","var(--green)","glissement","deslizamiento",
  "Pan-European landslide susceptibility mapping: ELSUS Version 2",
  "https://doi.org/10.1080/17445647.2018.1432511","DOI",
  "Carte europeenne de susceptibilite aux glissements (ELSUS v2), avec contribution francaise pour l'arc alpin.",
  "Mapa europeo de susceptibilidad a deslizamientos (ELSUS v2), con contribucion francesa para el arco alpino.",
  "Andreas Gunther; Jean-Philippe Malet; Paola Reichenbach; et al."),
 ("2020","var(--red)","seisme","sismo",
  "A probabilistic seismic hazard map for the metropolitan France",
  "https://doi.org/10.1007/s10518-020-00790-7","DOI",
  "Carte d'alea sismique probabiliste de la France metropolitaine, synthese du projet SIGMA et catalogue homogeneise.",
  "Mapa de amenaza sismica probabilista de la Francia metropolitana, sintesis del proyecto SIGMA y catalogo homogeneizado.",
  "Stephane Drouet; Gabriele Ameri; Kevin Le Dortz; et al."),
 ("2020","var(--amber)","feu de foret","incendio forestal",
  "Increased likelihood of heat-induced large wildfires in the Mediterranean Basin",
  "https://doi.org/10.1038/s41598-020-70069-z","DOI",
  "Montre l'augmentation des grands feux pilotes par les canicules dans le bassin mediterraneen, dont le sud francais.",
  "Muestra el aumento de los grandes incendios impulsados por las olas de calor en la cuenca mediterranea, incluido el sur frances.",
  "Julien Ruffault; Thomas Curt; Vincent Moron; et al."),
 ("2020","var(--amber)","feu de foret","incendio forestal",
  "Attributing increases in fire weather to anthropogenic climate change over France",
  "https://doi.org/10.3389/feart.2020.00104","DOI",
  "Attribue l'intensification du danger meteorologique de feu en France au changement climatique anthropique.",
  "Atribuye la intensificacion del peligro meteorologico de incendio en Francia al cambio climatico antropico.",
  "Nicolas Fargeon; Thibaut Frejaville; et al."),
 ("2021","var(--amber)","feu de foret","incendio forestal",
  "Point-process based Bayesian modeling of space-time structures of forest fire occurrences in Mediterranean France",
  "https://arxiv.org/abs/2002.12318","arXiv",
  "Modelisation bayesienne par processus ponctuels des occurrences de feux de foret en France mediterraneenne.",
  "Modelacion bayesiana por procesos puntuales de las ocurrencias de incendios forestales en la Francia mediterranea.",
  "Thomas Opitz; Florent Bonneu; Edith Gabriel"),
 ("2021","var(--cyan)","avalanche","avalancha",
  "Spatio-temporal variability of avalanche risk in the French Alps",
  "https://doi.org/10.1007/s10113-021-01838-3","DOI",
  "Caracterise la variabilite spatio-temporelle du risque d'avalanche dans les Alpes francaises.",
  "Caracteriza la variabilidad espacio-temporal del riesgo de avalancha en los Alpes franceses.",
  "Nicolas Eckert; Christophe Corona; Florie Giacona; et al."),
 ("2022","var(--green)","retrait-gonflement","retraccion-hinchamiento",
  "Predicting drought and subsidence risks in France",
  "https://doi.org/10.5194/nhess-22-2401-2022","DOI",
  "Modeles statistiques (random forests) predisant frequence et intensite des secheresses liees au retrait-gonflement des argiles.",
  "Modelos estadisticos (random forests) que predicen frecuencia e intensidad de las sequias ligadas a la retraccion-hinchamiento de arcillas.",
  "Arthur Charpentier; Molly James; Hani Ali"),
 ("2022","var(--amber)","feu de foret","incendio forestal",
  "Modelling fire risk exposure for France using machine learning",
  "https://doi.org/10.3390/app12031635","DOI",
  "Cartographie l'exposition au risque de feu en France par apprentissage automatique sur donnees environnementales.",
  "Cartografia la exposicion al riesgo de incendio en Francia mediante aprendizaje automatico sobre datos ambientales.",
  "Frederic Allaire; Vivien Mallet; Jean-Baptiste Filippi"),
 ("2022","var(--blue)","submersion","sumersion",
  "Partitioning the contributions of dependent offshore forcing conditions in the probabilistic assessment of future coastal flooding",
  "https://doi.org/10.5194/nhess-22-3167-2022","DOI",
  "Decompose les forcages marins dependants dans l'evaluation probabiliste de la submersion marine future.",
  "Descompone los forzamientos marinos dependientes en la evaluacion probabilista de la sumersion marina futura.",
  "Jeremy Rohmer; Deborah Idier; Remi Thieblemont; Goneri Le Cozannet; et al."),
 ("2022","var(--blue)","submersion","sumersion",
  "Method to identify the likelihood of death in residential buildings during coastal flooding",
  "https://doi.org/10.3390/buildings12020125","DOI",
  "Methode d'estimation de la probabilite de deces dans les batiments residentiels lors d'une submersion marine.",
  "Metodo de estimacion de la probabilidad de fallecimiento en edificios residenciales durante una sumersion marina.",
  "Axel Creach; et al."),
 ("2022","var(--blue)","mortalite","mortalidad",
  "Developing a large-scale dataset of flood fatalities for territories in the Euro-Mediterranean region (FFEM-DB)",
  "https://doi.org/10.1038/s41597-022-01273-x","DOI",
  "Base de donnees euro-mediterraneenne des deces par inondation, avec contribution francaise majeure (FFEM-DB).",
  "Base de datos euro-mediterranea de fallecidos por inundacion, con contribucion francesa importante (FFEM-DB).",
  "Olga Petrucci; Freddy Vinet; et al."),
 ("2022","var(--violet)","assurance","seguro",
  "Application of machine learning methods to predict drought cost in France",
  "https://doi.org/10.1007/s13385-022-00327-z","DOI",
  "Predit le cout assurantiel des secheresses geotechniques en France par apprentissage automatique sur donnees de sinistres.",
  "Predice el costo asegurador de las sequias geotecnicas en Francia mediante aprendizaje automatico sobre datos de siniestros.",
  "Geoffrey Ecoto; Antoine Chambaz"),
 ("2023","var(--blue)","cotier","costero",
  "Chronic flooding events due to sea-level rise in French Guiana",
  "https://doi.org/10.1038/s41598-023-48807-w","DOI",
  "Quantifie la montee des submersions chroniques a maree haute en Guyane francaise avec l'elevation du niveau marin.",
  "Cuantifica el aumento de las sumersiones cronicas en marea alta en la Guayana francesa con el ascenso del nivel del mar.",
  "Remi Thieblemont; Goneri Le Cozannet; Deborah Idier; et al."),
 ("2023","var(--blue)","cotier","costero",
  "Coastal flood at Gavres (Brittany): a simulated dataset to support risk management and metamodels development",
  "https://doi.org/10.3390/jmse11071314","DOI",
  "Jeu de donnees de simulations de submersion a Gavres (Bretagne) pour la gestion du risque et le developpement de metamodeles.",
  "Conjunto de datos de simulaciones de sumersion en Gavres (Bretana) para la gestion del riesgo y el desarrollo de metamodelos.",
  "Deborah Idier; Jeremy Rohmer; Remi Thieblemont; et al."),
 ("2024","var(--green)","retrait-gonflement","retraccion-hinchamiento",
  "A new approach for drought index adjustment to clay-shrinkage-induced subsidence over France",
  "https://doi.org/10.5194/nhess-24-999-2024","DOI",
  "Nouvel indice de secheresse (LAI interactif) correle aux sinistres de retrait-gonflement des argiles en France.",
  "Nuevo indice de sequia (LAI interactivo) correlacionado con los siniestros de retraccion-hinchamiento de arcillas en Francia.",
  "Sophie Barthelemy; Bertrand Bonan; Jean-Christophe Calvet; et al."),
 ("2024","var(--blue)","cotier","costero",
  "Satellite-derived sandy shoreline trends and interannual variability along the Atlantic coast of Europe",
  "https://doi.org/10.1038/s41598-024-63849-4","DOI",
  "Tendances et variabilite des traits de cote sableux atlantiques (dont le littoral francais) par teledetection satellitaire.",
  "Tendencias y variabilidad de las lineas de costa arenosas atlanticas (incluido el litoral frances) por teledeteccion satelital.",
  "Bruno Castelle; et al."),
 ("2024","var(--amber)","volcan","volcan",
  "Modeling staged and simultaneous evacuation during a volcanic crisis of La Soufriere of Guadeloupe",
  "https://doi.org/10.1177/00375497231209998","DOI",
  "Simulation multi-agent d'evacuations etagees et simultanees lors d'une crise volcanique a La Soufriere de Guadeloupe.",
  "Simulacion multi-agente de evacuaciones escalonadas y simultaneas durante una crisis volcanica en La Soufriere de Guadalupe.",
  "Olivier Gillet; Eric Daude; ...; Jean-Christophe Komorowski"),
 ("2018","var(--violet)","assurance","seguro",
  "Natural disasters: exposure and underinsurance",
  "https://www.jstor.org/stable/10.15609/annaeconstat2009.129.0053","JSTOR",
  "Analyse economique de la sous-assurance et de l'exposition aux catastrophes naturelles sous le regime CatNat francais.",
  "Analisis economico del subaseguramiento y de la exposicion a las catastrofes naturales bajo el regimen CatNat frances.",
  "Celine Grislain-Letremy"),
 ("2025","var(--blue)","crue eclair","crecida relampago",
  "Evaluating the French flash flood warning system using hydrological and impact data in south-eastern France",
  "https://onlinelibrary.wiley.com/doi/abs/10.1111/jfr3.70053","DOI",
  "Evaluation recente du systeme national d'alerte aux crues eclair croisant donnees hydrologiques et donnees d'impact.",
  "Evaluacion reciente del sistema nacional de alerta de crecidas relampago cruzando datos hidrologicos y datos de impacto.",
  "A. Godet; Pierre Javelle; Olivier Payrastre; et al."),
 ("2025","var(--blue)","hydrologie","hidrologia",
  "Will rivers become more intermittent in France? Learning from an extended set of hydrological projections",
  "https://doi.org/10.5194/hess-29-3629-2025","DOI",
  "Projette l'evolution de l'intermittence des rivieres francaises a partir d'un large ensemble de simulations hydrologiques.",
  "Proyecta la evolucion de la intermitencia de los rios franceses a partir de un amplio conjunto de simulaciones hidrologicas.",
  "Louise Mimeau; et al."),
 ("2026","var(--blue)","hydrologie","hidrologia",
  "A large transient multi-scenario multi-model ensemble of future streamflow and groundwater projections in France (Explore2)",
  "https://doi.org/10.5194/hess-30-2277-2026","DOI",
  "Ensemble Explore2 : projections de debits et de nappes pour la France, support des strategies d'adaptation au changement climatique.",
  "Conjunto Explore2: proyecciones de caudales y acuiferos para Francia, soporte de las estrategias de adaptacion al cambio climatico.",
  "Eric Sauquet; et al."),
 ("2025","var(--green)","retrait-gonflement","retraccion-hinchamiento",
  "A novel clay shrink-swell buildings damage model: from unstructured insurance data to a damage severity scale",
  "https://www.sciencedirect.com/science/article/pii/S2212420925004601","ScienceDirect",
  "Modele de dommage du bati par retrait-gonflement construit a partir de donnees assurantielles non structurees.",
  "Modelo de dano del edificado por retraccion-hinchamiento construido a partir de datos aseguradores no estructurados.",
  "Equipe BRGM / assurance"),
 ("2025","var(--violet)","gouvernance","gobernanza",
  "10 years and going strong? Coastal flood risk management in the wake of the 2010 Xynthia storm",
  "https://www.sciencedirect.com/science/article/pii/S2212096322000201","ScienceDirect",
  "Analyse l'evolution sur dix ans de la gestion du risque de submersion en Charente-Maritime apres la tempete Xynthia.",
  "Analiza la evolucion en diez anos de la gestion del riesgo de sumersion en Charente-Maritime tras la tormenta Xynthia.",
  "Equipe gestion du risque cotier"),
]

# 5. PANNEAU FRANCE : chercheurs
# (nom, pays_fr, pays_es, inst_fr, inst_es, travaux_fr, travaux_es, contact_html)
researchers = [
 ("Eric Gaume","France","Francia","Universite Gustave Eiffel (GERS)","Universite Gustave Eiffel (GERS)",
  "Crues eclair, inventaire europeen, hydrologie des bassins non jauges.",
  "Crecidas relampago, inventario europeo, hidrologia de cuencas no aforadas.",
  '<a href="mailto:eric.gaume@univ-eiffel.fr">eric.gaume@univ-eiffel.fr</a>'),
 ("Olivier Payrastre","France","Francia","Universite Gustave Eiffel","Universite Gustave Eiffel",
  "Crues eclair, modelisation distribuee, alerte sur bassins non jauges.",
  "Crecidas relampago, modelacion distribuida, alerta en cuencas no aforadas.",
  '<a href="mailto:olivier.payrastre@univ-eiffel.fr">olivier.payrastre@univ-eiffel.fr</a>'),
 ("Pierre Javelle","France","Francia","INRAE Aix-en-Provence (RECOVER)","INRAE Aix-en-Provence (RECOVER)",
  "Methode AIGA, alerte aux crues, pluie radar et seuils de debit.",
  "Metodo AIGA, alerta de crecidas, lluvia radar y umbrales de caudal.",
  '<a href="mailto:pierre.javelle@inrae.fr">pierre.javelle@inrae.fr</a>'),
 ("Freddy Vinet","France","Francia","Universite Paul-Valery Montpellier 3 (GRED)","Universite Paul-Valery Montpellier 3 (GRED)",
  "Mortalite par inondation, crues eclair, bases de donnees de victimes.",
  "Mortalidad por inundacion, crecidas relampago, bases de datos de victimas.",
  '<a href="mailto:freddy.vinet@univ-montp3.fr">freddy.vinet@univ-montp3.fr</a>'),
 ("David Moncoulon","France","Francia","Caisse Centrale de Reassurance (CCR)","Caisse Centrale de Reassurance (CCR)",
  "Modeles de pertes CatNat : inondation, submersion marine et secheresse.",
  "Modelos de perdidas CatNat: inundacion, sumersion marina y sequia.",
  '<a href="https://www.ccr.fr/" target="_blank" rel="noopener">CCR / modelisation</a>'),
 ("Nicolas Eckert","France","Francia","INRAE / IGE Grenoble (ETNA)","INRAE / IGE Grenoble (ETNA)",
  "Risque d'avalanche, statistiques d'extremes, effets du climat et de la foret.",
  "Riesgo de avalancha, estadistica de extremos, efectos del clima y del bosque.",
  '<a href="mailto:nicolas.eckert@inrae.fr">nicolas.eckert@inrae.fr</a>'),
 ("Mohamed Naaim","France","Francia","INRAE Grenoble (ETNA)","INRAE Grenoble (ETNA)",
  "Dynamique des avalanches et des ecoulements gravitaires rapides.",
  "Dinamica de las avalanchas y de los flujos gravitatorios rapidos.",
  '<a href="mailto:mohamed.naaim@inrae.fr">mohamed.naaim@inrae.fr</a>'),
 ("Deborah Idier","France","Francia","BRGM Orleans","BRGM Orleans",
  "Submersion marine, surcotes, metamodeles et incertitudes cotieres.",
  "Sumersion marina, sobreelevaciones, metamodelos e incertidumbres costeras.",
  '<a href="mailto:d.idier@brgm.fr">d.idier@brgm.fr</a>'),
 ("Goneri Le Cozannet","France","Francia","BRGM Orleans","BRGM Orleans",
  "Elevation du niveau marin, risques cotiers, adaptation (GIEC AR6).",
  "Ascenso del nivel del mar, riesgos costeros, adaptacion (IPCC AR6).",
  '<a href="mailto:g.lecozannet@brgm.fr">g.lecozannet@brgm.fr</a>'),
 ("Jeremy Rohmer","France","Francia","BRGM Orleans","BRGM Orleans",
  "Incertitudes, approches probabilistes et metamodeles pour la submersion marine.",
  "Incertidumbres, enfoques probabilistas y metamodelos para la sumersion marina.",
  '<a href="mailto:j.rohmer@brgm.fr">j.rohmer@brgm.fr</a>'),
 ("Jean-Philippe Malet","France","Francia","ITES / EOST, CNRS - Universite de Strasbourg","ITES / EOST, CNRS - Universite de Strasbourg",
  "Glissements de terrain, laves torrentielles, susceptibilite et surveillance.",
  "Deslizamientos, flujos de derrubios, susceptibilidad y monitoreo.",
  '<a href="mailto:jeanphilippe.malet@unistra.fr">jeanphilippe.malet@unistra.fr</a>'),
 ("Yannick Thiery","France","Francia","BRGM","BRGM",
  "Susceptibilite aux mouvements de terrain et cartographie de l'alea.",
  "Susceptibilidad a movimientos de terreno y cartografia de la amenaza.",
  '<a href="mailto:y.thiery@brgm.fr">y.thiery@brgm.fr</a>'),
 ("Philippe Gueguen","France","Francia","ISTerre, Universite Grenoble Alpes","ISTerre, Universite Grenoble Alpes",
  "Vulnerabilite sismique du bati, courbes de fragilite, echelle urbaine.",
  "Vulnerabilidad sismica del edificado, curvas de fragilidad, escala urbana.",
  '<a href="mailto:philippe.gueguen@univ-grenoble-alpes.fr">philippe.gueguen@univ-grenoble-alpes.fr</a>'),
 ("Caroline Beauval","France","Francia","ISTerre / IRD Grenoble","ISTerre / IRD Grenoble",
  "Alea sismique probabiliste, GMPE, arbres logiques et incertitudes.",
  "Amenaza sismica probabilista, GMPE, arboles logicos e incertidumbres.",
  '<a href="mailto:caroline.beauval@univ-grenoble-alpes.fr">caroline.beauval@univ-grenoble-alpes.fr</a>'),
 ("John Douglas","Royaume-Uni / France","Reino Unido / Francia","University of Strathclyde (ex-BRGM)","University of Strathclyde (ex-BRGM)",
  "Equations de prediction du mouvement du sol, alea sismique de la France.",
  "Ecuaciones de prediccion del movimiento del suelo, amenaza sismica de Francia.",
  '<a href="mailto:john.douglas@strath.ac.uk">john.douglas@strath.ac.uk</a>'),
 ("Thomas Curt","France","Francia","INRAE Aix-en-Provence (RECOVER)","INRAE Aix-en-Provence (RECOVER)",
  "Feux de foret, regimes de feu, causes d'allumage et prevention.",
  "Incendios forestales, regimenes de fuego, causas de ignicion y prevencion.",
  '<a href="mailto:thomas.curt@inrae.fr">thomas.curt@inrae.fr</a>'),
 ("Jean-Christophe Komorowski","France","Francia","IPGP, Universite Paris Cite","IPGP, Universite Paris Cite",
  "Alea volcanique, La Soufriere, scenarios eruptifs et modelisation d'impacts.",
  "Amenaza volcanica, La Soufriere, escenarios eruptivos y modelacion de impactos.",
  '<a href="mailto:komorowski@ipgp.fr">komorowski@ipgp.fr</a>'),
 ("Vazken Andreassian","France","Francia","INRAE Antony (HYCAR)","INRAE Antony (HYCAR)",
  "Modeles hydrologiques GR, prevision des debits, hydrologie comparative.",
  "Modelos hidrologicos GR, pronostico de caudales, hidrologia comparativa.",
  '<a href="mailto:vazken.andreassian@inrae.fr">vazken.andreassian@inrae.fr</a>'),
 ("Jean-Philippe Vidal","France","Francia","INRAE Lyon (RiverLy)","INRAE Lyon (RiverLy)",
  "Secheresse, projections climatiques et hydrologiques, projet Explore2.",
  "Sequia, proyecciones climaticas e hidrologicas, proyecto Explore2.",
  '<a href="mailto:jean-philippe.vidal@inrae.fr">jean-philippe.vidal@inrae.fr</a>'),
 ("Bruno Castelle","France","Francia","CNRS / Universite de Bordeaux (EPOC)","CNRS / Universite de Bordeaux (EPOC)",
  "Erosion cotiere, dynamique des plages sableuses, traits de cote.",
  "Erosion costera, dinamica de playas arenosas, lineas de costa.",
  '<a href="mailto:bruno.castelle@u-bordeaux.fr">bruno.castelle@u-bordeaux.fr</a>'),
 ("Celine Grislain-Letremy","France","Francia","Universite Paris-Dauphine / Banque de France","Universite Paris-Dauphine / Banque de France",
  "Economie de l'assurance des catastrophes naturelles, regime CatNat.",
  "Economia del seguro de catastrofes naturales, regimen CatNat.",
  '<a href="https://www.banque-france.fr/" target="_blank" rel="noopener">profil public</a>'),
 ("Arthur Charpentier","Canada / France","Canada / Francia","UQAM (ex-Univ. Rennes)","UQAM (ex-Univ. Rennes)",
  "Actuariat, modeles statistiques du risque de secheresse et de subsidence.",
  "Actuaria, modelos estadisticos del riesgo de sequia y de subsidencia.",
  '<a href="https://freakonometrics.hypotheses.org/" target="_blank" rel="noopener">site public</a>'),
]

# ---------------------------------------------------------------------------
# Generation HTML France
# ---------------------------------------------------------------------------
def esc(s):  # securite minimale (pas de < > & dans nos textes)
    return s

# --- FRANCE : extension du corpus (canicule, tsunami, sismicite historique, ----
#     prevision operationnelle, RGA, cotier, NaTech) ---------------------------
papers += [
 ("2008","var(--amber)","canicule","canicula",
  "Death toll exceeded 70,000 in Europe during the summer of 2003",
  "https://doi.org/10.1016/j.crvi.2007.12.001","DOI",
  "Estimation de la surmortalite europeenne de la canicule 2003, reference majeure du risque chaleur.",
  "Estimacion de la sobremortalidad europea de la ola de calor de 2003, referencia clave del riesgo de calor.",
  "Jean-Marie Robine; Siu Lan K. Cheung; Sophie Le Roy; Herman Van Oyen; Clare Griffiths; Jean-Pierre Michel; Francois R. Herrmann"),
 ("2006","var(--amber)","canicule","canicula",
  "Excess mortality related to the August 2003 heat wave in France",
  "https://doi.org/10.1007/s00420-006-0089-4","DOI",
  "Quantifie pres de 15 000 deces lies a la canicule d'aout 2003 en France et leurs facteurs de vulnerabilite.",
  "Cuantifica cerca de 15 000 muertes por la ola de calor de agosto de 2003 en Francia y sus factores de vulnerabilidad.",
  "Alain Fouillet; Gregoire Rey; Frederic Laurent; Gerard Pavillon; et al."),
 ("2009","var(--blue)","tsunami","tsunami",
  "The tsunami triggered by the 21 May 2003 Boumerdes-Zemmouri earthquake: French Mediterranean coast field survey and modelling",
  "https://doi.org/10.5194/nhess-9-1823-2009","DOI",
  "Enquetes de terrain et modelisation du tsunami de 2003 sur la cote mediterraneenne francaise.",
  "Investigaciones de campo y modelacion del tsunami de 2003 en la costa mediterranea francesa.",
  "Alexandre Sahal; Jean Roger; Sebastien Allgeyer; B. Lemaire; Helene Hebert; Francois Schindele; Franck Lavigne"),
 ("2020","var(--blue)","tsunami","tsunami",
  "Tsunami intensity scale based on wave amplitude and current applied to the French Riviera",
  "https://doi.org/10.1007/s11069-020-03921-0","DOI",
  "Echelle d'intensite tsunami appliquee a la Cote d'Azur pour la sismicite locale.",
  "Escala de intensidad de tsunami aplicada a la Costa Azul para la sismicidad local.",
  "Jean Roger; Helene Hebert; et al."),
 ("2018","var(--red)","seisme","sismo",
  "The French seismic CATalogue (FCAT-17)",
  "https://doi.org/10.1007/s10518-017-0236-1","DOI",
  "Catalogue sismique homogeneise de la France, socle des evaluations probabilistes d'alea sismique.",
  "Catalogo sismico homogeneizado de Francia, base de las evaluaciones probabilistas de amenaza sismica.",
  "Kevin Manchuel; Paola Traversa; David Baumont; Michel Cara; et al."),
 ("2021","var(--red)","seisme","sismo",
  "The SISFRANCE database of historical seismicity: state of the art and perspectives",
  "https://doi.org/10.5802/crgeos.91","DOI",
  "Base de sismicite historique (EDF-BRGM-IRSN) essentielle a l'alea sismique en contexte de faible deformation.",
  "Base de sismicidad historica (EDF-BRGM-IRSN) esencial para la amenaza sismica en contexto de baja deformacion.",
  "Oona Scotti; Christophe Sira; Antoine Schlupp; et al."),
 ("2025","var(--blue)","inondation","inundacion",
  "Vigicrues : 20 ans de progres pour la prevision des crues en France",
  "https://doi.org/10.1080/27678490.2025.2472646","DOI",
  "Bilan de 20 ans du dispositif national Vigicrues de prevision operationnelle des crues.",
  "Balance de 20 anos del dispositivo nacional Vigicrues de prevision operacional de crecidas.",
  "Schapi ; reseau Vigicrues"),
 ("2025","var(--green)","retrait-gonflement","retraccion-hinchamiento",
  "Analysis of past and future droughts causing clay shrinkage in France",
  "https://doi.org/10.5194/hess-29-2321-2025","DOI",
  "Analyse des secheresses passees et futures responsables du retrait-gonflement des argiles en France.",
  "Analisis de las sequias pasadas y futuras responsables de la retraccion-hinchamiento de arcillas en Francia.",
  "Sophie Barthelemy; Bertrand Bonan; Jean-Christophe Calvet; et al."),
 ("2024","var(--blue)","cotier","costero",
  "Scenarios nationaux de recul du trait de cote pour le littoral francais (horizons 2050 et 2100)",
  "https://www.geolittoral.developpement-durable.gouv.fr/","Cerema / Geolittoral",
  "Cartographies nationales du recul du trait de cote a 2050 et 2100 et exposition des biens du littoral.",
  "Cartografias nacionales del retroceso de la linea de costa a 2050 y 2100 y exposicion de los bienes del litoral.",
  "Cerema ; ministere de la Transition ecologique"),
 ("2024","var(--amber)","NaTech","NaTech",
  "Projet NaTech (PEPR IRiMa) : anticiper les accidents technologiques declenches par des aleas naturels",
  "https://www.pepr-risques.fr/en/flagship-projects/natech-risks-anticipating-and-managing-technological-accidents-triggered-natural","PEPR IRiMa",
  "Programme francais sur les risques NaTech, applique aux vallees de la Seine, de la Gironde et du Rhone.",
  "Programa frances sobre riesgos NaTech, aplicado a los valles del Sena, de la Gironda y del Rodano.",
  "Karine Adam (INERIS); Irene Korsakissok (IRSN)"),
]
researchers += [
 ("Centre Europeen de Prevention du Risque d'Inondation (CEPRI)","France","Francia",
  "CEPRI","CEPRI",
  "Reference nationale sur la prevention du risque d'inondation, vulnerabilite du bati et resilience des territoires.",
  "Referencia nacional sobre la prevencion del riesgo de inundacion, vulnerabilidad del edificado y resiliencia de los territorios.",
  '<a href="https://www.cepri.net/" target="_blank" rel="noopener">cepri.net</a>'),
 ("Caisse Centrale de Reassurance (CCR)","France","Francia",
  "CCR - direction R&D modelisation","CCR - direccion I+D modelacion",
  "Modeles de pertes CatNat (inondation, submersion marine, secheresse), donnees assurantielles nationales et projections climatiques.",
  "Modelos de perdidas CatNat (inundacion, sumersion marina, sequia), datos aseguradores nacionales y proyecciones climaticas.",
  '<a href="https://catnat.ccr.fr/" target="_blank" rel="noopener">catnat.ccr.fr</a>'),
 ("Institut de Radioprotection et de Surete Nucleaire (IRSN)","France","Francia",
  "IRSN","IRSN",
  "Alea sismique, mouvements de terrain (BDMvT), risques NaTech et surete des installations.",
  "Amenaza sismica, movimientos de terreno (BDMvT), riesgos NaTech y seguridad de las instalaciones.",
  '<a href="https://www.irsn.fr/" target="_blank" rel="noopener">irsn.fr</a>'),
 ("Cerema","France","Francia",
  "Cerema","Cerema",
  "Risques cotiers, recul du trait de cote, mouvements de terrain et adaptation des territoires littoraux.",
  "Riesgos costeros, retroceso de la linea de costa, movimientos de terreno y adaptacion de los territorios litorales.",
  '<a href="https://www.cerema.fr/" target="_blank" rel="noopener">cerema.fr</a>'),
 ("INERIS","France","Francia",
  "INERIS","INERIS",
  "Risques technologiques et NaTech : accidents industriels declenches par des aleas naturels.",
  "Riesgos tecnologicos y NaTech: accidentes industriales desencadenados por amenazas naturales.",
  '<a href="https://www.ineris.fr/" target="_blank" rel="noopener">ineris.fr</a>'),
 ("Helene Hebert","France","Francia",
  "CEA / CENALT","CEA / CENALT",
  "Modelisation de l'alea tsunami (Mediterranee, Antilles) et centre national d'alerte CENALT.",
  "Modelacion de la amenaza de tsunami (Mediterraneo, Antillas) y centro nacional de alerta CENALT.",
  '<a href="mailto:helene.hebert@cea.fr">helene.hebert@cea.fr</a>'),
 ("Kevin Manchuel","France","Francia",
  "EDF - consortium SISFRANCE","EDF - consorcio SISFRANCE",
  "Catalogue sismique FCAT, sismicite historique et alea sismique de la France.",
  "Catalogo sismico FCAT, sismicidad historica y amenaza sismica de Francia.",
  '<a href="mailto:kevin.manchuel@edf.fr">kevin.manchuel@edf.fr</a>'),
 ("Eric Sauquet","France","Francia",
  "INRAE Lyon (RiverLy)","INRAE Lyon (RiverLy)",
  "Hydrologie, etiages, projet Explore2 et projections de debits.",
  "Hidrologia, estiajes, proyecto Explore2 y proyecciones de caudales.",
  '<a href="mailto:eric.sauquet@inrae.fr">eric.sauquet@inrae.fr</a>'),
 ("Schapi - reseau Vigicrues","France","Francia",
  "Schapi (Service Central d'Hydrometeorologie)","Schapi (Servicio Central de Hidrometeorologia)",
  "Prevision operationnelle des crues (Vigicrues, Vigicrues Flash) et hydrometeorologie nationale.",
  "Prevision operacional de crecidas (Vigicrues, Vigicrues Flash) e hidrometeorologia nacional.",
  '<a href="https://www.vigicrues.gouv.fr/" target="_blank" rel="noopener">vigicrues.gouv.fr</a>'),
]

cards = []
for (yr, accent, fam_fr, fam_es, title, href, label, dfr, dfe, auth) in papers:
    slug = FAM2RISK.get(fam_fr, 'multirisque')
    cards.append(
        f'<li class="paper-card" data-risk="{slug}" style="--accent:{accent}">'
        f'<div class="paper-meta"><span>{yr}</span><span>{fam_fr}</span></div>'
        f'<h4 class="paper-title">{title}</h4>'
        f'<p>{dfr}</p>'
        f'<div class="paper-authors">{auth}</div>'
        f'<div class="paper-source"><a href="{href}" target="_blank" rel="noopener">{label}</a></div></li>'
    )
cards_html = "\n              ".join(cards)

rows = []
for (nom, pfr, pes, ifr, ies, wfr, wes, contact) in researchers:
    slugs = classify(nom + ' ' + wfr + ' ' + ifr)
    rows.append(
        f'<tr data-risk="{slugs}"><td>{nom}</td><td>{pfr}</td><td>{ifr}</td><td>{wfr}</td><td>{contact}</td></tr>'
    )
rows_html = "\n                  ".join(rows)

# Indicateurs France calcules dynamiquement
_fr_years = [int(p[0]) for p in papers]
fr_doc = len(papers)
fr_period = f"{min(_fr_years)}-{max(_fr_years)}"
fr_fam = len({FAM2RISK.get(p[2], 'multirisque') for p in papers})
fr_res = len(researchers)

france_panels = f'''
          <section class="diagram-board academia-panel" data-academia-panel-id="france">
            <div class="board-head">
              <div>
                <h3>Academie - modelisation des risques en France</h3>
                <p>Revue ciblee du corpus scientifique francais : crues eclair et inondation, submersion marine et littoral, seisme, mouvements de terrain et retrait-gonflement des argiles, avalanche, feu de foret, volcan et economie du risque.</p>
              </div>
            </div>

            <div class="academia-brief">
              <div class="academia-note">
                <strong>Perimetre retenu</strong>
                Corpus francais oriente vers les methodes transferables a un centre de modelisation : chaines alea-exposition-vulnerabilite-pertes, modeles probabilistes, incertitudes, donnees ouvertes et apprentissage automatique. Priorite aux equipes BRGM, INRAE (ex-Irstea/Cemagref), IPGP, ISTerre/EOST, Universite Gustave Eiffel, Meteo-France/CNRM et a la Caisse Centrale de Reassurance, ainsi qu'aux revues a fort impact (NHESS, HESS, Journal of Hydrology, Bulletin of Earthquake Engineering, Scientific Reports).
              </div>
              <div class="academia-stats">
                <div class="academia-stat"><strong>{fr_doc}</strong><span>documents reperes</span></div>
                <div class="academia-stat"><strong>{fr_period}</strong><span>periode couverte</span></div>
                <div class="academia-stat"><strong>{fr_fam}</strong><span>familles de risque</span></div>
                <div class="academia-stat"><strong>{fr_res}</strong><span>chercheurs clefs</span></div>
              </div>
            </div>

            <ul class="paper-list">
              {cards_html}
            </ul>
          </section>

          <section class="diagram-board academia-panel" data-academia-panel-id="france">
            <div class="board-head">
              <div>
                <h3>Chercheurs francais et contacts publics</h3>
                <p>Contacts institutionnels ou profils publics a mobiliser pour un comite scientifique, des echanges de methodes (AIGA, OpenQuake, modeles GR, modeles CCR) ou un cadrage multi-alea adapte au contexte francais.</p>
              </div>
            </div>
            <div class="researcher-table-wrap">
              <table class="researcher-table">
                <thead><tr><th>Nom</th><th>Pays / ancrage</th><th>Universite / organisme</th><th>Apport scientifique clef</th><th>Contact public</th></tr></thead>
                <tbody>
                  {rows_html}
                </tbody>
              </table>
            </div>
          </section>'''

# ---------------------------------------------------------------------------
# Dictionnaire ES du panneau France
# ---------------------------------------------------------------------------
fr_es = {
 # en-tete + brief + tableaux
 "Academie - modelisation des risques en France": "Academia - modelacion de riesgos en Francia",
 "Revue ciblee du corpus scientifique francais : crues eclair et inondation, submersion marine et littoral, seisme, mouvements de terrain et retrait-gonflement des argiles, avalanche, feu de foret, volcan et economie du risque.":
   "Revision focalizada del corpus cientifico frances: crecidas relampago e inundacion, sumersion marina y litoral, sismo, movimientos de terreno y retraccion-hinchamiento de arcillas, avalancha, incendio forestal, volcan y economia del riesgo.",
 "Corpus francais": "Corpus frances",
 "Corpus francais oriente vers les methodes transferables a un centre de modelisation : chaines alea-exposition-vulnerabilite-pertes, modeles probabilistes, incertitudes, donnees ouvertes et apprentissage automatique. Priorite aux equipes BRGM, INRAE (ex-Irstea/Cemagref), IPGP, ISTerre/EOST, Universite Gustave Eiffel, Meteo-France/CNRM et a la Caisse Centrale de Reassurance, ainsi qu'aux revues a fort impact (NHESS, HESS, Journal of Hydrology, Bulletin of Earthquake Engineering, Scientific Reports).":
   "Corpus frances orientado a metodos transferibles a un centro de modelacion: cadenas amenaza-exposicion-vulnerabilidad-perdidas, modelos probabilistas, incertidumbres, datos abiertos y aprendizaje automatico. Prioridad a los equipos BRGM, INRAE (ex-Irstea/Cemagref), IPGP, ISTerre/EOST, Universite Gustave Eiffel, Meteo-France/CNRM y a la Caisse Centrale de Reassurance, asi como a las revistas de alto impacto (NHESS, HESS, Journal of Hydrology, Bulletin of Earthquake Engineering, Scientific Reports).",
 "Chercheurs francais et contacts publics": "Investigadores franceses y contactos publicos",
 "Contacts institutionnels ou profils publics a mobiliser pour un comite scientifique, des echanges de methodes (AIGA, OpenQuake, modeles GR, modeles CCR) ou un cadrage multi-alea adapte au contexte francais.":
   "Contactos institucionales o perfiles publicos para movilizar en un comite cientifico, intercambios de metodos (AIGA, OpenQuake, modelos GR, modelos CCR) o un encuadre multiamenaza adaptado al contexto frances.",
}
# familles (tags)
for (_, _, fam_fr, fam_es, *rest) in papers:
    fr_es[fam_fr] = fam_es
# descriptions des papiers
for (_, _, _, _, _, _, _, dfr, dfe, _) in papers:
    fr_es[dfr] = dfe
# pays + institutions + travaux des chercheurs
for (nom, pfr, pes, ifr, ies, wfr, wes, contact) in researchers:
    fr_es[pfr] = pes
    if ifr != ies:
        fr_es[ifr] = ies
    fr_es[wfr] = wes

# sous-onglets + sous-titres deja geres cote JS (sous-onglets via textES)
fr_es["Modelisation des risques en Colombie"] = "Modelacion de riesgos en Colombia"
fr_es["Modelisation des risques dans le monde"] = "Modelacion de riesgos en el mundo"
fr_es["Modelisation des risques en France"] = "Modelacion de riesgos en Francia"

# serialisation du dict France en JS
def js_obj(d):
    out = []
    for k, v in d.items():
        k2 = k.replace("\\", "\\\\").replace('"', '\\"')
        v2 = v.replace("\\", "\\\\").replace('"', '\\"')
        out.append(f'      "{k2}": "{v2}"')
    return "{\n" + ",\n".join(out) + "\n    }"

# ===========================================================================
# EXTENSION DES CORPUS MONDE + COLOMBIE (cartes + chercheurs inseres dans
# les panneaux extraits, traductions ES, recalcul des indicateurs)
# ===========================================================================
# (annee, accent, fam_fr, fam_es, risk, titre, href, label, desc_fr, desc_es, auteurs)
monde_extra = [
 ("2015","var(--amber)","feu de foret","incendio forestal","feu",
  "Climate-induced variations in global wildfire danger from 1979 to 2013",
  "https://doi.org/10.1038/ncomms8537","DOI",
  "Montre l'allongement global de la saison de feu et l'extension des zones a fort danger.",
  "Muestra la prolongacion global de la temporada de incendios y la expansion de zonas de alto peligro.",
  "W. Matt Jolly; Mark A. Cochrane; Patrick H. Freeborn; Zachary A. Holden; Timothy J. Brown; et al."),
 ("2016","var(--amber)","feu de foret","incendio forestal","feu",
  "Impact of anthropogenic climate change on wildfire across western US forests",
  "https://doi.org/10.1073/pnas.1607171113","DOI",
  "Attribue au changement climatique anthropique le doublement des surfaces forestieres brulees a l'Ouest americain.",
  "Atribuye al cambio climatico antropico la duplicacion de las superficies forestales quemadas en el oeste de EE. UU.",
  "John T. Abatzoglou; A. Park Williams"),
 ("2010","var(--cyan)","secheresse","sequia","climat",
  "A multiscalar drought index sensitive to global warming: the SPEI",
  "https://doi.org/10.1175/2009JCLI2909.1","DOI",
  "Indice de secheresse SPEI integrant l'evapotranspiration, reference mondiale sensible au rechauffement.",
  "Indice de sequia SPEI que integra la evapotranspiracion, referencia mundial sensible al calentamiento.",
  "Sergio M. Vicente-Serrano; Santiago Begueria; Juan I. Lopez-Moreno"),
 ("2021","var(--amber)","canicule","canicula","climat",
  "The burden of heat-related mortality attributable to recent human-induced climate change",
  "https://doi.org/10.1038/s41558-021-01058-x","DOI",
  "Attribue plus d'un tiers des deces lies a la chaleur au changement climatique anthropique (43 pays).",
  "Atribuye mas de un tercio de las muertes por calor al cambio climatico antropico (43 paises).",
  "Ana M. Vicedo-Cabrera; Noah Scovronick; Francesco Sera; et al."),
 ("2018","var(--green)","glissement","deslizamiento","mouvement",
  "Global fatal landslide occurrence from 2004 to 2016",
  "https://doi.org/10.5194/nhess-18-2161-2018","DOI",
  "Base mondiale des glissements meurtriers : 55 997 deces en 4 862 evenements non sismiques.",
  "Base mundial de deslizamientos mortales: 55 997 muertes en 4 862 eventos no sismicos.",
  "Melanie J. Froude; David N. Petley"),
 ("2017","var(--blue)","tsunami","tsunami","tsunami",
  "Probabilistic tsunami hazard analysis: multiple sources and global applications",
  "https://doi.org/10.1002/2017RG000579","DOI",
  "Revue de reference des methodes probabilistes d'alea tsunami (PTHA) et de leurs applications globales.",
  "Revision de referencia de los metodos probabilistas de amenaza de tsunami (PTHA) y sus aplicaciones globales.",
  "Anita Grezio; Alexander Babeyko; Jorn Behrens; Gareth Davies; Finn Lovholt; et al."),
 ("2018","var(--blue)","tsunami","tsunami","tsunami",
  "A global probabilistic tsunami hazard assessment from earthquake sources",
  "https://doi.org/10.1144/SP456.5","DOI",
  "Premiere evaluation probabiliste mondiale de l'alea tsunami d'origine sismique.",
  "Primera evaluacion probabilista mundial de la amenaza de tsunami de origen sismico.",
  "Gareth Davies; Jonathan Griffin; Finn Lovholt; et al."),
 ("2017","var(--amber)","volcan","volcan","volcan",
  "Volcanic fatalities database: analysis of volcanic threat with distance and victim classification",
  "https://doi.org/10.1186/s13617-017-0067-y","DOI",
  "Base mondiale des deces volcaniques, utile pour calibrer le risque selon la distance et le type d'eruption.",
  "Base mundial de muertes volcanicas, util para calibrar el riesgo segun la distancia y el tipo de erupcion.",
  "Sarah K. Brown; Susanna F. Jenkins; R. Stephen J. Sparks; Henry Odbert; Melanie R. Auker"),
 ("2019","var(--violet)","IA","IA","multirisque",
  "Deep learning and process understanding for data-driven Earth system science",
  "https://doi.org/10.1038/s41586-019-0912-1","DOI",
  "Cadre de reference pour l'apprentissage profond et les modeles hybrides en sciences du systeme Terre.",
  "Marco de referencia para el aprendizaje profundo y los modelos hibridos en ciencias del sistema Tierra.",
  "Markus Reichstein; Gustau Camps-Valls; Bjorn Stevens; Martin Jung; Joachim Denzler; Nuno Carvalhais; et al."),
 ("2020","var(--green)","nature-based","nature-based","climat",
  "Understanding the value and limits of nature-based solutions to climate change and other global challenges",
  "https://doi.org/10.1098/rstb.2019.0120","DOI",
  "Cadre conceptuel sur la valeur et les limites des solutions fondees sur la nature face au changement climatique.",
  "Marco conceptual sobre el valor y los limites de las soluciones basadas en la naturaleza ante el cambio climatico.",
  "Nathalie Seddon; Alexandre Chausson; Pam Berry; Cecile A. J. Girardin; Alison Smith; Beth Turner"),
 ("2020","var(--green)","nature-based","nature-based","climat",
  "Mapping the effectiveness of nature-based solutions for climate change adaptation",
  "https://doi.org/10.1111/gcb.15310","DOI",
  "Cartographie systematique de l'efficacite des solutions fondees sur la nature pour l'adaptation.",
  "Cartografia sistematica de la eficacia de las soluciones basadas en la naturaleza para la adaptacion.",
  "Alexandre Chausson; Beth Turner; Dan Seddon; et al."),
]
colombie_extra = [
 ("1990","var(--amber)","volcan","volcan","volcan",
  "The 1985 Nevado del Ruiz volcano catastrophe: anatomy and retrospection",
  "https://doi.org/10.1016/0377-0273(90)90027-D","DOI",
  "Analyse de reference de la catastrophe d'Armero (Nevado del Ruiz, 1985) et de ses defaillances de gestion.",
  "Analisis de referencia de la catastrofe de Armero (Nevado del Ruiz, 1985) y de sus fallas de gestion.",
  "Barry Voight"),
 ("2014","var(--red)","seisme","sismo","seisme",
  "Fully probabilistic seismic risk assessment considering local site effects for the building portfolio of Medellin",
  "https://doi.org/10.1007/s10518-013-9550-4","DOI",
  "Evaluation probabiliste complete du risque sismique du parc bati de Medellin avec effets de site.",
  "Evaluacion probabilista completa del riesgo sismico del parque edificado de Medellin con efectos de sitio.",
  "Mario A. Salgado-Galvez; Gabriel A. Bernal; Daniela Zuloaga; Mabel C. Marulanda; Omar D. Cardona; et al."),
 ("2015","var(--red)","seisme","sismo","seisme",
  "Urban seismic risk index for Medellin, Colombia, based on probabilistic loss and casualties estimations",
  "https://doi.org/10.1007/s11069-015-2056-4","DOI",
  "Indice de risque sismique urbain integrant pertes probabilistes et estimations de victimes.",
  "Indice de riesgo sismico urbano que integra perdidas probabilistas y estimaciones de victimas.",
  "Mabel C. Marulanda; Martha L. Carreno; Omar D. Cardona; et al."),
 ("2022","var(--cyan)","sante","salud","sante",
  "Avoidable mortality due to long-term exposure to PM2.5 in Colombia 2014-2019",
  "https://doi.org/10.1186/s12940-022-00947-8","DOI",
  "Quantifie la mortalite evitable liee a l'exposition de long terme aux particules fines en Colombie.",
  "Cuantifica la mortalidad evitable por exposicion de largo plazo a particulas finas en Colombia.",
  "Laura A. Rodriguez-Villamizar; Luis Carlos Belalcazar-Ceron; Maria Paula Castillo; et al."),
 ("2024","var(--green)","glissement","deslizamiento","mouvement",
  "Landslide hazard and rainfall threshold assessment with physics-based models (Manizales)",
  "https://doi.org/10.3390/geosciences14100280","DOI",
  "Combine modeles physiques (TRIGRS, Scoops3D) et seuils de pluie pour l'alerte aux glissements a Manizales.",
  "Combina modelos fisicos (TRIGRS, Scoops3D) y umbrales de lluvia para la alerta de deslizamientos en Manizales.",
  "Roberto J. Marin; et al."),
 ("2025","var(--blue)","drainage","drenaje","inondation",
  "Modeling urban drainage in intermediate cities under extreme climate change scenarios: Tunja, Colombia",
  "https://doi.org/10.2166/h2oj.2025.007","DOI",
  "Modelise le drainage urbain de villes intermediaires colombiennes sous scenarios climatiques extremes.",
  "Modela el drenaje urbano de ciudades intermedias colombianas bajo escenarios climaticos extremos.",
  "Cesar Mauricio Daza Rodriguez; Camilo Lesmes Fabian; Jorge Andres Sarmiento-Rojas"),
]
monde_res_extra = [
 ("W. Matt Jolly","Etats-Unis","Estados Unidos","USDA Forest Service (RMRS)","USDA Forest Service (RMRS)",
  "Danger meteorologique de feu, indices globaux et saison des feux.",
  "Peligro meteorologico de incendio, indices globales y temporada de incendios.",
  '<a href="mailto:matt.jolly@usda.gov">matt.jolly@usda.gov</a>'),
 ("John T. Abatzoglou","Etats-Unis","Estados Unidos","University of California, Merced","University of California, Merced",
  "Climat et feux de foret, aridite, conditions meteorologiques de feu.",
  "Clima e incendios forestales, aridez, condiciones meteorologicas de incendio.",
  '<a href="mailto:jabatzoglou@ucmerced.edu">jabatzoglou@ucmerced.edu</a>'),
 ("Sergio M. Vicente-Serrano","Espagne","Espana","CSIC - Instituto Pirenaico de Ecologia","CSIC - Instituto Pirenaico de Ecologia",
  "Indices de secheresse (SPEI), aridification et hydroclimat.",
  "Indices de sequia (SPEI), aridificacion e hidroclima.",
  '<a href="mailto:svicen@ipe.csic.es">svicen@ipe.csic.es</a>'),
 ("Ana M. Vicedo-Cabrera","Suisse","Suiza","University of Bern","University of Bern",
  "Epidemiologie climatique, mortalite liee a la chaleur et attribution.",
  "Epidemiologia climatica, mortalidad por calor y atribucion.",
  '<a href="mailto:anamaria.vicedo@unibe.ch">anamaria.vicedo@unibe.ch</a>'),
 ("David N. Petley","Royaume-Uni","Reino Unido","University of Hull","University of Hull",
  "Glissements de terrain et base mondiale des glissements meurtriers.",
  "Deslizamientos y base mundial de deslizamientos mortales.",
  '<a href="mailto:d.petley@hull.ac.uk">d.petley@hull.ac.uk</a>'),
 ("Finn Lovholt","Norvege","Noruega","Norwegian Geotechnical Institute (NGI)","Norwegian Geotechnical Institute (NGI)",
  "Alea tsunami probabiliste et glissements sous-marins.",
  "Amenaza de tsunami probabilista y deslizamientos submarinos.",
  '<a href="mailto:finn.lovholt@ngi.no">finn.lovholt@ngi.no</a>'),
 ("Markus Reichstein","Allemagne","Alemania","Max Planck Institute for Biogeochemistry","Max Planck Institute for Biogeochemistry",
  "Apprentissage automatique pour le systeme Terre et les extremes.",
  "Aprendizaje automatico para el sistema Tierra y los extremos.",
  '<a href="mailto:mreichstein@bgc-jena.mpg.de">mreichstein@bgc-jena.mpg.de</a>'),
 ("Nathalie Seddon","Royaume-Uni","Reino Unido","University of Oxford","University of Oxford",
  "Solutions fondees sur la nature, adaptation et biodiversite.",
  "Soluciones basadas en la naturaleza, adaptacion y biodiversidad.",
  '<a href="mailto:nathalie.seddon@biology.ox.ac.uk">nathalie.seddon@biology.ox.ac.uk</a>'),
]
colombie_res_extra = [
 ("Mario A. Salgado-Galvez","Colombie / Espagne","Colombia / Espana","INGENIAR Risk Intelligence / CIMNE","INGENIAR Risk Intelligence / CIMNE",
  "Risque sismique probabiliste (CAPRA), pertes, exposition et assurance.",
  "Riesgo sismico probabilista (CAPRA), perdidas, exposicion y seguro.",
  '<a href="https://www.ingeniar-risk.com/" target="_blank" rel="noopener">ingeniar-risk.com</a>'),
 ("Roberto J. Marin","Colombie","Colombia","Universidad de Medellin","Universidad de Medellin",
  "Seuils de pluie, glissements superficiels, modeles physiques et alerte precoce.",
  "Umbrales de lluvia, deslizamientos superficiales, modelos fisicos y alerta temprana.",
  '<a href="https://scholar.google.com/scholar?q=Roberto+J.+Marin+landslide+Colombia" target="_blank" rel="noopener">profil Scholar</a>'),
 ("Laura A. Rodriguez-Villamizar","Colombie","Colombia","Universidad Industrial de Santander","Universidad Industrial de Santander",
  "Epidemiologie environnementale, PM2.5, mortalite attribuable et sante publique.",
  "Epidemiologia ambiental, PM2.5, mortalidad atribuible y salud publica.",
  '<a href="https://scholar.google.com/scholar?q=Laura+Rodriguez-Villamizar+PM2.5+Colombia" target="_blank" rel="noopener">profil Scholar</a>'),
 ("Servicio Geologico Colombiano (SGC)","Colombie","Colombia","SGC - Observatorios Vulcanologicos y Sismologicos","SGC - Observatorios Vulcanologicos y Sismologicos",
  "Surveillance des 23 volcans actifs, alea volcanique et sismologie nationale.",
  "Vigilancia de los 23 volcanes activos, amenaza volcanica y sismologia nacional.",
  '<a href="https://www.sgc.gov.co/" target="_blank" rel="noopener">sgc.gov.co</a>'),
]

def _build_card(c):
    yr, accent, fam_fr, fam_es, risk, title, href, label, dfr, dfe, auth = c
    fr_es[fam_fr] = fam_es
    fr_es[dfr] = dfe
    return (f'<li class="paper-card" data-risk="{risk}" style="--accent:{accent}">'
            f'<div class="paper-meta"><span>{yr}</span><span>{fam_fr}</span></div>'
            f'<h4 class="paper-title">{title}</h4><p>{dfr}</p>'
            f'<div class="paper-authors">{auth}</div>'
            f'<div class="paper-source"><a href="{href}" target="_blank" rel="noopener">{label}</a></div></li>')

def _build_row(r):
    nom, pfr, pes, ifr, ies, wfr, wes, contact = r
    fr_es[pfr] = pes
    if ifr != ies:
        fr_es[ifr] = ies
    fr_es[wfr] = wes
    slugs = classify(nom + ' ' + wfr + ' ' + ifr)
    return f'<tr data-risk="{slugs}"><td>{nom}</td><td>{pfr}</td><td>{ifr}</td><td>{wfr}</td><td>{contact}</td></tr>'

_col_cards = "\n              ".join(_build_card(c) for c in colombie_extra)
_mon_cards = "\n              ".join(_build_card(c) for c in monde_extra)
_col_rows = "\n                  ".join(_build_row(r) for r in colombie_res_extra)
_mon_rows = "\n                  ".join(_build_row(r) for r in monde_res_extra)

# Separer Colombie / Monde, inserer les cartes et lignes
_mi2 = panels.index('<section class="diagram-board academia-panel" data-academia-panel-id="monde">')
_col, _mon = panels[:_mi2], panels[_mi2:]
_col = _col.replace('</ul>', '\n              ' + _col_cards + '\n            </ul>', 1)
_col = _col.replace('</tbody>', '\n                  ' + _col_rows + '\n                </tbody>', 1)
_mon = _mon.replace('</ul>', '\n              ' + _mon_cards + '\n            </ul>', 1)
_mon = _mon.replace('</tbody>', '\n                  ' + _mon_rows + '\n                </tbody>', 1)

def _part_stats(part):
    found = re.findall(r'<li class="paper-card" data-risk="([a-z]+)"[^>]*><div class="paper-meta"><span>(\d{4})</span>', part)
    risks = [f[0] for f in found]
    years = [int(f[1]) for f in found]
    docs = len(found)
    fam = len(set(risks))
    period = f"{min(years)}-{max(years)}" if years else "—"
    res = len(re.findall(r'<tr data-risk=', part))
    return str(docs), period, str(fam), str(res)

def _set_stat(html, label, value):
    return re.sub(r'<strong>[^<]*</strong><span>' + re.escape(label) + r'</span>',
                  f'<strong>{value}</strong><span>{label}</span>', html, count=1)

_cd, _cp, _cf, _cr = _part_stats(_col)
_col = _set_stat(_col, "documents reperes", _cd)
_col = _set_stat(_col, "periode couverte", _cp)
_col = _set_stat(_col, "familles de risque", _cf)
_col = _set_stat(_col, "chercheurs clefs", _cr)
_md, _mp, _mf, _mr = _part_stats(_mon)
_mon = _set_stat(_mon, "papiers selectionnes", _md)
_mon = _set_stat(_mon, "periode couverte", _mp)
_mon = _set_stat(_mon, "familles methodologiques", _mf)
_mon = _set_stat(_mon, "chercheurs clefs", _mr)
panels = _col + _mon

france_es_js = js_obj(fr_es)

# ---------------------------------------------------------------------------
# Assemblage du fichier final
# ---------------------------------------------------------------------------
page = f'''<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>IDIGER | Academia y modelación</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500&display=swap" rel="stylesheet" />
  <style>{css}</style>
</head>
<body>
  <main>
    <header>
      <div class="topline">
        <div>
          <h2 id="page-title"><span class="t1">Academia y</span> <span class="t2">modelación</span></h2>
          <p class="subtitle" id="page-subtitle">Corpus mondial sur la gestion et la modelisation des risques : articles, theses et chercheurs de reference.</p>
        </div>
        <div class="toolbar">
          <div class="partner-band">
            <img src="assets/logos/partner-band.png" alt="IGN FI · 3E Conseils · THOT · Alcaldia Mayor de Bogota / IDIGER · AFD" />
          </div>
          <div class="lang-switch" aria-label="Langue">
            <button class="lang-btn active" type="button" data-lang="fr">FR</button>
            <button class="lang-btn" type="button" data-lang="es">ES</button>
          </div>
        </div>
      </div>
    </header>

    <section class="content">
      <div class="view active" id="academie">
        <div class="academia-subtabs" role="tablist" aria-label="Sous-onglets Academie">
          <button class="academia-subtab active" type="button" data-academia-panel="colombie"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18"/><path d="M5 21V9l7-5 7 5v12"/><path d="M9 21v-6h6v6"/></svg>Modelisation des risques en Colombie</button>
          <button class="academia-subtab" type="button" data-academia-panel="monde"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg>Modelisation des risques dans le monde</button>
          <button class="academia-subtab" type="button" data-academia-panel="france"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19V5"/><path d="M4 5h11l-2 3 2 3H4"/></svg>Modelisation des risques en France</button>
        </div>

        {panels}
{france_panels}
      </div>
    </section>
  </main>

  <script>
    const $ = (selector, root = document) => root.querySelector(selector);
    const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
    const langStorageKey = "idiger-academia-lang-v1";

    const PAGE = {{
      fr: {{ docTitle: "IDIGER | Academia y modelacion", langLabel: "Langue", title: "Academia y modelacion" }},
      es: {{ docTitle: "IDIGER | Academia y modelacion", langLabel: "Idioma", title: "Academia y modelacion" }}
    }};

    const SUBTITLES = {{
      colombie: {{
        fr: "Corpus mondial sur la gestion et la modelisation des risques : articles, theses et chercheurs de reference.",
        es: "Corpus mundial sobre la gestion y modelacion de riesgos: articulos, tesis e investigadores de referencia."
      }},
      monde: {{
        fr: "Panorama international recent des methodes de modelisation des risques : alea, exposition, vulnerabilite, pertes, multi-alea et aide a la decision.",
        es: "Panorama internacional reciente de los metodos de modelacion de riesgos: amenaza, exposicion, vulnerabilidad, perdidas, multiamenaza y apoyo a la decision."
      }},
      france: {{
        fr: "Corpus scientifique francais sur la modelisation des risques naturels : inondation, submersion, seisme, mouvements de terrain, avalanche, feu de foret et volcan.",
        es: "Corpus cientifico frances sobre la modelacion de riesgos naturales: inundacion, sumersion, sismo, movimientos de terreno, avalancha, incendio forestal y volcan."
      }}
    }};

    // Libelles des pastilles de filtrage (FR / ES)
    const RISK_LABELS = {{
      general:        {{ fr: "Général", es: "General" }},
      seisme:         {{ fr: "Séisme", es: "Sismo" }},
      inondation:     {{ fr: "Inondation & eau", es: "Inundación y agua" }},
      mouvement:      {{ fr: "Mouvements de terrain", es: "Movimientos de terreno" }},
      climat:         {{ fr: "Climat & adaptation", es: "Clima y adaptación" }},
      avalanche:      {{ fr: "Avalanche", es: "Avalancha" }},
      feu:            {{ fr: "Feu de forêt", es: "Incendio forestal" }},
      volcan:         {{ fr: "Volcan", es: "Volcán" }},
      tsunami:        {{ fr: "Tsunami", es: "Tsunami" }},
      gouvernance:    {{ fr: "Gouvernance & société", es: "Gobernanza y sociedad" }},
      infrastructure: {{ fr: "Infrastructures & réseaux", es: "Infraestructuras y redes" }},
      urgence:        {{ fr: "Urgence & réponse", es: "Emergencia y respuesta" }},
      sante:          {{ fr: "Santé", es: "Salud" }},
      multirisque:    {{ fr: "Multi-risque & méthodes", es: "Multirriesgo y métodos" }}
    }};
    const RISK_ORDER = ["general","seisme","inondation","mouvement","climat","avalanche","feu","volcan","tsunami","gouvernance","infrastructure","urgence","sante","multirisque"];

'''

# Bloc textES verbatim (definit "const textES = {...}; Object.assign(textES, {...});")
page += "    " + text_es_block + "\n"
# Traductions ES du panneau France
page += "    Object.assign(textES, " + france_es_js + ");\n"

page += '''
    const originalText = new Map();
    function collectTextNodes(root = document.body) {
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
          if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
          if (node.parentElement?.closest("script, style")) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        }
      });
      while (walker.nextNode()) originalText.set(walker.currentNode, walker.currentNode.nodeValue);
    }

    function activePanelId() {
      return $(".academia-subtab.active")?.dataset.academiaPanel || "colombie";
    }

    function setHeaderText(lang) {
      // Titre et slogan fixes (identiques sur les trois onglets) ;
      // seule la langue du slogan est actualisee.
      const sub = SUBTITLES.colombie;
      $("#page-subtitle").textContent = sub[lang] || sub.fr;
    }

    let currentLang = localStorage.getItem(langStorageKey) || "fr";

    function applyLanguage(lang) {
      const bundle = PAGE[lang] || PAGE.fr;
      currentLang = lang;
      document.documentElement.lang = lang;
      document.title = bundle.docTitle;
      $$(".lang-btn").forEach(btn => btn.classList.toggle("active", btn.dataset.lang === lang));
      $(".lang-switch")?.setAttribute("aria-label", bundle.langLabel);

      for (const [node, original] of originalText) {
        const trimmed = original.trim();
        const start = original.indexOf(trimmed);
        const before = start >= 0 ? original.slice(0, start) : "";
        const after = start >= 0 ? original.slice(start + trimmed.length) : "";
        node.nodeValue = lang === "es" && textES[trimmed] ? before + textES[trimmed] + after : original;
      }

      // Pastilles de filtrage : libelles geres hors textES
      $$(".filter-pill").forEach(p => { p.textContent = p.dataset[lang] || p.dataset.fr; });

      setHeaderText(lang);
      localStorage.setItem(langStorageKey, lang);
    }

    function buildFilters() {
      const view = $("#academie");
      const tabIds = [...new Set($$(".academia-panel", view).map(p => p.dataset.academiaPanelId))];
      tabIds.forEach(tabId => {
        const panels = $$('.academia-panel[data-academia-panel-id="' + tabId + '"]', view);
        const papersPanel = panels.find(p => p.querySelector(".paper-list"));
        if (!papersPanel) return;
        const cards = Array.from(papersPanel.querySelectorAll(".paper-card"));
        const rows = panels.reduce((acc, p) =>
          acc.concat(Array.from(p.querySelectorAll(".researcher-table tbody tr"))), []);
        const statEls = Array.from(papersPanel.querySelectorAll(".academia-stat strong"));
        const baseStats = statEls.map(e => e.textContent);
        const present = new Set(cards.map(c => c.dataset.risk).filter(Boolean));
        const slugs = RISK_ORDER.filter(s => s === "general" || present.has(s));

        function rowRisks(r) { return (r.dataset.risk || "").split(" ").filter(Boolean); }

        function applyFilter(slug) {
          cards.forEach(c => {
            c.style.display = (slug === "general" || c.dataset.risk === slug) ? "" : "none";
          });
          rows.forEach(r => {
            r.style.display = (slug === "general" || rowRisks(r).includes(slug)) ? "" : "none";
          });
          if (slug === "general") {
            statEls.forEach((e, i) => { e.textContent = baseStats[i]; });
            return;
          }
          const visCards = cards.filter(c => c.dataset.risk === slug);
          const visRows = rows.filter(r => rowRisks(r).includes(slug));
          const years = visCards
            .map(c => parseInt((c.querySelector(".paper-meta span") || {}).textContent, 10))
            .filter(n => !isNaN(n));
          if (statEls[0]) statEls[0].textContent = String(visCards.length);
          if (statEls[1]) {
            if (years.length) {
              const mn = Math.min(...years), mx = Math.max(...years);
              statEls[1].textContent = mn === mx ? String(mn) : mn + "-" + mx;
            } else statEls[1].textContent = "—";
          }
          if (statEls[2]) statEls[2].textContent = "1";
          if (statEls[3]) statEls[3].textContent = String(visRows.length);
        }

        const host = document.createElement("div");
        host.className = "academia-panel filter-host" + (papersPanel.classList.contains("active") ? " active" : "");
        host.dataset.academiaPanelId = tabId;
        const bar = document.createElement("div");
        bar.className = "filter-bar";
        bar.setAttribute("role", "tablist");
        host.appendChild(bar);

        slugs.forEach((slug, i) => {
          const label = RISK_LABELS[slug] || { fr: slug, es: slug };
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "filter-pill" + (i === 0 ? " active" : "");
          btn.dataset.risk = slug;
          btn.dataset.fr = label.fr;
          btn.dataset.es = label.es;
          btn.textContent = label[currentLang] || label.fr;
          btn.addEventListener("click", () => {
            bar.querySelectorAll(".filter-pill").forEach(p => p.classList.toggle("active", p === btn));
            applyFilter(slug);
          });
          bar.appendChild(btn);
        });

        panels[0].parentNode.insertBefore(host, panels[0]);
      });
    }

    function bindExclusiveTabs(buttonSelector, panelSelector, getTargetId, panelMatchesTarget, onChange = () => {}) {
      const buttons = $$(buttonSelector);
      const panels = $$(panelSelector);
      buttons.forEach(button => {
        button.addEventListener("click", () => {
          const targetId = getTargetId(button);
          if (!targetId) return;
          buttons.forEach(item => item.classList.toggle("active", item === button));
          panels.forEach(panel => panel.classList.toggle("active", panelMatchesTarget(panel, targetId)));
          onChange(targetId);
        });
      });
    }

    collectTextNodes();
    buildFilters();

    bindExclusiveTabs(
      ".academia-subtab",
      ".academia-panel",
      button => button.dataset.academiaPanel,
      (panel, targetId) => panel.dataset.academiaPanelId === targetId,
      () => setHeaderText(currentLang)
    );

    $$(".lang-btn").forEach(button => {
      button.addEventListener("click", () => applyLanguage(button.dataset.lang));
    });

    applyLanguage(currentLang);
  </script>
</body>
</html>
'''

OUT.write_text(page, encoding="utf-8")
print("OK ->", OUT)
print("Taille:", OUT.stat().st_size, "octets")
print("Papiers France:", len(papers), "| Chercheurs France:", len(researchers))
