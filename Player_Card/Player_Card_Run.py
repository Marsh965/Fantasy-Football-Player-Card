import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.offsetbox import AnchoredText
from my_functions import PLAYER_cleaner, Team_splitter, ADP_PLAYER_cleaner, PLAYER_cleaner_PT2, list_percent_change, \
    difference, best_fit_slope_and_intercept
import sys
import os

# Constants
SUPPORTED_POSITIONS = ['QB', 'RB', 'WR', 'TE']
SUPPORTED_YEARS = [2015, 2016, 2017, 2018, 2019]

# Dictionary for team colors, used exact hex code of logo, {WAS : Washington} might need updating
team_colors = {'BAL': '#511252', 'CIN': '#FB4F13', 'CLE': '#FF3C01', 'PIT': '#FFB612',
               'BUF': '#00348D', 'MIA': '#1F9DA4', 'NE': '#B2B8BD', 'NYJ': '#135941',
               'HOU': '#0F1676', 'IND': '#012D60', 'JAC': '#A07A2B', 'TEN': '#4B91DB',
               'DEN': '#FB4F13', 'KC': '#E83D57', 'LAC': '#FFC20F', 'LV': '#000000',
               'CHI': '#C83802', 'DET': '#0076B4', 'GB': '#203732', 'MIN': '#644092',
               'DAL': '#012244', 'NYG': '#0B2265', 'PHI': '#1F6269', 'WAS': '#5C2B30',
               'ATL': '#A8162D', 'CAR': '#0185CA', 'NO': '#D4BC8D', 'TB': '#A71930',
               'ARI': '#A43E55', 'LAR': '#FFAF00', 'SF': '#AA0001', 'SEA': '#6BBD2B'
               }
team_names = {'BAL': 'Ravens', 'CIN': 'Bengals', 'CLE': 'Browns', 'PIT': 'Steelers',
              'BUF': 'Bills', 'MIA': 'Dolphins', 'NE': 'Patriots', 'NYJ': 'Jets',
              'HOU': 'Texans', 'IND': 'Colts', 'JAC': 'Jaguars', 'TEN': 'Titans',
              'DEN': 'Broncos', 'KC': 'Chiefs', 'LAC': 'Chargers', 'LV': 'Raiders',
              'CHI': 'Bears', 'DET': 'Lions', 'GB': 'Packers', 'MIN': 'Vikings',
              'DAL': 'Cowboys', 'NYG': 'Giants', 'PHI': 'Eagles', 'WAS': 'Washington',
              'ATL': 'Falcons', 'CAR': 'Panthers', 'NO': 'Saints', 'TB': 'Buccaneers',
              'ARI': 'Cardinals', 'LAR': 'Rams', 'SF': '49ers', 'SEA': 'Seahawks'
              }
team_list = ['BAL', 'CIN', 'CLE', 'PIT', 'BUF', 'MIA', 'NE', 'NYJ', 'HOU', 'IND', 'JAC', 'TEN',
             'DEN', 'KC', 'LAC', 'LV', 'CHI', 'DET', 'GB', 'MIN', 'DAL', 'NYG', 'PHI', 'WAS',
             'ATL', 'CAR', 'NO', 'TB', 'ARI', 'LAR', 'SF', 'SEA']

weeks = list(range(1, 18))

# Lists that get appended
weekly_points = []
position_rank = []
total_player_index_list = []
count = -1  # Dumb way to index players have not improved yet

# ---------------------------------------------------Inputs/Checks--------------------------------------------------- #
while True:
    year = input('Enter the year you would like to analyze: ')
    if os.path.isfile(f'FF_{year}.csv'):
        break
    elif year == 'x':
        print('\n\n\nGoodbye.\n\n\n')
        sys.exit()
    else:
        print('\n\nSorry the files for that year cannot be found...\n'
              'Make sure you run Fantasy_Pros_Data_Get first...\n'
              'You can enter "x" to kill the program...\n\n')
        continue

