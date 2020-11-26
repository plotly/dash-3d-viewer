"""
A test application to test the performance of a minimal example that allows
slicing through a volume using a slider.
"""

import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import imageio
from dash_slicer.utils import img_array_to_uri


app = dash.Dash(__name__, update_title=None)
server = app.server

# Read volumes and create slicer objects
vol = imageio.volread("imageio:stent.npz")

slices_png = [img_array_to_uri(im) for im in vol]


##


fig = go.Figure(data=[])
fig.update_layout(
    template=None,
    margin={"l": 0, "r": 0, "b": 0, "t": 0, "pad": 4},
    dragmode="pan",  # user navigates by panning
)
fig.update_xaxes(
    showgrid=False,
    showticklabels=False,
    zeroline=False,
)
fig.update_yaxes(
    showgrid=False,
    scaleanchor="x",
    showticklabels=False,
    zeroline=False,
    range=[0, 128],
)


app.layout = html.Div(
    children=[
        html.Div(id="fps"),
        html.Br(),
        dcc.Slider(id="slider", min=0, max=256, step=1, value=128, updatemode="drag"),
        html.Br(),
        dcc.Graph(id="graph", figure=fig),
        dcc.Store(id="index", data=0),
        dcc.Store(id="data_png", data=slices_png),
    ]
)

##


app.clientside_callback(
    """
function update_index(index) {
    return index;
}
""",
    Output("index", "data"),
    [Input("slider", "value")],
)


app.clientside_callback(
    """
function update_figure(index, ori_figure, data_png) {

    // Get FPS
    let fps_result = dash_clientside.no_update;
    let now = performance.now();
    let etime = now - (window.lasttime || 0);
    if (etime > 1000) {
        let nframes = (window.framecount || 0) + 1;
        fps_result = Math.round(nframes * 1000 / etime) + " FPS";
        window.lasttime = now;
        window.framecount = 0;
    } else {
        window.framecount += 1;
    }

    // Get figure
    let figure_result = dash_clientside.no_update;

    if (true) {
        let trace = {type: 'image', source: data_png[index]};
        figure_result = {...ori_figure};
        figure_result.layout.yaxis.range = [128, 0];
        figure_result.data = [trace];
    } else {
        // unfavorable y-axis
        let trace = {type: 'image', source: data_png[index]};
        figure_result = {...ori_figure};
        figure_result.layout.yaxis.range = [0, 128];
        figure_result.data = [trace];
    }
    return [figure_result, fps_result];
}
""",
    [Output("graph", "figure"), Output("fps", "children")],
    [
        # Input("index", "data")],
        Input("slider", "value")
    ],
    [
        State("graph", "figure"),
        State("data_png", "data"),
    ],
)


if __name__ == "__main__":
    app.run_server(debug=True)
