from dash import Dash, html, dcc
from pce_cpi import pce_cpi_layout
from testtab import testtab_layout
from testtab2 import testtab_layout2
app = Dash(__name__)
server = app.server
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='PCE/CPI Analysis', children=pce_cpi_layout()),
        dcc.Tab(label='Test tab', children=testtab_layout()),
        dcc.Tab(label='Test tab2', children=testtab_layout2()),
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
