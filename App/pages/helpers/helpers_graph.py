'''
    This script is creates a football Pitch with the following infos:
    - Line up
    - Yellow and red cards
    - Goals
    - Substitutions
'''

# LIBRAIRIES ----------------------------------------------------
# STANDARD LIBRARIES
import pandas as pd
import warnings
import numpy as np
from datetime import datetime
import math
import ruptures as rpt
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('max_colwidth', 400)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

# GRAPHIC LIBRAIRIES----------------------------------------------------
# Plotly
import plotly.graph_objs as go
import plotly_football_pitch as pfp


# FUNCTIONS ----------------------------------------------------
def return_blank_fig(figure_height=20):
    '''
    Return a "blank" figure.
    '''    
    fig = go.Figure()
    # Set axes properties
    fig.update_xaxes(
        #range=[-1, 3],
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        #range=[-1, 3],
        showticklabels=False,
        showgrid=False,
        zeroline=False,
    )
    
    # Set figure size
    fig.update_layout(
        #width=800,
        height=figure_height,
        plot_bgcolor="white")
    return fig

def create_x_coord_line_up(nb_player_per_line, pitch_width = 68) : 
    '''
    This function creates the Xs coordinates as a list depending on the number of players per line
    in the line up
    '''
    x_coord =  [i*pitch_width/nb_player_per_line + (pitch_width/nb_player_per_line)/2 for i in range(0,nb_player_per_line)]
    return(x_coord)

def create_y_coord_line_up(nb_of_lines, pitch_length = 105) : 
    '''
    This function creates the Ys coordinates as a list depending on the number of lines in the line up
    '''
    yards_to_meters = 1.09361
    y_penalty_box = 18/yards_to_meters
    y_penalty_spot = (2 * y_penalty_box) /3
    length_mid_pitch = pitch_length/2 - y_penalty_spot - pitch_length /10
    y_coord =  [y_penalty_spot] + [y_penalty_spot +  i*length_mid_pitch/nb_of_lines for i in range(1,nb_of_lines+1)]
    return(y_coord)  

def create_lineup_based_on_formation(formation) :
    '''
    This functions associates the formation with the position's lineup
    '''
    if formation == '433' : 
        lineup = [
            ['Goalkeeper'],
            ['Left Back', 'Left Center Back','Right Center Back', 'Right Back'],
            ['Left Center Midfield','Center Defensive Midfield', 'Right Center Midfield'],
            ['Left Wing', 'Center Forward', 'Right Wing'],
        ]

    elif formation == '343' :
        lineup = [
            ['Goalkeeper'],
            ['Left Center Back', 'Center Back', 'Right Center Back'],
            ['Left Wing Back', 'Left Defensive Midfield', 'Right Defensive Midfield', 'Right Wing Back'],
            ['Left Wing','Center Forward', 'Right Wing'],
        ]

    elif formation == '4141' :
        lineup = [
            ['Goalkeeper'],
            ['Left Back', 'Left Center Back', 'Right Center Back','Right Back'],
            ['Center Defensive Midfield'],
            ['Left Midfield','Left Center Midfield','Right Center Midfield', 'Right Midfield'],
            ['Center Forward'],
        ]

    elif formation == '4231':
        lineup = [
            ['Goalkeeper'],
            ['Left Back', 'Left Center Back', 'Right Center Back','Right Back'],
            ['Left Defensive Midfield','Right Defensive Midfield'],
            ['Left Wing','Center Attacking Midfield','Right Wing'],
            ['Center Forward'],
        ]

    elif formation == '442' :
        lineup = [
            ['Goalkeeper'],
            ['Left Back','Left Center Back', 'Right Center Back', 'Right Back'], 
            ['Left Midfield', 'Left Defensive Midfield',  'Right Defensive Midfield', 'Right Midfield'],
            ['Left Center Forward', 'Right Center Forward'], 
        ]

    elif formation == '4411' :
        lineup = [
            ['Goalkeeper'],
            ['Left Back', 'Left Center Back', 'Right Center Back','Right Back'],
            ['Left Midfield','Left Defensive Midfield','Right Defensive Midfield', 'Right Midfield'],
            ['Center Attacking Midfield'],
            ['Center Forward'],
        ]

    elif formation == '3412':
        lineup = [
            ['Goalkeeper'],
            ['Left Wing Back','Left Defensive Midfield','Right Defensive Midfield', 'Right Wing Back'],
            ['Right Center Back','Center Back','Left Center Back'],
            ['Center Attacking Midfield'],
            ['Left Center Forward', 'Right Center Forward'],
        ]
    
    return(lineup)

