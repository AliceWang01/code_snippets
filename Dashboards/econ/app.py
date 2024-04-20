from fredapi import Fred
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd


fred = Fred(api_key="d0b19bd01f39fdd7318477768791c1a9")
df = pd.DataFrame({'Core_PCE':fred.get_series('PCEPILFE')})
