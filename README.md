# Dazzle Dash

L'objectif de ce projet est de créer un dashboard automatisé pour visualiser les données de manière interactive et intuitive. Le dashboard permettra aux utilisateurs de suivre les indicateurs clés de performance (KPI) et d'analyser les tendances à partir des données collectées.

## Veille technologique

On commence d'abord une veille technologique sur l'outil qu'on va utiliser pour créer le dashboard : Dash by Plotly. Dash est un framework open-source en Python qui permet de créer des applications web interactives pour la visualisation de données. Il est particulièrement adapté pour les projets de data science et d'analyse de données. On commence d'abord par apprendre à créer une page simple avec Dash pour ensuite ajouter des fonctionnalités plus avancées comme des graphiques interactifs, des filtres, des mises à jour en temps réel et multiple pages.

## Analyse exploratoire des données

Dans cette phase, nous allons explorer les données disponibles pour comprendre leur structure, leur qualité et les relations qui peuvent exister entre elles. Cela nous permettra de choisir les indicateurs clés de performance (KPI) à visualiser dans le dashboard et de définir les axes d'analyse principaux. On pourra ensuite nettoyer les données, traiter les valeurs manquantes et effectuer des transformations si nécessaire pour préparer les données à l'analyse.

### Analyse exploratoire des données d'intérêt

Une fois les données nettoyées et préparées, nous allons effectuer une analyse exploratoire pour identifier les tendances, les anomalies et les relations entre les différentes variables. Cela peut inclure des visualisations telles que des histogrammes, des diagrammes de dispersion, des cartes de chaleur et des graphiques en boîte pour mieux comprendre la distribution des données et les corrélations entre les variables. Ceci sera fait dans un Jupyter Notebook pour faciliter l'expérimentation et la documentation des résultats. Un Notebook par dataset sera créé pour organiser les analyses.

Tout sera adapté à un public non technique, donc les visualisations et les analyses seront présentées de manière claire et compréhensible, avec des explications sur les conclusions tirées des données. L'objectif est de fournir des insights exploitables pour le big boss, pour que ça lui plaise et qu'il puisse prendre des décisions éclairées basées sur les données.

### Résultats de l'analyse exploratoire

L'analyse complète, exécutée et commentée pour un public non technique, est disponible dans [`notebooks/01_exploration_esperance_de_vie.ipynb`](notebooks/01_exploration_esperance_de_vie.ipynb).

**Données** : 2 938 observations, 193 pays, 2000–2015, 22 variables (source OMS). Après nettoyage : 183 pays × 16 années = 2 928 observations. Deux jeux de données sont générés dans `data/clean/` : `life_expectancy_observations.csv` (données observées, sans imputation, pour l'analyse) et `life_expectancy_dashboard.csv` (version d'affichage où seules la scolarité, l'indice de revenu, la polio et la DTP3 sont interpolées, avec des colonnes `_estimee`). Les deux fichiers contiennent aussi `health_exp_log`, `gdp_clean` et `gdp_aberrant`.

**Principaux enseignements**

- **+4,9 ans** d'espérance de vie moyenne mondiale entre 2000 et 2015 (66,8 → 71,6 ans).
- **11 ans d'écart** entre pays développés et pays en développement en 2015, et **37 ans** entre le meilleur et le moins bon pays.
- Les facteurs les plus associés sont la **scolarité** (r = 0,78), l'**indice de revenu** (r = 0,73), la **mortalité adulte** (r = −0,70) et le **VIH/sida** (r = −0,56).
- Le **PIB nettoyé** est lié à l'espérance de vie de façon non linéaire (r ≈ 0,65 sur une échelle logarithmique) : les gains sont surtout importants aux faibles revenus.
- Les **dépenses de santé** ont une corrélation brute d'environ 0,60, mais une corrélation partielle de 0,12 avec le PIB brut et 0,07 avec le PIB nettoyé : c'est un indicateur secondaire, pas un levier indépendant.
- Les trajectoires nationales sont très contrastées : **Zimbabwe +21 ans**, **Syrie −8 ans** entre 2000 et 2015.

**Limites des données** : la colonne Population est incohérente et exclue (0/143 séries cohérentes, 703 transitions > ×10, 129 > ×100) ; l'IMC a une échelle douteuse et est exclu. Le PIB contient des valeurs aberrantes (plus de 600 observations signalées, 25 pays sans aucun PIB) : `gdp` reste brut et `gdp_clean` sert aux tendances. Les dépenses de santé sont un proxy de dépense par habitant : les 611 zéros sont traités comme des manquants, 2015 est exclue et la variable reste secondaire. Le statut Développé / En développement vient de la source et surprend parfois (la France et le Canada y sont classés « En développement »). Les valeurs manquantes ne sont pas réparties au hasard (notamment pour l'hépatite B et la scolarité) : l'analyse compare valeurs observées, cas complets et imputation simple, et montre que les corrélations principales restent stables (scolarité : 0,784 → 0,752 après imputation).

