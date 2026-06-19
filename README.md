# Academia y modelación

Page web autonome et bilingue (FR / ES) recensant le **corpus scientifique et les chercheurs de référence pour la modélisation des risques**, en appui au Centre de modélisation GRD & climat de l'IDIGER (Bogotá D.C.).

## Contenu

Trois onglets indépendants :

1. **Modélisation des risques en Colombie** — corpus mondial sur la gestion et la modélisation des risques à Bogotá et en Colombie (54 documents, 1989-2025) + chercheurs et contacts publics.
2. **Modélisation des risques dans le monde** — panorama international récent des méthodes (aléa, exposition, vulnérabilité, pertes, multi-aléas, aide à la décision ; 42 papiers, 2015-2026) + chercheurs internationaux.
3. **Modélisation des risques en France** — corpus scientifique français (40 documents, 2003-2026) couvrant inondation et crues éclair, submersion marine et littoral, séisme, mouvements de terrain et retrait-gonflement des argiles, avalanche, feu de forêt, volcan et économie du risque + 22 chercheurs et contacts publics.

## Fonctionnement

- Page statique mono-fichier (`index.html`), sans dépendance externe.
- Bascule de langue FR / ES par remplacement des nœuds texte (dictionnaire `textES`).
- Sous-onglets gérés en JavaScript pur.

## Génération

`build_page.py` assemble `index.html` : il extrait le style, les panneaux Colombie/Monde et les traductions ES depuis la page « Centre de modélisation GRD & climat », puis y ajoute le panneau France et ses traductions. Le script nécessite la page source voisine pour être rejoué.

---

IDIGER / AFD / IGN FI / 3E Conseils / Canal Clima
