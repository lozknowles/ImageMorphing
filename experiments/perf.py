import psutil
from dash import no_update
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import dash_cytoscape as cyto
import traceback
import os

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("System Performance Monitor", style={'textAlign': 'center'}),
    cyto.Cytoscape(
        id='system-monitor',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '600px'},
        elements=[
            {'data': {'id': 'center', 'label': 'System Monitor'}, 'position': {'x': 400, 'y': 300}},
            {'data': {'id': 'cpu', 'label': 'CPU'}, 'position': {'x': 200, 'y': 200}},
            {'data': {'id': 'memory', 'label': 'Memory'}, 'position': {'x': 600, 'y': 200}},
            {'data': {'id': 'disk', 'label': 'Disk'}, 'position': {'x': 400, 'y': 500}},
            {'data': {'source': 'center', 'target': 'cpu'}},
            {'data': {'source': 'center', 'target': 'memory'}},
            {'data': {'source': 'center', 'target': 'disk'}},
        ]
    ),
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
])

# Callback to update the node labels with current system metrics
@app.callback(Output('system-monitor', 'elements'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    try:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        
        # Use the root of the current drive
        current_drive = os.path.splitdrive(os.getcwd())[0]
        try:
            disk = psutil.disk_usage(current_drive).percent
        except Exception as disk_error:
            print(f"Error getting disk usage: {str(disk_error)}")
            disk = "N/A"

        elements = [
            {'data': {'id': 'center', 'label': 'System Monitor'}, 'position': {'x': 400, 'y': 300}},
            {'data': {'id': 'cpu', 'label': f'CPU\n{cpu}%'}, 'position': {'x': 200, 'y': 200}},
            {'data': {'id': 'memory', 'label': f'Memory\n{memory}%'}, 'position': {'x': 600, 'y': 200}},
            {'data': {'id': 'disk', 'label': f'Disk\n{disk}'}, 'position': {'x': 400, 'y': 500}},
            {'data': {'source': 'center', 'target': 'cpu'}},
            {'data': {'source': 'center', 'target': 'memory'}},
            {'data': {'source': 'center', 'target': 'disk'}},
        ]
        print(f"Updated elements: {elements}")  # Add this line for debugging
        return elements
    except Exception as e:
        print(f"Error updating metrics: {str(e)}")
        print(traceback.format_exc())
        return no_update

# Define styles for the Cytoscape component
app.layout['system-monitor'].style.update({
    'width': '100%',
    'height': '600px',
    'background-color': '#f8f9fa'
})

# Define styles for the nodes
node_style = {
    'content': 'data(label)',
    'text-valign': 'center',
    'text-halign': 'center',
    'background-color': '#6c757d',
    'color': 'white',
    'shape': 'round-rectangle',
    'width': '120px',
    'height': '60px',
    'font-size': '12px',
    'text-wrap': 'wrap'
}

app.layout['system-monitor'].stylesheet = [
    {
        'selector': 'node',
        'style': node_style
    },
    {
        'selector': 'edge',
        'style': {
            'width': 2,
            'line-color': '#6c757d'
        }
    }
]

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

