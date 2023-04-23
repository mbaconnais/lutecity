'''
    This script computes technical statistics for each player such as:
    - Pass accuracy
    - Shot accuracy
    - Tackles
    - Duels
    etc.

    This script also computes physical statistics on players during the game such as: 
    - velocity
    - distance covered
    - distance covered while walking, jogging, running, sprinting,
    - number of sustained sprints, etc.
'''

# LIBRAIRIES ----------------------------------------------------
import pandas as pd
import numpy as np
import json
import warnings
from math import *
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('max_colwidth', 400)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

# Laurie Shaw package
import pages.helpers.LaurieOnTracking_package.Metrica_Velocities as mvel

# TECHNICAL STATISTICS -------------------------------------
# SHOTS -------------------------------------
def compute_total_of_shots(df_events) :
    df_shot = df_events[df_events['type_name']=="Shot"]
    df_shot = df_shot.groupby(['team_name','player_id','player_name']).size().reset_index(name='Total shots')
    
    return(df_shot)

def compute_total_of_shots_on_target(df_events) :
    df_shot_on_target = df_events[(df_events['type_name']=="Shot") & df_events['shot_outcome_name'].isin(['Goal', 'Saved'])]
    df_shot_on_target = df_shot_on_target.groupby(['team_name','player_id','player_name']).size().reset_index(name='Shots on target')

    return(df_shot_on_target)

def compute_shot_accuracy(df_shot,df_shot_on_target) :
    df_shots = pd.merge(df_shot,
                        df_shot_on_target, 
                        on =['team_name','player_id','player_name'])
    df_shots['Shot accuracy (%)'] = ((df_shots['Shots on target'] / df_shots['Total shots']) * 100).round(1)
    return(df_shots)


# OFFSIDES -------------------------------------
# Offside infringement. Cases resulting from a shot or clearance (non-pass).
# Ball reaches teammate but pass is judged offside
def compute_total_of_offsides(df_events):
    df_offsides = df_events[(df_events['type_name']=='Offside') | ((df_events['type_name']=="Pass") & (df_events['pass_outcome_name']=="Pass Offside")) ]
    df_offsides = df_offsides.groupby(['team_name','player_id','player_name']).size().reset_index(name='Offsides')
    return(df_offsides)

# CROSSES -------------------------------------
def compute_total_of_crosses(df_events): 
    df_cross = df_events[(df_events['type_name']=="Pass") & (df_events['pass_cross']==True)]
    df_cross = df_cross.groupby(['team_name','player_id','player_name']).size().reset_index(name='Total crosses')
    return(df_cross)

def compute_total_of_successfull_crosses(df_events):
    df_cross_successfull = df_events[(df_events['type_name']=="Pass") & (df_events['pass_cross']==True) &
                    (df_events['pass_outcome_name'].isnull())]
    df_cross_successfull = df_cross_successfull.groupby(['team_name','player_id','player_name']).size().reset_index(name='Total succesfull crosses')
    return(df_cross_successfull)

# PASSES -------------------------------------
# Let's remove the following events : Injury Clearance, Unknown
def compute_total_of_passes(df_events):
    df_pass = df_events[(df_events['type_name']=="Pass") &
                    ~(df_events['pass_outcome_name'].isin(["Injury Clearance", "Unknown"]))]

    df_pass = df_pass.groupby(['team_name','player_id','player_name']).size().reset_index(name='Total passes')
    return(df_pass)

def compute_total_of_succesfull_passes(df_events):
    df_pass_successfull = df_events[(df_events['type_name']=="Pass") &
                    (df_events['pass_outcome_name'].isnull())]
    df_pass_successfull = df_pass_successfull.groupby(['team_name','player_id','player_name']).size().reset_index(name='Total successfull passes')
    return(df_pass_successfull)

