"""Point d'entrée de l'application Dazzle Dash."""
import dash_bootstrap_components as dbc
from dash import Dash

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    title="Dazzle Dash",
)
server = app.server

import index
import callbacks

app.layout = index.creer_layout()
callbacks.enregistrer_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
