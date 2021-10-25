import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Output, Input

import pandas as pd
import plotly.express as px

# read the data and process it for use in the control panel

data = pd.read_csv("data/timesData.csv")
data["Year"] = pd.to_datetime(data["year"], format="%Y")
data.sort_values("year", inplace=True)
# data[' index'] = range(1, len(data) + 1)


df = data.groupby(
    ['university_name', 'country', 'num_students', 'international_students'])[
    ['year']].mean()
df.reset_index(inplace=True)
pd.options.display.max_columns = len(df.columns)
df[' index'] = range(1, len(df) + 1)

# graph-01
fig = px.scatter(data, x="num_students", y="year",
                 size="year", color="country", hover_name="university_name",
                 log_x=True)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

# graph-02
figure = px.bar(data, x="country", y="num_students", color="year",
                barmode='group')

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
MENU_STYLE = {
    "margin-bottom": "25px",
}

# initialize a WSGI application with Flask (__ name__).
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=external_stylesheets)
server = app.server
app.title = "World University Rankings"

PAGE_SIZE = 25

# initialize the application and define the appearance using the application's layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🎓", className="header-emoji"),
                html.H1(
                    children="World University Dataset",
                    className="header-title"
                ),
                html.P(
                    children="Investigate the best universities in the world. "
                             "Ranking universities is a difficult, political, "
                             "and controversial practice.",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        # tab content
        html.Div([
            dcc.Tabs(
                id="tabs-with-classes",
                value='tab-2',
                parent_className='custom-tabs',
                className='custom-tabs-container',
                children=[
                    dcc.Tab(
                        label='Table',
                        value='tab-1',
                        className='custom-tab',
                        selected_className='custom-tab--selected'
                    ),
                    dcc.Tab(
                        label='Graphics',
                        value='tab-2',
                        className='custom-tab',
                        selected_className='custom-tab--selected'
                    ),
                ]),
            html.Div(id='tabs-content-classes')
        ]
        ),
    ]
)


# callbacks
@app.callback(
    Output('tabs-content-classes', 'children'),
    Input('tabs-with-classes', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('University Ranking Data'),
            dcc.Dropdown(
                id='select_page_size',
                options=[{'label': '25', 'value': 25},
                         {'label': '50', 'value': 50},
                         {'label': '100', 'value': 100}],
                value=15,
                placeholder="Please select number of rows",
            ),
            html.Div([
                dash_table.DataTable(
                    id='datatable-paging',
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    page_size=PAGE_SIZE,
                    page_current=0,
                    style_as_list_view=False,
                    style_cell={'padding': '5px', },
                    style_header={
                        'textTransform': 'uppercase',
                        'fontWeight': 'bold',
                        'backgroundColor': 'rgb(30, 30, 30)',
                        'color': 'white',
                    },
                    fill_width=False,
                    style_cell_conditional=[
                        {
                            'if': {'column_id': c},
                            'textAlign': 'left',
                        } for c in ['country', 'university_name']
                    ],
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)',
                        }
                    ],
                ),
            ]
            ),
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H4('Distribution by number of students'),
            html.Div([
                dcc.Graph(
                    id='life-exp-vs-gdp',
                    figure=fig
                )
            ]),

            html.H4('Distribution by country'),
            html.Div([
                dcc.Graph(
                    id='example-graph',
                    figure=figure
                )
            ]),
        ])


@app.callback(
    Output('datatable-paging', 'page_size'),
    [Input('select_page_size', 'value')])
def update_graph(page_size):
    return page_size


# launch the application
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=5000)
