import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, ClientsideFunction, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
from datetime import datetime, date, timedelta


key_metrics_df = pd.read_csv("data/key_metrics.csv")

def process_key_metrics_df(key_metrics_df):
    df = key_metrics_df
    df["sessions_per_user"] = df["sessions"] / df["total_users"]
    df["to_carts_per_user"] = df["add_to_carts"] / df["total_users"]
    df["checkouts_per_to_cart"] = df["checkouts"] / df["add_to_carts"]
    df["purchases_per_checkout"] = df["ecommerce_purchases"] / df["checkouts"]
    df["average_order_value"] = df["gross_purchase_revenue"] / df["ecommerce_purchases"]

    df.loc[df["property"] == "properties/319751093", "store"] = "Shopify SG"
    df.loc[df["property"] == "properties/311983201", "store"] = "Shopify AU"
    df.loc[df["property"] == "properties/309559498", "store"] = "Shopify INTL"
    df.loc[df["property"] == "properties/374182661", "store"] = "Shopify HK"
    df.loc[df["property"] == "properties/368744614", "store"] = "Shopify TW"
    return df
key_metrics_df = process_key_metrics_df(key_metrics_df)
scorecard_len = 6
metrics_list = ["sessions", "total_users", "add_to_carts", "checkouts", "ecommerce_purchases", "gross_purchase_revenue",
                "sessions_per_user", "to_carts_per_user", "checkouts_per_to_cart", "purchases_per_checkout", "average_order_value"]

def get_the_date_before(end_date, days):
    if type(end_date) == str:
        start_date = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days = days)
    else:
        start_date = end_date - timedelta(days = days)
    return datetime.strftime(start_date, "%Y-%m-%d")

def get_compare_style(v):
    if v > 0:
        return {"color": "green"}
    elif v < 0:
        return {"color": "red"}

def value_to_pct(v):
    if v == 0:
        return "-"
    return str(round(v * 100, 1)) + "%"

def scorecard_content_data(df, store, date):
    df_target = df[ (df["store"] == store) & (df["date"] == date) ].reset_index()
    df_compare = df[ (df["store"] == store) & (df["date"] == get_the_date_before(date, 1)) ].reset_index()

    def get_compare_value(col):
        target = df_target.loc[0, col]
        compare = df_compare.loc[0, col]
        if compare == 0 or compare is None or compare == "inf":
            return 0
        else:
            return (target - compare) / compare

    scorecard_content = [
        {"name":"Sessions", "value":df_target.loc[0,"sessions"], 
         "compare": value_to_pct(get_compare_value("sessions")),
         "compare_style": get_compare_style( get_compare_value("sessions") )},
        {"name":"Users", "value":df_target.loc[0,"total_users"],  
         "compare": value_to_pct(get_compare_value("total_users")),
         "compare_style": get_compare_style( get_compare_value("total_users") )},
        {"name":"Add to Carts", "value":df_target.loc[0,"add_to_carts"],  
         "compare": value_to_pct(get_compare_value("add_to_carts")),
         "compare_style": get_compare_style( get_compare_value("add_to_carts") )},
        {"name":"Checkouts", "value":df_target.loc[0,"checkouts"],  
         "compare": value_to_pct(get_compare_value("checkouts")),
         "compare_style": get_compare_style( get_compare_value("checkouts") )},
        {"name":"Purchase", "value":df_target.loc[0,"ecommerce_purchases"],  
         "compare": value_to_pct(get_compare_value("ecommerce_purchases")),
         "compare_style": get_compare_style( get_compare_value("ecommerce_purchases") )},
        {"name":"Gross Revenue", "value":round(df_target.loc[0,"gross_purchase_revenue"], 2),  
         "compare": value_to_pct(get_compare_value("gross_purchase_revenue")),
         "compare_style": get_compare_style( get_compare_value("gross_purchase_revenue") )},
    ]
    return scorecard_content