while True:
    player = input('Select a player to analyze: ').upper()  # Converts the players name to uppercase for easier checking
    year_file = pd.read_csv(F"FF_{year}.csv")
    year_file['Player'] = year_file['Player'].str.upper()  # Makes the players name uppercase
    row = (
    year_file.loc[year_file['Player'] == player])  # Locates where the player is and creates a DataFrame called row
    if player == 'X':
        print('\n\n\nGoodbye.\n\n\n')
        sys.exit()
    elif row.empty or row['Team'].item() == 'FA':  # Checks if the player is in the FF_{year}.csv or if their team is FA
        print('You can type "x" at any time to cancel the program')
        print('\nSorry that player can not be found for any of the following reasons:\n'
              '   1. Misspelled name (A.J., D.K., Smith-Schuster, Beckham Jr., etc)\n'
              '   2. They are a rookie\n'
              '   3. They are a free agent\n'
              '   4. They are a defensive player\n'
              '   5. They are so bad they did not make the top 804 Fantasy Players that year\n')
        continue
    player_position = row.iloc[0, 3]
    if player_position in SUPPORTED_POSITIONS:
        break
    else:
        print('Sorry, that position is not yet supported. Please try again.\n')
        continue

# ----------------------------------------------FILE READING---------------------------------------------------------- #

# Reads the yearly file for easier stat grabbing/manipulation, no empty rows

year_file = pd.read_csv(F"FF_{year}.csv")
year_file['Player'] = year_file['Player'].str.upper()  # Makes the players name uppercase
row = (year_file.loc[year_file['Player'] == player])  # Locates where the player is and creates a DataFrame called row
player_city = row.iloc[0, 2]
player_position = row.iloc[0, 3]
player_total_points = row.iloc[0, 4]
player_total_games = row.iloc[0, 5]
player_yearly_avg = row.iloc[0, 6]
year_pos_file = year_file.loc[
    year_file['Position'] == player_position]  # Creates a DataFrame of only the players position
overall_player_year_rank = (year_pos_file.loc[year_pos_file['Player'] == player])[
    'Rank'].item()  # Finds the overall rank of the player out of all positions
for rank, index in enumerate(year_pos_file['Rank'], start=1):  # Finds the positional rank for the year
    if overall_player_year_rank == index:
        position_player_year_rank = rank

# Loops through the csv files of weeks 1 through 17 for fantasy points
for week in weeks:
    file = pd.read_csv(F"FF_{year}_Week{week}.csv")  # Reads the FF_points for each week based on the year
    file['Player'] = file['Player'].str.upper()  # Makes the players name uppercase
    rows = pd.DataFrame()  # Creates an empty DataFrame named rows
    row = (file.loc[file['Player'] == player])  # Create a DataFrame of the row where the player is
    pos_file = (file.loc[file['Position'] == player_position])  # Creates a DataFrame of only the players position
    if row.empty:  # If the player did not play that particular week, then fills in the needed values
        new_row = pd.DataFrame({'Rank': np.nan, 'Player': player, 'Team': player_city,
                                'Position': player_position, 'Points': 0, 'Games': 0,
                                'Avg': np.nan}, index=[np.nan])
        week_points = new_row['Points'].item()  # Grabs the week_points which is set at 0
    else:  # If the player played that week
        new_row = row  # Sets new_row = row so that we can append if and else at the same item
        week_points = new_row['Points'].item()  # Grabs the week_points for that week
    rows = rows.append(new_row)  # Appends the empty rows and the filled rows to a DataFrame
    weekly_points.append(week_points)  # Appends the weekly points for the line graph

    # Start of weekly positional ranking code
    total_player_index = rows.index.item()  # Grabs the index of the player for each week
    total_player_index_list.append(total_player_index)  # Appends the value to a list
    count += 1  # Count to help with iterating through the list
    for rank, index in enumerate(pos_file.index, start=1):  # For loop for appending the positional rank each week
        if total_player_index_list[count] == index:
            position_rank.append(rank)  # If the total_index = positional_index then append the position rank
    if np.isnan(total_player_index_list[count]):
        position_rank.append(np.nan)  # Appends nan if the player did not play that week (Outside of loop)

