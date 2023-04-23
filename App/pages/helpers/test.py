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
import helpers_processing, helpers_graph, helpers_statistics

##############################################################
#                       DATA LOADING 
##############################################################
# STATSBOMB INFOS ----------------------------------------------------
# LINEUP INFOS ----------------------------------------------------
mancity_arsenal_lineup_path = os.path.join(os.getcwd(),'assets/Data/StatsBomb/ManCity_Arsenal_lineups.json')
with open(mancity_arsenal_lineup_path, encoding='utf-8') as f:
    data_json_line_up = json.load(f)
    
formations_infos, df_line_up_infos, events_infos = helpers_processing.extract_dataframe_from_json(data_json_line_up)
# df_line_up_home = df_line_up_infos[(df_line_up_infos['team_name'] == 'Manchester City WFC')]
# df_line_up_away = df_line_up_infos[~(df_line_up_infos['team_name'] == 'Manchester City WFC')]
# df_formation_home = formations_infos[(formations_infos['reason'] == "Starting XI") & 
#                                     (formations_infos['team_name'] == 'Manchester City WFC')]
# df_formation_away = formations_infos[(formations_infos['reason'] == "Starting XI") & 
#                                     ~(formations_infos['team_name'] == 'Manchester City WFC')]
# formation_home = str(df_formation_home['formation'].values[0])
# formation_away = str(df_formation_away['formation'].values[0])

# df_home = helpers_graph.create_df_line_up_stat(formation_home,df_line_up_home, events_infos,type = 'home')
# df_away = helpers_graph.create_df_line_up_stat(formation_away,df_line_up_away, events_infos,type = 'away')
# df_line_up = pd.concat([df_home, df_away])
# df_line_up = helpers_graph.add_emojis_to_events(df_line_up)

# df_substitutes_home =  df_line_up[~(df_line_up['from']==0) & 
#                                     (df_line_up['team_name'] == 'Manchester City WFC')]
# df_substitutes_away =  df_line_up[~(df_line_up['from'] == 0) & 
#                                     ~(df_line_up['team_name'] == 'Manchester City WFC')].sort_values(by = 'from')

# # EVENTS INFOS ----------------------------------------------------
# mancity_arsenal_events_path = os.path.join(os.getcwd(),'assets/Data/StatsBomb/ManCity_Arsenal_events.json')
# with open(mancity_arsenal_events_path, encoding='utf-8') as f:
#     data_json_events = json.load(f)
#     df_events = pd.json_normalize(data_json_events, sep = "_")

# # TECHNICAL INFOS ----------------------------------------------------
# df_cumulative_vaep_path = os.path.join(os.getcwd(),'assets/Data/arsenal_game_cumulative_vaep.csv')
# df_cumulative_vaep = pd.read_csv(df_cumulative_vaep_path,sep=',', encoding = "utf-8-sig")

# df_mean_vaep_path = os.path.join(os.getcwd(),'assets/Data/other_games_grouped_cumulative_vaep.csv')
# df_mean_vaep = pd.read_csv(df_mean_vaep_path,sep=',', encoding = "utf-8-sig")

# df_substitution_vaep_path = os.path.join(os.getcwd(),'assets/Data/vaep_rating_on_previous_games_per_positions.csv')
# df_substitution_vaep = pd.read_csv(df_substitution_vaep_path,sep=',', encoding = "utf-8-sig")

# SECOND SPECTRUM INFOS ----------------------------------------------------
df_tracking_home_path = os.path.join(os.getcwd(),'assets/Data/tracking_home.csv')
df_tracking_home = pd.read_csv(df_tracking_home_path,sep=';', encoding = "utf-8-sig")

df_tracking_away_path = os.path.join(os.getcwd(),'assets/Data/tracking_away.csv')
df_tracking_away = pd.read_csv(df_tracking_away_path,sep=';', encoding = "utf-8-sig")

filepath_metadata = os.path.join(os.getcwd(),'assets/Data/Second_Spectrum/g2312135_SecondSpectrum_meta.json')
teamsheet = read_teamsheets_from_meta_json(filepath_metadata)

teamsheet_home = teamsheet['Home']
teamsheet_away = teamsheet['Away']
# print(df_tracking_home)

# 
# print(df_stats)



player_id = 4637


# id_second_spectrum = extract_from_second_spectrum_id(df_line_up_infos, df_teamsheet, player_id)