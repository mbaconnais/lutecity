#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    File name: match_analysis.py
    Use: Script relative to the Match Analysis part of the app
    Author: Lutecity (Melanie Baconnais & Chloe Gobe) 
    Date created: 04/2023
    Python Version: 3.10.4
"""

##############################################################
#                       IMPORTS
##############################################################
# LIBRAIRIES ----------------------------------------------------
import pandas as pd
import numpy as np
import json
from datetime import datetime
from math import *
import os
from floodlight.io.secondspectrum import read_position_data_jsonl, read_teamsheets_from_meta_json

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('max_colwidth', 400)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

# GRAPHIC LIBRAIRIES----------------------------------------------------
# Dash
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH
from dash import dash_table

# Plotly
import plotly.graph_objs as go
import plotly as plotly

# LOCAL LIBRARIES ----------------------------------------------------
from app import app
from pages.helpers import helpers_processing, helpers_graph, helpers_statistics

##############################################################
#                       DATA LOADING 
##############################################################
# STATSBOMB INFOS ----------------------------------------------------
# LINEUP INFOS ----------------------------------------------------
mancity_arsenal_lineup_path = os.path.join(os.getcwd(),'assets/Data/StatsBomb/ManCity_Arsenal_lineups.json')
with open(mancity_arsenal_lineup_path, encoding='utf-8') as f:
    data_json_line_up = json.load(f)
    
formations_infos, df_line_up_infos, events_infos = helpers_processing.extract_dataframe_from_json(data_json_line_up)
df_line_up_home = df_line_up_infos[(df_line_up_infos['team_name'] == 'Manchester City WFC')]
df_line_up_away = df_line_up_infos[~(df_line_up_infos['team_name'] == 'Manchester City WFC')]
df_formation_home = formations_infos[(formations_infos['reason'] == "Starting XI") & 
                                    (formations_infos['team_name'] == 'Manchester City WFC')]
df_formation_away = formations_infos[(formations_infos['reason'] == "Starting XI") & 
                                    ~(formations_infos['team_name'] == 'Manchester City WFC')]
formation_home = str(df_formation_home['formation'].values[0])
formation_away = str(df_formation_away['formation'].values[0])

df_home = helpers_graph.create_df_line_up_stat(formation_home,df_line_up_home, events_infos,type = 'home')
df_away = helpers_graph.create_df_line_up_stat(formation_away,df_line_up_away, events_infos,type = 'away')
df_line_up = pd.concat([df_home, df_away])
df_line_up = helpers_graph.add_emojis_to_events(df_line_up)

df_substitutes_home =  df_line_up[~(df_line_up['from']==0) & 
                                    (df_line_up['team_name'] == 'Manchester City WFC')]
df_substitutes_away =  df_line_up[~(df_line_up['from'] == 0) & 
                                    ~(df_line_up['team_name'] == 'Manchester City WFC')].sort_values(by = 'from')

# EVENTS INFOS ----------------------------------------------------
mancity_arsenal_events_path = os.path.join(os.getcwd(),'assets/Data/StatsBomb/ManCity_Arsenal_events.json')
with open(mancity_arsenal_events_path, encoding='utf-8') as f:
    data_json_events = json.load(f)
    df_events = pd.json_normalize(data_json_events, sep = "_")

# TECHNICAL INFOS ----------------------------------------------------
df_cumulative_vaep_path = os.path.join(os.getcwd(),'assets/Data/arsenal_game_cumulative_vaep.csv')
df_cumulative_vaep = pd.read_csv(df_cumulative_vaep_path,sep=',', encoding = "utf-8-sig")

df_mean_vaep_path = os.path.join(os.getcwd(),'assets/Data/other_games_grouped_cumulative_vaep.csv')
df_mean_vaep = pd.read_csv(df_mean_vaep_path,sep=',', encoding = "utf-8-sig")

df_substitution_vaep_path = os.path.join(os.getcwd(),'assets/Data/vaep_rating_on_previous_games_per_positions.csv')
df_substitution_vaep = pd.read_csv(df_substitution_vaep_path,sep=',', encoding = "utf-8-sig")

# SECOND SPECTRUM INFOS ----------------------------------------------------
df_tracking_home_path = os.path.join(os.getcwd(),'assets/Data/tracking_home.csv')
df_tracking_home = pd.read_csv(df_tracking_home_path,sep=';', encoding = "utf-8-sig")

df_tracking_away_path = os.path.join(os.getcwd(),'assets/Data/tracking_away.csv')
df_tracking_away = pd.read_csv(df_tracking_away_path,sep=';', encoding = "utf-8-sig")

filepath_metadata = os.path.join(os.getcwd(),'assets/Data/Second_Spectrum/g2312135_SecondSpectrum_meta.json')
teamsheet = read_teamsheets_from_meta_json(filepath_metadata)
teamsheet_home = teamsheet['Home']
teamsheet_home['player'] = teamsheet_home['player'].str.replace("Angeldahl","Angeldal")
teamsheet_away = teamsheet['Away']

# METABOLIC POWER INFOS ----------------------------------------------------
metabolic_power_home_path = os.path.join(os.getcwd(),'assets/Data/metabolic_power_home.csv')
metabolic_power_home = pd.read_csv(metabolic_power_home_path,sep=";", encoding = "utf-8-sig")

metabolic_power_away_path = os.path.join(os.getcwd(),'assets/Data/metabolic_power_away.csv')
metabolic_power_away = pd.read_csv(metabolic_power_away_path,sep=";", encoding = "utf-8-sig")

##############################################################
#                       GRAPHICAL SET UP
##############################################################
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": '47%',
    "bottom": 0,
    "width": "54%",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "overflow-y": "auto",
    "transition": "all 0.5s",
    "padding": "0.5rem 1rem",
    "background-color": "whitesmoke",
}

SIDEBAR_HIDDEN = {
    "position": "fixed",
    "top": 62.5,
    "left": "-16rem",
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "z-index": 1,
    "overflow-x": "hidden",
    "transition": "all 0.5s",
    "padding": "0rem 0rem",
    "background-color": "whitesmoke",
}
##############################################################
#                       DASH
##############################################################
def generate_line_substitute(time, jersey, player_name, yellow_card, red_card, goals, className):
    if yellow_card != yellow_card :
        yellow_card = ""
    if red_card != red_card :
        red_card = ""
    div = html.P(str(time) + "' " + str(jersey) + '. ' + player_name + " " + str(goals)+ " "+ yellow_card + " " + red_card,className=className)
    return div

match_analysis_content = html.Div(
    [
        dcc.Store(id='side_click',storage_type='session'),

        html.Div(
            [
                html.Div(
                    [
                        html.Img(src=app.get_relative_path('/assets/Images/logo_mancity.png'),className="logo_football_club"),
                        html.H4("Manchester City vs Arsenal", className="app__header__title"),
                        html.Img(src=app.get_relative_path('/assets/Images/logo_arsenal.png'),className="logo_football_club"),
                    ], className="app__header__desc",
                ),
                
                html.Div(
                    [
                        html.P("Score: 2 - 1"),
                    ],className = 'center_flex_container'
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [    
                                        generate_line_substitute(time, jersey, player_name, yellow_card, red_card, goals, className = "substitutes_away") 
                                        for time, jersey, player_name, yellow_card, red_card, goals in zip(df_substitutes_away['from'], 
                                                        df_substitutes_away['jersey_number'],df_substitutes_away['player_name'], 
                                                        df_substitutes_away['Yellow Card'],df_substitutes_away['Red Card'], 
                                                        df_substitutes_away['goals'])
                                    ]
                                ),

                                html.Div(
                                    [

                                    ], style = {'height' : '25vh'}
                                ), 
                                html.Div(
                                    [    
                                        generate_line_substitute(time, jersey, player_name, yellow_card, red_card, goals, className = "substitutes_home") 
                                        for time, jersey, player_name, yellow_card, red_card, goals in zip(df_substitutes_home['from'], 
                                                        df_substitutes_home['jersey_number'],df_substitutes_home['player_name'], 
                                                        df_substitutes_home['Yellow Card'],df_substitutes_home['Red Card'], 
                                                        df_substitutes_home['goals'])
                                    ] 
                                ),
                            ], className = 'left_flex_container_pitch'
                        ),

                        html.Div(
                            [
                                dcc.Loading(
                                    children=[
                                        dcc.Graph(
                                            id = 'pitch-graph', 
                                            figure = helpers_graph.plot_line_up_on_pitch(df_line_up), 
                                            responsive=True,
                                            config={
                                                'displayModeBar': False,
                                                'displaylogo': False,
                                                'autosizable': False, 
                                                'doubleClick':False,
                                                'responsive' :True,
                                                'scrollZoom' :False,
                                                'showAxisDragHandles' : False,
                                            },
                                        ),
                                    ],
                                    type="circle",
                                    color='#5db7d3',
                                    fullscreen = False,
                                ),
                            ], className = 'right_flex_container_pitch'
                        )
                    ]
                )
            ],className = 'left_flex_container'
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(id = 'player_name'),
                                
                                dbc.Button(
                                    html.Span(
                                        [
                                            html.Div(children  =["\U000003A7"])
                                        ]
                                    ), className="xmark_sidebar_show",
                                    id = 'xmark_sidebar'
                                ),              
                            ]
                        ),
                        
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.Div(
                                                                    [
                                                                        # NAME
                                                                        html.P('Age',className = 'athlete_infos_item'),
                                                                        html.P(id='player_age',className = 'athlete_infos__text'),
                                                                    ],
                                                                    className="athlete_info_container",
                                                                ),

                                                                html.Div(
                                                                    [
                                                                        # COUNTRY
                                                                        html.P('Country',className = 'athlete_infos_item'),
                                                                        html.P(id='player_country',className = 'athlete_infos__text'),
                                                                    ],className="athlete_info_container",
                                                                ),
                                                            ],className="athlete_info_container",
                                                        ),

                                                        html.Div(
                                                            [
                                                                html.Div(
                                                                    [
                                                                        # HEIGHT
                                                                        html.P('Height',className = 'athlete_infos_item'),
                                                                        html.P(id='player_height',className = 'athlete_infos__text'),
                                                                    ],
                                                                    className="athlete_info_container",
                                                                ),

                                                                html.Div(
                                                                    [
                                                                        # WEIGHT
                                                                        html.P('Weight',className = 'athlete_infos_item'),
                                                                        html.P(id='player_weight',className = 'athlete_infos__text'),
                                                                    ],
                                                                    className="athlete_info_container",
                                                                ),
                                                            ],className="athlete_info_container",
                                                        ),

                                                        html.Div(
                                                            [
                                                                html.Div(
                                                                    [
                                                                        # POSITION
                                                                        html.P('Position',className = 'athlete_infos_item'),
                                                                        html.P(id='player_position',className = 'athlete_infos__text'),
                                                                    ], className="athlete_info_container",
                                                                ),

                                                                html.Div(
                                                                    [
                                                                        # JERSEY NUMBER
                                                                        html.P('Jersey number',className = 'athlete_infos_item'),
                                                                        html.P(id='player_jersey_number',className = 'athlete_infos__text')
                                                                    ],className="athlete_info_container",
                                                                ),
                                                            ], className="athlete_info_container",
                                                        )
                                                    ],className='athlete_infos_container',
                                                ),
                                            ],className = 'flex_content_transparent'
                                        ),
                                    ]
                                )
                            ]
                        ),

                        html.Br(),

                        # TECHNICAL PART
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.P("Technical analysis", id='technical-title'),
                                                            ], className = "flex_content_transparent"
                                                        ),

                                                        html.Div(
                                                            [
                                                                dcc.Loading(
                                                                    id = 'loading-technical-graph',
                                                                    children=[
                                                                        dcc.Graph(
                                                                            id = 'technical-graph', 
                                                                            config={
                                                                                'displayModeBar': False,
                                                                                'displaylogo': False,
                                                                                'autosizable': False, 
                                                                                'doubleClick':False,
                                                                                'responsive' :True,
                                                                                'scrollZoom' :False,
                                                                                'showAxisDragHandles' : False,
                                                                            },
                                                                        )
                                                                    ],
                                                                    type="circle",
                                                                    fullscreen = False,
                                                                ),
                                                            ],className = 'left_flex_container_stats'
                                                        ),

                                                        html.Div(
                                                            [
                                                            
                                                                html.Div(
                                                                    id = 'technical_stats'
                                                                ),
                                                            ],className = 'right_flex_container_stats'
                                                        )
                                                    ]
                                                )
                                            ], className="flex_content_transparent"
                                        )
                                        
                                    ]
                                )
                            ]
                        ),

                        html.Br(),

                        # PHYSICAL PART
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                html.P("Physical analysis", id='physical-title'),
                                            ], className = "flex_content_transparent"
                                        ),

                                        html.Div(
                                            [
                                                dcc.Loading(
                                                    id= 'loading-physical-graph',
                                                    children=[
                                                        dcc.Graph(
                                                            id = 'physical-graph', 
                                                            config={
                                                                'displayModeBar': False,
                                                                'displaylogo': False,
                                                                'autosizable': False, 
                                                                'doubleClick':False,
                                                                'responsive' :True,
                                                                'scrollZoom' :False,
                                                                'showAxisDragHandles' : False,
                                                            },
                                                        )
                                                    ],
                                                    type="circle",
                                                    fullscreen = False,
                                                ),
                                            ],className = 'left_flex_container_stats'
                                        ),

                                        html.Div(
                                            [
                                            
                                                html.Div(
                                                    id = 'physical_stats'
                                                ),
                                            ],className = 'right_flex_container_stats'
                                        )
                                    ]
                                )
                            ]
                        ),

                        html.Br(),

                        # SUBSTITUTION PART
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                html.P("Recommended substitution", id='substitution-title'),
                                            ], className = "flex_content_transparent"
                                        ),

                                        

                                        html.Div(
                                            [
                                                html.Div(
                                                    id = 'possible_substitution'
                                                ),
                                            ],className = 'flex_content_transparent'
                                        )
                                    ]
                                )
                            ]
                        ),

                    
                    ],style = {'display' : "none"},
                    id = 'show-sidebar'
                    
                ),
            ],className = 'right_flex_container'
        ),


        #FOOTER
        html.Div(
            [
                html.Div(
                    [
                        html.P('© Lutecity, 2023')
                    ],
                    className="footer_text",
                )
            ],
            className="footer_container",
        ),
    ]
)

def match_analysis():
    layout = html.Div(
        [
            match_analysis_content
        ]
    )
    return layout


##############################################################
#                       CALLBACK
##############################################################
# SHOW SIDEBAR WITH INDIVIDUAL STATS --------------------------------
@app.callback(
    [
        Output(component_id="show-sidebar", component_property="style"),
        Output(component_id="side_click", component_property="data"),
    ],
    [
        Input(component_id = 'pitch-graph', component_property = 'clickData'),
        Input(component_id = "xmark_sidebar", component_property="n_clicks")
    ],
    [
        State(component_id = "side_click", component_property="data")
    ]

)
def display_left_part(clickData,n_xmark,nclick):
    if not clickData:
        raise dash.exceptions.PreventUpdate
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"]

    x_clickData = clickData['points'][0]['x']
    y_clickData = clickData['points'][0]['y']
    df_line_up_player = df_line_up[(df_line_up['x_coord']==x_clickData) & (df_line_up['y_coord']==y_clickData)]
    position = df_line_up_player['position'].unique()[0]

    if input_id == "pitch-graph.clickData" : 
        sidebar_style = SIDEBAR_STYLE
        cur_nclick = "HIDDEN"
    
    if n_xmark : 
        if nclick == "SHOW":
            sidebar_style = {'display' : 'none'}
            cur_nclick = "HIDDEN"
        else : 
            sidebar_style = SIDEBAR_STYLE
            cur_nclick = "SHOW"
    else : 
        sidebar_style = SIDEBAR_STYLE
        cur_nclick = "SHOW"
    
    if position == 'Goalkeeper' : 
        sidebar_style = {'display' : 'none'}
        cur_nclick = "SHOW"
    return sidebar_style, cur_nclick



# DISPLAY PLAYER'S INFOS --------------------------------
@app.callback(
    [
        Output(component_id = 'player_name', component_property = 'children'),
        Output(component_id = 'player_name', component_property = 'className'),
        Output(component_id = 'player_age', component_property = 'children'),
        Output(component_id = 'player_country', component_property = 'children'),
        Output(component_id = 'player_height', component_property = 'children'),
        Output(component_id = 'player_weight', component_property = 'children'),
        Output(component_id = 'player_position', component_property = 'children'),
        Output(component_id = 'player_jersey_number', component_property = 'children'),
        Output(component_id = 'technical-title', component_property = 'className'),
        Output(component_id = 'physical-title', component_property = 'className'),
        Output(component_id = 'substitution-title', component_property = 'className'),
        Output(component_id = 'loading-technical-graph', component_property = 'color'),
        Output(component_id = 'loading-physical-graph', component_property = 'color'),
    ],
    [
        Input(component_id = 'pitch-graph', component_property = 'clickData')
    ]
)
def display_player_infos(clickData):
    if not clickData:
        raise dash.exceptions.PreventUpdate

    # Access the player infos depending of each click on graph
    x_clickData = clickData['points'][0]['x']
    y_clickData = clickData['points'][0]['y']
    df_line_up_player = df_line_up[(df_line_up['x_coord']==x_clickData) & (df_line_up['y_coord']==y_clickData)]
    player_id = df_line_up_player['player_id'].iloc[0]
    df_line_up_infos_player = df_line_up_infos[df_line_up_infos['player_id']==player_id]
    
    # Team
    team = df_line_up_infos_player['team_name'].iloc[0]

    # Player name
    player_name = df_line_up_infos_player['player_name'].iloc[0]
    player_jersey_number = str(df_line_up_infos_player['jersey_number'].iloc[0])
    if team == "Arsenal WFC" :
        player_name_style = "text_arsenal"
    else :
        player_name_style = "text_mancity"

    # Age
    player_birth_date = df_line_up_infos_player['birth_date'].iloc[0]
    if pd.isnull(player_birth_date):
        player_age = ""
    else: 
        player_birth_date = datetime.strptime(player_birth_date,"%Y-%m-%d")
        match_date = datetime.strptime("2023-11-02", "%Y-%m-%d")
        player_age = format(np.round((match_date - player_birth_date).days/365.2425,1), '.0f')

    # Country
    player_country = df_line_up_infos_player['country.name'].iloc[0]

    # Height
    player_height = df_line_up_infos_player['player_height'].iloc[0]
    if player_height != player_height :
        player_height = format(player_height,'.0f') + " cm"
    else :
        player_height = "-"

    # Weight
    player_weight = df_line_up_infos_player['player_weight'].iloc[0]
    if player_weight != player_weight :
        player_weight = format(player_weight,'.0f') + " cm"
    else :
        player_weight = "-"

    # Position
    player_position = df_line_up_infos_player['position'].iloc[0]

    # Loading color
    if team == "Arsenal WFC" :
        color = "#d52e22"
    else :
        color = "#5db7d3"
    return player_jersey_number + ". " +player_name, player_name_style, player_age, player_country, player_height, player_weight, player_position,player_jersey_number,player_name_style,player_name_style,player_name_style, color, color


# DISPLAY VAEP GRAPH --------------------------------
@app.callback(
    Output(component_id = 'technical-graph', component_property = 'figure'),
    [
        Input(component_id = 'pitch-graph', component_property = 'clickData')
    ]
)
def display_vaep_graph(clickData):
    if not clickData:
        raise dash.exceptions.PreventUpdate

    # Access the player infos depending of each click on graph
    x_clickData = clickData['points'][0]['x']
    y_clickData = clickData['points'][0]['y']
    df_line_up_player = df_line_up[(df_line_up['x_coord']==x_clickData) & (df_line_up['y_coord']==y_clickData)]
    player_id = df_line_up_player['player_id'].iloc[0]
    position = df_line_up_player['position'].unique()[0]

    df_cumulative_vaep_player = df_cumulative_vaep[df_cumulative_vaep['player_id']==player_id]
    df_mean_vaep_player = df_mean_vaep[df_mean_vaep['player_id']==player_id]

    if position == 'Goalkeeper' :
        graph = helpers_graph.return_blank_fig(figure_height=20)
    else :
        graph = helpers_graph.create_vaep_graph(df_cumulative_vaep_player, df_mean_vaep_player)
    return graph 

# DISPLAY PLAYER'S TECHNICAL STATS --------------------------------
@app.callback(
    Output(component_id = 'technical_stats', component_property = 'children'),
    [
        Input(component_id = 'pitch-graph', component_property = 'clickData')
    ]
)
def display_technical_stats(clickData):
    if not clickData:
        raise dash.exceptions.PreventUpdate

    # Access the player infos depending of each click on graph
    x_clickData = clickData['points'][0]['x']
    y_clickData = clickData['points'][0]['y']
    df_line_up_player = df_line_up[(df_line_up['x_coord']==x_clickData) & (df_line_up['y_coord']==y_clickData)]
    player_id = df_line_up_player['player_id'].iloc[0]
    df_line_up_infos_player = df_line_up_infos[df_line_up_infos['player_id']==player_id]
    position = df_line_up_player['position'].unique()[0]
    player_position_id = df_line_up_infos_player['position_id'].unique()[0]

    if position == 'Goalkeeper' : 
        div = []
    else :
        # Compute_statistics
        df_events_sub = df_events[df_events['player_id']==player_id]
        df_stats = helpers_statistics.aggregate_technical_statistics(df_events_sub)
        df_player = helpers_statistics.differentiate_statistics(df_events_sub, df_stats, player_position_id)
        
        df_player = df_player[df_player.columns[~df_player.columns.isin(['team_name', 'player_id', 'player_name'])]]
        
        div_left, div_right = [], []
        for col_index in range(len(df_player.columns)) :
            col = df_player.columns[col_index]
            if col_index % 2 == 0 :
                div_left.append(
                    html.Div(
                        [
                            html.P(col,className = 'athlete_infos_item'),
                            html.P(df_player.loc[:,col],className = 'athlete_infos__text'),
                        ],className="athlete_info_container",
                    )
                )
            else : 
                div_right.append(
                    html.Div(
                        [
                            html.P(col,className = 'athlete_infos_item'),
                            html.P(df_player.loc[:,col],className = 'athlete_infos__text'),
                        ],className="athlete_info_container",
                    )
                )
        div = html.Div(
            [
                html.Div(
                    div_left,
                    className="athlete_info_container"
                ),
                html.Div(
                    div_right,
                    className="athlete_info_container"
                ),
            ],className = "athlete_infos_container"
        )
    return div


# DISPLAY METABOLIC POWER GRAPH --------------------------------
@app.callback(
    Output(component_id = 'physical-graph', component_property = 'figure'),
    [
        Input(component_id = 'pitch-graph', component_property = 'clickData')
    ]
)
def display_metabolic_power_graph(clickData):
    if not clickData:
        raise dash.exceptions.PreventUpdate

    # Access the player infos depending of each click on graph
    x_clickData = clickData['points'][0]['x']
    y_clickData = clickData['points'][0]['y']
    df_line_up_player = df_line_up[(df_line_up['x_coord']==x_clickData) & (df_line_up['y_coord']==y_clickData)]
    player_id = df_line_up_player['player_id'].iloc[0]
    df_line_up_infos_player = df_line_up_infos[df_line_up_infos['player_id']==player_id]
    team_name = df_line_up_infos_player['team_name'].unique()[0]
    position = df_line_up_player['position'].unique()[0]

    if team_name == "Manchester City WFC" :
        df_teamsheet = teamsheet_home
        df_metabolic_power = metabolic_power_home
        teamname = 'Home'
    else :
        df_teamsheet = teamsheet_away
        df_metabolic_power = metabolic_power_away
        teamname = 'Away'

    id_second_spectrum = helpers_graph.extract_from_second_spectrum_id(df_line_up_infos, df_teamsheet, player_id)
    df_metabolic_power = df_metabolic_power[['Period','Time_sec','official_clock',teamname +'_'+str(id_second_spectrum)+"_Metabolic_power"]]
    metabolic_power = df_metabolic_power[df_metabolic_power['Time_sec'] > 3000][teamname +'_'+str(id_second_spectrum)+"_Metabolic_power"]
    list_threshold = helpers_graph.find_fatigue_threshold(metabolic_power)

    if position == 'Goalkeeper' :
        graph = helpers_graph.return_blank_fig(figure_height=20)
    else :
        graph = helpers_graph.create_metabolic_power_graph(df_metabolic_power, list_threshold,team_name)
    return graph 

# DISPLAY PLAYER'S PHYSICAL STATS --------------------------------
@app.callback(
    Output(component_id = 'physical_stats', component_property = 'children'),
    [
        Input(component_id = 'pitch-graph', component_property = 'clickData')
    ]
)
def display_physical_stats(clickData):
    if not clickData:
        raise dash.exceptions.PreventUpdate

    # Access the player infos depending of each click on graph
    x_clickData = clickData['points'][0]['x']
    y_clickData = clickData['points'][0]['y']
    df_line_up_player = df_line_up[(df_line_up['x_coord']==x_clickData) & (df_line_up['y_coord']==y_clickData)]
    player_id = df_line_up_player['player_id'].iloc[0]
    df_line_up_infos_player = df_line_up_infos[df_line_up_infos['player_id']==player_id]
    team_name = df_line_up_infos_player['team_name'].unique()[0]
    jersey_number = df_line_up_infos_player['jersey_number'].unique()[0]
    position = df_line_up_player['position'].unique()[0]

    if position == 'Goalkeeper' :
        div = []
    else:
        if team_name == "Manchester City WFC" :
            df_stats = helpers_statistics.aggregate_physical_statistics(df_tracking_home, teamsheet_home, 'Home')
        else :
            df_stats = helpers_statistics.aggregate_physical_statistics(df_tracking_away, teamsheet_away, 'Away')

        # Compute_statistics        
        df_player = df_stats[df_stats['jID']==jersey_number]
        df_player = df_player.drop(columns = ['jID','player'])

        div_left, div_right = [], []
        for col_index in range(len(df_player.columns)) :
            col = df_player.columns[col_index]
            if col_index % 2 == 0 :
                div_left.append(
                    html.Div(
                        [
                            html.P(col,className = 'athlete_infos_item'),
                            html.P(df_player.loc[:,col],className = 'athlete_infos__text'),
                        ],className="athlete_info_container",
                    )
                )
            else : 
                div_right.append(
                    html.Div(
                        [
                            html.P(col,className = 'athlete_infos_item'),
                            html.P(df_player.loc[:,col],className = 'athlete_infos__text'),
                        ],className="athlete_info_container",
                    )
                )
        div = html.Div(
            [
                html.Div(
                    div_left,
                    className="athlete_info_container"
                ),
                html.Div(
                    div_right,
                    className="athlete_info_container"
                ),
            ],className = "athlete_infos_container"
        )
    return div

# DISPLAY POSSIBLE SUBSTITUTION --------------------------------
@app.callback(
    Output(component_id = 'possible_substitution', component_property = 'children'),
    [
        Input(component_id = 'pitch-graph', component_property = 'clickData')
    ]
)
def display_technical_stats(clickData):
    if not clickData:
        raise dash.exceptions.PreventUpdate

    # Access the player infos depending of each click on graph
    x_clickData = clickData['points'][0]['x']
    y_clickData = clickData['points'][0]['y']
    df_line_up_player = df_line_up[(df_line_up['x_coord']==x_clickData) & (df_line_up['y_coord']==y_clickData)]
    player_id = df_line_up_player['player_id'].iloc[0]
    df_line_up_infos_player = df_line_up_infos[df_line_up_infos['player_id']==player_id]
    player_position_name = df_line_up_infos_player['position'].unique()[0]
    
    if player_position_name == 'Goalkeeper' :
        div = []

    else : 
        df_substitution_vaep_position = df_substitution_vaep[df_substitution_vaep['position']==player_position_name] 
        df_substitution_vaep_position = df_substitution_vaep_position.sort_values(by='vaep_rating_per_mn_played', ascending = False)

        div_left = [
            html.Div(
                [
                    html.P('Player',className = 'athlete_infos__text_substitution'),
                    html.P(' ',className = 'athlete_infos__text_substitution'),
                ],className="athlete_info_container",
            )
        ]
                
        div_right = [
            html.Div(
                [
                    html.P('Technical efficiency per 90min',className = 'athlete_infos__text_substitution'),
                ],className="athlete_info_container",
            )
        ]

        for i in range(len(df_substitution_vaep_position )) :
            player_name = df_substitution_vaep_position.iloc[i,:]['player_name']
            vaep = df_substitution_vaep_position.iloc[i,:]['vaep_rating_per_mn_played'].round(2)
            
            div_left.append(
                html.Div(
                    [
                        html.P(player_name,className = 'athlete_infos_item_substitution'),
                    ],className="athlete_info_container",
                )
            )

            div_right.append(
                html.Div(
                    [
                        html.P(vaep,className = 'athlete_infos_item_substitution'),
                    ],className="athlete_info_container",
                )
            )
        
        div = html.Div(
            [
                html.Div(
                    div_left,
                    className="athlete_info_container"
                ),
                html.Div(
                    div_right,
                    className="athlete_info_container"
                ),
            ],className = "athlete_infos_container"
        )
    return div
