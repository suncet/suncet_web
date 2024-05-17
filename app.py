import dash
from dash import dcc, html, Input, Output, State
import os
import cv2
import numpy as np

app = dash.Dash(__name__)

# Sample data: list of JPEG2000 files
image_folder = 'images/'
images = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('.jp2')])

# Function to read and process images
def load_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    return img

app.layout = html.Div([
    html.H1("SunCET Interactive Movie Viewer"),
    dcc.Input(id='start-time', type='text', placeholder='Start Time'),
    dcc.Input(id='end-time', type='text', placeholder='End Time'),
    dcc.Slider(id='frame-rate', min=1, max=30, step=1, value=15, marks={i: str(i) for i in range(1, 31)}),
    html.Button('Play', id='play-button'),
    html.Button('Pause', id='pause-button'),
    html.Button('Step Forward', id='step-forward-button'),
    html.Button('Step Backward', id='step-backward-button'),
    dcc.Checklist(
        id='toggle-difference',
        options=[{'label': 'Running Difference', 'value': 'DIFF'}],
        value=[]
    ),
    dcc.Graph(id='image-display'),
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
])

@app.callback(
    Output('image-display', 'figure'),
    [Input('interval-component', 'n_intervals'),
     Input('step-forward-button', 'n_clicks'),
     Input('step-backward-button', 'n_clicks'),
     Input('toggle-difference', 'value')],
    [State('start-time', 'value'),
     State('end-time', 'value'),
     State('frame-rate', 'value')]
)
def update_image(n_intervals, step_forward, step_backward, diff_toggle, start_time, end_time, frame_rate):
    current_frame_index = n_intervals % len(images)  # Simplified cycling through images
    img = load_image(images[current_frame_index])

    if 'DIFF' in diff_toggle and current_frame_index > 0:
        prev_img = load_image(images[current_frame_index - 1])
        img = cv2.absdiff(img, prev_img)

    fig = {
        'data': [{
            'z': img,
            'type': 'heatmap',
            'colorscale': 'Gray'
        }],
        'layout': {
            'xaxis': {'visible': False},
            'yaxis': {'visible': False}
        }
    }
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
