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

    /* Pastilles de filtrage par type de risque */
    .filter-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin: 2px 0 16px;
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
            'retrait-gonflement':'mouvement','mortalite':'gouvernance','gouvernance':'gouvernance'}

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
  "Incertitudes, approches probabilistes, metamodeles et analyse de sensibilite.",
  "Incertidumbres, enfoques probabilistas, metamodelos y analisis de sensibilidad.",
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
    rows.append(
        f'<tr><td>{nom}</td><td>{pfr}</td><td>{ifr}</td><td>{wfr}</td><td>{contact}</td></tr>'
    )
rows_html = "\n                  ".join(rows)

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
                <div class="academia-stat"><strong>40</strong><span>documents reperes</span></div>
                <div class="academia-stat"><strong>2003-2026</strong><span>periode couverte</span></div>
                <div class="academia-stat"><strong>8</strong><span>familles de risque</span></div>
                <div class="academia-stat"><strong>22</strong><span>chercheurs clefs</span></div>
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

france_es_js = js_obj(fr_es)

# ---------------------------------------------------------------------------
# Assemblage du fichier final
# ---------------------------------------------------------------------------
page = f'''<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>IDIGER | Academia y modelacion</title>
  <style>{css}</style>
</head>
<body>
  <main>
    <header>
      <div class="topline">
        <div>
          <div class="partner-band">
            <img src="assets/logos/partner-band.png" alt="IGN FI · 3E Conseils · THOT · Alcaldia Mayor de Bogota / IDIGER · AFD" />
          </div>
          <h2 id="page-title">Academia y modelacion</h2>
          <p class="subtitle" id="page-subtitle">Corpus mondial sur la gestion et la modelisation des risques : articles, theses et chercheurs de reference.</p>
        </div>
        <div class="toolbar">
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
      gouvernance:    {{ fr: "Gouvernance & société", es: "Gobernanza y sociedad" }},
      infrastructure: {{ fr: "Infrastructures & réseaux", es: "Infraestructuras y redes" }},
      urgence:        {{ fr: "Urgence & réponse", es: "Emergencia y respuesta" }},
      sante:          {{ fr: "Santé", es: "Salud" }},
      multirisque:    {{ fr: "Multi-risque & méthodes", es: "Multirriesgo y métodos" }}
    }};
    const RISK_ORDER = ["general","seisme","inondation","mouvement","climat","avalanche","feu","volcan","gouvernance","infrastructure","urgence","sante","multirisque"];

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
      const bundle = PAGE[lang] || PAGE.fr;
      $("#page-title").textContent = bundle.title;
      const sub = SUBTITLES[activePanelId()] || SUBTITLES.colombie;
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
      $$(".academia-panel").forEach(panel => {
        const list = panel.querySelector(".paper-list");
        if (!list) return;
        const cards = Array.from(list.querySelectorAll(".paper-card"));
        const present = new Set(cards.map(c => c.dataset.risk).filter(Boolean));
        const slugs = RISK_ORDER.filter(s => s === "general" || present.has(s));
        const bar = document.createElement("div");
        bar.className = "filter-bar";
        bar.setAttribute("role", "tablist");
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
            cards.forEach(c => {
              c.style.display = (slug === "general" || c.dataset.risk === slug) ? "" : "none";
            });
          });
          bar.appendChild(btn);
        });
        list.parentNode.insertBefore(bar, list);
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