def scorecard_connection_content_data(df, store, date):
    df_target = df[ (df["store"] == store) & (df["date"] == date) ].reset_index()
    df_compare = df[ (df["store"] == store) & (df["date"] == get_the_date_before(date, 1)) ].reset_index()

    def cal_ratio(col1, col2, to_pct):
        a = df_target.loc[0,col1]
        b = df_target.loc[0,col2]
        if b == 0:
            return "-"
        if to_pct == True:
            return value_to_pct(a / b)
        elif to_pct == False:
            return round(a / b, 2)

    scorecard_content = [
        {"name": "sessions per user",  "value": cal_ratio("sessions", "total_users", False),
         "name_to_show":html.Div(className="scorecard-connection-name-container", 
                                 children = [
                                    html.P(html.B("\u2798"), style={"color":"darksalmon"}), 
                                    html.P("\u00F7"), 
                                    html.Code("sessions per user"), 
                                    html.P("\u003D"),
                                    html.P(html.B("\u279A"), style={"color":"darksalmon"}),
                                ])}, 
        {"name": "add to carts per user",  "value": cal_ratio("add_to_carts", "total_users", True),
         "name_to_show": html.Div(className="scorecard-connection-name-container", 
                                  children = [ 
                                    html.P(html.B("\u2798"), style={"color":"darksalmon"}), 
                                    html.P("\u00D7"),
                                    html.Code("to_cart per user"), 
                                    html.P("\u003D"),
                                    html.P(html.B("\u279A"), style={"color":"darksalmon"}),
                                ])}, 
        {"name": "checkouts per add to cart",  "value": cal_ratio("checkouts", "add_to_carts", True),
         "name_to_show":html.Div(className="scorecard-connection-name-container", 
                                 children = [
                                    html.P(html.B("\u2798"), style={"color":"darksalmon"}), 
                                    html.P("\u00D7"), 
                                    html.Code("checkouts per to_cart"), 
                                    html.P("\u003D"),
                                    html.P(html.B("\u279A"), style={"color":"darksalmon"}),
                                ])}, 
        {"name": "purchases per checkout",  "value": cal_ratio("ecommerce_purchases", "checkouts", True),
         "name_to_show":html.Div(className="scorecard-connection-name-container", 
                                 children = [
                                    html.P(html.B("\u2798"), style={"color":"darksalmon"}), 
                                    html.P("\u00D7"), 
                                    html.Code("perchases per checkout"), 
                                    html.P("\u003D"),
                                    html.P(html.B("\u279A"), style={"color":"darksalmon"}),
                                ])}, 
        {"name": "average order value",  "value": cal_ratio("gross_purchase_revenue", "ecommerce_purchases", False),
         "name_to_show":html.Div(className="scorecard-connection-name-container", 
                                 children = [
                                    html.P(html.B("\u2798"), style={"color":"darksalmon"}), 
                                    html.P("\u00D7"), 
                                    html.Code("average order value"), 
                                    html.P("\u003D"),
                                    html.P(html.B("\u279A"), style={"color":"darksalmon"}),
                                ])}, 
    ]
    return scorecard_content


def build_tab1_key_metrics():
    return html.Div(
        className="data-pannel",
        id="tab1-key-metrics-content-panel",
        style={'display': 'block'},
        children=[
            html.Div(id="scorecard-with-graph-container")
        ]
    )

@callback(
    Output("scorecard-with-graph-container", "children"),
    Input("key-metrics-store-selection", "value"),
    Input("key-metrics-date-selection", "date"),
    Input("key-metrics-range-selection", "value"),   
)
def build_scorecards_with_graph(store, date, date_range):
    scorecard_content = scorecard_content_data(key_metrics_df, store, date)
    scorecard_connection_content = scorecard_connection_content_data(key_metrics_df, store, date)
    
    children = []
    for i in range(scorecard_len):
        s = scorecard_content[i]
        children.append(
            html.Div(id=f"scorecard-{i+1}", className="scorecard", children=
                        [
                            html.H5(f"{s.get('name')}"),
                            html.H4(html.B(f"{s.get('value')}")),
                            html.P(f"{s.get('compare')}", style = s.get("compare_style")),
                        ])
        )
    return html.Div(
        id="key-matrics-and-graph-container",
        children=[
            html.Div(className=f"grid-container-{len(scorecard_content)}", children=children),
            design_scorecard_connection(scorecard_connection_content),
            dcc.Graph(id="responsible-graph")
        ]
    )

