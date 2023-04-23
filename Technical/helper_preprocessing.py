
'''
This script creates dataframes from the files provided by StatsBomb
'''

# LIBRAIRIES ----------------------------------------------------
# STANDARD LIBRARIES

import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('max_colwidth', 400)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

# FUNCTIONS ----------------------------------------------------

def extract_dataframe_from_json(data_json) :
    '''
    This functions extracts several dataframes from the json file provided by StatsBomb:
    - formations_infos
    - line_up_infos
    - events_infos
    '''

    # Extract infos about formation
    formations_infos =  pd.json_normalize(data_json,record_path = ['formations'], meta = ["team_id", 'team_name'])

    # Extract infos about goals, assists and penalties
    stats_player_infos =  pd.json_normalize(data_json, record_path = ['lineup'], meta = ["team_id", 'team_name'])

    # Extract infos about line up
    line_up_infos =  pd.json_normalize(data_json,
                                        record_path = ['lineup','positions'], 
                                        meta = ["team_id", 
                                                'team_name',
                                                ['lineup','player_id'],
                                                ['lineup','player_name'],
                                                ['lineup','player_nickname'],
                                                ['lineup','birth_date'],
                                                ['lineup','player_gender'],
                                                ['lineup','player_height'],
                                                ['lineup','player_weight'],
                                                ['lineup','jersey_number'],
                                                ['lineup','country','id'],
                                                ['lineup','country','name']
                                            ]
                                        )
    stats_player_infos = stats_player_infos[['player_id','stats.own_goals',
        'stats.goals', 'stats.assists', 'stats.penalties_scored',
        'stats.penalties_missed', 'stats.penalties_saved']]

    # Add line up infos to stats infos
    df_line_up_infos = pd.merge(line_up_infos, stats_player_infos, 
                                how = 'left', 
                                left_on = "lineup.player_id",
                                right_on = "player_id")

    df_line_up_infos = df_line_up_infos.drop(columns=['lineup.player_id'])
    df_line_up_infos.columns = df_line_up_infos.columns.str.replace('lineup.', '')
    df_line_up_infos.columns = df_line_up_infos.columns.str.replace('stats.', '')

    # Extract events infos
    events_infos =  pd.json_normalize(data_json, record_path = ['events'], meta = ["team_id", 'team_name'])

    return formations_infos, df_line_up_infos, events_infos
