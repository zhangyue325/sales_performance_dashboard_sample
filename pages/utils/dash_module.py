import dash
from dash import html, dcc


def build_banner():
    return html.Div(
        className="banner",
        children=[
            html.Div(
                className="banner-text",
                children=[
                    html.H5(
                        [
                            html.B(["AI-Powered Online Sales Analytics"])
                        ], 
                        style={"margin-top":"0.2rem", "margin-bottom":"0.2rem"}),
                    html.Div(
                        [
                            html.P("Have a big picture with the\u00A0"),
                            html.P(html.B("Dashboard")),
                            html.P(". Ask detailed questions to\u00A0"),
                            html.P(html.B("AI Assistant")),
                            html.P("."),
                        ],
                        style={"display":"flex"})
                ]
            ),
            html.Div(
                className="banner-logo",
                children=[
                    html.Img(src=dash.get_asset_url("plotly_logo.avif"))
                ]
            )
        ]   
    )



def build_tabs(tabs_content):
    tab_style = {
        'borderBottom': '1px solid #d6d6d6',
        'padding': '6px',
        'fontWeight': 'bold',
        'backgroundColor': '#1e2130',
        'color': 'aliceblue'
    }
    tab_selected_style = {
        'borderTop': '3px solid #1e2130',
        'borderBottom': '1px solid #d6d6d6',
        'backgroundColor': '#f9f9f9',
        'color': '#1e2130',
        'padding': '10px'
    }

    children = []
    for k, v in tabs_content.items():
        children.append(
            dcc.Tab(
                label=k,
                value=k,
                style=tab_style,
                selected_style=tab_selected_style,
                children=[
                    html.Div(
                        className="tab-container",
                        children=v
                    )    
                ]
            )
        )

    return html.Div(
        className="tabs",
        children=dcc.Tabs(
            className="custom-tabs",
            value=next(iter(tabs_content)),
            children=children
        )
    )
