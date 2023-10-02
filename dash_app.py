import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import subprocess

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Button('Run Python Script', id='run-button'),
    html.Div(id='output-div')
])

@app.callback(
    Output('output-div', 'children'),
    [Input('run-button', 'n_clicks')]
)
def run_python_script(n_clicks):
    if n_clicks is None:
        return ''

    # Replace with the path to your Python script
    script_path = 'scraper.py'

    # Run the Python script
    try:
        result = subprocess.check_output(['python', script_path], universal_newlines=True)
        return f'Success! Script output: {result}'
    except subprocess.CalledProcessError as e:
        return f'Error running script: {e.output}'

if __name__ == '__main__':
    app.run_server(debug=True)
