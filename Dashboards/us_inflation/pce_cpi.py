from dash import Dash, html, dcc, dash_table
import pandas as pd
import plotly.express as px
from fredapi import Fred

def pce_cpi_layout():
    fred = Fred(api_key="d0b19bd01f39fdd7318477768791c1a9")
    df = pd.DataFrame({series: fred.get_series(series) for series in ['PCEPILFE', 'CPILFESL']})
    df = df.pct_change(12,fill_method=None) * 100 
    df['PCE, CPI Wedge (Core)'] = df['PCEPILFE'] - df['CPILFESL']
    df.dropna(inplace=True)
    df = df[df.index.year > 2013]
    df.columns = ['Core_PCE_yoy', 'Core_CPI_yoy', 'PCE, CPI Wedge (Core)']

    # Format data for display
    display_df = df.copy()
    display_df = display_df.map("{:.2f}".format)  
    display_df.index = display_df.index.to_period('M').astype(str)
    display_df.reset_index(inplace=True)
    display_df.columns = ['Date', 'Core_PCE_yoy', 'Core_CPI_yoy', 'PCE, CPI Wedge (Core)']
    # Graphs and table setup
    time_series_fig = px.line(df, x=df.index, y=['Core_PCE_yoy', 'Core_CPI_yoy'], title='Time Series of Core PCE and Core CPI YoY Change')
    time_series_fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=df.index.min(),
            dtick="M3",
            tickformat="%Y-%m"
        )
    )
    time_series_fig.update_xaxes(title_text='Date')

    dist_plot_fig = px.histogram(df, x='PCE, CPI Wedge (Core)', nbins=30, title='Distribution of CPI-PCE Wedge')

    # App layout
    return html.Div([
        html.Div([
            html.Div([
                dash_table.DataTable(
                    data=display_df.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in display_df.columns],
                    page_size=12
                )
            ], style={'width': '50%', 'display': 'inline-block'}),

            html.Div([
                dcc.Graph(
                    id='dist-plot',
                    figure=dist_plot_fig
                )
            ], style={'width': '50%', 'display': 'inline-block'})
        ], style={'display': 'flex'}),

        html.Div([
            dcc.Graph(
                id='time-series',
                figure=time_series_fig
            )
        ])
    ])