# Analysis of the team target files for creating pie and corresponding bar chart
team_target_file = pd.read_csv(F"FF_{year}_Team_Targets.csv")
Team_splitter(team_target_file)  # Calls the function to split the teams (Green Bay Packers --> Packers)
target_row = team_target_file.loc[team_target_file['Name'] == team_names.get(
    player_city)]  # Locates the row needed based on the team_names dictionary
WR_percent = target_row['WR %'].item()
RB_percent = target_row['RB %'].item()
TE_percent = target_row['TE %'].item()
if player_position == 'WR':  # Checks player position
    WR_target_file = pd.read_csv(F"FF_{year}_Targets_WR.csv")  # Reads the target file for that position
    Team_splitter(WR_target_file)  # Goes through the Team_splitter function as well
    pos_target_row = WR_target_file.loc[WR_target_file['Name'] == team_names.get(
        player_city)]  # Creates a row for the players team and knows by using the dictionary
if player_position == 'RB':
    RB_target_file = pd.read_csv(F"FF_{year}_Targets_RB.csv")
    Team_splitter(RB_target_file)
    pos_target_row = RB_target_file.loc[RB_target_file['Name'] == team_names.get(player_city)]
if player_position == 'TE':
    TE_target_file = pd.read_csv(F"FF_{year}_Targets_TE.csv")
    Team_splitter(TE_target_file)
    pos_target_row = TE_target_file.loc[TE_target_file['Name'] == team_names.get(player_city)]

# Reading/Cleaning ADP DataFrame
ADP_file = pd.read_csv('FF_2020_ADP.csv')
ADP_PLAYER_cleaner(ADP_file)
ADP_row = (ADP_file.loc[ADP_file['Player'] == player])  # Creates a ADP row for the player
if ADP_row.empty:
    print('Sorry, that player is outside of the top 30 rounds of the draft')
    ADP = np.nan
else:
    ADP = ADP_row['AVG'].item()  # Grabs the ADP from that row

# Reads/Cleans the stats DataFrame
stats_df = pd.read_csv(f'FF_{year}_Stats_{player_position}.csv')
PLAYER_cleaner(stats_df)
stats_df_row = stats_df.loc[stats_df['Player'] == player]  # Creates a stats row for the player
stats_player_index = (stats_df.loc[
    stats_df['Player'] == player]).index.item() - 1  # Finds the player index in the stats_df

# Reads/Cleans the Projections DataFrame
projections_df = pd.read_csv(f'FF_{year}_Projections_{player_position}.csv')
PLAYER_cleaner_PT2(projections_df)
projections_df_row = projections_df.loc[projections_df['Player'] == player]
projected_positional_rank = projections_df_row.index.item()

# Reads the snaps csv file to DataFrame
snaps_df = pd.read_csv(f'FF_{year}_Snaps_{player_position}.csv')
snaps_df['Player'] = snaps_df['Player'].str.upper()
snaps_df_row = snaps_df.loc[snaps_df['Player'] == player]
snaps_player_index = (snaps_df.loc[snaps_df['Player'] == player]).index.item()

# ------------------------------------------POSITION BASED VARIABLES-------------------------------------------------- #

