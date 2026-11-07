"""Composants de mise en page de l'application Dazzle Dash."""
from dash import dcc, html
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

import data


def _fr(valeur: float, decimales: int = 1) -> str:
    return f"{valeur:.{decimales}f}".replace(".", ",")


def creer_navbar() -> dbc.Navbar:
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand("Dazzle Dash", href="/", className="marque-dazzle"),
                dbc.Nav(
                    [
                        dbc.NavLink("Vue d'ensemble", href="/", id="nav-accueil", active=False),
                        dbc.NavLink(
                            "Explorer", href="/preston", id="nav-preston", active=False
                        ),
                        dbc.NavLink(
                            "Inégalités", href="/inegalites", id="nav-inegalites", active=False
                        ),
                        dbc.NavLink(
                            "Déterminants",
                            href="/determinants",
                            id="nav-determinants",
                            active=False,
                        ),
                        dbc.NavLink(
                            "Comparateur",
                            href="/comparateur",
                            id="nav-comparateur",
                            active=False,
                        ),
                        dbc.NavLink(
                            "Méthodologie", href="/methodologie", id="nav-methodologie", active=False
                        ),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="primary",
        dark=True,
        className="navbar-dazzle",
    )


def creer_footer() -> html.Footer:
    return html.Footer(
        html.P(
            "Dazzle Dash — Atlas de la longévité. Données OMS 2000-2015. Les associations présentées ne sont pas des relations causales.",
            className="texte-pied",
        ),
        className="pied-page",
    )


def kpi_card(titre: str, valeur: str = "—", id_valeur: str | None = None) -> dbc.Card:
    contenu = html.Div(valeur, className="kpi-valeur")
    if id_valeur is not None:
        contenu = html.Div(id=id_valeur, className="kpi-valeur", children=valeur)
    return dbc.Card(
        [contenu, html.Div(titre, className="kpi-libelle")],
        className="carte-kpi h-100",
    )


def kpi_card_dynamique(id_valeur: str) -> dbc.Card:
    return dbc.Card(html.Div(id=id_valeur), className="carte-kpi h-100")


def page_accueil() -> html.Div:
    df = data.charger_donnees()
    derniere = df[df["year"] == data.ANNEE_MAX]
    moyenne_2015 = derniere["life_expectancy"].mean()
    moyenne_2000 = df[df["year"] == data.ANNEE_MIN]["life_expectancy"].mean()
    progression = moyenne_2015 - moyenne_2000

    if "Développé" in derniere["statut"].values and "En développement" in derniere["statut"].values:
        ecart = (
            derniere.loc[derniere["statut"] == "Développé", "life_expectancy"].mean()
            - derniere.loc[derniere["statut"] == "En développement", "life_expectancy"].mean()
        )
    else:
        ecart = float("nan")

    return dbc.Container(
        [
            html.Div(
                [
                    html.P("Atlas de la longévité · OMS 2000–2015", className="surtitre"),
                    html.H1("L'espérance de vie, et ce qui la fait varier", className="titre-page"),
                    html.P(
                        "Un dashboard pour explorer les écarts entre pays, suivre les trajectoires "
                        "et comparer plusieurs facteurs sanitaires et socio-économiques.",
                        className="texte-intro",
                    ),
                ],
                className="entete-page",
            ),
            dbc.Row(
                [
                    dbc.Col(kpi_card("Espérance de vie en 2015", f"{_fr(moyenne_2015)} ans"), md=3),
                    dbc.Col(kpi_card("Progression depuis 2000", f"+{_fr(progression)} ans"), md=3),
                    dbc.Col(kpi_card("Écart Nord / Sud", f"{_fr(ecart)} ans"), md=3),
                    dbc.Col(kpi_card("Pays étudiés", f"{df['country'].nunique()}"), md=3),
                ],
                className="g-3 mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Ce que contient l'application"),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "La page Explorer propose deux modes : la courbe de "
                                            "Preston pour comparer les pays à revenu donné, et "
                                            "l'évolution dans le temps pour suivre un ou plusieurs "
                                            "pays avec tous les paramètres, sans dépendre du PIB."
                                        ),
                                        dbc.Button(
                                            "Explorer les données",
                                            href="/preston",
                                            color="primary",
                                            className="bouton-principal",
                                        ),
                                    ]
                                ),
                            ],
                            className="section-carte",
                        ),
                        md=7,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("À garder en tête"),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Les données sont observationnelles. Une corrélation "
                                            "n'implique pas une causalité, et la moyenne simple ne "
                                            "pondère pas les pays par leur population."
                                        ),
                                        html.P(
                                            "Le PIB manque pour une partie des pays et certaines "
                                            "valeurs sont signalées comme aberrantes.",
                                            className="texte-secondaire mb-0",
                                        ),
                                    ]
                                ),
                            ],
                            className="section-carte",
                        ),
                        md=5,
                    ),
                ],
                className="g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Inégalités"),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Qui vit le plus longtemps ? Où se situent les "
                                            "pays ? Montre la distribution, le classement et "
                                            "l'écart Nord/Sud."
                                        ),
                                        dbc.Button(
                                            "Voir",
                                            href="/inegalites",
                                            color="secondary",
                                            outline=True,
                                        ),
                                    ]
                                ),
                            ],
                            className="section-carte h-100",
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Déterminants"),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Quels facteurs sont associés à l'espérance de vie ? "
                                            "Classement des corrélations et explorateur facteur par "
                                            "facteur."
                                        ),
                                        dbc.Button(
                                            "Voir",
                                            href="/determinants",
                                            color="secondary",
                                            outline=True,
                                        ),
                                    ]
                                ),
                            ],
                            className="section-carte h-100",
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Comparateur"),
                                dbc.CardBody(
                                    [
                                        html.P(
                                            "Comment se comparent plusieurs pays sur un ensemble "
                                            "d'indicateurs ? Profils normalisés et tableau."
                                        ),
                                        dbc.Button(
                                            "Voir",
                                            href="/comparateur",
                                            color="secondary",
                                            outline=True,
                                        ),
                                    ]
                                ),
                            ],
                            className="section-carte h-100",
                        ),
                        md=4,
                    ),
                ],
                className="g-3 mt-3",
            ),
        ],
        fluid=True,
        className="page-accueil",
    )


