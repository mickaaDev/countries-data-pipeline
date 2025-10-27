import os
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv



load_dotenv()

def get_database_connection():
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_name = os.getenv('POSTGRES_DB')
    db_host = 'localhost'
    db_port = os.getenv('POSTGRES_PORT')
    
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(connection_string)

def load_countries_data():
    engine = get_database_connection()
    query = "SELECT * FROM countries"
    return pd.read_sql(query, engine)

app = Dash(__name__)

df = load_countries_data()

df['population'] = df['population'].apply(lambda x: f"{x:,}")
df['area'] = df['area'].apply(lambda x: f"{x:,}")



app.layout = html.Div([

    html.H1('Countries Dashboard', style={'textAlign': 'center', 'marginBottom': 30}),
    
    html.Div([
        dcc.Dropdown(
            id='region-filter',
            options=[{'label': region, 'value': region} for region in sorted(df['region'].unique())],
            placeholder='Filter by Region',
            style={'width': '50%', 'margin': '10px'}
        )
    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
    
    html.Div([
        html.Div([
            html.H3('Countries Data'),
            dash_table.DataTable(
                id='countries-table',
                page_size=15,
                page_action='native',
                sort_action='native',
                sort_mode='multi',
                filter_action='native',
                row_selectable='single', 
                selected_rows=[0],  
                style_table={
                    'overflowX': 'auto',
                    'minWidth': '100%'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'minWidth': '100px',
                    'maxWidth': '300px',
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_header={
                    'backgroundColor': 'lightgrey',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data={
                    'border': '1px solid lightgrey'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    },
                    {
                        'if': {'state': 'selected'},
                        'backgroundColor': 'rgb(0, 116, 217)',
                        'color': 'white'
                    }
                ]
            )
        ], style={'width': '70%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.H3('Country Flag', style={'textAlign': 'center'}),
            html.Div(id='flag-display', style={
                'textAlign': 'center',
                'padding': '20px',
                'border': '2px solid #ddd',
                'borderRadius': '10px',
                'margin': '10px',
                'minHeight': '200px',
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'justifyContent': 'center'
            }),
            html.Div(id='country-info', style={
                'textAlign': 'center',
                'marginTop': '20px',
                'padding': '15px',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '5px'
            })
        ], style={'width': '28%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '2%'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    
    html.Div([
        html.H3('Population Distribution by Region'),
        dcc.Graph(id='population-chart')
    ])
])

@callback(
    Output('countries-table', 'data'),
    Output('countries-table', 'columns'),
    Output('population-chart', 'figure'),
    Output('flag-display', 'children'),
    Output('country-info', 'children'),
    Input('region-filter', 'value'),
    Input('countries-table', 'selected_rows')
)
def update_dashboard(selected_region, selected_rows):
    if selected_region: filtered_df = df[df['region'] == selected_region].copy()
    else: filtered_df = df.copy()
    
    engine = get_database_connection()

    numeric_df = pd.read_sql("SELECT region, population::numeric,    area::numeric FROM countries", engine)
    pop_df = numeric_df.groupby('region')['population'].sum().reset_index()
    
    fig = px.bar(pop_df, x='region',  y = 'population', 
                 title='Total Population by Region',
                 labels={'population':  'Population', 'region': 'Region'},
                 color='population',
                 color_continuous_scale= 'viridis')
    fig.update_layout(showlegend=False)
    
    table_data = filtered_df.to_dict('records')
    table_columns = [
        {"name": "Country", "id": "country"},
        {"name": "Capital", "id": "capital"},
        {"name": "Region", "id": "region"},
        {"name": "Subregion", "id": "subregion"},
        {"name": "Population", "id": "population"},
        {"name": "Area (km)", "id": "area"}
    ]
    
    if selected_rows and len(selected_rows) > 0:
        selected_index = selected_rows[0]
        if selected_index < len(table_data):

            selected_country = table_data[selected_index]
            flag_url = selected_country['flag_url'] if 'flag_url' in selected_country else filtered_df.iloc[selected_index]['flag_url']
            
            flag_display = html.Div([
                html.Img(
                    src=flag_url,
                    style={
                        'width': '200px' ,
                        'height': '120px',
                        'border': '2px solid #333',
                        'borderRadius': '5px',
                        'boxShadow': '0 4px 8px rgba(0,0,0,0.2)'
                    }
                )
            ])
            



            country_info = html.Div([
                html.H4(selected_country['country'], style={'marginBottom': '10px', 'color': '#333'}),
                html.P(f"Capital: {selected_country['capital']}", style={'margin': '5px 0'}),
                html.P(f"Region: {selected_country['region']}", style={ 'margin': '5px 0'}),
                html.P(f"Population: {selected_country['population']}", style={'margin': '5px 0'}),
                html.P(f"Area: {selected_country[ 'area']} km²", style={'margin': '5px 0'})


            ])
        else:
            flag_display = html.P('No country selected', style={'color': '#666'})
            country_info = html.P("Select a country from table", style={'color': '#666'})
    else:

        flag_display = html.P("No country selected", style={'color': '#666'})
        country_info = html.P("Select a country from the table", style={'color': '#666'})
    
    return table_data, table_columns, fig, flag_display, country_info



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)