# Positional if statements for grabbing/plotting data
if player_position == 'QB':  # if statements for selecting position based stats to analyze and graph
    CUTOFF = 60  # Cutoff value to make plots more readable and statistically significant
    FanPoints = stats_df_row['MISC.2'].item()
    PassYds = stats_df_row['PASSING.3'].item()
    PassTD = stats_df_row['PASSING.5'].item()
    RushYds = stats_df_row['RUSHING.1'].item()
    RushTD = stats_df_row['RUSHING.2'].item()
    INT = stats_df_row['PASSING.6'].item()
    ProFanPoints = projections_df_row['MISC.1'].item()
    ProPassYds = projections_df_row['PASSING.2'].item()
    ProRushYds = projections_df_row['RUSHING.1'].item()
    ProPassTD = projections_df_row['PASSING.3'].item()
    ProRushTD = projections_df_row['RUSHING.2'].item()
    ProINT = projections_df_row['PASSING.4'].item()
    string = f'{year} Stats versus 2020 Projections\n\nFantasy Points:           ({FanPoints} --> {ProFanPoints})\nPassing Yards:            ({PassYds} --> {ProPassYds})\nRushing Yards:           ({RushYds} --> {ProRushYds})\nPassing Touchdowns: ({PassTD} --> {ProPassTD})\nRushing Touchdowns: ({RushTD} --> {ProRushTD})\nInterceptions:             ({INT} --> {ProINT})'
    bar_graph_labels = ['PASS ATT', 'CMP', 'PASS YDS', 'PASS TD', 'INT', 'RUSH ATT', 'RUSH YDS', 'RUSH TD', 'FL',
                        'FPTS']
    scatter_labels = ['Pass ATT', 'Pass TD', 'Rush ATT', 'Rush TD']  # used for labeling axis
    x_scatter_plot1 = [int(i) for i in (stats_df['PASSING.1'][0:CUTOFF].tolist())]
    y_scatter_plot1 = [int(i) for i in (stats_df['PASSING.5'][0:CUTOFF].tolist())]
    x_scatter_plot2 = [int(i) for i in (stats_df['RUSHING'][0:CUTOFF].tolist())]
    y_scatter_plot2 = [int(i) for i in (stats_df['RUSHING.2'][0:CUTOFF].tolist())]
    projection_stats = [projections_df_row['PASSING'].item(), projections_df_row['PASSING.1'].item(),
                        projections_df_row['PASSING.2'].item(), projections_df_row['PASSING.3'].item(),
                        projections_df_row['PASSING.4'].item(),
                        projections_df_row['RUSHING'].item(), projections_df_row['RUSHING.1'].item(),
                        projections_df_row['RUSHING.2'].item(),
                        projections_df_row['MISC'].item(), projections_df_row['MISC.1'].item()]
    actual_stats = [stats_df_row['PASSING.1'].item(), stats_df_row['PASSING'].item(), stats_df_row['PASSING.3'].item(),
                    stats_df_row['PASSING.5'].item(),
                    stats_df_row['PASSING.6'].item(), stats_df_row['RUSHING'].item(), stats_df_row['RUSHING.1'].item(),
                    stats_df_row['RUSHING.2'].item(),
                    stats_df_row['MISC'].item(), stats_df_row['MISC.2'].item()]

if player_position == 'RB':
    RushATT = stats_df_row['RUSHING'].item()
    RushYds = stats_df_row['RUSHING.1'].item()
    RushTD = stats_df_row['RUSHING.5'].item()
    REC = stats_df_row['RECEIVING'].item()
    RecYds = stats_df_row['RECEIVING.2'].item()
    RecTD = stats_df_row['RECEIVING.4'].item()
    FanPoints = stats_df_row['MISC.2'].item()
    ProRushATT = projections_df_row['RUSHING'].item()
    ProRushYds = projections_df_row['RUSHING.1'].item()
    ProRushTD = projections_df_row['RUSHING.2'].item()
    ProREC = projections_df_row['RECEIVING'].item()
    ProRecYds = projections_df_row['RECEIVING.1'].item()
    ProRecTD = projections_df_row['RECEIVING.2'].item()
    ProFanPoints = projections_df_row['MISC.1'].item()
    string = f'Fantasy Points:              ({FanPoints} --> {ProFanPoints})\nRushing Attempts:         ({RushATT} --> {ProRushATT})\nRushing Yards:               ({RushYds} --> {ProRushYds})\nRushing Touchdowns:    ({RushTD} --> {ProRushTD})\nReceptions:                   ({REC} --> {ProREC})\nReceiving Yards:            ({RecYds} --> {ProRecYds})\nReceiving Touchdowns: ({RecTD} --> {ProRecTD})'
    scatter_labels = ['Rush ATT', 'Rush TD', 'Receptions', ' Rec TD']
    bar_graph_labels = ['RUSH ATT', 'RUSH YDS', 'RUSH TD', 'RECEPTIONS', 'REC YDS', 'REC TDS', 'FL', 'FPTS']
    CUTOFF = 150
    x_scatter_plot1 = [int(i) for i in (stats_df['RUSHING'][0:CUTOFF].tolist())]
    y_scatter_plot1 = [int(i) for i in (stats_df['RUSHING.5'][0:CUTOFF].tolist())]
    x_scatter_plot2 = [int(i) for i in (stats_df['RECEIVING'][0:CUTOFF].tolist())]
    y_scatter_plot2 = [int(i) for i in (stats_df['RECEIVING.4'][0:CUTOFF].tolist())]
    projection_stats = [projections_df_row['RUSHING'].item(), projections_df_row['RUSHING.1'].item(),
                        projections_df_row['RUSHING.2'].item(),
                        projections_df_row['RECEIVING'].item(), projections_df_row['RECEIVING.1'].item(),
                        projections_df_row['RECEIVING.2'].item(),
                        projections_df_row['MISC'].item(), projections_df_row['MISC.1'].item()]
    actual_stats = [stats_df_row['RUSHING'].item(), stats_df_row['RUSHING.1'].item(), stats_df_row['RUSHING.5'].item(),
                    stats_df_row['RECEIVING'].item(), stats_df_row['RECEIVING.2'].item(),
                    stats_df_row['RECEIVING.4'].item(),
                    stats_df_row['MISC'].item(), stats_df_row['MISC.2'].item()]