def create_df_line_up_stat(formation,df_line_up, events_infos,type) :
    '''
    This function create a dataframe with the following informations:
    - id_player, Player_name
    - goals, yellow cards, red cards, 
    - position, position_id, x_coord, y_coord,
    -counter_part_id, counterpart_name (substitutes)
    '''
    pitch_width = 68
    list_of_lines = list(map(int, str(formation)))

    # Change player_name to nickname 
    df_line_up['player_name'] = np.where(df_line_up['player_nickname'].isnull(), df_line_up['player_name'], df_line_up['player_nickname'])

    df_line_up_starting_xi = df_line_up[(df_line_up['start_reason'] == "Starting XI")]
    df_line_up_substitute = df_line_up[(df_line_up['start_reason'].str.contains("Substitution"))]

    y_coord = create_y_coord_line_up(nb_of_lines = len(list_of_lines), pitch_length = 105)
    x_coord = [[pitch_width /2]] + [create_x_coord_line_up(nb_player_per_line = int(line), pitch_width = 68) for line in list_of_lines]
    y_coord = [[y] * len(x) for x,y in zip(x_coord, y_coord)]
    positions = create_lineup_based_on_formation(formation)

    data_pos = [list(zip(position,x,y)) for x,y, position in zip(x_coord,y_coord,positions)] 
    df_pos = pd.DataFrame([t for lst in data_pos for t in lst], columns = ['position','x_coord','y_coord'])
    if type == 'away' :
        df_pos['y_coord'] = 105 - df_pos['y_coord'] 

    # Add player's infos on pitch
    df_starting_xi = pd.merge(df_pos, 
                df_line_up_starting_xi[['from_period','from','team_id','team_name','position', 'position_id','player_id','player_name','jersey_number','counterpart_id','counterpart_name','goals']],
                how = 'left',
                on = 'position'
    )

    # Infos about substitutes will be added on the bottom and top part of the graph.
    # We create Xs and Ys coordinates for each substitute.
    df_substitute = df_line_up_substitute[['from_period','from','team_id','team_name','position', 'position_id','player_id','player_name','jersey_number','goals']]
    n_substitutes = len(df_substitute)
    yoffset_substitutes = [i*2 for i in range(1,n_substitutes+1)]
    df_substitute['y_coord'] = yoffset_substitutes
    df_substitute['x_coord'] = [0] * n_substitutes

    df = pd.concat([df_starting_xi, df_substitute])

    # Add the fouls committed
    df_fouls = events_infos[events_infos['outcome'].str.contains('Card',na=False)]
    df_fouls = df_fouls.groupby(['player_id','outcome']).size().reset_index(name= 'counts')
    df_fouls = df_fouls.pivot(index='player_id', columns='outcome', values='counts').reset_index()

    df = pd.merge(df, 
                df_fouls[['player_id'] + list(df_fouls.columns[df_fouls.columns.str.contains('Card')].values)],
                how = 'left',
                left_on = 'player_id',
                right_on = 'player_id'
    )

    # Change time format
    df['from'] = df['from'].apply(lambda x: math.ceil((datetime.strptime(x, '%H:%M:%S.%f') - datetime(1900,1,1)).total_seconds() /60))
    df['from_format'] = np.where(df['from_period'] == 1,
                                np.where(df['from'] > 45,
                                        df['from'].apply(lambda x: str(45) + "'+" + str(x - 45)),
                                        df['from'].astype(str)
                                ), 
                                np.where(df['from'] > 90,
                                        df['from'].apply(lambda x: str(90) + "'+" + str(x - 90)),
                                        df['from'].astype(str)
                                ),
                            )
    df = df[['from_format','from', 'team_id','team_name','player_id', 'jersey_number','player_name','goals'] + list(df.columns[df.columns.str.contains('Card')].values) + ['position', 'position_id','x_coord', 'y_coord', 'counterpart_id', 'counterpart_name']]
    
    if not 'Yellow Card' in df.columns :
        df['Yellow Card'] = np.nan

    if not 'Red Card' in df.columns :
        df['Red Card'] = np.nan
    return(df)

def add_emojis_to_events(df_line_up_stat) :
    '''
    This function is a graphical function. Emojis are added for specific events such as goals, card and substitutes.
    '''
    goals = {1 : "\U000026BD", 0 : ""}
    df_line_up_stat['goals'] = df_line_up_stat['goals'].replace(goals, regex=True)
    
    yellow_cards = {1 : "\U0001F7E8", 0 : "", 2 :  "\U0001F7E8\U0001F7E8"}
    df_line_up_stat['Yellow Card'] = df_line_up_stat['Yellow Card'].replace(yellow_cards, regex=True)

    red_cards = {1 : "\U0001F7E5", 0 : ""}
    df_line_up_stat['Red Card'] = df_line_up_stat['Red Card'].replace(red_cards, regex=True)

    df_line_up_stat['player_name'] = np.where(df_line_up_stat['from'] == 0, 
                                                np.where(df_line_up_stat['counterpart_id'].isnull(),
                                                        df_line_up_stat['player_name'],
                                                        "\U0001F53B" + df_line_up_stat['player_name']
                                                ),
                                                "\U0001F53A" + df_line_up_stat['player_name']
                                                )
    return(df_line_up_stat)