def page_preston() -> html.Div:
    options_pays = data.options_pays("Tous")
    options_parametres = data.options_parametres(data.ANNEE_MAX, toutes_annees=False)

    return dbc.Container(
        [
            html.Div(
                [
                    html.P("Exploration interactive", className="surtitre"),
                    html.H1("Explorer l'espérance de vie", className="titre-page"),
                    html.P(
                        "Deux façons de lire les mêmes données : comparer les pays à revenu "
                        "donné avec la courbe de Preston, ou suivre un pays dans le temps avec "
                        "tous les paramètres.",
                        className="texte-intro",
                    ),
                ],
                className="entete-page",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Label("Mode d'exploration", className="fw-semibold"),
                        dbc.RadioItems(
                            id="preston-mode",
                            options=[
                                {
                                    "label": "Comparer les pays (Preston)",
                                    "value": "preston",
                                },
                                {
                                    "label": "Évolution dans le temps",
                                    "value": "evolution",
                                },
                            ],
                            value="preston",
                            inline=True,
                            className="mode-selector",
                        ),
                        html.P(
                            "Preston compare les pays à revenu donné. Évolution suit un ou "
                            "plusieurs pays dans le temps, sans dépendre du PIB.",
                            className="texte-mini mb-0",
                        ),
                    ]
                ),
                className="carte-filtre mb-4",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Pays"),
                                        dcc.Dropdown(
                                            id="preston-pays",
                                            options=options_pays,
                                            value=data.PAYS_DEFAUT,
                                            multi=True,
                                            disabled=True,
                                            placeholder="Choisir des pays",
                                            className="dropdown-dazzle",
                                        ),
                                    ],
                                    md=5,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Statut"),
                                        dcc.Dropdown(
                                            id="preston-statut",
                                            options=[
                                                {"label": "Tous", "value": "Tous"},
                                                {"label": "Développé", "value": "Développé"},
                                                {
                                                    "label": "En développement",
                                                    "value": "En développement",
                                                },
                                            ],
                                            value="Tous",
                                            clearable=False,
                                            className="dropdown-dazzle",
                                        ),
                                    ],
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Options"),
                                        html.Div(
                                            dbc.Switch(
                                                id="preston-tous-pays",
                                                label="Tous les pays",
                                                value=True,
                                                className="switch-dazzle",
                                            ),
                                            id="bloc-tous-pays",
                                        ),
                                        html.Div(
                                            dbc.Switch(
                                                id="preston-afficher-aberrants",
                                                label="Afficher les PIB signalés",
                                                value=False,
                                                className="switch-dazzle",
                                            ),
                                            id="bloc-aberrants",
                                        ),
                                        html.P(
                                            "En évolution, la sélection de pays est limitée "
                                            "à 8 pour la lisibilité.",
                                            className="texte-mini mb-0",
                                        ),
                                    ],
                                    md=4,
                                ),
                            ],
                            className="g-3 mb-3",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Paramètres (4 max en Preston, tous en évolution)"
                                        ),
                                        dcc.Dropdown(
                                            id="preston-parametres",
                                            options=options_parametres,
                                            value=data.PARAMETRES_DEFAUT,
                                            multi=True,
                                            placeholder="Aucun paramètre",
                                            className="dropdown-dazzle",
                                        ),
                                    ],
                                    md=5,
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                dbc.Label("Année"),
                                                dcc.Slider(
                                                    id="preston-annee",
                                                    min=data.ANNEE_MIN,
                                                    max=data.ANNEE_MAX,
                                                    step=1,
                                                    value=data.ANNEE_MAX,
                                                    marks={
                                                        annee: str(annee)
                                                        if annee % 3 == 0
                                                        else ""
                                                        for annee in range(
                                                            data.ANNEE_MIN,
                                                            data.ANNEE_MAX + 1,
                                                        )
                                                    },
                                                    tooltip={"placement": "bottom"},
                                                ),
                                            ],
                                            id="bloc-annee-preston",
                                        ),
                                        html.Div(
                                            [
                                                dbc.Label("Période (évolution)"),
                                                dcc.RangeSlider(
                                                    id="preston-periode",
                                                    min=data.ANNEE_MIN,
                                                    max=data.ANNEE_MAX,
                                                    step=1,
                                                    value=[data.ANNEE_MIN, data.ANNEE_MAX],
                                                    marks={
                                                        2000: "2000",
                                                        2005: "2005",
                                                        2010: "2010",
                                                        2015: "2015",
                                                    },
                                                    tooltip={"placement": "bottom"},
                                                ),
                                            ],
                                            id="bloc-periode-evolution",
                                            style={"display": "none"},
                                        ),
                                    ],
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Temps"),
                                        html.Div(
                                            [
                                                dbc.Switch(
                                                    id="preston-toutes-annees",
                                                    label="Toutes les années",
                                                    value=False,
                                                    className="switch-dazzle",
                                                ),
                                                html.P(
                                                    "En mode Preston, les paramètres indisponibles "
                                                    "en 2015 sont retirés automatiquement.",
                                                    className="texte-mini mb-0",
                                                ),
                                            ],
                                            id="bloc-toutes-annees",
                                        ),
                                    ],
                                    md=3,
                                ),
                            ],
                            className="g-3",
                        ),
                    ]
                ),
                className="carte-filtre mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(kpi_card_dynamique("preston-kpi-pays"), md=3),
                    dbc.Col(kpi_card_dynamique("preston-kpi-pente"), md=3),
                    dbc.Col(kpi_card_dynamique("preston-kpi-r2"), md=3),
                    dbc.Col(kpi_card_dynamique("preston-kpi-couverture"), md=3),
                ],
                className="g-3 mb-4",
            ),
            html.Div(id="preston-alertes", className="mb-3"),
            dbc.Card(
                [
                    dbc.CardHeader("Visualisation"),
                    dbc.CardBody(
                        dcc.Loading(
                            dcc.Graph(
                                id="preston-graphique",
                                config={"displayModeBar": False},
                                className="graphique-preston",
                            ),
                            type="circle",
                        )
                    ),
                ],
                className="section-carte mb-4",
            ),
            dbc.Card(
                [
                    dbc.CardHeader("Données de la sélection"),
                    dbc.CardBody(
                        dag.AgGrid(
                            id="preston-tableau",
                            columnDefs=[],
                            rowData=[],
                            defaultColDef={
                                "sortable": True,
                                "filter": True,
                                "resizable": True,
                                "minWidth": 110,
                            },
                            dashGridOptions={
                                "pagination": True,
                                "paginationPageSize": 25,
                                "paginationPageSizeSelector": [10, 25, 50, 100],
                                "rowHeight": 32,
                            },
                            getRowId="params.data.id_ligne",
                            columnSize="responsiveSizeToFit",
                            className="ag-theme-alpine tableau-preston",
                        )
                    ),
                ],
                className="section-carte mb-4",
            ),
            dbc.Card(
                [
                    dbc.CardHeader("Lecture de la sélection"),
                    dbc.CardBody(html.Div(id="preston-synthese")),
                ],
                className="section-carte",
            ),
        ],
        fluid=True,
        className="page-preston",
    )