def compute_pass_accuracy(df_pass,df_pass_successfull):
    df_passes = pd.merge(df_pass,
                        df_pass_successfull,
                        on = ['team_name','player_name','player_id'],
                        how='left')
    df_passes = df_passes.replace(np.nan,0)
    df_passes['Pass accuracy (%)'] = (df_passes["Total successfull passes"] / (df_pass["Total passes"]) * 100).round(1)
    return(df_passes)

# FOULS -------------------------------------
def compute_total_of_fouls(df_events):
    df_fouls = df_events[df_events['type_name']=='Foul Committed']
    df_fouls = df_fouls.groupby(['team_name','player_id','player_name']).size().reset_index(name='Fouls')
    return(df_fouls)

# TACKLES -------------------------------------
def compute_total_of_tackles(df_events):
    df_tackle = df_events[(df_events['type_name']=="Duel") & (df_events['duel_type_name']=="Tackle")]
    df_tackle = df_tackle.groupby(['team_name','player_id','player_name']).size().reset_index(name='Total tackles')
    return(df_tackle)

def compute_total_of_successfull_tackles(df_events):
    df_tackle_successfull = df_events[(df_events['type_name']=="Duel") & (df_events['duel_type_name']=="Tackle") & 
                            (df_events['duel_outcome_name'].isin(['Success In Play','Won','Success Out','Success']))]
    df_tackle_successfull = df_tackle_successfull.groupby(['team_name','player_id','player_name']).size().reset_index(name='Total successfull tackles')
    return(df_tackle_successfull)

def compute_tackle_accuracy(df_tackle,df_tackle_successfull):
    df_tackles = pd.merge(df_tackle,
                        df_tackle_successfull,
                        on = ['team_name','player_name','player_id'],
                        how='left')
    df_tackles = df_tackles.replace(np.nan,0)
    df_tackles['Tackle accuracy (%)'] = (df_tackles["Total successfull tackles"] / (df_tackles["Total tackles"]) * 100).round(1)
    return(df_tackles)

# DUELS -------------------------------------
def compute_total_of_duels(df_events) : 
    df_duels = df_events[df_events['type_name']=='Duel']
    df_duels = df_duels.groupby(['team_name','player_id','player_name']).size().reset_index(name='Duels')
    return(df_duels)

def compute_total_of_successfull_duels(df_events):
    df_duels_successfull = df_events[(df_events['type_name']=="Duel")& 
                            (df_events['duel_outcome_name'].isin(['Success In Play','Won','Success Out','Success']))]
    df_duels_successfull = df_duels_successfull.groupby(['team_name','player_id','player_name']).size().reset_index(name='Total successfull duels')
    return(df_duels_successfull)

# INTERCEPTIONS -------------------------------------
def compute_total_of_interceptions(df_events):
    df_interceptions = df_events[(df_events['type_name']=='Interception') & 
                                    (df_events['interception_outcome_name'].isin(['Success In Play','Won','Success Out','Success']))]
    df_interceptions = df_interceptions.groupby(['team_name','player_id','player_name']).size().reset_index(name='Interceptions')
    return(df_interceptions)

# CLEARANCES -------------------------------------
def compute_total_of_clearances(df_events):
    df_clearances = df_events[df_events['type_name']=='Clearance']
    df_clearances = df_clearances.groupby(['team_name','player_id','player_name']).size().reset_index(name='Clearances')
    return(df_clearances)

# LOST BALLS -------------------------------------
def compute_total_of_lost_balls(df_events):
    df_lost_ball = df_events[(df_events['type_name']=='Dispossessed') | (df_events['type_name']=='Miscontrol')]
    df_lost_ball = df_lost_ball.groupby(['team_name','player_id','player_name']).size().reset_index(name='Total of lost balls')
    return(df_lost_ball)