def design_scorecard_connection(scorecard_connection_content):
    children = []

    i=1
    for c in scorecard_connection_content:
        children.append(html.Div(
            className="connection-content",
            id=f"connection-content-{i}",
            children = [
                html.P(c.get("name_to_show")),
                html.B(c.get("value")),
            ]
        ))
        i+=1

    return html.Div(
        className="scorecard-content-connection-container",
        children=children,
    )

@callback(
    [Output('responsible-graph', 'figure')] + \
    [Output(f'scorecard-{i+1}', 'style') for i in range(scorecard_len)] + \
    [Output(f'connection-content-{i+1}', 'style') for i in range(scorecard_len-1)],
    [Input(f'scorecard-{i+1}', 'n_clicks') for i in range(scorecard_len)] +\
    [Input(f'connection-content-{i+1}', 'n_clicks') for i in range(scorecard_len-1)] +\
    [Input("key-metrics-store-selection", "value"), Input("key-metrics-date-selection", "date"), Input("key-metrics-range-selection", "value")]
)
def update_responsible_graph(*args):
    # Default styles for scorecards
    default_style = {'cursor': 'pointer'}
    clicked_style = {'backgroundColor': '#eaeaea'}

    ctx = dash.callback_context

    selected_store = args[-3]
    selected_date = args[-2]
    selected_date_range = args[-1]
    selected_date_range = selected_date_range.split(" ")[0]
    selected_date_range = int(selected_date_range)
    args = args[:-3]

    not_clicked = True
    for sc in args:
        if sc != 0:
            not_clicked = False

    def get_styles(i):
        styles = [default_style] * (scorecard_len * 2 - 1)
        styles[i-1] = clicked_style
        return styles

    # If no scorecard was clicked
    if not ctx.triggered or not_clicked:
        return tuple([build_metrics_graph(key_metrics_df, selected_store, selected_date, selected_date_range, metrics_list[0])] + get_styles(1))
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    for i in range(scorecard_len):
        if button_id == f"scorecard-{i+1}":
            return tuple([build_metrics_graph(key_metrics_df, selected_store, selected_date, selected_date_range, metrics_list[i])] + get_styles(i+1))
        if button_id == f"connection-content-{i+1}":
            return tuple([build_metrics_graph(key_metrics_df, selected_store, selected_date, selected_date_range, metrics_list[scorecard_len + i])] +\
                          get_styles( scorecard_len+(i+1) ))

def build_metrics_graph(df, selected_store, selected_date, selected_date_range, col):
    df_target = df[(df["store"] == selected_store) & (df["date"] <= selected_date)].sort_values(by = "date", ascending = False)
    df_target = df_target[["date", col]]
    df_target = df_target.head(selected_date_range)
    x = df_target["date"].values
    y = df_target[col].values

    fig = go.Figure()
    if selected_date_range <= 30:
        fig.add_trace(go.Scatter(x=x, y=y, text=[round(e, 2) for e in y], mode='lines+text', textposition='bottom center', line_shape='spline', line_color='darksalmon'))
        fig.update_layout(
            title = f"{col} in {selected_date_range} days",
            margin=dict(t=50, b=30, l=50, r=50))
    else:
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_shape='spline', line_color='darksalmon'))
        fig.update_layout(
            title = f"{col} in {selected_date_range} days",
            margin=dict(t=50, b=30, l=50, r=50))
    return fig    

if __name__ == "__main__":
    d = scorecard_content_data(key_metrics_df, "Shopify AU", "2023-11-19")