def carte_graphique(titre: str, id_graphique: str) -> dbc.Card:
    return dbc.Card(
        [
            dbc.CardHeader(titre),
            dbc.CardBody(
                dcc.Loading(
                    dcc.Graph(
                        id=id_graphique,
                        config={"displayModeBar": False},
                        className="graphique-preston",
                    ),
                    type="circle",
                )
            ),
        ],
        className="section-carte mb-4",
    )


def carte_tableau(id_tableau: str) -> dbc.Card:
    return dbc.Card(
        [
            dbc.CardHeader("Données de la sélection"),
            dbc.CardBody(
                dag.AgGrid(
                    id=id_tableau,
                    columnDefs=[],
                    rowData=[],
                    defaultColDef={
                        "sortable": True,
                        "filter": True,
                        "resizable": True,
                        "minWidth": 110,
                    },
                    dashGridOptions={
                        "pagination": True,
                        "paginationPageSize": 25,
                        "paginationPageSizeSelector": [10, 25, 50, 100],
                        "rowHeight": 32,
                    },
                    getRowId="params.data.id_ligne",
                    columnSize="responsiveSizeToFit",
                    className="ag-theme-alpine tableau-preston",
                )
            ),
        ],
        className="section-carte mb-4",
    )


def page_inegalites() -> html.Div:
    return dbc.Container(
        [
            html.Div(
                [
                    html.P("Les écarts entre pays", className="surtitre"),
                    html.H1("Inégalités", className="titre-page"),
                    html.P(
                        "Qui vit le plus longtemps, et où ? Cette page montre la distribution, "
                        "le classement des pays et l'évolution de l'écart entre statuts.",
                        className="texte-intro",
                    ),
                ],
                className="entete-page",
            ),
            dbc.Card(
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Année"),
                                    dcc.Slider(
                                        id="ineg-annee",
                                        min=data.ANNEE_MIN,
                                        max=data.ANNEE_MAX,
                                        step=1,
                                        value=data.ANNEE_MAX,
                                        marks={
                                            annee: str(annee) if annee % 3 == 0 else ""
                                            for annee in range(data.ANNEE_MIN, data.ANNEE_MAX + 1)
                                        },
                                        tooltip={"placement": "bottom"},
                                    ),
                                ],
                                md=8,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Statut"),
                                    dcc.Dropdown(
                                        id="ineg-statut",
                                        options=[
                                            {"label": "Tous", "value": "Tous"},
                                            {"label": "Développé", "value": "Développé"},
                                            {
                                                "label": "En développement",
                                                "value": "En développement",
                                            },
                                        ],
                                        value="Tous",
                                        clearable=False,
                                        className="dropdown-dazzle",
                                    ),
                                ],
                                md=4,
                            ),
                        ],
                        className="g-3",
                    )
                ),
                className="carte-filtre mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(kpi_card_dynamique("ineg-kpi-moyenne"), md=3),
                    dbc.Col(kpi_card_dynamique("ineg-kpi-etendue"), md=3),
                    dbc.Col(kpi_card_dynamique("ineg-kpi-ecart"), md=3),
                    dbc.Col(kpi_card_dynamique("ineg-kpi-pays"), md=3),
                ],
                className="g-3 mb-4",
            ),
            html.Div(id="ineg-alertes", className="mb-3"),
            carte_graphique("Carte mondiale", "ineg-graph-carte"),
            dbc.Row(
                [
                    dbc.Col(carte_graphique("Distribution", "ineg-graph-distribution"), md=6),
                    dbc.Col(carte_graphique("Top et flop", "ineg-graph-classement"), md=6),
                ],
                className="g-3",
            ),
            carte_graphique("Évolution des moyennes", "ineg-graph-evolution"),
            carte_tableau("ineg-tableau"),
            dbc.Card(
                [
                    dbc.CardHeader("Lecture de la sélection"),
                    dbc.CardBody(html.Div(id="ineg-synthese")),
                ],
                className="section-carte",
            ),
        ],
        fluid=True,
        className="page-inegalites",
    )


