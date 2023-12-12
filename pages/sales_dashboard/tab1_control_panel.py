import dash
from dash import html, dcc

from datetime import datetime, date, timedelta


def get_the_date_before(end_date, days):
    if type(end_date) == str:
        start_date = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days = days)
    else:
        start_date = end_date - timedelta(days = days)
    return start_date



def build_tab1_control_pannel(df):

    return html.Div(
        className="control-pannel",
        children=[
            html.Br(),
            html.H5(html.B("What You Want To See?")),
            dcc.RadioItems(
                id="tab1-content-selection",
                options=["Key Metrics", "Sankey Diagram"],
                value= "Sankey Diagram",
                inline=True
            ),
            html.Hr(),
            build_key_metrics_control_panel(df),
            build_sankey_diagram_control_panel(df)
        ]
    )


def build_key_metrics_control_panel(df):
    TODAY = datetime.today() 
    start_date_in_selection = get_the_date_before(TODAY, 1)

    return html.Div(
        id="key-metrics-control-pannel",
        style={"display":"block"},
        children=[
            html.H5(html.B("Key Metrics Controller")),
            html.Br(),
            html.P(html.B("Store Selection")),
            dcc.Dropdown(
                id='key-metrics-store-selection',
                options=["Shopify SG", "Shopify INTL", "Shopify AU", "Shopify TW", "Shopify HK"],
                value="Shopify SG"
            ),
            html.Br(),  
            html.P(html.B("Date Selection")),
            dcc.DatePickerSingle(
                id='key-metrics-date-selection',
                initial_visible_month=date(2023, 11, 20),
                date=date(2023, 11, 20),
                # initial_visible_month=date(start_date_in_selection.year, start_date_in_selection.month, start_date_in_selection.day),
                # date=date(start_date_in_selection.year, start_date_in_selection.month, start_date_in_selection.day),
            ),
            html.Br(),  
            html.Br(), 
            html.P(html.B("Date Range in Graph")),
            dcc.Dropdown(
                id='key-metrics-range-selection',
                options=["7 days", "30 days", "90 days", "365 days"],
                value="30 days"
            ),
            html.Br(),  
        ]
    )

def build_sankey_diagram_control_panel(df):
    COUNTRY_LIST = sorted(df["country"].unique().tolist())
    LEVEL2_LIST = df["level2_category"].unique().tolist()

    # TODAY = datetime.today() 
    TODAY = date(2023, 11, 20)
    start_date_in_selection = get_the_date_before(TODAY, 30)

    return html.Div(
        id="sankey-diagram-control-pannel",
        style={"display":"block"},
        children=[
            html.H5(html.B("Sankey Diagram Controller")),
            html.Br(),
            html.P(html.B("Sankey Diagram Layers")),
            dcc.Dropdown(
                id="layer-selection",
                options=["country", "store", "level2_category", "level3_category"],
                value=["country", "store", "level2_category"],
                multi=True,
            ),
            html.Br(),
            html.P(html.B("Date Filter")),
            dcc.DatePickerRange(
                id='date-selection',
                initial_visible_month=date(TODAY.year, TODAY.month, TODAY.day),
                start_date=date(start_date_in_selection.year, start_date_in_selection.month, start_date_in_selection.day),
                end_date=date(TODAY.year, TODAY.month, TODAY.day)
            ),
            html.Br(),
            html.Br(),
            html.P(html.B("Country Filter")),
            dcc.Dropdown(
                id="country-selection",
                options=COUNTRY_LIST,
                value= ["Singapore", "Australia", "New Zealand" , "Indonesia", "United States", "Philippines", "Hong Kong", "Taiwan", "Malaysia", "Brunei"],
                multi=True,
            ),
            dcc.RadioItems(
                id="country-toggle",
                options=["Display unticked countries as 'others'", "Do not display unticked countries"],
                value= "Do not display unticked countries"
            ),
            html.Br(),
            html.P(html.B("Level2 Category Filter")),
            dcc.Dropdown(
                id="level2-selection",
                options=LEVEL2_LIST,
                value= LEVEL2_LIST,
                multi=True,
            ),
            html.Br(),
            html.Br(),
        ]
    )
