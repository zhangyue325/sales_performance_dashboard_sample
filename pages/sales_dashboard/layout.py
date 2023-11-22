import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, ClientsideFunction, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

from pages.utils.dash_module import build_banner, build_tabs
from pages.sales_dashboard.tab1_control_panel import build_tab1_control_pannel
from pages.sales_dashboard.tab1_key_metrics import build_tab1_key_metrics
from pages.sales_dashboard.tab1_sankey_diagram import build_tab1_sankey_diagram
from pages.sales_dashboard.tab2_content_panel import build_tab2_content

dash.register_page(__name__, path='/', title="Sales Analysis")

sales_df = pd.read_csv("data/sales_data.csv")
sales_df.fillna("UNKNOWN", inplace = True)


tabs_content = {
    "Dashboard":[build_tab1_control_pannel(sales_df), build_tab1_key_metrics(), build_tab1_sankey_diagram()], 
    "AI Assistant":[build_tab2_content()],
    }

@callback(
    Output('key-metrics-control-pannel', 'style'),
    Output('tab1-key-metrics-content-panel', 'style'),
    Output('sankey-diagram-control-pannel', 'style'),
    Output('tab1-sankey-diagram-content-panel', 'style'),
    [Input('tab1-content-selection', 'value')],
)
def toggle_visibility(selected_option):
    if selected_option == 'Key Metrics':
        return {'display': 'block'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
    elif selected_option == 'Sankey Diagram':
         return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'}


layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        build_tabs(tabs_content)
    ]
)