def page_determinants() -> html.Div:
    options_facteurs = data.options_parametres(data.ANNEE_MAX, toutes_annees=False)
    return dbc.Container(
        [
            html.Div(
                [
                    html.P("Les facteurs associés", className="surtitre"),
                    html.H1("Déterminants", className="titre-page"),
                    html.P(
                        "Quels facteurs sont associés à l'espérance de vie ? Le classement donne "
                        "les corrélations brutes ; les panneaux montrent la forme du lien pour les "
                        "facteurs sélectionnés ; le tableau ajoute le contrôle du PIB.",
                        className="texte-intro",
                    ),
                ],
                className="entete-page",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Année"),
                                        dcc.Slider(
                                            id="det-annee",
                                            min=data.ANNEE_MIN,
                                            max=data.ANNEE_MAX,
                                            step=1,
                                            value=data.ANNEE_MAX,
                                            marks={
                                                annee: str(annee) if annee % 3 == 0 else ""
                                                for annee in range(
                                                    data.ANNEE_MIN, data.ANNEE_MAX + 1
                                                )
                                            },
                                            tooltip={"placement": "bottom"},
                                        ),
                                    ],
                                    md=6,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Statut"),
                                        dcc.Dropdown(
                                            id="det-statut",
                                            options=[
                                                {"label": "Tous", "value": "Tous"},
                                                {"label": "Développé", "value": "Développé"},
                                                {
                                                    "label": "En développement",
                                                    "value": "En développement",
                                                },
                                            ],
                                            value="Tous",
                                            clearable=False,
                                            className="dropdown-dazzle",
                                        ),
                                    ],
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Temps"),
                                        dbc.Switch(
                                            id="det-toutes-annees",
                                            label="Toutes les années",
                                            value=False,
                                            className="switch-dazzle",
                                        ),
                                    ],
                                    md=3,
                                ),
                            ],
                            className="g-3 mb-3",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label(
                                            "Facteurs à explorer (4 max en graphique)"
                                        ),
                                        dcc.Dropdown(
                                            id="det-facteurs",
                                            options=options_facteurs,
                                            value=data.FACTEURS_DETERMINANTS_DEFAUT,
                                            multi=True,
                                            className="dropdown-dazzle",
                                        ),
                                    ],
                                    md=12,
                                ),
                            ]
                        ),
                    ]
                ),
                className="carte-filtre mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(kpi_card_dynamique("det-kpi-fort"), md=3),
                    dbc.Col(kpi_card_dynamique("det-kpi-facteurs"), md=3),
                    dbc.Col(kpi_card_dynamique("det-kpi-obs"), md=3),
                    dbc.Col(kpi_card_dynamique("det-kpi-partiel"), md=3),
                ],
                className="g-3 mb-4",
            ),
            html.Div(id="det-alertes", className="mb-3"),
            dbc.Row(
                [
                    dbc.Col(carte_graphique("Classement des corrélations", "det-graph-corr"), md=6),
                    dbc.Col(carte_graphique("Facteurs sélectionnés", "det-graph-scatter"), md=6),
                ],
                className="g-3",
            ),
            carte_tableau("det-tableau"),
            dbc.Card(
                [
                    dbc.CardHeader("Lecture de la sélection"),
                    dbc.CardBody(html.Div(id="det-synthese")),
                ],
                className="section-carte",
            ),
        ],
        fluid=True,
        className="page-determinants",
    )