if player_position == 'WR':
    REC = stats_df_row['RECEIVING'].item()
    RecYds = stats_df_row['RECEIVING.2'].item()
    RecTD = stats_df_row['RECEIVING.6'].item()
    RushATT = stats_df_row['RUSHING'].item()
    RushYds = stats_df_row['RUSHING.1'].item()
    RushTD = stats_df_row['RUSHING.2'].item()
    FanPoints = stats_df_row['MISC.2'].item()
    ProREC = projections_df_row['RECEIVING'].item()
    ProRecYds = projections_df_row['RECEIVING.1'].item()
    ProRecTD = projections_df_row['RECEIVING.2'].item()
    ProRushATT = projections_df_row['RUSHING'].item()
    ProRushYds = projections_df_row['RUSHING.1'].item()
    ProRushTD = projections_df_row['RUSHING.2'].item()
    ProFanPoints = projections_df_row['MISC.1'].item()
    string = f'Fantasy Points:              ({FanPoints} --> {ProFanPoints})\nReceptions:                   ({REC} --> {ProREC})\nReceiving Yards:            ({RecYds} --> {ProRecYds})\nReceiving Touchdowns: ({RecTD} --> {ProRecTD})\nRushing Attempts:         ({RushATT} --> {ProRushATT})\nRushing Yards:               ({RushYds} --> {ProRushYds})\nRushing Touchdowns:    ({RushTD} --> {ProRushTD})'
    scatter_labels = ['Receiving Yards', 'Receiving TD', 'Targets', 'Receptions']
    bar_graph_labels = ['RECEPTIONS', 'REC YDS', 'REC TDS', 'RUSH ATT', 'RUSH YDS', 'RUSH TD', 'FL', 'FPTS']
    CUTOFF = 152
    x_scatter_plot1 = [int(i) for i in (stats_df['RECEIVING.2'][0:CUTOFF].tolist())]
    y_scatter_plot1 = [int(i) for i in (stats_df['RECEIVING.6'][0:CUTOFF].tolist())]
    x_scatter_plot2 = [int(i) for i in (stats_df['RECEIVING.1'][0:CUTOFF].tolist())]
    y_scatter_plot2 = [float(i) for i in (stats_df['RECEIVING'][0:CUTOFF].tolist())]
    projection_stats = [projections_df_row['RECEIVING'].item(), projections_df_row['RECEIVING.1'].item(),
                        projections_df_row['RECEIVING.2'].item(),
                        projections_df_row['RUSHING'].item(), projections_df_row['RUSHING.1'].item(),
                        projections_df_row['RUSHING.2'].item(),
                        projections_df_row['MISC'].item(), projections_df_row['MISC.1'].item()]
    actual_stats = [stats_df_row['RECEIVING'].item(), stats_df_row['RECEIVING.2'].item(),
                    stats_df_row['RECEIVING.6'].item(),
                    stats_df_row['RUSHING'].item(), stats_df_row['RUSHING.1'].item(),
                    stats_df_row['RUSHING.2'].item(),
                    stats_df_row['MISC'].item(), stats_df_row['MISC.2'].item()]

