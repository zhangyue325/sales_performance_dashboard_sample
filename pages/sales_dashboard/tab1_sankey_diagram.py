import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, ClientsideFunction, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
from datetime import datetime, date, timedelta


sales_df = pd.read_csv("data/sales_data.csv")
sales_df.fillna("UNKNOWN", inplace = True)

def get_the_date_before(end_date, days):
    if type(end_date) == str:
        start_date = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days = days)
    else:
        start_date = end_date - timedelta(days = days)
    return start_date

def filter_data(df, start_date, end_date, countries, country_toggle, level2):
    df.fillna("UNKNOWN", inplace = True)

    # filter country data
    if country_toggle == "Display unticked countries as 'others'": 
        df.loc[~df["country"].isin(countries), "country"] = "Others"
    elif country_toggle == "Do not display unticked countries": 
        df = df[df["country"].isin(countries)]
    
    # filter level2 data
    df = df[df["level2_category"].isin(level2)]

    # filter date
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df[(df["created_at"] >= start_date) & (df["created_at"] < end_date)]

    return df

def build_tab1_sankey_diagram():
    return html.Div(
        className="data-pannel",
        id="tab1-sankey-diagram-content-panel",
        style={'display': 'none'},
        children=[
            html.Div(
                id="sankey-and-first-message",
                children = [
                    dcc.Graph(id="sankey-diagram", 
                            config={'staticPlot': False, 'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False}),
                    html.Div(children = [
                        html.H5("Click any\u00A0"),
                        html.H5("\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0", id="sample-node"),
                        html.H5(html.B("node")),
                        html.H5("\u00A0above☝️☝️ to show its detailed information."),
                    ],
                            id="first-message"),
                    html.Br(),
                    html.Br(),
                ],
            ),
            dcc.Store(id='last-clicked-node', storage_type='memory'),
            html.Br(),
            html.Div(id="clicked-node-info-container"),
            html.Br()
        ]
    )

def get_sankey_data(layers, df):
    metric = "name"

    df = df.copy()
    t = df.groupby(layers)[metric].count().reset_index()
    data = dict(
        label = [],
        source = [],
        target = [],
        value = []
    )
    for i in range(t.shape[1]-2):
        if i == 0:
            label_this_layer = t.loc[:, layers[i]].unique().tolist()
        else:
            label_this_layer = label_next_layer


        tt = t.groupby([layers[i], layers[i+1]])[metric].sum().reset_index()

        source_this_layer = [len(data["label"]) + label_this_layer.index(item) for item in tt[layers[i]].tolist()]
        data["source"] += source_this_layer

        data["label"] += label_this_layer
        label_next_layer = t.loc[:, layers[i+1]].unique().tolist()

        target_this_layer = [len(data["label"]) + label_next_layer.index(item) for item in tt[layers[i+1]].tolist()]
        data["target"] += target_this_layer

        value_this_layer = tt[metric].tolist()
        data["value"] += value_this_layer

    data["label"] += label_next_layer
    return data

@callback(
    Output('sankey-diagram', 'figure'),
    Input('layer-selection', 'value'),
    Input('date-selection', 'start_date'),
    Input('date-selection', 'end_date'),
    Input('country-selection', 'value'),
    Input('country-toggle', 'value'),
    Input('level2-selection', 'value'),
)
def build_sankey_diagram(layers, start_date, end_date, countries, country_toggle, level2):
    df = filter_data(sales_df, start_date, end_date, countries, country_toggle, level2)

    data = get_sankey_data(layers, df)
    fig = go.Figure(data = [go.Sankey(
            node = dict(
                pad = 20,
                thickness = 80,
                color = "darksalmon",
                line = dict(color = "black", width = 1.0),
                label = data["label"],
                customdata = data["label"],
            ),
            link = dict(
                source = data["source"],
                target = data["target"],
                value  = data["value"],
                customdata = data["value"],
            ),
            arrangement = 'fixed'
        )]
    )
    fig.update_layout(font_size=15, margin=dict(t=30, b=30, l=30, r=30))
    return fig

@callback(
    Output('clicked-node-info-container', 'children'),
    Input('sankey-diagram', 'clickData'),
    Input('layer-selection', 'value'),
    Input('date-selection', 'start_date'),
    Input('date-selection', 'end_date'),
    Input('country-selection', 'value'),
    Input('country-toggle', 'value'),
    Input('level2-selection', 'value'),
)
def display_node_info(clickData, layers, start_date, end_date, countries, country_toggle, level2):
    if clickData is None:
        return html.Div("")
    if 'depth' not in clickData["points"][0]:
        return html.H5(f"Please click a valid node instead of the link between nodes.")

    df = filter_data(sales_df, start_date, end_date, countries, country_toggle, level2)

    point = clickData["points"][0]
    depth = point["depth"]
    clicked_val = point["label"]
    clicked_col = layers[depth]
    
    if depth == 0:
        dimension_list = [layers[depth + 1]]
    elif depth == len(layers)-1:
        dimension_list = [layers[depth - 1]]
    else:
        dimension_list = [layers[depth - 1], layers[depth + 1]]

    return html.Div(
        children=[
            html.Div(
                children=[
                    build_clicked_layout(df, clicked_col, clicked_val, dimension_list, start_date)
                ]
            )
        ]
    )

def build_clicked_layout(df, clicked_col, clicked_val, dimension_list, start_date):
    if (dimension_list is None) or len(dimension_list) == 0:
        return html.H5("No infomation to be shown.")
    compare_end_date = datetime.strptime(start_date, "%Y-%m-%d") 
    compare_start_date = get_the_date_before(compare_end_date, 30)
    this_layer_vals = df[clicked_col].unique().tolist()
    this_layer_vals.remove(clicked_val)
    return html.Div(
        children=[
            html.Div(
                id="clicked-graph-container",
                style = {'display': 'flex', 'flexDirection': 'column', 'height': '100vh', 'width': '100%'},
                children = [
                    # title 
                    html.H5(f"break {clicked_val} orders down"),
                    html.Br(),

                    # first row 
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "10px"},
                        children = [

                            # comparison dimension
                            html.P("break down by: "),
                            dcc.Dropdown(
                                id=f"breakdown-dimention-value",
                                options=dimension_list,
                                value=dimension_list[0],
                                multi=False,
                                style={"width": "50%"}
                            ),

                            # # top 10 
                            # dcc.Checklist(
                            #     id=f"top10-selection",
                            #     options=[""],
                            #     inline=True
                            # ),
                            # html.P("   Show top 10 only"),
                        ]
                    ),

                    # comparsion with other value 
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "10px"},
                        children = [
                            dcc.Checklist(
                                id=f"compare-value-flag",
                                options=[""],
                                inline=True
                            ),
                            html.P("   Compare with another value: "), 
                            dcc.Dropdown(
                                id=f"compare-value-selection",
                                options=this_layer_vals,
                                value=this_layer_vals[0],
                                multi=False,
                                style={"width": "50%"}
                            ),
                        ]
                    ),

                    # comparsion with other date 
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "10px"},
                        children = [
                            dcc.Checklist(
                                id=f"compare-date-flag",
                                options=[""],
                                inline=True
                            ),
                            html.P("Compare with another date range: "),
                            dcc.DatePickerRange(
                                id="compare-date-selection",
                                initial_visible_month=date(compare_end_date.year, compare_end_date.month, compare_end_date.day),
                                start_date=date(compare_start_date.year, compare_start_date.month, compare_start_date.day),
                                end_date=date(compare_end_date.year, compare_end_date.month, compare_end_date.day),
                            ),
                        ]
                    ),

                    # graph
                    dcc.Graph(id=f'interactive-graph', style={'flexGrow': 1}),

                    html.Br(),
                    html.Div(id='dummy-output', style={'display': 'none'}),
                    html.H5(id='clicked-graph-bottom', 
                            children=[f"scroll down👇👇 to find or download the data."],
                            style={"text-align": "center"}),
                    html.Br(),
                    
            ]),
            # table
            html.Div(id=f'interactive-table')
        ],
    )