def page_comparateur() -> html.Div:
    options_pays = data.options_pays("Tous")
    options_indicateurs = [
        {"label": meta["libelle"], "value": cle}
        for cle, meta in data.INDICATEURS_COMPARATEUR.items()
    ]
    return dbc.Container(
        [
            html.Div(
                [
                    html.P("Comparaison multi-indicateurs", className="surtitre"),
                    html.H1("Comparateur de pays", className="titre-page"),
                    html.P(
                        "Comment se comparent plusieurs pays sur un ensemble d'indicateurs ? "
                        "Le radar utilise des rangs percentiles : 100 correspond au meilleur "
                        "pays de l'année. Le tableau donne les valeurs brutes.",
                        className="texte-intro",
                    ),
                ],
                className="entete-page",
            ),
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Pays (2 à 5)"),
                                        dcc.Dropdown(
                                            id="comp-pays",
                                            options=options_pays,
                                            value=data.PAYS_COMPARATEUR_DEFAUT,
                                            multi=True,
                                            placeholder="Choisir des pays",
                                            className="dropdown-dazzle",
                                        ),
                                    ],
                                    md=5,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Année"),
                                        dcc.Slider(
                                            id="comp-annee",
                                            min=data.ANNEE_MIN,
                                            max=data.ANNEE_MAX,
                                            step=1,
                                            value=data.ANNEE_MAX,
                                            marks={
                                                annee: str(annee) if annee % 3 == 0 else ""
                                                for annee in range(
                                                    data.ANNEE_MIN, data.ANNEE_MAX + 1
                                                )
                                            },
                                            tooltip={"placement": "bottom"},
                                        ),
                                    ],
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Indicateurs"),
                                        dcc.Dropdown(
                                            id="comp-indicateurs",
                                            options=options_indicateurs,
                                            value=data.INDICATEURS_COMPARATEUR_DEFAUT,
                                            multi=True,
                                            placeholder="Choisir des indicateurs",
                                            className="dropdown-dazzle",
                                        ),
                                    ],
                                    md=4,
                                ),
                            ],
                            className="g-3",
                        ),
                    ]
                ),
                className="carte-filtre mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(kpi_card_dynamique("comp-kpi-pays"), md=3),
                    dbc.Col(kpi_card_dynamique("comp-kpi-annee"), md=3),
                    dbc.Col(kpi_card_dynamique("comp-kpi-indicateurs"), md=3),
                    dbc.Col(kpi_card_dynamique("comp-kpi-meilleure"), md=3),
                ],
                className="g-3 mb-4",
            ),
            html.Div(id="comp-alertes", className="mb-3"),
            carte_graphique("Profils normalisés", "comp-graph-radar"),
            carte_tableau("comp-tableau"),
            dbc.Card(
                [
                    dbc.CardHeader("Lecture de la sélection"),
                    dbc.CardBody(html.Div(id="comp-synthese")),
                ],
                className="section-carte",
            ),
        ],
        fluid=True,
        className="page-comparateur",
    )


