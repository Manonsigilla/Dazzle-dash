"""Chargement et catalogue de données partagés par l'application Dash."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import pycountry

RACINE = Path(__file__).resolve().parent
CHEMIN_DASH = RACINE / "data" / "clean" / "life_expectancy_dashboard.csv"
ANNEE_MIN = 2000
ANNEE_MAX = 2015

# Palette "Atlas de la longévité".
MARINE = "#0B2A3A"
TEAL = "#1F7A8C"
MENTHE = "#3FBF8F"
CORAL = "#F26B4E"
SAFRAN = "#F2B134"
BRUME = "#EDF3F2"
ARDOISE = "#5C6F73"

# Noms historiques conservés pour ne pas casser les callbacks existants.
BLEU = TEAL
ORANGE = CORAL
VERT = MENTHE
GRIS = ARDOISE

SPECTRE_LONGÉVITÉ = ["#F26B4E", "#F2B134", "#3FBF8F", "#1F7A8C"]
ECHELLE_CARTE = [
    [0.0, "#F26B4E"],
    [0.35, "#F2B134"],
    [0.70, "#8FD6B4"],
    [1.0, "#1F7A8C"],
]

# Template Plotly commun : le même que les cartes HTML.
TEMPLATE_DAZZLE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="IBM Plex Sans, Segoe UI, sans-serif", color=MARINE, size=12),
        title=dict(
            font=dict(family="Newsreader, Georgia, serif", size=20, color=MARINE),
            x=0.01,
            xanchor="left",
        ),
        colorway=[
            TEAL,
            CORAL,
            SAFRAN,
            MENTHE,
            "#6B4E71",
            MARINE,
            "#C8553D",
            "#2A9D8F",
        ],
        xaxis=dict(
            gridcolor="#E3ECEA",
            linecolor="#D3DFDC",
            zerolinecolor="#D3DFDC",
            tickfont=dict(family="IBM Plex Sans, sans-serif", size=10),
        ),
        yaxis=dict(
            gridcolor="#E3ECEA",
            linecolor="#D3DFDC",
            zerolinecolor="#D3DFDC",
            tickfont=dict(family="IBM Plex Sans, sans-serif", size=10),
        ),
        legend=dict(font=dict(family="IBM Plex Sans, sans-serif", size=11)),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor="#D3DFDC",
            font=dict(family="IBM Plex Sans, sans-serif", size=11, color=MARINE),
        ),
    )
)
pio.templates["dazzle"] = TEMPLATE_DAZZLE
pio.templates.default = "dazzle"
COULEURS_STATUT = {"Développé": BLEU, "En développement": ORANGE}

# Paramètres comparables dans la page Preston.
# "colonne" est utilisée pour le calcul et la couleur.
# "annees_exclues" évite de proposer une variable quasi vide sur une année.
PARAMETRES = {
    "schooling": {
        "colonne": "schooling",
        "libelle": "Scolarité (années)",
        "unite": "ans",
        "flag_estimee": "schooling_estimee",
        "colorscale": "Blues",
        "annees_exclues": set(),
    },
    "income_comp": {
        "colonne": "income_comp",
        "libelle": "Indice de revenu (0-1)",
        "unite": "indice",
        "flag_estimee": "income_comp_estimee",
        "colorscale": "Viridis",
        "annees_exclues": set(),
    },
    "adult_mortality": {
        "colonne": "adult_mortality",
        "libelle": "Mortalité adulte (pour 1 000)",
        "unite": "pour 1 000",
        "flag_estimee": None,
        "colorscale": "Reds",
        "annees_exclues": set(),
    },
    "hiv_aids": {
        "colonne": "hiv_aids",
        "libelle": "Décès VIH/sida (pour 1 000 naissances)",
        "unite": "pour 1 000",
        "flag_estimee": None,
        "colorscale": "OrRd",
        "annees_exclues": set(),
    },
    "polio": {
        "colonne": "polio",
        "libelle": "Vaccination polio (%)",
        "unite": "%",
        "flag_estimee": "polio_estimee",
        "colorscale": "Greens",
        "annees_exclues": set(),
    },
    "diphtheria": {
        "colonne": "diphtheria",
        "libelle": "Vaccination DTP3 (%)",
        "unite": "%",
        "flag_estimee": "diphtheria_estimee",
        "colorscale": "Teal",
        "annees_exclues": set(),
    },
    "health_exp_log": {
        "colonne": "health_exp_log",
        "colonne_table": "health_exp",
        "libelle": "Dépenses de santé (log10 USD/hab.)",
        "unite": "log10 USD",
        "flag_estimee": None,
        "colorscale": "YlGnBu",
        "annees_exclues": {2015},
    },
    "alcohol": {
        "colonne": "alcohol",
        "libelle": "Consommation d'alcool (L/hab.)",
        "unite": "L/hab.",
        "flag_estimee": None,
        "colorscale": "Purples",
        "annees_exclues": {2015},
    },
    "total_exp": {
        "colonne": "total_exp",
        "libelle": "Dépenses publiques de santé (% du budget)",
        "unite": "%",
        "flag_estimee": None,
        "colorscale": "PuBu",
        "annees_exclues": {2015},
    },
}

PARAMETRES_DEFAUT = ["schooling", "income_comp"]
FACTEURS_DETERMINANTS_DEFAUT = [
    "schooling",
    "income_comp",
    "adult_mortality",
    "hiv_aids",
]

# Indicateurs utilisés par le comparateur. Ils sont complets pour toutes les années.
INDICATEURS_COMPARATEUR = {
    "life_expectancy": {
        "libelle": "Espérance de vie (années)",
        "libelle_court": "Espérance de vie",
        "unite": "ans",
        "sens": 1,
        "format": 1,
    },
    "schooling": {
        "libelle": "Scolarité (années)",
        "libelle_court": "Scolarité",
        "unite": "ans",
        "sens": 1,
        "format": 1,
    },
    "income_comp": {
        "libelle": "Indice de revenu (0-1)",
        "libelle_court": "Indice de revenu",
        "unite": "indice",
        "sens": 1,
        "format": 2,
    },
    "adult_mortality": {
        "libelle": "Mortalité adulte (pour 1 000)",
        "libelle_court": "Faible mortalité adulte",
        "unite": "pour 1 000",
        "sens": -1,
        "format": 0,
    },
    "hiv_aids": {
        "libelle": "Décès VIH/sida (pour 1 000 naissances)",
        "libelle_court": "Faible VIH/sida",
        "unite": "pour 1 000",
        "sens": -1,
        "format": 1,
    },
    "polio": {
        "libelle": "Vaccination polio (%)",
        "libelle_court": "Vaccination polio",
        "unite": "%",
        "sens": 1,
        "format": 0,
    },
    "diphtheria": {
        "libelle": "Vaccination DTP3 (%)",
        "libelle_court": "Vaccination DTP3",
        "unite": "%",
        "sens": 1,
        "format": 0,
    },
}
INDICATEURS_COMPARATEUR_DEFAUT = list(INDICATEURS_COMPARATEUR)
PAYS_COMPARATEUR_DEFAUT = ["Japan", "Germany", "Brazil", "Nigeria"]
PAYS_DEFAUT = [
    "France",
    "Japan",
    "Brazil",
    "India",
    "Nigeria",
    "Germany",
    "South Africa",
]

MANUEL_ISO3 = {
    "Bolivia (Plurinational State of)": "BOL",
    "Côte d'Ivoire": "CIV",
    "Democratic People's Republic of Korea": "PRK",
    "Democratic Republic of the Congo": "COD",
    "Iran (Islamic Republic of)": "IRN",
    "Lao People's Democratic Republic": "LAO",
    "Micronesia (Federated States of)": "FSM",
    "Republic of Korea": "KOR",
    "Republic of Moldova": "MDA",
    "Russian Federation": "RUS",
    "Swaziland": "SWZ",
    "Syrian Arab Republic": "SYR",
    "The former Yugoslav republic of Macedonia": "MKD",
    "Timor-Leste": "TLS",
    "Turkey": "TUR",
    "United Kingdom of Great Britain and Northern Ireland": "GBR",
    "United Republic of Tanzania": "TZA",
    "United States of America": "USA",
    "Venezuela (Bolivarian Republic of)": "VEN",
    "Viet Nam": "VNM",
}


def _vers_iso3(nom: str) -> str | None:
    if nom in MANUEL_ISO3:
        return MANUEL_ISO3[nom]
    try:
        return pycountry.countries.lookup(nom).alpha_3
    except LookupError:
        return None


COLONNES_REQUISES = [
    "country",
    "year",
    "statut",
    "life_expectancy",
    "gdp",
    "gdp_clean",
    "gdp_aberrant",
    "health_exp",
    "health_exp_log",
    "health_exp_disponible",
    "schooling_estimee",
    "income_comp_estimee",
    "polio_estimee",
    "diphtheria_estimee",
]


@lru_cache(maxsize=1)
def charger_donnees() -> pd.DataFrame:
    """Charge le CSV dashboard une seule fois."""
    if not CHEMIN_DASH.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {CHEMIN_DASH}. "
            "Exécuter d'abord le notebook d'analyse exploratoire."
        )

    df = pd.read_csv(CHEMIN_DASH, encoding="utf-8")
    manquantes = [colonne for colonne in COLONNES_REQUISES if colonne not in df.columns]
    if manquantes:
        raise ValueError(
            "Colonnes manquantes dans le CSV dashboard : "
            + ", ".join(manquantes)
            + ". Régénérer les données avec le notebook 01 avant de lancer l'application."
        )

    if "iso3" not in df.columns:
        df["iso3"] = df["country"].map(_vers_iso3)

    for colonne in [
        "gdp_aberrant",
        "health_exp_zero",
        "health_exp_disponible",
        "schooling_estimee",
        "income_comp_estimee",
        "polio_estimee",
        "diphtheria_estimee",
    ]:
        if colonne in df.columns:
            df[colonne] = df[colonne].fillna(False).astype(bool)

    return df


def options_pays(statut: str = "Tous") -> list[dict]:
    df = charger_donnees()
    if statut != "Tous":
        df = df[df["statut"] == statut]
    pays = sorted(df["country"].dropna().unique())
    return [{"label": pays_nom, "value": pays_nom} for pays_nom in pays]


def options_parametres(annee: int | None = None, toutes_annees: bool = False) -> list[dict]:
    options = []
    for cle, meta in PARAMETRES.items():
        if not toutes_annees and annee is not None and int(annee) in meta["annees_exclues"]:
            continue
        options.append({"label": meta["libelle"], "value": cle})
    return options


def pays_sans_pib(df: pd.DataFrame) -> list[str]:
    serie_muette = df.groupby("country")["gdp_clean"].apply(lambda serie: serie.notna().sum() == 0)
    return sorted(serie_muette[serie_muette].index.tolist())


def correlation_partielle(x: pd.Series, y: pd.Series, z: pd.Series) -> tuple[float, int]:
    """Corrélation de x et y en contrôlant z, sur les lignes complètes."""
    masque = x.notna() & y.notna() & z.notna()
    x, y, z = x[masque], y[masque], z[masque]
    if len(x) < 3:
        return np.nan, len(x)
    rxy = x.corr(y)
    rxz = x.corr(z)
    ryz = y.corr(z)
    denominateur = np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    if denominateur == 0:
        return np.nan, len(x)
    return (rxy - rxz * ryz) / denominateur, len(x)
