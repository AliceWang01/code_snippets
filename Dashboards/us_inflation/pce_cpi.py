from dash import Dash, html, dcc, dash_table
import pandas as pd
import plotly.express as px
from fredapi import Fred
import requests
from io import BytesIO
import plotly.graph_objects as go


def pce_cpi_layout():
    fred = Fred(api_key="d0b19bd01f39fdd7318477768791c1a9")
    df = pd.DataFrame({series: fred.get_series(series) for series in ['PCEPILFE', 'CPILFESL']})
    df = df.pct_change(12,fill_method=None) * 100 
    df['PCE, CPI YoY Wedge (Core)'] = df['PCEPILFE'] - df['CPILFESL']
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
    time_series_fig = go.Figure()
    time_series_fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Core_PCE_yoy'],
        name='Core_PCE_yoy',
        mode='lines',
        line=dict(color='red')
    ))
    time_series_fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Core_CPI_yoy'],
        name='Core_CPI_yoy',
        mode='lines',
        line=dict(color='blue')
    ))

    # Update layout for stacked bar chart
    start_date = df.index.min()
    end_date = df.index.max() 

    tickvals = pd.date_range(start=start_date, end=end_date, freq='3ME')


    time_series_fig.update_layout(
        title='Core PCE vs CPI',
        xaxis_title='Date',
        yaxis_title='Percent Change, year ago',
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            tickformat="%Y-%m"
        )
        
    )

    dist_plot_fig = px.histogram(df, x='PCE, CPI Wedge (Core)', nbins=30, title='Distribution of CPI-PCE Wedge')

    def get_web_xls(url):
        response = requests.get(url, headers = {"user-agent":"xinxianwang21@gmail.com"})
        data = BytesIO(response.content)
        return data

    dallas_trim = get_web_xls('https://www.dallasfed.org/~/media/documents/research/pce/pcehist')
    dallas_trim = pd.read_excel(dallas_trim, header=3)
    dallas_trim.columns = dallas_trim.columns.str.strip()
    dallas_trim['Unnamed: 0'] = pd.to_datetime(dallas_trim['Unnamed: 0'])
    dallas_trim = dallas_trim[dallas_trim['Unnamed: 0'].dt.year>2013]

    sf_cyc = get_web_xls('https://www.frbsf.org/wp-content/uploads/cyclical-acyclical-core-pce-data.xlsx')
    sf_cyc = pd.read_excel(sf_cyc,sheet_name='Data')
    sf_cyc['Total Core PCE (y/y)'] = sf_cyc['Cyclical core PCE contribution (y/y)'] + sf_cyc['Ayclical core PCE contribution (y/y)']
    def process_date(x):
        year, month = x.strip().split('m')  
        return f"{year}-{month.zfill(2)}" 
   
    sf_cyc['time_month'] = pd.to_datetime(sf_cyc['time_month'].apply(process_date), format='%Y-%m')
    sf_cyc = sf_cyc[sf_cyc['time_month'].dt.year>2013]
    # Create a stacked bar chart
    fig_alt = go.Figure()
    fig_alt.add_trace(go.Bar(
        x=sf_cyc['time_month'],
        y=sf_cyc['Cyclical core PCE contribution (y/y)'],
        name='SF Fed Cyclical core PCE contribution (y/y)',
        marker_color='indianred'
    ))
    fig_alt.add_trace(go.Bar(
        x=sf_cyc['time_month'],
        y=sf_cyc['Ayclical core PCE contribution (y/y)'],
        name='SF Fed Ayclical core PCE contribution (y/y)',
        marker_color='lightsalmon'
    ))
    fig_alt.add_trace(go.Scatter(
        x=sf_cyc['time_month'],
        y=sf_cyc['Total Core PCE (y/y)'],
        name='Total Core PCE (y/y)',
        mode='lines',
        line=dict(color='grey', width=2)
    ))

    fig_alt.add_trace(go.Scatter(
        x=dallas_trim['Unnamed: 0'],
        y=dallas_trim['1-month'].astype(float),
        name='Dallas Fed Trimmed Mean PCE',
        mode='lines',
        line=dict(color='rgb(0, 70, 140)')
    ))

 

    fig_alt.update_layout(
        barmode='stack',
        title='Alternative Core PCE Measures',
        xaxis_title='Date',
        yaxis_title='Percent Change, year ago',
        xaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            tickformat="%Y-%m"
        )
    )



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
        ], style={'width': '1100px'}),
        html.Div([
            dcc.Graph(
                id='time-series',
                figure=fig_alt
            )
        ], style={'width': '1250px'})
    ])