if player_position == 'TE':
    REC = stats_df_row['RECEIVING'].item()
    RecYds = stats_df_row['RECEIVING.2'].item()
    RecTD = stats_df_row['RECEIVING.6'].item()
    FanPoints = stats_df_row['MISC.2'].item()
    ProREC = projections_df_row['RECEIVING'].item()
    ProRecYds = projections_df_row['RECEIVING.1'].item()
    ProRecTD = projections_df_row['RECEIVING.2'].item()
    ProFanPoints = projections_df_row['MISC.1'].item()
    string = f'Fantasy Points:              ({FanPoints} --> {ProFanPoints})\nReceptions:                   ({REC} --> {ProREC})\nReceiving Yards:            ({RecYds} --> {ProRecYds})\nReceiving Touchdowns: ({RecTD} --> {ProRecTD})'
    table_row_labels = ['Fantasy Points', 'Receptions', 'Receiving Yds', 'Receiving TD']
    scatter_labels = ['Receiving Yards', 'Receiving TD', 'Plays of 20+ Yds', 'Fantasy Points']
    bar_graph_labels = ['RECEPTIONS', 'REC YDS', 'REC TDS', 'FL', 'FPTS']
    CUTOFF = 100
    x_scatter_plot1 = [int(i) for i in (stats_df['RECEIVING.2'][0:CUTOFF].tolist())]
    y_scatter_plot1 = [int(i) for i in (stats_df['RECEIVING.6'][0:CUTOFF].tolist())]
    x_scatter_plot2 = [int(i) for i in (stats_df['RECEIVING.5'][0:CUTOFF].tolist())]
    y_scatter_plot2 = [float(i) for i in (stats_df['MISC.2'][0:CUTOFF].tolist())]
    projection_stats = [projections_df_row['RECEIVING'].item(), projections_df_row['RECEIVING.1'].item(),
                        projections_df_row['RECEIVING.2'].item(),
                        projections_df_row['MISC'].item(), projections_df_row['MISC.1'].item()]
    actual_stats = [stats_df_row['RECEIVING'].item(), stats_df_row['RECEIVING.2'].item(),
                    stats_df_row['RECEIVING.6'].item(),
                    stats_df_row['MISC'].item(), stats_df_row['MISC.2'].item()]

# Indexes the list to help annotate the player on the scatter plots
x_scatter1 = x_scatter_plot1[stats_player_index]
y_scatter1 = y_scatter_plot1[stats_player_index]
x_scatter2 = x_scatter_plot2[stats_player_index]
y_scatter2 = y_scatter_plot2[stats_player_index]

# Line of best fit for Scatter1
xs1 = np.array(x_scatter_plot1, dtype=np.float64)
ys1 = np.array(y_scatter_plot1, dtype=np.float64)
m1, b1 = best_fit_slope_and_intercept(xs1, ys1)
regression_line1 = [(m1 * x) + b1 for x in xs1]

# Line of best fit for Scatter2
xs2 = np.array(x_scatter_plot2, dtype=np.float64)
ys2 = np.array(y_scatter_plot2, dtype=np.float64)
m2, b2 = best_fit_slope_and_intercept(xs2, ys2)
regression_line2 = [(m2 * x) + b2 for x in xs2]

# Finds the percent change between the selected year and the projected year
percent_change = list_percent_change(pd.to_numeric(actual_stats), pd.to_numeric(projection_stats))
difference = difference(pd.to_numeric(actual_stats), pd.to_numeric(projection_stats))

