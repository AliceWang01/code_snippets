from dash import html
from dash import dash_table
import requests
import pandas as pd
from io import StringIO
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")


def cpi_layout():
    def get_bls_txt(url):
        response = requests.get(url, headers = {"user-agent":"xinxianwang21@gmail.com"})
        data = StringIO(response.text)
        df = pd.read_csv(data, sep='\t',low_memory=False)
        df.columns = df.columns.str.strip()
        return df

    def order_df(df, list, mapping_df):
        '''Orders a pivot table based on series id list'''
        df = df[df['series_id'].isin(list)]
        df = df.pivot_table(values='value', columns = 'date', index='series_id').reindex(list)
        df = df.merge(mapping_df, on='series_id', how='left')
        df = df.set_index('series_title')
        df = df.drop('series_id',axis=1)
        return df

    ## get series id and value df
    index_url = 'https://download.bls.gov/pub/time.series/cu/cu.data.0.Current'
    df = get_bls_txt(index_url)
    df['month'] = df['period'].str.extract(r'(\d{2})')[0]
    df = df[(df['month'] != '13') & (df['year'] > 2012)].reset_index()
    df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'], format='%Y-%m')
    df['series_id'] = df['series_id'].str.strip()
    df = df[['date', 'series_id', 'value']]

    ## get series id and names mapping
    name_url = 'https://download.bls.gov/pub/time.series/cu/cu.series'
    name_df = get_bls_txt(name_url)
    name_df = name_df[['series_id','series_title']]
    name_df['series_id'] = name_df['series_id'].str.strip()


    sa_ids = [
        'CUSR0000SA0',  # All items
        'CUSR0000SAF1',  # Food
        'CUSR0000SAF11',  # Food at home
        'CUSR0000SEFV',  # Food away from home
        'CUSR0000SA0E',  # Energy
        'CUSR0000SA0L1E',  # All items less food and energy
        'CUSR0000SACL1E',  # Commodities less food and energy commodities
        'CUSR0000SAA',  # Apparel
        'CUSR0000SETA01',  # New vehicles
        'CUSR0000SETA02',  # Used cars and trucks
        'CUSR0000SAM1',  # Medical care commodities
        'CUSR0000SAF116', # Alcoholic Beverages
        'CUSR0000SEGA',  # Tobacco and smoking products
        'CUSR0000SASLE', # Services less Energy Services
        'CUSR0000SAH1',  # Shelter
        'CUSR0000SEHA',  # Rent of primary residence
        'CUSR0000SEHC',  # Owners' equivalent rent of residences
        'CUSR0000SAM2',  # Medical care services
        'CUSR0000SEMC01',  # Physicians' services
        'CUSR0000SEMD01',  # Hospital services
        'CUSR0000SAS4',  # Transportation services
        'CUSR0000SETD',  # Motor vehicle maintenance and repair
        'CUSR0000SETE',  # Motor vehicle insurance
        'CUSR0000SETG01'  # Airline fares
    ]

    sa_df = order_df(df, sa_ids, name_df)
    sa_df.index = sa_df.index.str.replace(" in U.S. city average, all urban consumers, seasonally adjusted", "", regex=False)
    sa_df_clean = sa_df.T
    sa_df_clean = sa_df_clean.pct_change(fill_method=None)*100
    sa_df_clean = sa_df_clean.iloc[-13:].sort_index(ascending=False)
    sa_df_clean.index = pd.to_datetime(sa_df_clean.index).to_period('M')
    sa_df_clean.loc['3m-MA'] = sa_df_clean.iloc[0:3].mean()
    sa_df_clean.loc['6m-MA'] = sa_df_clean.iloc[0:6].mean()
    new_order = ['3m-MA', '6m-MA'] + [row for row in sa_df_clean.index if row not in ['3m-MA', '6m-MA']]
    sa_df_clean = sa_df_clean.loc[new_order]

    columns_not_to_round = ['All items less food and energy']

    rounding_dict = {col: 1 for col in sa_df_clean.columns if col not in columns_not_to_round}
    for col in columns_not_to_round:
        rounding_dict[col] = 2

    sa_df_clean = sa_df_clean.round(rounding_dict)
    sa_df_clean = sa_df_clean.astype(object).T
    sa_df_clean = sa_df_clean.reset_index()
    sa_df_clean.columns =  sa_df_clean.columns.astype(str)

    return html.Div([html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in sa_df_clean.columns],
            data=sa_df_clean.to_dict('records'),
            style_table={'height': '300px', 'overflowX': 'auto'},
            style_data_conditional=[
                {
                'if': {
                    'filter_query': '{series_title} = "All items less food and energy"',
                },
                'backgroundColor': 'yellow',
                'color': 'black'
                }
            ]
         )
    ])
        ])