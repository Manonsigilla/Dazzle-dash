"""Callbacks de navigation et de la page Preston."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, html, no_update
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

import data
import layout


_CALLBACKS: list[tuple[tuple, dict, object]] = []


def callback(*args, **kwargs):
    """Enregistre les callbacks pour les attacher ensuite à l'application."""
    def decorateur(fonction):
        _CALLBACKS.append((args, kwargs, fonction))
        return fonction
    return decorateur


def enregistrer_callbacks(application) -> None:
    for args, kwargs, fonction in _CALLBACKS:
        application.callback(*args, **kwargs)(fonction)


def _fr(valeur: float, decimales: int = 1) -> str:
    return f"{valeur:.{decimales}f}".replace(".", ",")


COULEURS_EVOLUTION = [
    data.CORAL,
    data.TEAL,
    data.SAFRAN,
    data.MENTHE,
    "#6B4E71",
    data.MARINE,
    "#C8553D",
    "#2A9D8F",
]


def _kpi(valeur: str, libelle: str) -> html.Div:
    return html.Div(
        [
            html.Div(valeur, className="kpi-valeur"),
            html.Div(libelle, className="kpi-libelle"),
        ]
    )


TITRES_COURTS = {
    "schooling": "Scolarité",
    "income_comp": "Indice de revenu",
    "adult_mortality": "Mortalité adulte",
    "hiv_aids": "VIH/sida",
    "polio": "Polio",
    "diphtheria": "DTP3",
    "health_exp_log": "Dépenses santé (log10)",
    "alcohol": "Alcool",
    "total_exp": "Dépenses publiques",
}