def plot_line_up_on_pitch(df):
    '''
    This function plots the lineup on a football pitch depending on the starting formation
    '''
    color_team = {'Manchester City WFC' : '#5db7d3', 'Arsenal WFC': '#d52e22'}

    # Draw the pitch
    dimensions = pfp.PitchDimensions()
    fig = pfp.make_pitch_figure(
        dimensions,
        figure_height_pixels=800*1.2,
        figure_width_pixels=600*1.2,
        pitch_background=pfp.SingleColourBackground("#F5F5F5"),
        orientation=pfp.PitchOrientation.VERTICAL,
        marking_width = 0.5,
        marking_colour= 'grey',
        
    )

    df_starting_xi = df[df['from'] == 0]
    df_substitutes = df[~(df['from'] == 0)]

    # Draw the lineup
    for team in df['team_name'].unique() :
        df_starting_xi_team = df_starting_xi[df_starting_xi['team_name']==team]
        df_substitutes_team = df_substitutes[df_substitutes['team_name']==team]

        fig.add_trace(
            go.Scatter(
                x = df_starting_xi_team['x_coord'], 
                y = df_starting_xi_team['y_coord'], 
                mode="markers+text",
                marker={
                        "size": 25, 
                        "color": color_team[df_starting_xi_team['team_name'].unique()[0]],
                        'opacity' : 0.8
                },
                hoverinfo="none",
                text = df_starting_xi_team['player_name'],
                textposition="bottom center",
            )
        )

        # Add jersey number
        for x,y,jersey in zip(df_starting_xi_team['x_coord'], df_starting_xi_team['y_coord'],df_starting_xi_team['jersey_number']) :
            fig.add_annotation(
                x = x, 
                y = y,
                text=jersey,
                showarrow=False,
                font=dict(
                    color="black",
                    size=10
                ),
            )

    # Plot yellow cards
    for x,y,yellow_card in zip(df_starting_xi['x_coord'], df_starting_xi['y_coord'],df_starting_xi['Yellow Card']) :
        if yellow_card != yellow_card :
            yellow_card = ""
        fig.add_annotation(
            x = x, 
            y = y,
            xshift = -10,
            yshift = 12,
            text=yellow_card,
            showarrow=False,
            font=dict(
                size=10
            ),
        )

    # Plot yellow cards
    for x,y,red_card in zip(df_starting_xi['x_coord'], df_starting_xi['y_coord'],df_starting_xi['Red Card']) :
        if red_card != red_card :
            red_card = ""
        fig.add_annotation(
            x = x, 
            y = y,
            xshift = -10,
            yshift = 8,
            text=red_card,
            showarrow=False,
            font=dict(
                size=10
            ),
        )

    # Plot goals
    for x,y,goal in zip(df_starting_xi['x_coord'], df_starting_xi['y_coord'],df_starting_xi['goals']) :
        if goal != goal :
            goal = ""
        fig.add_annotation(
            x = x, 
            y = y,
            xshift = 10,
            yshift = 12,
            text=goal,
            showarrow=False,
            font=dict(
                size=10
            ),
        )

    fig.update_layout(
        showlegend = False,
        margin=dict(
            l=20,
            r=20,
            b=0,
            t=0
        ),
        font=dict(
            size=9,
        ),
        paper_bgcolor="whitesmoke",
        plot_bgcolor='whitesmoke',
        dragmode = False,
        clickmode = 'event',
    )
    return(fig)