# Random stats that can be applied to every position
GamesPlayed = stats_df_row['MISC.1'].item()
OWN = stats_df_row['MISC.4'].item()

# ----------------------------------------------FIGURE PLOTS---------------------------------------------------------- #

# Figure Setup
fig = plt.figure(figsize=(12, 8), constrained_layout=True)
gs = fig.add_gridspec(5, 4)

# Text Axes
title = fig.text(0.05, 0.95,
                 f'{player} {player_position}: ({position_player_year_rank} --> {projected_positional_rank})', size=25,
                 color='white', bbox=dict(boxstyle='round', facecolor=team_colors.get(player_city), edgecolor='black'))
body = fig.text(0.05, 0.92, string, size=16, va='top',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))

# Bar Chart Axes
width = 0.5  # the width of the bars
ind = np.arange(len(percent_change))  # the x locations for the groups
bar_color_list = []  # Empty list to append red or green to
for x in percent_change:  # Color code percent change red or green based on growth or decay
    if x < 0:
        bar_color = 'r'
        bar_color_list.append(bar_color)
    elif x >= 0:
        bar_color = 'g'
        bar_color_list.append(bar_color)
    elif np.isnan(x):
        bar_color = 'black'
        bar_color_list.append(bar_color)
ax_bars = fig.add_subplot(gs[2:4, 0:2])
rects = ax_bars.bar(ind, percent_change, width, label='Actual', color=bar_color_list)
ax_bars.set(title='Projections', xticks=np.arange(len(bar_graph_labels)))
ax_bars.set_xticklabels(labels=bar_graph_labels, rotation=45)
ax_bars.axhline(0, color='black', lw=2)
ax_bars.yaxis.set_major_formatter(ticker.PercentFormatter())
# Annotation lists for bar chart
height_list = []
x_pos_list = []
rect_width_list = []
for rect in rects:
    height_list.append(rect.get_height())
    x_pos_list.append(rect.get_x())
    rect_width_list.append(rect.get_width() / 2)
for x in range(len(difference)):
    ax_bars.annotate(f'{difference[x]}',
                     xy=(x_pos_list[x] + rect_width_list[x], height_list[x]),
                     xytext=(0, 3),  # 3 points vertical offset
                     textcoords="offset points",
                     ha='center', va='bottom')

# Pie Chart/Corresponding Bar chart Axes
pie_labels = ['WR', 'RB', 'TE']
target_percent = [WR_percent, RB_percent, TE_percent]
ax_pie = fig.add_subplot(gs[0:2, 3])  # Creates the pie plot location
ax_bar_pie = fig.add_subplot(gs[0:2, 2])  # Creates the bar plot for the pie chart location
ax_pie.set(title=f'{team_names.get(player_city)} Targets by Position')
ax_bar_pie.set(title=f'{team_names.get(player_city)} {player_position} Targets')
ax_bar_pie.axis('off')
if player_position == 'WR':  # WR customized pie and corresponding target bar chart
    explode = [0.1, 0, 0]  # makes the WR slice explode
    angle = -180 * target_percent[0]
    ratios = [pos_target_row['Targets'].item(), pos_target_row['Targets.1'].item(), pos_target_row['Targets.2'].item()]
    WR1 = pos_target_row['WR1'].item()  # Grabs the target data for the WR1, WR2, WR3
    WR2 = pos_target_row['WR2'].item()
    WR3 = pos_target_row['WR3'].item()
    legend = (WR1, WR2, WR3)
elif player_position == 'RB':  # RB customized pie and corresponding target bar chart
    explode = [0, 0.1, 0]  # makes the RB slice explode
    angle = -180 * target_percent[1]
    ratios = [pos_target_row['Targets'].item(), pos_target_row['Targets.1'].item(), pos_target_row['Targets.2'].item()]
    RB1 = pos_target_row['RB1'].item()  # Grabs the target data for the RB1, RB2, RB3
    RB2 = pos_target_row['RB2'].item()
    RB3 = pos_target_row['RB3'].item()
    legend = (RB1, RB2, RB3)