**KPI retenus pour le dashboard** : espérance de vie mondiale, progression depuis 2000, écart Nord/Sud, top/flop 5 pays, classement des facteurs associés, carte mondiale, évolution temporelle, comparateur de pays, **courbe de Preston interactive** et **mode évolution par pays**.

### Application Dash

L'application se lance avec `python app.py` puis `http://127.0.0.1:8050`. Elle propose six routes : `/` (vue d'ensemble), `/preston` (Explorer avec les modes Preston et évolution), `/inegalites` (distribution, top/flop et écart Nord/Sud), `/determinants` (corrélations et explorateur de facteurs), `/comparateur` (profils multi-indicateurs) et `/methodologie` (choix de nettoyage et limites).

La page Explorer propose deux modes complémentaires. Le mode **Comparer les pays (Preston)** sélectionne un, plusieurs ou tous les pays, fait varier l'année ou empile toutes les années, et compare jusqu'à quatre paramètres en petits multiples. Le mode **Évolution dans le temps** suit un à huit pays sur la période 2000–2015, avec tous les paramètres disponibles, sans dépendre du PIB : il fonctionne donc même quand la valeur de PIB manque ou est signalée comme aberrante. Dans les deux modes, le tableau AgGrid et la synthèse se mettent à jour automatiquement. La page **Inégalités** répond à la question « quelles inégalités ? » avec la distribution, le classement et l'écart Nord/Sud. La page **Déterminants** répond à « quels facteurs et interactions ? » avec le classement des corrélations, les corrélations partielles et un explorateur facteur par facteur. La page **Comparateur** répond à « comment se comparent les pays ? » avec un radar de rangs percentiles et un tableau de valeurs brutes. Le code est réparti entre `app.py`, `index.py`, `layout.py`, `callbacks.py`, `data.py` et `assets/theme.css`.

## UX/UI Design

### Direction visuelle : « Atlas de la longévité »

Le dashboard ne reprend pas le thème Bootstrap par défaut. Il suit une direction éditoriale inspirée des atlas scientifiques : marine profond, brume froide, typographies Newsreader / IBM Plex Sans / IBM Plex Mono, et un **spectre de longévité** corail → safran → menthe → bleu pétrole utilisé sur les KPI, le hero et la carte.

- **Hero** : bandeau marine avec trame cartographique et barre spectrale.
- **Cartes** : fond papier, ombre douce, barre spectrale sur les KPI.
- **Carte mondiale** : océan marine, terres claires, pays colorés selon l'espérance de vie.
- **Graphiques** : template Plotly dédié, grilles discrètes, titres en Newsreader, palette cohérente avec les statuts.
- **Tableaux** : AG Grid habillé aux couleurs de l'atlas.
- **Accessibilité** : focus visible, contrastes, respect de `prefers-reduced-motion`.

La page Inégalités inclut une carte choroplèthe interactive de l'espérance de vie par pays, avec l'année et le filtre de statut.