def create_vaep_graph(df_cumulative_vaep, df_mean_vaep) :
    '''
    This function creates the vaep plot, i.e the cumulative vaep as a function of time.
    '''
    color_team = {'Manchester City WFC' : '#5db7d3', 'Arsenal WFC': '#d52e22'}

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x = df_cumulative_vaep['time'],
            y = df_cumulative_vaep['adjusted_vaep'],
            name = 'Technical efficiency',
            line = {
                "color": color_team[df_cumulative_vaep['team_name'].unique()[0]]
            },
            hovertext = (
                '<br>Time: '
                + df_cumulative_vaep['official_clock']
                + "<br>Impact on game: "
                + df_cumulative_vaep["adjusted_vaep"].round(2).astype(str)
            ),
            hoverinfo = 'text'
        )
    )

    fig.add_trace(
        go.Scatter(
            x = df_mean_vaep['time'],
            y = df_mean_vaep['adjusted_vaep'],
            name = 'Technical efficiency on previous games',
            hovertext = (
                "<br>Impact on game: "
                + df_mean_vaep["adjusted_vaep"].round(2).astype(str)
            ),
            line = {
                "color": 'grey'
            }
        )
    )

    # Define x tick as official time
    df_official_clock = df_cumulative_vaep[['time','official_clock']].drop_duplicates()
    df_official_clock['official_mod'] = df_cumulative_vaep['official_clock'].apply(lambda x: int(x.split("'+")[-1]))
    df_official_clock = df_official_clock[df_official_clock['official_mod'] % 5 == 0]
    x_tick_val = df_official_clock['time'].tolist()
    x_tick_labels = df_official_clock['official_clock'].tolist()

    fig.update_layout(
        xaxis = dict(
            title = 'Time',
            tickmode = 'array',
            tickvals = x_tick_val,
            ticktext = x_tick_labels
        ),

        yaxis = {
            'title' : 'Technical efficiency'
        },
        template="plotly_white",
        legend = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        font=dict(
            size=9,
        ),
        margin=dict(
            l=0,
            r=10,
            b=0,
            t=0
        ),
        hoverlabel=dict(
            font_size=11,
        ),
        height = 275,
    )

    return(fig)

def extract_from_second_spectrum_id(df_line_up_infos, df_teamsheet, player_id) :
    '''
    This function extracts from StatsBombs player id, the id used in Second Spectrum
    '''
    
    player_name = df_line_up_infos[df_line_up_infos['player_id']==player_id]['player_name'].unique()[0]
    df_name_in_second_spectrum = pd.DataFrame(df_teamsheet['player'], columns=['player'])
    df_name_in_second_spectrum['Fake_name'] = df_name_in_second_spectrum['player'].apply(lambda x: x.split(". ")[-1])
    df_name_in_second_spectrum['pID'] = df_name_in_second_spectrum.index
    for fake_name in df_name_in_second_spectrum['Fake_name'] :
        list_player_name =  player_name.split(" ")
        list_fake_name = fake_name.split(" ")
        if (set(list_fake_name) & set(list_player_name)) == set(list_fake_name) :
            id_player_ss = df_name_in_second_spectrum[df_name_in_second_spectrum['Fake_name']==fake_name]['pID'].unique()[0]
    return(id_player_ss)

def find_fatigue_threshold(metabolic_power) : 
    '''
    This function find the spot where substitution should happen.
    '''
    signal = np.array(metabolic_power).reshape((len(metabolic_power),1))
    algo = rpt.Binseg(model="l2").fit(signal) ##potentially finding spot where substitution should happen
    result = algo.predict(n_bkps=1) #big_seg
    result = [x + 3000 for x in result]
    return(result)


def create_metabolic_power_graph(df_tracking, list_threshold,teamname) :
    '''
    This function creates the metabolic power plot
    '''
    color_team = {'Manchester City WFC' : '#5db7d3', 'Arsenal WFC': '#d52e22'}

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x = df_tracking.loc[:,'Time_sec'],
            y = df_tracking.iloc[:, 3],
            line = {
                "color":color_team[teamname]
            }
        )
    )

    fig.add_vrect(
        x0=list_threshold[0], 
        x1=list_threshold[1], 
        line_width=0, 
        fillcolor = color_team[teamname],
        opacity=0.2
    )

    # Define x tick as official time
    df_official_clock = df_tracking[['Time_sec','official_clock']].drop_duplicates()
    df_official_clock['official_mod'] = df_tracking['official_clock'].apply(lambda x: int(x.split("'+")[-1]))
    df_official_clock = df_official_clock[df_official_clock['official_mod'] % 5 == 0].drop_duplicates(subset = 'official_clock')
    x_tick_val = df_official_clock['Time_sec'].tolist()
    x_tick_labels = df_official_clock['official_clock'].tolist()

    fig.update_layout(
        xaxis = dict(
                title = 'Time',
                tickmode = 'array',
                tickvals = x_tick_val,
                ticktext = x_tick_labels
            ),
        yaxis = {
            'title' : 'Metabolic power'
        },
        template="plotly_white",
        legend = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        font=dict(
            size=9,
        ),
        margin=dict(
            l=0,
            r=10,
            b=0,
            t=0
        ),
        hoverlabel=dict(
            font_size=11,
        ),
        height = 275,
    )
    return(fig)
