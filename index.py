"""Layout racine de l'application."""
from dash import dcc, html

import layout


def creer_layout() -> html.Div:
    return html.Div(
        [
            dcc.Location(id="url"),
            dcc.Store(id="route-active", data="/"),
            layout.creer_navbar(),
            html.Main(id="page-contenu", className="app-contenu"),
            layout.creer_footer(),
        ],
        className="application",
    )