elif player_position == 'TE':  # TE customized pie and corresponding target bar chart
    explode = [0, 0, 0.1]  # makes the TE slice explode
    angle = -180 * target_percent[2]
    ratios = [pos_target_row['Targets'].item(), pos_target_row['Targets.1'].item()]
    TE1 = pos_target_row['TE1'].item()  # Grabs only the target data for the TE1 and TE2 (no TE3 on website)
    TE2 = pos_target_row['TE2'].item()
    legend = (TE1, TE2)
else:  # If the player is a QB
    angle = 90
    explode = [0, 0, 0]
    ratios = [target_row['WR Targets'].item(), target_row['RB Targets'].item(), target_row['TE Targets'].item()]
    legend = ('WR', 'RB', 'TE')
xpos = 0
bottom = 0
width = 0.5
if player_city != 'LV' or 'FA':  # The Stat sheet for the LV Raiders is empty for team targets
    for j in range(len(ratios)):
        height = ratios[j]
        ax_bar_pie.bar(xpos, height, width, bottom=bottom)
        ypos = bottom + ax_bar_pie.patches[j].get_height() / 2
        bottom += height
        ax_bar_pie.text(xpos, ypos, (ax_bar_pie.patches[j].get_height()), ha='center')
    ax_bar_pie.legend(legend, bbox_to_anchor=(0.70, 0.97), loc='best', borderaxespad=0)
    ax_bar_pie.set_xlim(-2.5 * width, 2.5 * width)
    ax_pie.pie(target_percent, labels=pie_labels, autopct='%1.1f%%', shadow=False, startangle=angle, explode=explode)

# Scatter Plot 1 Axes
ax_scatter1 = fig.add_subplot(gs[2, 2:])
ax_scatter1.set(xlabel=scatter_labels[0], ylabel=scatter_labels[1])
ax_scatter1.annotate(f'{player}: ({x_scatter1}, {y_scatter1})', xy=(x_scatter1, y_scatter1), xycoords='data',
                     xytext=(0.01, 0.88), textcoords='axes fraction',
                     arrowprops=dict(arrowstyle='->', connectionstyle='angle3'))
ax_scatter1.scatter(x_scatter_plot1, y_scatter_plot1, c=team_colors.get(player_city), edgecolor='black',
                    linewidth=1, alpha=0.75)
ax_scatter1.plot(xs1, regression_line1, linestyle='dashed', color='black')

# Scatter Plot 2 Axes
ax_scatter2 = fig.add_subplot(gs[3, 2:])
ax_scatter2.set(xlabel=scatter_labels[2], ylabel=scatter_labels[3])
ax_scatter2.annotate(f'{player}: ({x_scatter2}, {y_scatter2})', xy=(x_scatter2, y_scatter2), xycoords='data',
                     xytext=(0.01, 0.88), textcoords='axes fraction',
                     arrowprops=dict(arrowstyle='->', connectionstyle='angle3'))
ax_scatter2.scatter(x_scatter_plot2, y_scatter_plot2, c=team_colors.get(player_city), edgecolor='black',
                    linewidth=1, alpha=0.75)
ax_scatter2.plot(xs2, regression_line2, linestyle='dashed', color='black')

# Line Plot Axes
ax_line = fig.add_subplot(gs[4, :])
ax_line.plot(range(1, 18), weekly_points, '-o', c=team_colors.get(player_city), label=str(player_city))
for i in range(0, 16):
    ax_line.annotate(f'{player_position}: {position_rank[i]}', xy=(i + 1, weekly_points[i]),
                     xytext=(i + 1, weekly_points[i]), ha='center', va='bottom')
ax_line.set(xlabel='Week Number', ylabel='Points', xticks=np.arange(1, 18, 1))
at = AnchoredText('Games Played:' + str(GamesPlayed), prop=dict(size=10), frameon=True, loc='lower right')
at.patch.set_boxstyle("round,pad=0.,rounding_size=0.3")
ax_line.add_artist(at)

plt.show()