def page_methodologie() -> html.Div:
    return dbc.Container(
        [
            html.Div(
                [
                    html.P("Repères", className="surtitre"),
                    html.H1("Méthodologie et limites", className="titre-page"),
                    html.P(
                        "Les choix de nettoyage et les précautions à garder en tête quand on lit "
                        "les graphiques.",
                        className="texte-intro",
                    ),
                ],
                className="entete-page",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Les données"),
                                dbc.CardBody(
                                    html.Ul(
                                        [
                                            html.Li(
                                                "Source : Life Expectancy Data (OMS), 2 938 observations "
                                                "brutes, 193 pays, 2000-2015."
                                            ),
                                            html.Li(
                                                "Après nettoyage : 183 pays × 16 années = 2 928 observations."
                                            ),
                                            html.Li(
                                                "La population est exclue : aucune série nationale n'est "
                                                "cohérente (0/143)."
                                            ),
                                            html.Li(
                                                "L'IMC est exclu : échelle douteuse et valeurs aberrantes."
                                            ),
                                            html.Li(
                                                "Le statut Développé / En développement vient de "
                                                "la source : la France et le Canada y sont classés "
                                                "« En développement »."
                                            ),
                                        ]
                                    )
                                ),
                            ],
                            className="section-carte h-100",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("PIB et dépenses de santé"),
                                dbc.CardBody(
                                    html.Ul(
                                        [
                                            html.Li(
                                                "Le PIB contient des erreurs d'échelle. Les valeurs "
                                                "signalées ne servent pas aux tendances."
                                            ),
                                            html.Li(
                                                "Les dépenses de santé sont un proxy de dépense par "
                                                "habitant, en log10, limité à 2000-2014."
                                            ),
                                            html.Li(
                                                "Leur corrélation avec l'espérance de vie est largement "
                                                "expliquée par le PIB : c'est un indicateur secondaire."
                                            ),
                                        ]
                                    )
                                ),
                            ],
                            className="section-carte h-100",
                        ),
                        md=6,
                    ),
                ],
                className="g-3 mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("La courbe de Preston"),
                                dbc.CardBody(
                                    html.Ul(
                                        [
                                            html.Li(
                                                "Chaque point est un pays-année. L'axe x est le PIB "
                                                "par habitant en logarithme."
                                            ),
                                            html.Li(
                                                "La pente indique le nombre d'années gagnées quand le "
                                                "PIB est multiplié par 10."
                                            ),
                                            html.Li(
                                                "La régression n'est pas pondérée par la population et "
                                                "ne prouve pas une causalité."
                                            ),
                                            html.Li(
                                                "Les petits multiples comparent plusieurs paramètres ; "
                                                "le tableau et la synthèse donnent les corrélations."
                                            ),
                                            html.Li(
                                                "Le mode évolution suit un ou plusieurs pays dans le "
                                                "temps, sans utiliser le PIB : il fonctionne même quand "
                                                "le PIB manque ou est signalé."
                                            ),
                                        ]
                                    )
                                ),
                            ],
                            className="section-carte h-100",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Données manquantes et valeurs estimées"),
                                dbc.CardBody(
                                    html.Ul(
                                        [
                                            html.Li(
                                                "Les valeurs manquantes ne sont pas aléatoires, "
                                                "notamment pour l'hépatite B et la scolarité."
                                            ),
                                            html.Li(
                                                "Quatre variables seulement sont interpolées pour "
                                                "l'affichage : scolarité, indice de revenu, polio, DTP3."
                                            ),
                                            html.Li(
                                                "Les colonnes suffixées _estimee signalent ces valeurs "
                                                "dans le tableau."
                                            ),
                                            html.Li(
                                                "Alcool et dépenses publiques sont presque vides en 2015."
                                            ),
                                        ]
                                    )
                                ),
                            ],
                            className="section-carte h-100",
                        ),
                        md=6,
                    ),
                ],
                className="g-3",
            ),
        ],
        fluid=True,
        className="page-methodologie",
    )