# AGGREGATE TECHNINCAL STATISTICS -------------------------------------
def aggregate_technical_statistics(df_events) :
    df_shot = compute_total_of_shots(df_events)
    df_shot_on_target = compute_total_of_shots_on_target(df_events)
    df_shots = compute_shot_accuracy(df_shot,df_shot_on_target)
    df_offsides = compute_total_of_offsides(df_events)
    df_crosses = compute_total_of_crosses(df_events)
    df_successfull_crosses = compute_total_of_successfull_crosses(df_events)
    df_pass = compute_total_of_passes(df_events)
    df_successfull_pass = compute_total_of_succesfull_passes(df_events)
    df_passes = compute_pass_accuracy(df_pass,df_successfull_pass)
    df_fouls = compute_total_of_fouls(df_events)
    df_tackle = compute_total_of_tackles(df_events)
    df_successfull_tackle = compute_total_of_successfull_tackles(df_events)
    df_tackles = compute_tackle_accuracy(df_tackle,df_successfull_tackle)
    df_duels = compute_total_of_duels(df_events)
    df_successfull_duels = compute_total_of_successfull_duels(df_events)
    df_interceptions = compute_total_of_interceptions(df_events)
    df_clearances = compute_total_of_clearances(df_events)
    df_lost_balls = compute_total_of_lost_balls(df_events)

    df_players = df_events[~(df_events['player_id'].isnull())][['team_name','player_id','player_name']].drop_duplicates()

    list_of_df = [df_shots,df_offsides, df_crosses, df_successfull_crosses, df_passes, df_fouls, df_tackles, df_duels, 
                    df_successfull_duels, df_interceptions,df_clearances, df_lost_balls]

    for df in list_of_df :
        df_players = pd.merge(df_players,
                            df, 
                            on = ['team_name','player_id','player_name'],
                            how = 'left')
    df_players = df_players.replace(np.nan,0)

    return(df_players)


# Let's differentiate statistics based on the player's position
def differentiate_statistics(df_events, df_players, position_id) :
    defending_position = df_events[(df_events['position_id']>=2) &(df_events['position_id']<=8)]['position_id'].unique()
    middlefield_position = df_events[(df_events['position_id']>=9) &(df_events['position_id']<=20)]['position_id'].unique()
    attacking_position = df_events[(df_events['position_id']>=21)]['position_id'].unique()

    if position_id in attacking_position :
        cols_to_keep = ['team_name', 'player_id', 'player_name', 
        'Shot accuracy (%)','Pass accuracy (%)',
        'Total shots','Total of lost balls',
        'Shots on target', 'Offsides']
    elif position_id in middlefield_position :
        cols_to_keep = ['team_name', 'player_id', 'player_name', 
    'Shot accuracy (%)','Pass accuracy (%)', 
    'Tackle accuracy (%)','Total successfull tackles',
    'Interceptions','Total of lost balls']
    elif position_id in defending_position :
        cols_to_keep = ['team_name', 'player_id', 'player_name',
        'Pass accuracy (%)',
        'Total crosses',
        'Tackle accuracy (%)',
        'Interceptions', 'Clearances', 'Total of lost balls','Fouls']
    
    df_players = df_players[cols_to_keep]
    return(df_players)




# PHYSICAL STATISTICS -------------------------------------
# MINUTES PLAYED BY EACH PLAYER -------------------------------------
def calculate_minutes_played(df_tracking, teamname):
    player_columns = [c.split('_')[1] for c in df_tracking.columns if c[-2:].lower()=='_x' and c[:4] in ['Home','Away']]
    minutes = []
    for player in player_columns:
        # search for first and last frames that we have a position observation for each player (when a player is not on the pitch positions are NaN)
        column = teamname + '_' + player + '_x' # use player x-position coordinate
        last_index = df_tracking[column].last_valid_index()
        first_index = df_tracking[column].first_valid_index()
        if first_index is not None and last_index is not None: 
            player_minutes = ( last_index - first_index + 1 ) / 25 / 60. # convert to minutes
        else : 
            player_minutes = 0
        minutes.append( player_minutes )
    return(minutes)

