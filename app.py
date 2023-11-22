import dash
from dash import Dash, html
import dash_auth


app = Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}],
    use_pages=True
    )

app.title = "Sales Analytics"
server = app.server
app.config.suppress_callback_exceptions = True



app.layout = html.Div(
    dash.page_container
)

if __name__ == '__main__':
    app.run(debug=True)