@callback(
    Output("interactive-graph", "figure"),
    Output("interactive-table", "children"),

    Input('sankey-diagram', 'clickData'),

    # input in control panel
    Input('layer-selection', 'value'),
    Input('date-selection', 'start_date'),
    Input('date-selection', 'end_date'),
    Input('country-selection', 'value'),
    Input('country-toggle', 'value'),
    Input('level2-selection', 'value'),

    # input above the graph
    Input('breakdown-dimention-value', 'value'),
    Input('compare-value-flag', 'value'),
    Input('compare-value-selection', 'value'), 
    Input('compare-date-flag', 'value'),
    Input('compare-date-selection', 'start_date'), 
    Input('compare-date-selection', 'end_date'), 
)
def build_parent_graph_table(clickData, layers, start_date, end_date, countries, country_toggle, level2,
                             breakdown_dimension, 
                             compare_value_flag, compare_value,
                             compare_date_flag, compare_start_date, compare_end_date):
    
    value_comparsion_not_selected = ((compare_value_flag is None) or (compare_value_flag == []))
    value_comparsion_selected = (not value_comparsion_not_selected)
    date_comparsion_not_selected = ((compare_date_flag is None) or (compare_date_flag == []))
    date_comparsion_selected = (not date_comparsion_not_selected)

    point = clickData["points"][0]
    depth = point["depth"]
    clicked_val = point["label"]
    clicked_col = layers[depth]
    compare_col = breakdown_dimension

    # the dataframe in the original data range
    df_target = filter_data(sales_df, start_date, end_date, countries, country_toggle, level2)
    df_target["date_type"] = "target data range"
    df_target = df_target[df_target[clicked_col].isin([clicked_val, compare_value])]

    # the dataframe in the compare data range
    df_compare = filter_data(sales_df, compare_start_date, compare_end_date, countries, country_toggle, level2)
    df_compare["date_type"] = "compare data range"
    df_compare = df_compare[df_compare[clicked_col].isin([clicked_val, compare_value])]

    df = pd.concat([df_target, df_compare], ignore_index = True)    
    df = df.groupby([clicked_col, "date_type", compare_col])["name"].count().reset_index()
    df = df.rename(columns={"name": "sold amount"})

    if value_comparsion_not_selected and date_comparsion_not_selected:
        df = df[(df["date_type"] == "target data range") & (df[clicked_col] == clicked_val)]
        df = df.sort_values("sold amount", ascending = False)
        fig = go.Figure([
            go.Bar(name=f"{clicked_val} between {str(start_date)} and {str(end_date)}", 
                   x=df.iloc[:,-2].tolist(), y=df.iloc[:,-1].tolist(), 
                   text=df.iloc[:,-1].tolist(), textposition='auto',
                   marker=dict(color='darksalmon')  
                   ),
                   
            ])
    elif value_comparsion_selected and date_comparsion_not_selected:
        df = df[(df["date_type"] == "target data range")]
        df = df.sort_values("sold amount", ascending = False)
        df1 = df[df[clicked_col] == clicked_val]
        df2 = df[df[clicked_col] == compare_value]
        fig = go.Figure([
            go.Bar(name=f"{clicked_val} between {str(start_date)} and {str(end_date)}", 
                   x=df1.iloc[:,-2].tolist(), y=df1.iloc[:,-1].tolist(), 
                   text=df1.iloc[:,-1].tolist(), textposition='auto',
                   marker=dict(color='darksalmon'),
                   ),
            go.Bar(name=f"{compare_value} between {str(start_date)} and {str(end_date)}", 
                   x=df2.iloc[:,-2].tolist(), y=df2.iloc[:,-1].tolist(),
                   text=df2.iloc[:,-1].tolist(), textposition='auto',
                   marker=dict(color='darkseagreen')
                   )
        ])  
    elif value_comparsion_not_selected and date_comparsion_selected:
        df = df[(df[clicked_col] == clicked_val)]
        df = df.sort_values("sold amount", ascending = False)
        df1 = df[df["date_type"] == "target data range"]
        df2 = df[df["date_type"] == "compare data range"]
        fig = go.Figure([
            go.Bar(name=f"{clicked_val} between {str(start_date)} and {str(end_date)}", 
                   x=df1.iloc[:,-2].tolist(), y=df1.iloc[:,-1].tolist(), 
                   text=df1.iloc[:,-1].tolist(), textposition='auto',
                   marker=dict(color='darksalmon')  
                   ),
            go.Bar(name=f"{clicked_val} between {str(compare_start_date)} and {str(compare_end_date)}", 
                   x=df2.iloc[:,-2].tolist(), y=df2.iloc[:,-1].tolist(), 
                   text=df2.iloc[:,-1].tolist(), textposition='auto',
                   marker=dict(color='#c5a89e') # light salmon
                   )
        ])  
    else:
        df = df.sort_values("sold amount", ascending = False)
        df1 = df[(df["date_type"] == "target data range") & (df[clicked_col] == clicked_val)]
        df2 = df[(df["date_type"] == "compare data range") & (df[clicked_col] == clicked_val)]
        df3 = df[(df["date_type"] == "target data range") & (df[clicked_col] == compare_value)]
        df4 = df[(df["date_type"] == "compare data range") & (df[clicked_col] == compare_value)]
        fig = go.Figure([
            go.Bar(name=f"{clicked_val} between {str(start_date)} and {str(end_date)}", 
                   x=df1.iloc[:,-2].tolist(), y=df1.iloc[:,-1].tolist(), 
                   text=df1.iloc[:,-1].tolist(), textposition='auto',
                   marker=dict(color='darksalmon')
                   ),
            go.Bar(name=f"{clicked_val} between {str(compare_start_date)} and {str(compare_end_date)}", 
                   x=df2.iloc[:,-2].tolist(), y=df2.iloc[:,-1].tolist(), 
                   text=df2.iloc[:,-1].tolist(), textposition='auto',
                   marker=dict(color='#c5a89e') # light salmon
                   ),
            go.Bar(name=f"{compare_value} between {str(start_date)} and {str(end_date)}", 
                   x=df3.iloc[:,-2].tolist(), y=df3.iloc[:,-1].tolist(), 
                   text=df3.iloc[:,-1].tolist(), textposition='auto',
                   marker=dict(color='darkseagreen')
                   ),
            go.Bar(name=f"{compare_value} between {str(compare_start_date)} and {str(compare_end_date)}", 
                   x=df4.iloc[:,-2].tolist(), y=df4.iloc[:,-1].tolist(), 
                   text=df4.iloc[:,-1].tolist(), textposition='auto',
                   marker=dict(color='#9dae9d') # light sea green
                   )
        ])  

    table = html.Div(
        children=[
            html.Br(),
            dash_table.DataTable(
                columns=[{"name": i, "id": i} 
                        for i in df.columns],
                data=df.to_dict('records'),
                style_cell=dict(textAlign='left'),
                style_header=dict(backgroundColor="paleturquoise"),
                style_data=dict(backgroundColor="lavender")
            ),
            
        ]

    )
    return fig, table

# Clientside callback to handle node clicks and scroll if a new node is clicked
dash.clientside_callback(
    """
    function(clickData, lastClickedNode) {
        return new Promise(resolve => {
            if (clickData) {
                const currentNode = clickData.points[0].pointNumber;
                if (lastClickedNode !== currentNode) {
                    setTimeout(() => {
                        // Find the element to scroll to
                        const element = document.getElementById('clicked-graph-bottom');
                        // Only scroll to the element if it's found
                        if (element) {
                            element.scrollIntoView({behavior: 'smooth', block: 'end'});
                        }
                        // Resolve the promise with the new node after the timeout
                        resolve(currentNode);
                    }, 200); // 1000 milliseconds = 1 second delay
                } else {
                    // If the node is the same, resolve immediately
                    resolve(lastClickedNode);
                }
            } else {
                // If clickData is null, resolve with the last clicked node or null
                resolve(lastClickedNode);
            }
        });
    }
    """,
    Output('last-clicked-node', 'data'),  # Update the store with the last clicked node's information
    [Input('sankey-diagram', 'clickData')],  # Listen to click events on the Sankey diagram
)