# DISTANCE COVERED BY EACH PLAYER -------------------------------------
def calculate_total_distance_covered(df_tracking, teamname) : 
    player_columns = [c.split('_')[1] for c in df_tracking.columns if c[-2:].lower()=='_x' and c[:4] in ['Home','Away']]
    distance = []
    for player in player_columns:
        column = teamname +'_' + player + '_speed'
        player_distance = df_tracking[column].sum()/25./1000 # this is the sum of the distance travelled from one observation to the next (1/25 = 40ms) in km.
        distance.append( player_distance )
    return(distance)

# DISTANCE COVERED BY EACH PLAYER WHILE WALKING, JOGGING, RUNNING, SPRINTING -------------------------------------
def calculate_distance_in_each_speed(df_tracking, teamname) : 
    walking = []
    jogging = []
    running = []
    sprinting = []
    player_columns = [c.split('_')[1] for c in df_tracking.columns if c[-2:].lower()=='_x' and c[:4] in ['Home','Away']]
    for player in player_columns:
        column = teamname + '_' + player + '_speed'
        # walking (less than 2 m/s)
        player_distance = df_tracking.loc[df_tracking[column] < 2, column].sum()/25./1000
        walking.append( player_distance )
        # jogging (between 2 and 4 m/s)
        player_distance = df_tracking.loc[ (df_tracking[column] >= 2) & (df_tracking[column] < 4), column].sum()/25./1000
        jogging.append( player_distance )
        # running (between 4 and 7 m/s)
        player_distance = df_tracking.loc[ (df_tracking[column] >= 4) & (df_tracking[column] < 7), column].sum()/25./1000
        running.append( player_distance )
        # sprinting (greater than 7 m/s)
        player_distance = df_tracking.loc[ df_tracking[column] >= 7, column].sum()/25./1000
        sprinting.append( player_distance )
    
    return walking, jogging, running, sprinting

# SUSTAINED SPRINTS -------------------------------------
def calculate_nb_sustained_sprints(df_tracking, teamname) : 
    nsprints = []
    sprint_threshold = 7 # minimum speed to be defined as a sprint (m/s)
    sprint_window = 1*25 # minimum duration sprint should be sustained (in this case, 1 second = 25 consecutive frames)
    player_columns = [c.split('_')[1] for c in df_tracking.columns if c[-2:].lower()=='_x' and c[:4] in ['Home','Away']]
    for player in player_columns:
        column = teamname+ '_' + player + '_speed'
        # trick here is to convolve speed with a window of size 'sprint_window', and find number of occassions that sprint was sustained for at least one window length
        # diff helps us to identify when the window starts
        player_sprints = np.diff( 1*( np.convolve( 1*(df_tracking[column]>=sprint_threshold), np.ones(sprint_window), mode='same' ) >= sprint_window ) )
        nsprints.append( np.sum( player_sprints == 1 ) )

    return(nsprints)

# AGGREGATE PHYSICAL STATISTICS -------------------------------------
def aggregate_physical_statistics(df_tracking, teamsheet, teamname) : 
    df_summary = teamsheet[['jID','player']].drop_duplicates()
    df_tracking = mvel.calc_player_velocities(df_tracking,smoothing=True)
    
    minutes = calculate_minutes_played(df_tracking,teamname)
    df_summary.loc[:,'Minutes Played'] = minutes

    distance = calculate_total_distance_covered(df_tracking,teamname)
    df_summary.loc[:,'Distance [km]'] = distance

    walking, jogging, running, sprinting = calculate_distance_in_each_speed(df_tracking,teamname)
    df_summary.loc[:,'Walking [km]'] = walking
    df_summary.loc[:,'Jogging [km]'] = jogging
    df_summary.loc[:,'Running [km]'] = running
    df_summary.loc[:,'Sprinting [km]'] = sprinting

    nsprints = calculate_nb_sustained_sprints(df_tracking, teamname)
    df_summary['Number of sprints'] = nsprints

    df_summary = df_summary.round(2)
    return(df_summary)