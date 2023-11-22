import dash
from dash import Dash, dcc, html, Input, Output, State, callback

import base64

from pages.sales_dashboard.chatbot_backend import *


init_questions = [
    "show me the sales performance on 2022-11-11 for all stores using a bar chart",
    "show me the top 10 sold products in Singapore using a pie chart",
    "compare the sales performance for stores between Shopify INTL and Shopify AU",
    "break down sales by level2 category using a graph"
]

def build_tab2_content():
    return html.Div(
        children=[
            html.Div(
                id='conversation', 
                children = [build_init_conversation()],
                style={'border': '1px solid black', 'overflow': 'auto'}),
            dcc.Input(id='user-input', type='text'),
            html.Button('Send', id='send-button', n_clicks=0),
        ]
    )

def build_init_conversation():
    return html.Div(
        id="init-conversation",
        children=[
            html.Img(src=dash.get_asset_url('robotic.png'), height="50rem"),
            html.H4(html.B("How can I help you today?")),
            html.P("Please wait for the response from AI Assistant while the website tab title is 'Updating...'"),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Div(
                id="init-questions",
                children=[
                    html.P(className="init-question", id="question1", 
                           children=[init_questions[0]]),
                    html.P(className="init-question", id="question2", 
                           children=[init_questions[1]]),
                    html.P(className="init-question", id="question3", 
                           children=[init_questions[2]]),
                    html.P(className="init-question", id="question4", 
                           children=[init_questions[3]]),
                ]
            )
        ]
    )


def display_last_response_in_plotly(messages):
    messages = show_json(messages)
    with open("messages.json", 'w') as f:  #open the file in write mode
        json.dump(messages, f)
    last_response = []

    for response in messages["data"]:
        if response["role"] == "user":
            return last_response[::-1]

        response_contents = response["content"]
        for content in response_contents:
            if "text" in content:
                response_text = content["text"]["value"]
                last_response  += [html.P(f"AI Assistant: {response_text}")]
            if "image_file" in content:
                response_img_id = content["image_file"]["file_id"]
                image_data = client.files.content(response_img_id)
                image_data_bytes = image_data.read()
                encoded_image = base64.b64encode(image_data_bytes).decode('utf-8')
                last_response += [html.Img(src=f"data:image/png;base64,{encoded_image}", alt="chatbot_output_img", width="auto", height="80%")]

# Callback to update the conversation
@callback(
    Output('conversation', 'children'),
    Output('init-conversation', 'style'),
    Input('send-button', 'n_clicks'), 
    State('user-input', 'value'),
    State('conversation', 'children'),
    Input('question1', 'n_clicks'),
    Input('question2', 'n_clicks'),
    Input('question3', 'n_clicks'),
    Input('question4', 'n_clicks'),
    prevent_initial_call=True
)
def update_conversation(n_clicks, user_input, conversation_children, q1_click, q2_click, q3_click, q4_click):
    global thread
    if conversation_children is None:
        conversation_children = []

    if q1_click is not None:
        if n_clicks == 0:
            thread = create_new_thread(client)
            user_input = init_questions[0]

        add_message(client, thread, user_input)
        user_input = [html.P(f"User: {user_input}")]

        last_response = [html.P(f"You said: {user_input}")]
        run_chat(client, thread, assistant)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        last_response = display_last_response_in_plotly(messages)

    if q2_click is not None:
        if n_clicks == 0:
            thread = create_new_thread(client)
            user_input = init_questions[1]

        add_message(client, thread, user_input)
        user_input = [html.P(f"User: {user_input}")]

        run_chat(client, thread, assistant)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        last_response = display_last_response_in_plotly(messages)

    if q3_click is not None:
        if n_clicks == 0:
            thread = create_new_thread(client)
            user_input = init_questions[2]

        add_message(client, thread, user_input)
        user_input = [html.P(f"User: {user_input}")]

        run_chat(client, thread, assistant)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        last_response = display_last_response_in_plotly(messages)

    if q4_click is not None:
        if n_clicks == 0:
            thread = create_new_thread(client)
            user_input = init_questions[3]

        add_message(client, thread, user_input)
        user_input = [html.P(f"User: {user_input}")]

        run_chat(client, thread, assistant)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        last_response = display_last_response_in_plotly(messages)

    if q1_click is None and q2_click is None and q3_click is None and q4_click is None and n_clicks > 0:
        if n_clicks == 1:
            thread = create_new_thread(client)
        
        add_message(client, thread, user_input)
        user_input = [html.P(f"User: {user_input}")]

        run_chat(client, thread, assistant)
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        last_response = display_last_response_in_plotly(messages)

    return conversation_children + user_input + last_response, {'display': 'none'}