def _figure_vide(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        align="center",
        font=dict(size=14, color=data.GRIS),
    )
    fig.update_layout(
        template="dazzle",
        height=420,
        margin=dict(l=20, r=20, t=40, b=30),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def _colonnes_base() -> list[dict]:
    return [
        {"field": "country", "headerName": "Pays", "minWidth": 170},
        {"field": "year", "headerName": "Année", "minWidth": 90, "type": "numericColumn"},
        {"field": "statut", "headerName": "Statut", "minWidth": 140},
        {
            "field": "life_expectancy",
            "headerName": "Espérance de vie (ans)",
            "minWidth": 150,
            "type": "numericColumn",
        },
        {
            "field": "gdp",
            "headerName": "PIB (USD/hab.)",
            "minWidth": 130,
            "type": "numericColumn",
        },
        {"field": "gdp_statut", "headerName": "PIB (qualité)", "minWidth": 115},
        {"field": "estimation", "headerName": "Estimation", "minWidth": 110},
    ]


def _colonnes_base_evolution() -> list[dict]:
    return [
        {"field": "country", "headerName": "Pays", "minWidth": 170},
        {"field": "year", "headerName": "Année", "minWidth": 90, "type": "numericColumn"},
        {"field": "statut", "headerName": "Statut", "minWidth": 140},
        {
            "field": "life_expectancy",
            "headerName": "Espérance de vie (ans)",
            "minWidth": 150,
            "type": "numericColumn",
        },
        {"field": "estimation", "headerName": "Estimation", "minWidth": 110},
    ]


def _colonnes_parametres(parametres: list[str]) -> list[dict]:
    colonnes = []
    for cle in parametres:
        meta = data.PARAMETRES[cle]
        if cle == "health_exp_log":
            colonnes.append(
                {
                    "field": "health_exp",
                    "headerName": "Dépenses santé (USD/hab.)",
                    "minWidth": 180,
                    "type": "numericColumn",
                }
            )
            colonnes.append(
                {
                    "field": "health_exp_log",
                    "headerName": "Dépenses santé (log10)",
                    "minWidth": 160,
                    "type": "numericColumn",
                }
            )
        else:
            colonnes.append(
                {
                    "field": meta["colonne"],
                    "headerName": meta["libelle"],
                    "minWidth": 180,
                    "type": "numericColumn",
                }
            )
    return colonnes


def _preparer_tableau(df: pd.DataFrame, parametres: list[str]) -> tuple[list[dict], list[dict]]:
    table = df.sort_values(["country", "year"]).copy()
    table["id_ligne"] = table["country"].astype(str) + " | " + table["year"].astype(str)
    table["gdp_statut"] = np.select(
        [
            table["gdp"].isna(),
            table["gdp_aberrant"],
        ],
        ["Manquant", "Signalé"],
        default="Fiable",
    )

    flags = [
        data.PARAMETRES[cle]["flag_estimee"]
        for cle in parametres
        if data.PARAMETRES[cle].get("flag_estimee")
    ]
    if flags:
        table["estimation"] = np.where(table[flags].any(axis=1), "Estimée", "Observée")
    else:
        table["estimation"] = "—"

    colonnes = [
        "id_ligne",
        "country",
        "year",
        "statut",
        "life_expectancy",
        "gdp",
        "gdp_statut",
        "estimation",
    ]
    for cle in parametres:
        meta = data.PARAMETRES[cle]
        if cle == "health_exp_log":
            colonnes.extend(["health_exp", "health_exp_log"])
        else:
            colonnes.append(meta["colonne"])

    for colonne in ["life_expectancy", "gdp", "health_exp", "health_exp_log"]:
        if colonne in table.columns:
            table[colonne] = table[colonne].round(2)
    for cle in parametres:
        colonne = data.PARAMETRES[cle]["colonne"]
        if colonne in table.columns:
            table[colonne] = table[colonne].round(2)

    table = table[colonnes].astype(object).where(pd.notna(table[colonnes]), None)
    return table.to_dict("records"), _colonnes_base() + _colonnes_parametres(parametres)


def _preparer_tableau_evolution(
    df: pd.DataFrame, parametres: list[str]
) -> tuple[list[dict], list[dict]]:
    table = df.sort_values(["country", "year"]).copy()
    table["id_ligne"] = table["country"].astype(str) + " | " + table["year"].astype(str)

    flags = [
        data.PARAMETRES[cle]["flag_estimee"]
        for cle in parametres
        if data.PARAMETRES[cle].get("flag_estimee")
    ]
    if flags:
        table["estimation"] = np.where(table[flags].any(axis=1), "Estimée", "Observée")
    else:
        table["estimation"] = "—"

    colonnes = ["id_ligne", "country", "year", "statut", "life_expectancy", "estimation"]
    for cle in parametres:
        meta = data.PARAMETRES[cle]
        if cle == "health_exp_log":
            colonnes.extend(["health_exp", "health_exp_log"])
        else:
            colonnes.append(meta["colonne"])

    for colonne in ["life_expectancy", "health_exp", "health_exp_log"]:
        if colonne in table.columns:
            table[colonne] = table[colonne].round(2)
    for cle in parametres:
        colonne = data.PARAMETRES[cle]["colonne"]
        if colonne in table.columns:
            table[colonne] = table[colonne].round(2)

    table = table[colonnes].astype(object).where(pd.notna(table[colonnes]), None)
    return table.to_dict("records"), _colonnes_base_evolution() + _colonnes_parametres(
        parametres
    )


def _ajuster_axes(fig: go.Figure, nb_panneaux: int) -> None:
    fig.update_xaxes(
        type="log",
        title_text="PIB par habitant (USD, échelle log)",
        tickfont=dict(size=9),
    )
    fig.update_yaxes(title_text="Espérance de vie (années)", tickfont=dict(size=9))
    fig.update_layout(
        template="dazzle",
        height=620 if nb_panneaux <= 3 else 880,
        margin=dict(l=30, r=110, t=80, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="closest",
    )
    fig.update_annotations(font_size=11)


def _figure_preston(
    df: pd.DataFrame,
    parametres: list[str],
    afficher_aberrants: bool,
) -> tuple[go.Figure, float | None, float | None, int, int]:
    base = df[df["gdp"].notna() & (df["gdp"] > 0)].copy()
    if base.empty:
        return _figure_vide("Aucun PIB exploitable pour cette sélection."), None, None, 0, 0

    trace = base[base["gdp_clean"].notna() & base["life_expectancy"].notna()].copy()
    pente: float | None = None
    r2: float | None = None
    coef = None
    if len(trace) >= 3 and trace["gdp_clean"].nunique() > 1:
        x_log = np.log10(trace["gdp_clean"])
        y = trace["life_expectancy"]
        coef = np.polyfit(x_log, y, 1)
        r = np.corrcoef(x_log, y)[0, 1]
        pente = float(coef[0])
        r2 = float(r ** 2)

    aberrants = base[base["gdp_aberrant"]].copy()
    # Les points colorés excluent toujours les PIB signalés.
    # Le switch ne fait qu'ajouter les croix grises, il ne les remet pas dans la tendance.
    plot_base = base[~base["gdp_aberrant"]].copy()

    panneaux: list[str | None] = parametres[:4] if parametres else [None]
    nb = len(panneaux)
    if nb == 1:
        lignes, colonnes = 1, 1
    elif nb == 2:
        lignes, colonnes = 1, 2
    elif nb == 3:
        lignes, colonnes = 1, 3
    else:
        lignes, colonnes = 2, 2

    titres = []
    for cle in panneaux:
        if cle is None:
            titres.append("Par statut")
            continue
        meta = data.PARAMETRES[cle]
        sous_ensemble = trace[["life_expectancy", meta["colonne"]]].dropna()
        if len(sous_ensemble) > 2:
            r_param = sous_ensemble[meta["colonne"]].corr(sous_ensemble["life_expectancy"])
            titres.append(f"{TITRES_COURTS.get(cle, cle)} (r = {_fr(r_param, 2)})")
        else:
            titres.append(TITRES_COURTS.get(cle, cle))

    fig = make_subplots(
        rows=lignes,
        cols=colonnes,
        shared_xaxes=True,
        shared_yaxes=True,
        subplot_titles=titres,
        horizontal_spacing=0.10,
        vertical_spacing=0.14,
    )

    for index, cle in enumerate(panneaux):
        ligne = index // colonnes + 1
        colonne = index % colonnes + 1
        premier = index == 0

        if cle is None:
            for statut_nom, couleur in data.COULEURS_STATUT.items():
                sous_ensemble = plot_base[plot_base["statut"] == statut_nom]
                if sous_ensemble.empty:
                    continue
                fig.add_trace(
                    go.Scattergl(
                        x=sous_ensemble["gdp"],
                        y=sous_ensemble["life_expectancy"],
                        mode="markers",
                        name=statut_nom,
                        marker=dict(size=7, color=couleur, opacity=0.72),
                        customdata=sous_ensemble[["country", "year", "statut"]].to_numpy(),
                        hovertemplate=(
                            "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                            "PIB : %{x:,.0f} USD<br>"
                            "Espérance de vie : %{y:.1f} ans<extra></extra>"
                        ),
                        showlegend=premier,
                    ),
                    row=ligne,
                    col=colonne,
                )
        else:
            meta = data.PARAMETRES[cle]
            sous_ensemble = plot_base[plot_base[meta["colonne"]].notna()].copy()
            if sous_ensemble.empty:
                fig.add_annotation(
                    text="Aucune donnée pour ce paramètre",
                    x=0.5,
                    y=0.5,
                    xref=f"x{index + 1} domain" if index > 0 else "x domain",
                    yref=f"y{index + 1} domain" if index > 0 else "y domain",
                    showarrow=False,
                    font=dict(size=11, color=data.GRIS),
                )
            else:
                axe_x = f"xaxis{index + 1}" if index > 0 else "xaxis"
                axe_y = f"yaxis{index + 1}" if index > 0 else "yaxis"
                domaine_x = getattr(fig.layout, axe_x).domain
                domaine_y = getattr(fig.layout, axe_y).domain
                fig.add_trace(
                    go.Scattergl(
                        x=sous_ensemble["gdp"],
                        y=sous_ensemble["life_expectancy"],
                        mode="markers",
                        name=TITRES_COURTS.get(cle, cle),
                        marker=dict(
                            size=7,
                            color=sous_ensemble[meta["colonne"]],
                            colorscale=meta["colorscale"],
                            showscale=True,
                            colorbar=dict(
                                title=TITRES_COURTS.get(cle, cle),
                                thickness=8,
                                len=0.42,
                                x=float(domaine_x[1]) + 0.008,
                                y=float(domaine_y[1]),
                                xanchor="left",
                                yanchor="top",
                            ),
                            line=dict(width=0),
                        ),
                        customdata=sous_ensemble[["country", "year", "statut"]].to_numpy(),
                        hovertemplate=(
                            "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                            "PIB : %{x:,.0f} USD<br>"
                            "Espérance : %{y:.1f} ans<br>"
                            + f"{meta['libelle']} : %{{marker.color:.2f}}<extra></extra>"
                        ),
                        showlegend=False,
                    ),
                    row=ligne,
                    col=colonne,
                )

        if afficher_aberrants and not aberrants.empty:
            fig.add_trace(
                go.Scattergl(
                    x=aberrants["gdp"],
                    y=aberrants["life_expectancy"],
                    mode="markers",
                    name="PIB signalé",
                    marker=dict(symbol="x", size=6, color=data.GRIS, opacity=0.65),
                    customdata=aberrants[["country", "year"]].to_numpy(),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                        "PIB signalé : %{x:,.0f} USD<extra></extra>"
                    ),
                    showlegend=premier,
                ),
                row=ligne,
                col=colonne,
            )

        if coef is not None:
            grille = np.linspace(
                np.log10(trace["gdp_clean"]).min(),
                np.log10(trace["gdp_clean"]).max(),
                100,
            )
            fig.add_trace(
                go.Scatter(
                    x=10 ** grille,
                    y=np.polyval(coef, grille),
                    mode="lines",
                    name="Tendance",
                    line=dict(color=data.GRIS, dash="dash", width=2),
                    showlegend=premier,
                ),
                row=ligne,
                col=colonne,
            )

    _ajuster_axes(fig, nb)
    return fig, pente, r2, len(trace), len(aberrants)


def _synthese(
    df: pd.DataFrame,
    parametres: list[str],
    pente: float | None,
    r2: float | None,
    n_trace: int,
    toutes_annees: bool,
) -> html.Div:
    n_obs = len(df)
    n_pays = df["country"].nunique()
    n_annees = df["year"].nunique()

    enfants: list = [html.H5("Ce que montre la sélection", className="titre-synthese")]
    enfants.append(
        html.P(
            f"{n_obs} observations, {n_pays} pays et {n_annees} année(s) dans la sélection.",
            className="mb-2",
        )
    )

    if pente is not None and r2 is not None:
        signe = "+" if pente >= 0 else ""
        enfants.append(
            html.P(
                f"Quand le PIB par habitant est multiplié par 10, l'espérance de vie varie "
                f"en moyenne de {signe}{_fr(pente)} ans (R² = {_fr(r2, 2)}, {n_trace} observations "
                "avec un PIB fiable).",
                className="mb-2",
            )
        )
    else:
        enfants.append(
            html.P(
                "Il n'y a pas assez de points avec un PIB fiable pour estimer une tendance.",
                className="mb-2",
            )
        )

    if parametres:
        elements = []
        for cle in parametres:
            meta = data.PARAMETRES[cle]
            colonne = meta["colonne"]
            sous_ensemble = df[["life_expectancy", colonne, "gdp_clean"]].dropna()
            if len(sous_ensemble) < 3:
                elements.append(html.Li(f"{meta['libelle']} : pas assez de données."))
                continue
            r = sous_ensemble[colonne].corr(sous_ensemble["life_expectancy"])
            log_pib = np.log10(sous_ensemble["gdp_clean"].where(sous_ensemble["gdp_clean"] > 0))
            r_partiel, n_partiel = data.correlation_partielle(
                sous_ensemble[colonne], sous_ensemble["life_expectancy"], log_pib
            )
            phrase = f"{meta['libelle']} : r = {_fr(r, 2)} (n = {len(sous_ensemble)})"
            if not pd.isna(r_partiel):
                phrase += f" ; corrélation partielle au PIB : {_fr(r_partiel, 2)} (n = {n_partiel})"
            if cle == "health_exp_log":
                phrase += ". Proxy de dépense par habitant, 2000-2014 ; à lire comme un indicateur secondaire."
            elements.append(html.Li(phrase))
        enfants.append(html.Div([html.P("Paramètres sélectionnés :", className="mb-1"), html.Ul(elements)]))
    else:
        enfants.append(html.P("Aucun paramètre sélectionné : les points sont colorés par statut."))

    moyennes = df.groupby("statut")["life_expectancy"].mean()
    if {"Développé", "En développement"}.issubset(moyennes.index):
        ecart = moyennes["Développé"] - moyennes["En développement"]
        enfants.append(
            html.P(
                f"Écart moyen entre pays développés et pays en développement : {_fr(ecart)} ans.",
                className="mb-2",
            )
        )

    n_pays_pib = df.loc[df["gdp_clean"].notna(), "country"].nunique()
    enfants.append(html.P(f"PIB fiable pour {n_pays_pib} pays sur {n_pays}.", className="mb-2"))

    if toutes_annees:
        enfants.append(
            html.P(
                "Les années sont empilées : les observations d'un même pays ne sont pas indépendantes.",
                className="texte-secondaire mb-2",
            )
        )

    enfants.append(
        html.P(
            "Ces écarts décrivent la sélection. Ils ne prouvent pas une causalité et ne sont pas "
            "pondérés par la population.",
            className="texte-secondaire mb-0",
        )
    )
    return html.Div(enfants)


def _alertes(
    df: pd.DataFrame,
    parametres: list[str],
    indisponibles: list[str],
    tronques: list[str],
    pente: float | None,
    afficher_aberrants: bool,
    toutes_annees: bool,
) -> html.Div:
    messages = []

    if indisponibles:
        noms = ", ".join(data.PARAMETRES[cle]["libelle"] for cle in indisponibles)
        messages.append(
            dbc.Alert(
                f"Paramètres indisponibles en 2015 et retirés de la sélection : {noms}.",
                color="warning",
                className="py-2 mb-2",
            )
        )
    if tronques:
        messages.append(
            dbc.Alert(
                "La comparaison graphique est limitée à 4 paramètres. Les suivants ne sont pas affichés.",
                color="warning",
                className="py-2 mb-2",
            )
        )

    pays_sans = data.pays_sans_pib(df)
    if pays_sans:
        exemples = ", ".join(pays_sans[:5])
        suffixe = "…" if len(pays_sans) > 5 else ""
        if len(pays_sans) == 1:
            texte_pib = (
                f"{pays_sans[0]} n'a pas de PIB fiable dans la sélection. "
                "Il apparaît dans le tableau mais pas sur la courbe."
            )
        else:
            texte_pib = (
                f"{len(pays_sans)} pays n'ont pas de PIB fiable dans la sélection "
                f"({exemples}{suffixe}). Ils apparaissent dans le tableau mais pas sur la courbe."
            )
        messages.append(dbc.Alert(texte_pib, color="warning", className="py-2 mb-2"))

    nb_aberrants = int(df["gdp_aberrant"].sum())
    if nb_aberrants:
        if nb_aberrants == 1:
            sujet = "1 observation au PIB signalé"
        else:
            sujet = f"{nb_aberrants} observations au PIB signalé"
        if afficher_aberrants:
            texte_ab = (
                f"{sujet} est affichée en croix grise et reste exclue de la tendance."
                if nb_aberrants == 1
                else f"{sujet} sont affichées en croix grises et restent exclues de la tendance."
            )
        else:
            texte_ab = (
                f"{sujet} est exclue de la tendance. Activez « Afficher les PIB signalés » pour la voir."
                if nb_aberrants == 1
                else f"{sujet} sont exclues de la tendance. Activez « Afficher les PIB signalés » pour les voir."
            )
        messages.append(dbc.Alert(texte_ab, color="info", className="py-2 mb-2"))

    flags = [
        data.PARAMETRES[cle]["flag_estimee"]
        for cle in parametres
        if data.PARAMETRES[cle].get("flag_estimee")
    ]
    if flags:
        nb_estimees = int(df[flags].any(axis=1).sum())
        if nb_estimees:
            messages.append(
                dbc.Alert(
                    (f"1 observation utilise au moins une valeur estimée par interpolation." if nb_estimees == 1 else f"{nb_estimees} observations utilisent au moins une valeur estimée par interpolation."),
                    color="info",
                    className="py-2 mb-2",
                )
            )

    if toutes_annees:
        messages.append(
            dbc.Alert(
                "Le mode « toutes les années » empile les pays-années ; la tendance est indicative.",
                color="info",
                className="py-2 mb-2",
            )
        )
    if pente is None:
        messages.append(
            dbc.Alert(
                "Pas assez de points avec un PIB fiable pour tracer une tendance. "
                "Ajoutez des pays ou activez toutes les années.",
                color="info",
                className="py-2 mb-2",
            )
        )

    n_pays = df["country"].nunique()
    if n_pays == 1:
        if toutes_annees:
            texte_un_pays = (
                "Un seul pays : la tendance décrit une trajectoire temporelle, pas une "
                "comparaison entre pays. Le mode évolution est plus adapté."
            )
        else:
            texte_un_pays = (
                "Un seul pays et une seule année : aucune courbe de Preston n'est possible. "
                "Passez en mode évolution pour voir ses séries temporelles."
            )
        messages.append(
            dbc.Alert(texte_un_pays, color="info", className="py-2 mb-2")
        )

    messages.append(
        dbc.Alert(
            "Les corrélations décrivent des associations, pas des relations causales. "
            "La régression n'est pas pondérée par la population.",
            color="secondary",
            className="py-2 mb-0",
        )
    )
    return html.Div(messages)


def _figure_evolution(
    df: pd.DataFrame,
    parametres: list[str],
    periode: list[int],
) -> go.Figure:
    pays = sorted(df["country"].unique())
    panneaux: list[str | None] = [None] + list(parametres)
    nb_colonnes = 3
    nb_lignes = int(np.ceil(len(panneaux) / nb_colonnes))

    titres = ["Espérance de vie (années)"] + [
        TITRES_COURTS.get(cle, cle) for cle in parametres
    ]
    fig = make_subplots(
        rows=nb_lignes,
        cols=nb_colonnes,
        subplot_titles=titres,
        shared_xaxes=True,
        vertical_spacing=0.08,
        horizontal_spacing=0.07,
    )

    for index, cle in enumerate(panneaux):
        ligne = index // nb_colonnes + 1
        colonne = index % nb_colonnes + 1
        trace_ajoutee = False

        for i_pays, pays_nom in enumerate(pays):
            d = df[df["country"] == pays_nom].sort_values("year")
            if cle is None:
                y = d["life_expectancy"]
                libelle = "Espérance de vie"
            else:
                meta = data.PARAMETRES[cle]
                y = d[meta["colonne"]]
                libelle = meta["libelle"]

            masque = d["year"].notna() & y.notna()
            if not masque.any():
                continue

            couleur = COULEURS_EVOLUTION[i_pays % len(COULEURS_EVOLUTION)]
            fig.add_trace(
                go.Scatter(
                    x=d.loc[masque, "year"],
                    y=y[masque],
                    mode="lines+markers",
                    name=pays_nom,
                    line=dict(color=couleur, width=2),
                    marker=dict(size=4, color=couleur),
                    connectgaps=False,
                    hovertemplate=(
                        "<b>" + pays_nom + "</b><br>"
                        "Année : %{x}<br>"
                        + libelle
                        + " : %{y:.2f}<extra></extra>"
                    ),
                    showlegend=(index == 0),
                ),
                row=ligne,
                col=colonne,
            )
            trace_ajoutee = True

        if not trace_ajoutee:
            xref = f"x{index + 1} domain" if index > 0 else "x domain"
            yref = f"y{index + 1} domain" if index > 0 else "y domain"
            fig.add_annotation(
                text="Aucune donnée",
                x=0.5,
                y=0.5,
                xref=xref,
                yref=yref,
                showarrow=False,
                font=dict(size=11, color=data.GRIS),
            )

    total_cases = nb_lignes * nb_colonnes
    for index in range(len(panneaux), total_cases):
        ligne = index // nb_colonnes + 1
        colonne = index % nb_colonnes + 1
        fig.update_xaxes(visible=False, row=ligne, col=colonne)
        fig.update_yaxes(visible=False, row=ligne, col=colonne)

    fig.update_xaxes(dtick=2, tickangle=-45, tickfont=dict(size=9))
    fig.update_yaxes(tickfont=dict(size=9))
    fig.update_layout(
        template="dazzle",
        height=max(520, 240 * nb_lignes),
        margin=dict(l=30, r=20, t=80, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="closest",
    )
    fig.update_annotations(font_size=10)
    return fig


def _synthese_evolution(
    df: pd.DataFrame,
    parametres: list[str],
    periode: list[int],
) -> html.Div:
    n_obs = len(df)
    pays_presents = sorted(df["country"].unique())
    debut, fin = int(periode[0]), int(periode[1])

    enfants: list = [html.H5("Ce que montrent les trajectoires", className="titre-synthese")]
    enfants.append(
        html.P(
            f"{n_obs} observations, {len(pays_presents)} pays, période {debut}–{fin}.",
            className="mb-2",
        )
    )

    elements_ev = []
    for pays_nom in pays_presents[:6]:
        d = df[df["country"] == pays_nom][["year", "life_expectancy"]].dropna().sort_values("year")
        if len(d) < 2:
            continue
        premier, dernier = d.iloc[0], d.iloc[-1]
        variation = float(dernier["life_expectancy"] - premier["life_expectancy"])
        signe = "+" if variation >= 0 else ""
        elements_ev.append(
            html.Li(
                f"{pays_nom} : {_fr(premier['life_expectancy'])} → "
                f"{_fr(dernier['life_expectancy'])} ans "
                f"({signe}{_fr(variation)}), de {int(premier['year'])} à {int(dernier['year'])}."
            )
        )
    if len(pays_presents) > 6:
        elements_ev.append(html.Li(f"… et {len(pays_presents) - 6} autre(s) pays."))
    if elements_ev:
        enfants.append(
            html.Div([html.P("Espérance de vie :", className="mb-1"), html.Ul(elements_ev)])
        )

    if len(pays_presents) == 1 and parametres:
        pays_nom = pays_presents[0]
        d = df[df["country"] == pays_nom].sort_values("year")
        elements_params = []
        for cle in parametres:
            meta = data.PARAMETRES[cle]
            serie = d[["year", meta["colonne"]]].dropna()
            if serie.empty:
                elements_params.append(html.Li(f"{meta['libelle']} : aucune donnée."))
                continue
            premier, dernier = serie.iloc[0], serie.iloc[-1]
            valeur_debut = float(premier[meta["colonne"]])
            valeur_fin = float(dernier[meta["colonne"]])
            variation = valeur_fin - valeur_debut
            signe = "+" if variation >= 0 else ""
            elements_params.append(
                html.Li(
                    f"{meta['libelle']} : {_fr(valeur_debut, 2)} → {_fr(valeur_fin, 2)} "
                    f"({signe}{_fr(variation, 2)}) ; {len(serie)} années renseignées."
                )
            )
        enfants.append(
            html.Div(
                [
                    html.P(f"Paramètres de {pays_nom} :", className="mb-1"),
                    html.Ul(elements_params),
                ]
            )
        )
    elif len(pays_presents) > 1:
        enfants.append(
            html.P(
                "Les panneaux détaillent chaque paramètre ; le tableau donne les valeurs "
                "par pays et par année."
            )
        )
    else:
        enfants.append(html.P("Aucun paramètre sélectionné : seul l'espérance de vie est tracée."))

    flags = [
        data.PARAMETRES[cle]["flag_estimee"]
        for cle in parametres
        if data.PARAMETRES[cle].get("flag_estimee")
    ]
    if flags:
        nb_estimees = int(df[flags].any(axis=1).sum())
        if nb_estimees:
            enfants.append(
                html.P(
                    f"{nb_estimees} observations reposent sur au moins une valeur estimée.",
                    className="texte-secondaire mb-2",
                )
            )

    enfants.append(
        html.P(
            "Ces trajectoires sont descriptives. Elles ne prouvent pas qu'un paramètre cause "
            "l'espérance de vie, et les corrélations internes portent sur peu d'années.",
            className="texte-secondaire mb-0",
        )
    )
    return html.Div(enfants)


def _alertes_evolution(
    df: pd.DataFrame,
    parametres: list[str],
    tronques: list[str],
    periode: list[int],
) -> html.Div:
    messages = []

    if tronques:
        messages.append(
            dbc.Alert(
                "La sélection est limitée à 8 pays pour la lisibilité. "
                f"Pays non affichés : {', '.join(tronques)}.",
                color="warning",
                className="py-2 mb-2",
            )
        )

    if df["year"].nunique() < 2:
        messages.append(
            dbc.Alert(
                "La période sélectionnée ne contient qu'une année : les courbes sont réduites "
                "à des points.",
                color="info",
                className="py-2 mb-2",
            )
        )

    flags = [
        data.PARAMETRES[cle]["flag_estimee"]
        for cle in parametres
        if data.PARAMETRES[cle].get("flag_estimee")
    ]
    if flags:
        nb_estimees = int(df[flags].any(axis=1).sum())
        if nb_estimees:
            messages.append(
                dbc.Alert(
                    (f"1 observation utilise au moins une valeur estimée." if nb_estimees == 1 else f"{nb_estimees} observations utilisent au moins une valeur estimée."),
                    color="info",
                    className="py-2 mb-2",
                )
            )

    params_vides = [
        data.PARAMETRES[cle]["libelle"]
        for cle in parametres
        if df[data.PARAMETRES[cle]["colonne"]].notna().sum() == 0
    ]
    if params_vides:
        messages.append(
            dbc.Alert(
                "Aucune donnée pour : " + ", ".join(params_vides) + ".",
                color="warning",
                className="py-2 mb-2",
            )
        )

    if int(periode[1]) >= 2015:
        params_2015 = [
            data.PARAMETRES[cle]["libelle"]
            for cle in parametres
            if 2015 in data.PARAMETRES[cle]["annees_exclues"]
        ]
        if params_2015:
            messages.append(
                dbc.Alert(
                    "Les séries suivantes s'arrêtent en 2014 : "
                    + ", ".join(params_2015)
                    + ".",
                    color="info",
                    className="py-2 mb-2",
                )
            )

    messages.append(
        dbc.Alert(
            "Les trajectoires décrivent des évolutions. Elles ne prouvent pas une causalité.",
            color="secondary",
            className="py-2 mb-0",
        )
    )
    return html.Div(messages)


def _etat_vide(message: str, mode: str = "preston"):
    if mode == "evolution":
        colonnes = _colonnes_base_evolution()
        kpis = (
            _kpi("—", "Pays affichés"),
            _kpi("—", "Variation de l'EV"),
            _kpi("—", "Période"),
            _kpi("—", "Observations"),
        )
    else:
        colonnes = _colonnes_base()
        kpis = (
            _kpi("—", "Pays affichés"),
            _kpi("—", "Gain par ×10 de PIB"),
            _kpi("—", "Qualité de l'ajustement (R²)"),
            _kpi("—", "PIB fiable"),
        )
    return (
        _figure_vide(message),
        colonnes,
        [],
        html.Div([html.H5("Aucune donnée"), html.P(message)]),
        *kpis,
        dbc.Alert(message, color="info", className="py-2"),
    )


@callback(
    Output("page-contenu", "children"),
    Output("route-active", "data"),
    Input("url", "pathname"),
)
def afficher_page(pathname: str):
    if pathname == "/preston":
        return layout.page_preston(), "/preston"
    if pathname == "/inegalites":
        return layout.page_inegalites(), "/inegalites"
    if pathname == "/determinants":
        return layout.page_determinants(), "/determinants"
    if pathname == "/comparateur":
        return layout.page_comparateur(), "/comparateur"
    if pathname == "/methodologie":
        return layout.page_methodologie(), "/methodologie"
    return layout.page_accueil(), "/"


@callback(
    Output("nav-accueil", "active"),
    Output("nav-preston", "active"),
    Output("nav-inegalites", "active"),
    Output("nav-determinants", "active"),
    Output("nav-comparateur", "active"),
    Output("nav-methodologie", "active"),
    Input("url", "pathname"),
)
def activer_navigation(pathname: str):
    return (
        pathname == "/",
        pathname == "/preston",
        pathname == "/inegalites",
        pathname == "/determinants",
        pathname == "/comparateur",
        pathname == "/methodologie",
    )


@callback(
    Output("preston-pays", "disabled"),
    Input("preston-tous-pays", "value"),
    Input("route-active", "data"),
)
def desactiver_pays(tous_pays: bool, route: str):
    if route != "/preston":
        return no_update
    return bool(tous_pays)


@callback(
    Output("preston-pays", "options"),
    Output("preston-pays", "value"),
    Input("preston-statut", "value"),
    Input("route-active", "data"),
    State("preston-pays", "value"),
)
def maj_pays(statut: str, route: str, selection: list[str] | None):
    if route != "/preston":
        return no_update, no_update
    options = data.options_pays(statut or "Tous")
    valeurs = {option["value"] for option in options}
    selection = [pays for pays in (selection or []) if pays in valeurs]
    if not selection:
        selection = [option["value"] for option in options[:5]]
    return options, selection


@callback(
    Output("preston-parametres", "options"),
    Output("preston-parametres", "value"),
    Input("preston-annee", "value"),
    Input("preston-toutes-annees", "value"),
    Input("preston-mode", "value"),
    Input("route-active", "data"),
    State("preston-parametres", "value"),
)
def maj_parametres(
    annee: int,
    toutes_annees: bool,
    mode: str,
    route: str,
    selection: list[str] | None,
):
    if route != "/preston":
        return no_update, no_update
    if mode == "evolution":
        options = data.options_parametres(None, True)
    else:
        options = data.options_parametres(int(annee), bool(toutes_annees))
    valeurs = {option["value"] for option in options}
    selection = [cle for cle in (selection or []) if cle in valeurs]
    if not selection:
        selection = [cle for cle in data.PARAMETRES_DEFAUT if cle in valeurs]
    return options, selection


@callback(
    Output("preston-annee", "disabled"),
    Input("preston-toutes-annees", "value"),
    Input("route-active", "data"),
)
def desactiver_slider(toutes_annees: bool, route: str):
    if route != "/preston":
        return no_update
    return bool(toutes_annees)


@callback(
    Output("bloc-tous-pays", "style"),
    Output("bloc-aberrants", "style"),
    Output("bloc-annee-preston", "style"),
    Output("bloc-toutes-annees", "style"),
    Output("bloc-periode-evolution", "style"),
    Output("preston-tous-pays", "value"),
    Input("preston-mode", "value"),
)
def gerer_mode(mode: str):
    if mode == "evolution":
        return (
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
            {"display": "block"},
            False,
        )
    return (
        {"display": "block"},
        {"display": "block"},
        {"display": "block"},
        {"display": "block"},
        {"display": "none"},
        no_update,
    )


@callback(
    Output("preston-graphique", "figure"),
    Output("preston-tableau", "columnDefs"),
    Output("preston-tableau", "rowData"),
    Output("preston-synthese", "children"),
    Output("preston-kpi-pays", "children"),
    Output("preston-kpi-pente", "children"),
    Output("preston-kpi-r2", "children"),
    Output("preston-kpi-couverture", "children"),
    Output("preston-alertes", "children"),
    Input("preston-pays", "value"),
    Input("preston-tous-pays", "value"),
    Input("preston-statut", "value"),
    Input("preston-parametres", "value"),
    Input("preston-annee", "value"),
    Input("preston-toutes-annees", "value"),
    Input("preston-afficher-aberrants", "value"),
    Input("preston-periode", "value"),
    Input("preston-mode", "value"),
    Input("route-active", "data"),
)
def actualiser_preston(
    pays_selectionnes: list[str] | None,
    tous_pays: bool,
    statut: str,
    parametres: list[str] | None,
    annee: int,
    toutes_annees: bool,
    afficher_aberrants: bool,
    periode: list[int],
    mode: str,
    route: str,
):
    if route != "/preston":
        return (no_update,) * 9

    df_base = data.charger_donnees().copy()
    if statut and statut != "Tous":
        df_base = df_base[df_base["statut"] == statut]

    # Mode évolution : séries temporelles, sans dépendance au PIB.
    if mode == "evolution":
        pays = [pays_nom for pays_nom in (pays_selectionnes or []) if pays_nom]
        if not pays:
            return _etat_vide(
                "Sélectionnez au moins un pays pour voir son évolution.", "evolution"
            )

        pays = sorted(set(pays))
        tronques_pays = pays[8:]
        pays = pays[:8]
        df_evo = df_base[df_base["country"].isin(pays)].copy()
        debut, fin = (int(periode[0]), int(periode[1])) if periode else (data.ANNEE_MIN, data.ANNEE_MAX)
        df_evo = df_evo[(df_evo["year"] >= debut) & (df_evo["year"] <= fin)]

        if df_evo.empty:
            return _etat_vide("Aucune observation sur cette période.", "evolution")

        parametres_evo = [cle for cle in (parametres or []) if cle in data.PARAMETRES]
        fig = _figure_evolution(df_evo, parametres_evo, periode)
        row_data, column_defs = _preparer_tableau_evolution(df_evo, parametres_evo)
        synthese = _synthese_evolution(df_evo, parametres_evo, periode)
        alertes = _alertes_evolution(df_evo, parametres_evo, tronques_pays, periode)

        n_pays = df_evo["country"].nunique()
        variations = []
        for pays_nom in sorted(df_evo["country"].unique()):
            d = df_evo[df_evo["country"] == pays_nom][
                ["year", "life_expectancy"]
            ].dropna().sort_values("year")
            if len(d) >= 2:
                variations.append(
                    float(d["life_expectancy"].iloc[-1] - d["life_expectancy"].iloc[0])
                )

        if variations:
            variation_moyenne = float(np.mean(variations))
            libelle_variation = (
                "Variation de l'EV" if n_pays == 1 else "Variation moyenne de l'EV"
            )
            kpi_variation = _kpi(
                f"{variation_moyenne:+.1f}".replace(".", ",") + " ans",
                libelle_variation,
            )
        else:
            kpi_variation = _kpi("—", "Variation de l'EV")

        kpis = (
            _kpi(str(n_pays), "Pays affichés"),
            kpi_variation,
            _kpi(f"{debut}–{fin}", "Période"),
            _kpi(str(len(df_evo)), "Observations"),
        )
        return (fig, column_defs, row_data, synthese, *kpis, alertes)

    # Mode Preston : comparaison entre pays, avec PIB.
    if tous_pays:
        df = df_base
    else:
        pays_selectionnes = pays_selectionnes or []
        if not pays_selectionnes:
            return _etat_vide(
                "Sélectionnez au moins un pays, ou activez « Tous les pays ».", "preston"
            )
        df = df_base[df_base["country"].isin(pays_selectionnes)]

    if not toutes_annees:
        df = df[df["year"] == int(annee)]

    if df.empty:
        return _etat_vide("Aucune observation ne correspond à ces filtres.", "preston")

    parametres = [cle for cle in (parametres or []) if cle in data.PARAMETRES]
    indisponibles = [
        cle
        for cle in parametres
        if not toutes_annees and int(annee) in data.PARAMETRES[cle]["annees_exclues"]
    ]
    parametres = [cle for cle in parametres if cle not in indisponibles]
    tronques = parametres[4:]
    parametres = parametres[:4]

    fig, pente, r2, n_trace, _nb_aberrants = _figure_preston(
        df, parametres, bool(afficher_aberrants)
    )
    row_data, column_defs = _preparer_tableau(df, parametres)
    synthese = _synthese(df, parametres, pente, r2, n_trace, bool(toutes_annees))
    alertes = _alertes(
        df,
        parametres,
        indisponibles,
        tronques,
        pente,
        bool(afficher_aberrants),
        bool(toutes_annees),
    )

    n_pays = df["country"].nunique()
    n_pays_pib = df.loc[df["gdp_clean"].notna(), "country"].nunique()
    kpis = (
        _kpi(str(n_pays), "Pays affichés"),
        _kpi(
            "—" if pente is None else f"{pente:+.1f}".replace(".", ",") + " ans",
            "Gain par ×10 de PIB",
        ),
        _kpi("—" if r2 is None else _fr(r2, 2), "Qualité de l'ajustement (R²)"),
        _kpi(f"{n_pays_pib} / {n_pays}", "PIB fiable"),
    )
    return (fig, column_defs, row_data, synthese, *kpis, alertes)



# ===========================================================================
# Page Inégalités
# ===========================================================================
def _colonnes_inegalites() -> list[dict]:
    return [
        {"field": "rang", "headerName": "Rang", "minWidth": 80, "type": "numericColumn"},
        {"field": "country", "headerName": "Pays", "minWidth": 170},
        {"field": "statut", "headerName": "Statut", "minWidth": 140},
        {
            "field": "life_expectancy",
            "headerName": "Espérance de vie (ans)",
            "minWidth": 150,
            "type": "numericColumn",
        },
        {
            "field": "gdp",
            "headerName": "PIB (USD/hab.)",
            "minWidth": 130,
            "type": "numericColumn",
        },
        {"field": "gdp_statut", "headerName": "PIB (qualité)", "minWidth": 115},
    ]


def _preparer_tableau_inegalites(df: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    table = df.sort_values("life_expectancy", ascending=False).copy()
    table["rang"] = range(1, len(table) + 1)
    table["id_ligne"] = table["country"].astype(str) + " | " + table["year"].astype(str)
    table["gdp_statut"] = np.select(
        [table["gdp"].isna(), table["gdp_aberrant"]],
        ["Manquant", "Signalé"],
        default="Fiable",
    )
    for colonne in ["life_expectancy", "gdp"]:
        table[colonne] = table[colonne].round(2)
    colonnes = ["id_ligne", "rang", "country", "statut", "life_expectancy", "gdp", "gdp_statut"]
    table = table[colonnes].astype(object).where(pd.notna(table[colonnes]), None)
    return table.to_dict("records"), _colonnes_inegalites()


def _etat_vide_inegalites(message: str):
    return (
        _figure_vide(message),
        _figure_vide(message),
        _figure_vide(message),
        _figure_vide(message),
        _colonnes_inegalites(),
        [],
        html.Div([html.H5("Aucune donnée"), html.P(message)]),
        _kpi("—", "Espérance de vie moyenne"),
        _kpi("—", "Écart max–min"),
        _kpi("—", "Écart Nord/Sud"),
        _kpi("—", "Pays affichés"),
        dbc.Alert(message, color="info", className="py-2"),
    )


@callback(
    Output("ineg-graph-distribution", "figure"),
    Output("ineg-graph-classement", "figure"),
    Output("ineg-graph-evolution", "figure"),
    Output("ineg-graph-carte", "figure"),
    Output("ineg-tableau", "columnDefs"),
    Output("ineg-tableau", "rowData"),
    Output("ineg-synthese", "children"),
    Output("ineg-kpi-moyenne", "children"),
    Output("ineg-kpi-etendue", "children"),
    Output("ineg-kpi-ecart", "children"),
    Output("ineg-kpi-pays", "children"),
    Output("ineg-alertes", "children"),
    Input("ineg-annee", "value"),
    Input("ineg-statut", "value"),
    Input("route-active", "data"),
)
def actualiser_inegalites(annee: int, statut: str, route: str):
    if route != "/inegalites":
        return (no_update,) * 12

    df_all = data.charger_donnees().copy()
    df_annee = df_all[df_all["year"] == int(annee)].copy()
    if statut and statut != "Tous":
        df_annee = df_annee[df_annee["statut"] == statut]

    if df_annee.empty:
        return _etat_vide_inegalites("Aucune observation pour cette sélection.")

    fig_distribution = px.box(
        df_annee,
        x="statut",
        y="life_expectancy",
        color="statut",
        color_discrete_map=data.COULEURS_STATUT,
        points="outliers",
        labels={"statut": "", "life_expectancy": "Espérance de vie (années)"},
        title=f"Distribution de l'espérance de vie en {annee}",
    )
    fig_distribution.update_layout(template="dazzle", showlegend=False, height=520)

    hauts = df_annee.nlargest(10, "life_expectancy")[["country", "life_expectancy"]].assign(
        groupe="Top 10"
    )
    bas = df_annee.nsmallest(10, "life_expectancy")[["country", "life_expectancy"]].assign(
        groupe="Flop 10"
    )
    classement = pd.concat([hauts, bas]).sort_values("life_expectancy")
    fig_classement = px.bar(
        classement,
        x="life_expectancy",
        y="country",
        orientation="h",
        color="groupe",
        color_discrete_map={"Top 10": data.VERT, "Flop 10": data.ORANGE},
        labels={"life_expectancy": "Espérance de vie (années)", "country": "", "groupe": ""},
        title=f"Les 10 meilleurs et les 10 moins bons pays en {annee}",
    )
    fig_classement.update_layout(template="dazzle", height=620)

    df_evo = df_all if statut == "Tous" else df_all[df_all["statut"] == statut]
    evolution = (
        df_evo.groupby(["year", "statut"], as_index=False)["life_expectancy"]
        .mean()
        .sort_values("year")
    )
    fig_evolution = px.line(
        evolution,
        x="year",
        y="life_expectancy",
        color="statut",
        color_discrete_map=data.COULEURS_STATUT,
        markers=True,
        labels={
            "year": "Année",
            "life_expectancy": "Espérance de vie moyenne (années)",
            "statut": "Statut",
        },
        title="Évolution de l'espérance de vie moyenne",
    )
    fig_evolution.update_layout(template="dazzle", height=460)

    df_carte = df_annee.dropna(subset=["iso3", "life_expectancy"]).copy()
    titre_carte = f"Espérance de vie dans le monde en {annee}"
    if statut != "Tous":
        titre_carte += f" — {statut}"
    fig_carte = px.choropleth(
        df_carte,
        locations="iso3",
        color="life_expectancy",
        hover_name="country",
        hover_data={"statut": True, "life_expectancy": ":.1f", "iso3": False},
        color_continuous_scale=data.ECHELLE_CARTE,
        range_color=(45, 85),
        labels={"life_expectancy": "Espérance de vie (ans)"},
        title=titre_carte,
    )
    fig_carte.update_layout(
        template="dazzle",
        height=610,
        margin=dict(l=0, r=0, t=52, b=0),
        coloraxis_colorbar=dict(
            title="Années",
            thickness=10,
            len=0.72,
            tickfont=dict(family="IBM Plex Mono, monospace", size=10, color=data.MARINE),
            title_font=dict(
                family="IBM Plex Sans, sans-serif", size=11, color=data.MARINE
            ),
        ),
        geo=dict(
            showframe=False,
            showcoastlines=False,
            bgcolor=data.MARINE,
            landcolor="#E8F1EF",
            showland=True,
            showcountries=True,
            countrycolor="#B9CDC9",
            showocean=True,
            oceancolor=data.MARINE,
            projection_type="natural earth",
        ),
    )
    fig_carte.add_annotation(
        text="Source : OMS, 2000-2015",
        xref="paper",
        yref="paper",
        x=0.01,
        y=0.01,
        showarrow=False,
        font=dict(family="IBM Plex Sans, sans-serif", size=10, color=data.GRIS),
    )

    rows, cols = _preparer_tableau_inegalites(df_annee)

    moyenne = float(df_annee["life_expectancy"].mean())
    mediane = float(df_annee["life_expectancy"].median())
    minimum = float(df_annee["life_expectancy"].min())
    maximum = float(df_annee["life_expectancy"].max())
    etendue = maximum - minimum
    meilleur = df_annee.loc[df_annee["life_expectancy"].idxmax(), "country"]
    moins_bon = df_annee.loc[df_annee["life_expectancy"].idxmin(), "country"]
    n_pays = int(df_annee["country"].nunique())

    ecart = None
    if {"Développé", "En développement"}.issubset(set(df_annee["statut"])):
        ecart = float(
            df_annee.loc[df_annee["statut"] == "Développé", "life_expectancy"].mean()
            - df_annee.loc[df_annee["statut"] == "En développement", "life_expectancy"].mean()
        )

    synthese = html.Div(
        [
            html.H5("Ce que montre la sélection", className="titre-synthese"),
            html.P(
                f"En {annee}, l'espérance de vie moyenne est de {_fr(moyenne)} ans "
                f"(médiane {_fr(mediane)} ans). Le pays le plus favorisé est {meilleur} "
                f"({_fr(maximum)} ans) et le moins favorisé est {moins_bon} "
                f"({_fr(minimum)} ans), soit un écart de {_fr(etendue)} ans.",
                className="mb-2",
            ),
            html.P(
                (
                    f"L'écart moyen entre pays développés et pays en développement est de "
                    f"{_fr(ecart)} ans."
                    if ecart is not None
                    else "L'écart Nord/Sud n'est pas calculé quand un seul statut est filtré."
                ),
                className="mb-2",
            ),
            html.P(
                "La distribution montre à la fois le niveau moyen et les situations extrêmes. "
                "Elle ne dit pas pourquoi ces écarts existent.",
                className="texte-secondaire mb-0",
            ),
        ]
    )

    alertes = []
    if statut != "Tous":
        alertes.append(
            dbc.Alert(
                f"Filtre actif : {statut}. Le classement et la distribution portent uniquement "
                "sur ce groupe.",
                color="info",
                className="py-2 mb-2",
            )
        )
    if n_pays < 10:
        alertes.append(
            dbc.Alert(
                "Moins de 10 pays dans la sélection : les classements sont indicatifs.",
                color="info",
                className="py-2 mb-2",
            )
        )
    alertes.append(
        dbc.Alert(
            "Les écarts décrivent la distribution observée, pas une relation causale.",
            color="secondary",
            className="py-2 mb-0",
        )
    )

    return (
        fig_distribution,
        fig_classement,
        fig_evolution,
        fig_carte,
        cols,
        rows,
        synthese,
        _kpi(f"{_fr(moyenne)} ans", "Espérance de vie moyenne"),
        _kpi(f"{_fr(etendue)} ans", "Écart max–min"),
        _kpi("—" if ecart is None else f"{_fr(ecart)} ans", "Écart Nord/Sud"),
        _kpi(str(n_pays), "Pays affichés"),
        html.Div(alertes),
    )


# ===========================================================================
# Page Déterminants
# ===========================================================================
def _colonnes_determinants() -> list[dict]:
    return [
        {"field": "facteur", "headerName": "Facteur", "minWidth": 280},
        {"field": "r", "headerName": "r avec l'EV", "minWidth": 110, "type": "numericColumn"},
        {"field": "n", "headerName": "n", "minWidth": 80, "type": "numericColumn"},
        {
            "field": "r_partiel",
            "headerName": "r partiel (PIB)",
            "minWidth": 130,
            "type": "numericColumn",
        },
        {"field": "n_partiel", "headerName": "n partiel", "minWidth": 100, "type": "numericColumn"},
    ]


def _etat_vide_determinants(message: str):
    return (
        _figure_vide(message),
        _figure_vide(message),
        _colonnes_determinants(),
        [],
        html.Div([html.H5("Aucune donnée"), html.P(message)]),
        _kpi("—", "Facteur le plus associé"),
        _kpi("—", "Facteurs comparés"),
        _kpi("—", "Observations"),
        _kpi("—", "Corrélation partielle max"),
        dbc.Alert(message, color="info", className="py-2"),
    )


@callback(
    Output("det-facteurs", "options"),
    Output("det-facteurs", "value"),
    Input("det-annee", "value"),
    Input("det-toutes-annees", "value"),
    Input("route-active", "data"),
    State("det-facteurs", "value"),
)
def maj_facteurs(annee: int, toutes_annees: bool, route: str, selection: list[str] | None):
    if route != "/determinants":
        return no_update, no_update
    options = data.options_parametres(int(annee), bool(toutes_annees))
    valeurs = {option["value"] for option in options}
    selection = [cle for cle in (selection or []) if cle in valeurs]
    if not selection:
        selection = [cle for cle in data.FACTEURS_DETERMINANTS_DEFAUT if cle in valeurs]
    if not selection:
        selection = [option["value"] for option in options[:4]]
    return options, selection


@callback(
    Output("det-annee", "disabled"),
    Input("det-toutes-annees", "value"),
    Input("route-active", "data"),
)
def desactiver_annee_determinants(toutes_annees: bool, route: str):
    if route != "/determinants":
        return no_update
    return bool(toutes_annees)


@callback(
    Output("det-graph-corr", "figure"),
    Output("det-graph-scatter", "figure"),
    Output("det-tableau", "columnDefs"),
    Output("det-tableau", "rowData"),
    Output("det-synthese", "children"),
    Output("det-kpi-fort", "children"),
    Output("det-kpi-facteurs", "children"),
    Output("det-kpi-obs", "children"),
    Output("det-kpi-partiel", "children"),
    Output("det-alertes", "children"),
    Input("det-annee", "value"),
    Input("det-toutes-annees", "value"),
    Input("det-statut", "value"),
    Input("det-facteurs", "value"),
    Input("route-active", "data"),
)
def actualiser_determinants(
    annee: int,
    toutes_annees: bool,
    statut: str,
    facteurs: list[str] | None,
    route: str,
):
    if route != "/determinants":
        return (no_update,) * 10

    df = data.charger_donnees().copy()
    if statut and statut != "Tous":
        df = df[df["statut"] == statut]
    if not toutes_annees:
        df = df[df["year"] == int(annee)]

    if df.empty:
        return _etat_vide_determinants("Aucune observation pour cette sélection.")

    disponibles = [option["value"] for option in data.options_parametres(
        int(annee), bool(toutes_annees)
    )]

    stats = []
    for cle in disponibles:
        meta = data.PARAMETRES[cle]
        observe = df[["life_expectancy", cle]].dropna()
        if len(observe) < 3:
            continue
        r = float(observe[cle].corr(observe["life_expectancy"]))
        avec_pib = df[["life_expectancy", cle, "gdp_clean"]].dropna()
        r_partiel = None
        n_partiel = len(avec_pib)
        if len(avec_pib) >= 3:
            log_pib = np.log10(avec_pib["gdp_clean"].where(avec_pib["gdp_clean"] > 0))
            rp, npa = data.correlation_partielle(avec_pib[cle], avec_pib["life_expectancy"], log_pib)
            if not pd.isna(rp):
                r_partiel = float(rp)
                n_partiel = int(npa)
        stats.append(
            {
                "cle": cle,
                "facteur": meta["libelle"],
                "r": r,
                "n": len(observe),
                "r_partiel": r_partiel,
                "n_partiel": n_partiel,
            }
        )

    if not stats:
        return _etat_vide_determinants("Pas assez de données pour calculer des corrélations.")

    stats_triees = sorted(stats, key=lambda item: item["r"])
    labels = [item["facteur"] for item in stats_triees]
    valeurs = [item["r"] for item in stats_triees]
    couleurs = [data.VERT if valeur > 0 else data.ORANGE for valeur in valeurs]

    fig_corr = go.Figure(
        go.Bar(
            x=valeurs,
            y=labels,
            orientation="h",
            marker_color=couleurs,
            text=[_fr(valeur, 2) for valeur in valeurs],
            textposition="auto",
        )
    )
    fig_corr.update_layout(
        template="dazzle",
        height=max(420, 34 * len(stats) + 100),
        margin=dict(l=20, r=20, t=40, b=30),
        xaxis_title="Corrélation avec l'espérance de vie (r de Pearson)",
        yaxis_title="",
    )

    selection = [cle for cle in (facteurs or []) if any(item["cle"] == cle for item in stats)]
    if not selection:
        selection = [
            item["cle"]
            for item in sorted(stats, key=lambda item: abs(item["r"]), reverse=True)[:4]
        ]
    selection = selection[:4]
    nb = len(selection)
    if nb == 1:
        lignes, colonnes = 1, 1
    elif nb == 2:
        lignes, colonnes = 1, 2
    elif nb == 3:
        lignes, colonnes = 1, 3
    else:
        lignes, colonnes = 2, 2

    titres = []
    for cle in selection:
        item = next(item for item in stats if item["cle"] == cle)
        titres.append(f"{TITRES_COURTS.get(cle, cle)} (r = {_fr(item['r'], 2)})")

    fig_scatter = make_subplots(
        rows=lignes,
        cols=colonnes,
        subplot_titles=titres,
        shared_yaxes=True,
        horizontal_spacing=0.08,
        vertical_spacing=0.14,
    )

    for index, cle in enumerate(selection):
        ligne = index // colonnes + 1
        colonne = index % colonnes + 1
        sous_ensemble = df[df[cle].notna() & df["life_expectancy"].notna()].copy()
        if sous_ensemble.empty:
            xref = f"x{index + 1} domain" if index > 0 else "x domain"
            yref = f"y{index + 1} domain" if index > 0 else "y domain"
            fig_scatter.add_annotation(
                text="Aucune donnée",
                x=0.5,
                y=0.5,
                xref=xref,
                yref=yref,
                showarrow=False,
                font=dict(size=11, color=data.GRIS),
            )
            continue

        for statut_nom, couleur in data.COULEURS_STATUT.items():
            d = sous_ensemble[sous_ensemble["statut"] == statut_nom]
            if d.empty:
                continue
            fig_scatter.add_trace(
                go.Scattergl(
                    x=d[cle],
                    y=d["life_expectancy"],
                    mode="markers",
                    name=statut_nom,
                    marker=dict(size=6, color=couleur, opacity=0.65),
                    customdata=d[["country", "year"]].to_numpy(),
                    hovertemplate=(
                        "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                        + data.PARAMETRES[cle]["libelle"]
                        + " : %{x:.2f}<br>Espérance : %{y:.1f} ans<extra></extra>"
                    ),
                    showlegend=(index == 0),
                ),
                row=ligne,
                col=colonne,
            )

        x = sous_ensemble[cle].to_numpy()
        y = sous_ensemble["life_expectancy"].to_numpy()
        if len(x) >= 3 and np.nanstd(x) > 0:
            coef = np.polyfit(x, y, 1)
            grille = np.linspace(np.nanmin(x), np.nanmax(x), 100)
            fig_scatter.add_trace(
                go.Scatter(
                    x=grille,
                    y=np.polyval(coef, grille),
                    mode="lines",
                    name="Tendance",
                    line=dict(color=data.GRIS, dash="dash", width=2),
                    showlegend=(index == 0),
                ),
                row=ligne,
                col=colonne,
            )

    fig_scatter.update_layout(
        template="dazzle",
        height=620 if nb <= 2 else 820,
        margin=dict(l=30, r=20, t=70, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="closest",
    )
    fig_scatter.update_annotations(font_size=10)
    fig_scatter.update_yaxes(title_text="Espérance de vie (années)", row=1, col=1)

    rows_table = [
        {
            "facteur": item["facteur"],
            "r": round(item["r"], 3),
            "n": item["n"],
            "r_partiel": None if item["r_partiel"] is None else round(item["r_partiel"], 3),
            "n_partiel": item["n_partiel"],
        }
        for item in sorted(stats, key=lambda item: item["r"], reverse=True)
    ]

    fort = max(stats, key=lambda item: abs(item["r"]))
    partiels = [item for item in stats if item["r_partiel"] is not None]
    partiel_fort = max(partiels, key=lambda item: abs(item["r_partiel"])) if partiels else None

    positifs = sorted([item for item in stats if item["r"] > 0], key=lambda item: item["r"], reverse=True)
    negatifs = sorted([item for item in stats if item["r"] < 0], key=lambda item: item["r"])

    synthese = html.Div(
        [
            html.H5("Ce que montrent les corrélations", className="titre-synthese"),
            html.P(
                f"Sur {len(df)} observations, le facteur le plus associé est "
                f"{fort['facteur']} (r = {_fr(fort['r'], 2)}).",
                className="mb-2",
            ),
        ]
    )
    if positifs:
        synthese.children.append(
            html.P(
                "Liens positifs les plus forts : "
                + ", ".join(
                    f"{item['facteur']} ({_fr(item['r'], 2)})" for item in positifs[:3]
                )
                + ".",
                className="mb-2",
            )
        )
    if negatifs:
        synthese.children.append(
            html.P(
                "Liens négatifs les plus forts : "
                + ", ".join(
                    f"{item['facteur']} ({_fr(item['r'], 2)})" for item in negatifs[:3]
                )
                + ".",
                className="mb-2",
            )
        )
    if partiel_fort is not None:
        synthese.children.append(
            html.P(
                f"Après contrôle du PIB nettoyé, la corrélation partielle la plus forte est "
                f"{partiel_fort['facteur']} ({_fr(partiel_fort['r_partiel'], 2)}). Les autres "
                "liens peuvent être en partie expliqués par le niveau de revenu.",
                className="mb-2",
            )
        )
    synthese.children.append(
        html.P(
            "Une corrélation décrit une association, pas une causalité, et ne dit pas dans quel "
            "sens les facteurs agissent.",
            className="texte-secondaire mb-0",
        )
    )

    alertes = []
    if toutes_annees:
        alertes.append(
            dbc.Alert(
                "Les années sont empilées : les observations d'un même pays ne sont pas "
                "indépendantes.",
                color="info",
                className="py-2 mb-2",
            )
        )
    if len(stats) < 3 or len(df) < 10:
        alertes.append(
            dbc.Alert(
                "Peu de données : les corrélations sont indicatives.",
                color="info",
                className="py-2 mb-2",
            )
        )
    alertes.append(
        dbc.Alert(
            "Les corrélations ne prouvent pas une causalité.",
            color="secondary",
            className="py-2 mb-0",
        )
    )

    return (
        fig_corr,
        fig_scatter,
        _colonnes_determinants(),
        rows_table,
        synthese,
        _kpi(
            f"{TITRES_COURTS.get(fort['cle'], fort['cle'])} ({_fr(fort['r'], 2)})",
            "Facteur le plus associé",
        ),
        _kpi(str(len(stats)), "Facteurs comparés"),
        _kpi(str(len(df)), "Observations"),
        _kpi(
            "—"
            if partiel_fort is None
            else f"{TITRES_COURTS.get(partiel_fort['cle'], partiel_fort['cle'])} "
            f"({_fr(partiel_fort['r_partiel'], 2)})",
            "Corrélation partielle max",
        ),
        html.Div(alertes),
    )


# ===========================================================================
# Page Comparateur
# ===========================================================================
def _colonnes_comparateur(indicateurs: list[str]) -> list[dict]:
    colonnes = [
        {"field": "country", "headerName": "Pays", "minWidth": 180},
        {"field": "statut", "headerName": "Statut", "minWidth": 140},
    ]
    for cle in indicateurs:
        meta = data.INDICATEURS_COMPARATEUR[cle]
        colonnes.append(
            {
                "field": cle,
                "headerName": meta["libelle"],
                "minWidth": 180,
                "type": "numericColumn",
            }
        )
    return colonnes


def _etat_vide_comparateur(message: str):
    return (
        _figure_vide(message),
        _colonnes_comparateur([]),
        [],
        html.Div([html.H5("Aucune donnée"), html.P(message)]),
        _kpi("—", "Pays comparés"),
        _kpi("—", "Année"),
        _kpi("—", "Indicateurs"),
        _kpi("—", "Meilleure EV"),
        dbc.Alert(message, color="info", className="py-2"),
    )


@callback(
    Output("comp-graph-radar", "figure"),
    Output("comp-tableau", "columnDefs"),
    Output("comp-tableau", "rowData"),
    Output("comp-synthese", "children"),
    Output("comp-kpi-pays", "children"),
    Output("comp-kpi-annee", "children"),
    Output("comp-kpi-indicateurs", "children"),
    Output("comp-kpi-meilleure", "children"),
    Output("comp-alertes", "children"),
    Input("comp-pays", "value"),
    Input("comp-annee", "value"),
    Input("comp-indicateurs", "value"),
    Input("route-active", "data"),
)
def actualiser_comparateur(
    pays_selectionnes: list[str] | None,
    annee: int,
    indicateurs: list[str] | None,
    route: str,
):
    if route != "/comparateur":
        return (no_update,) * 9

    pays = [pays_nom for pays_nom in (pays_selectionnes or []) if pays_nom]
    if len(pays) < 2:
        return _etat_vide_comparateur("Sélectionnez au moins 2 pays.")

    tronques = pays[5:]
    pays = sorted(set(pays[:5]))

    indicateurs = [cle for cle in (indicateurs or []) if cle in data.INDICATEURS_COMPARATEUR]
    if len(indicateurs) < 3:
        return _etat_vide_comparateur("Sélectionnez au moins 3 indicateurs.")

    df = data.charger_donnees().copy()
    df_annee = df[df["year"] == int(annee)].copy()
    if df_annee.empty:
        return _etat_vide_comparateur("Aucune observation pour cette année.")

    # Scores percentiles : 100 = meilleur pays de l'année pour l'indicateur.
    scores = {}
    for cle in indicateurs:
        meta = data.INDICATEURS_COMPARATEUR[cle]
        serie = df_annee[["country", cle]].dropna().copy()
        if serie.empty:
            continue
        rang = serie[cle].rank(pct=True)
        if meta["sens"] < 0:
            rang = 1 - rang
        scores[cle] = dict(zip(serie["country"], (rang * 100).round(1)))

    indicateurs_presents = [cle for cle in indicateurs if cle in scores]
    if len(indicateurs_presents) < 3:
        return _etat_vide_comparateur(
            "Pas assez d'indicateurs renseignés pour construire le radar."
        )

    pays_valides = []
    pays_incomplets = []
    for pays_nom in pays:
        valeurs = [scores[cle].get(pays_nom) for cle in indicateurs_presents]
        if any(valeur is None for valeur in valeurs):
            pays_incomplets.append(pays_nom)
        else:
            pays_valides.append((pays_nom, [float(valeur) for valeur in valeurs]))

    if len(pays_valides) < 2:
        return _etat_vide_comparateur(
            "Pas assez de pays avec des données complètes pour comparer."
        )

    theta = [data.INDICATEURS_COMPARATEUR[cle]["libelle_court"] for cle in indicateurs_presents]
    theta = theta + [theta[0]]

    fig = go.Figure()
    for index, (pays_nom, valeurs) in enumerate(pays_valides):
        couleur = COULEURS_EVOLUTION[index % len(COULEURS_EVOLUTION)]
        fig.add_trace(
            go.Scatterpolar(
                r=valeurs + [valeurs[0]],
                theta=theta,
                fill="toself",
                name=pays_nom,
                line=dict(color=couleur, width=2),
                opacity=0.55,
            )
        )
    fig.update_layout(
        template="dazzle",
        height=620,
        margin=dict(l=30, r=30, t=50, b=30),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                tickfont=dict(size=9),
            )
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="left", x=0),
        title=f"Profils normalisés en {annee} (100 = meilleur pays de l'année)",
    )

    table = df_annee[df_annee["country"].isin(pays)].copy()
    table = table.sort_values("life_expectancy", ascending=False)
    table["id_ligne"] = table["country"].astype(str) + " | " + table["year"].astype(str)
    for cle in indicateurs:
        meta = data.INDICATEURS_COMPARATEUR[cle]
        table[cle] = table[cle].round(meta["format"])
    colonnes = ["id_ligne", "country", "statut"] + indicateurs
    table = table[colonnes].astype(object).where(pd.notna(table[colonnes]), None)
    rows = table.to_dict("records")

    sub = df_annee[df_annee["country"].isin(pays)].dropna(subset=["life_expectancy"])
    if not sub.empty:
        meilleur = sub.loc[sub["life_expectancy"].idxmax()]
        kpi_meilleure = _kpi(
            f"{meilleur['country']} : {_fr(meilleur['life_expectancy'])} ans",
            "Meilleure EV",
        )
    else:
        kpi_meilleure = _kpi("—", "Meilleure EV")

    ecarts = []
    for cle in indicateurs_presents:
        valeurs = [scores[cle].get(pays_nom) for pays_nom in pays if scores[cle].get(pays_nom) is not None]
        if valeurs:
            ecarts.append((data.INDICATEURS_COMPARATEUR[cle]["libelle_court"], max(valeurs) - min(valeurs)))
    ecart_max = max(ecarts, key=lambda item: item[1]) if ecarts else None

    synthese = html.Div(
        [
            html.H5("Ce que montre la comparaison", className="titre-synthese"),
            html.P(
                "Le radar compare les pays sur des rangs percentiles : 100 correspond au "
                "meilleur pays de l'année pour l'indicateur. Ce ne sont pas des notes absolues.",
                className="mb-2",
            ),
        ]
    )
    if not sub.empty:
        meilleur = sub.loc[sub["life_expectancy"].idxmax()]
        moins_bon = sub.loc[sub["life_expectancy"].idxmin()]
        synthese.children.append(
            html.P(
                f"Pour l'espérance de vie, {meilleur['country']} est en tête "
                f"({_fr(meilleur['life_expectancy'])} ans) et {moins_bon['country']} en bas "
                f"({_fr(moins_bon['life_expectancy'])} ans).",
                className="mb-2",
            )
        )
    if ecart_max is not None:
        synthese.children.append(
            html.P(
                f"L'indicateur le plus dispersé dans la sélection est {ecart_max[0]} "
                f"(écart de {_fr(ecart_max[1], 1)} points de percentile).",
                className="mb-2",
            )
        )
    synthese.children.append(
        html.P(
            "Les valeurs de scolarité et d'indice de revenu peuvent être interpolées. "
            "La comparaison est descriptive et ne prouve pas de causalité.",
            className="texte-secondaire mb-0",
        )
    )

    alertes = []
    if tronques:
        alertes.append(
            dbc.Alert(
                "La comparaison est limitée à 5 pays. Pays non affichés : "
                + ", ".join(tronques)
                + ".",
                color="warning",
                className="py-2 mb-2",
            )
        )
    if pays_incomplets:
        alertes.append(
            dbc.Alert(
                "Données incomplètes pour : " + ", ".join(pays_incomplets) + ".",
                color="warning",
                className="py-2 mb-2",
            )
        )
    alertes.append(
        dbc.Alert(
            "Les scores sont relatifs à l'année sélectionnée ; ils ne mesurent pas un niveau "
            "absolu.",
            color="info",
            className="py-2 mb-2",
        )
    )
    alertes.append(
        dbc.Alert(
            "Une comparaison n'est pas une preuve de causalité.",
            color="secondary",
            className="py-2 mb-0",
        )
    )

    return (
        fig,
        _colonnes_comparateur(indicateurs),
        rows,
        synthese,
        _kpi(str(len(pays)), "Pays comparés"),
        _kpi(str(annee), "Année"),
        _kpi(str(len(indicateurs)), "Indicateurs"),
        kpi_meilleure,
        html.Div(alertes),
    )
