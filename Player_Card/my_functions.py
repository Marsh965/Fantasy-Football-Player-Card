import urllib
import urllib.request
from bs4 import BeautifulSoup
import requests
import sys
import pandas as pd
import numpy as np
from statistics import mean


# -----------------------------------------Web Scraping Functions----------------------------------------------------- #

def make_soup(url, year, start_week, end_week):
    r = requests.get(url + 'year=' + str(year) + '&start=' + str(start_week) + '&end=' + str(end_week))
    if r.status_code == 200:
        r = urllib.request.urlopen(url + 'year=' + str(year) + '&start=' + str(start_week) + '&end=' + str(end_week))
        soupdata = BeautifulSoup(r, 'html.parser')
        return soupdata
    else:
        print('Invalid URL')
        sys.exit()


def pos_make_soup(year, position):
    r = requests.get(
        F'https://www.fantasypros.com/nfl/reports/targets-distribution/{position}.php?year={year}&start=1&end=17&show=totals')
    if r.status_code == 200:
        r = urllib.request.urlopen(
            F'https://www.fantasypros.com/nfl/reports/targets-distribution/{position}.php?year={year}&start=1&end=17&show=totals')
        soupdata = BeautifulSoup(r, 'html.parser')
        return soupdata
    else:
        print('Invalid URL')
        sys.exit()


def ADP_make_soup():
    r = requests.get('https://www.fantasypros.com/nfl/adp/half-point-ppr-overall.php')
    if r.status_code == 200:
        r = urllib.request.urlopen('https://www.fantasypros.com/nfl/adp/half-point-ppr-overall.php')
        soupdata = BeautifulSoup(r, 'html.parser')
        return soupdata
    else:
        print('Invalid URL')
        sys.exit()


def stats_make_soup(pos, year):
    r = requests.get(f'https://www.fantasypros.com/nfl/stats/{pos}.php?year={year}&scoring=HALF')
    if r.status_code == 200:
        r = urllib.request.urlopen(f'https://www.fantasypros.com/nfl/stats/{pos}.php?year={year}&scoring=HALF')
        soupdata = BeautifulSoup(r, 'html.parser')
        return soupdata
    else:
        print('Invalid URL')
        sys.exit()


def snap_count(pos, year):
    r = requests.get(F'https://www.fantasypros.com/nfl/reports/snap-counts/{pos}.php?year={year}')
    if r.status_code == 200:
        r = urllib.request.urlopen(F'https://www.fantasypros.com/nfl/reports/snap-counts/{pos}.php?year={year}')
        soupdata = BeautifulSoup(r, 'html.parser')
        return soupdata
    else:
        print('Invalid URL')
        sys.exit()


def projections_make_soup(pos, scoring_type):
    r = requests.get(
        F'https://www.fantasypros.com/nfl/projections/{pos}.php?week=draft&scoring={scoring_type}&week=draft')
    if r.status_code == 200:
        r = urllib.request.urlopen(
            F'https://www.fantasypros.com/nfl/projections/{pos}.php?week=draft&scoring={scoring_type}&week=draft')
        soupdata = BeautifulSoup(r, 'html.parser')
        return soupdata
    else:
        print('Invalid URL')
        sys.exit()


# ---------------------------------------Data Cleaning Functions------------------------------------------------------ #

def PLAYER_cleaner(file):  # Used on the stats DataFrames
    upper_index = file['Unnamed: 1_level_0']
    split_file = upper_index[0:].str.split(' ')  # Turns the PLAYER into a split string to clean
    split_list = split_file.tolist()  # Converts the PLAYER column to a list
    clean_names = []  # List to be appended with cleaned names
    for i, name in enumerate(split_list):  # Deletes the last element in each list and joins them and appends to list
        del name[-1]
        clean_name = ' '.join(name)
        clean_names.append(clean_name)
    file.drop(columns=['Unnamed: 1_level_0'], inplace=True)  # Drops the original files PLAYER column
    clean_df = pd.DataFrame(clean_names, columns=['name'])  # Converts a list back into a DataFrame
    file.insert(1, 'Player', clean_df)  # Inserts the cleaned names back into the original DataFrame
    file.drop(index=0, inplace=True)  # drops the second level of index
    file['Player'] = file['Player'].str.upper()  # Converts the PLAYER column to upper case
    return file


def PLAYER_cleaner_PT2(file):  # Used on the Projections DataFrame
    upper_index = file['Unnamed: 0_level_0']
    split_file = upper_index[0:].str.split(' ')  # Turns the PLAYER into a split string to clean
    split_list = split_file.tolist()  # Converts the PLAYER column to a list
    clean_names = []  # List to be appended with cleaned names
    city_names = []
    for i, name in enumerate(split_list):  # Deletes the last element in each list and joins them and appends to list
        city = name[-1]
        del name[-1]
        clean_name = ' '.join(name)
        clean_names.append(clean_name)
        city_names.append(city)
    file.drop(columns=['Unnamed: 0_level_0'], inplace=True)  # Drops the original files PLAYER column
    clean_df = pd.DataFrame(clean_names, columns=['name'])  # Converts a list back into a DataFrame
    city_df = pd.DataFrame(city_names, columns=['city'])
    file.insert(0, 'Player', clean_df)  # Inserts the cleaned names back into the original DataFrame
    file.insert(1, 'City', city_df)
    file.drop(index=0, inplace=True)  # drops the second level of index
    file['Player'] = file['Player'].str.upper()  # Converts the PLAYER column to upper case
    return file


def ADP_PLAYER_cleaner(file):  # Used on the ADP DataFrame
    split_file = file['Player Team (Bye)'].str.split(' ')  # Turns the PLAYER into a split string to clean
    split_list = split_file.tolist()  # Converts the PLAYER column to a list
    clean_names = []  # List to be appended with cleaned names
    for i, name in enumerate(
            split_list):  # Deletes the last two elements in each list and joins them and appends to list
        del name[-1]
        del name[-1]
        clean_name = ' '.join(name)
        clean_names.append(clean_name)
    file.drop(columns='Player Team (Bye)', inplace=True)  # Drops the original files PLAYER column
    clean_df = pd.DataFrame(clean_names, columns=['name'])  # Converts a list back into a DataFrame
    file.insert(1, 'Player', clean_df)  # Inserts the cleaned names back into the original DataFrame
    file['Player'] = file['Player'].str.upper()  # Converts the PLAYER column to upper case
    return file


def Team_splitter(file):  # Used on the target and positional target DataFrames
    team_list = file['Team'].tolist()  # Creates a list of the team names from the file
    short_team_list = []  # Creates a empty list to append the team name to (Packers, Texans, etc.)
    for i, team in enumerate(team_list):  # Enumerates through the team_list
        short_team_list.append(team.split()[-1])  # Grabs the last string of each team element in a list and appends it
    file.insert(1, 'Name', short_team_list)  # Inserts the new column
    return file


# -----------------------------------------------Math Functions------------------------------------------------------ #

def list_percent_change(Stats_List, Projected_List):
    try:
        percent_change = (((np.array(Projected_List) - np.array(Stats_List)) / abs((Stats_List))) * 100).tolist()
        return percent_change
    except ZeroDivisionError:
        percent_change = 0
        return percent_change


def difference(list1, list2):
    difference = (np.array(list2) - np.array(list1)).tolist()
    rounded_list = []
    for x in difference:
        rounded = round(x, 3)
        rounded_list.append(rounded)
    return rounded_list


def best_fit_slope_and_intercept(xs, ys):
    m = (((mean(xs) * mean(ys)) - mean(xs * ys)) /
         ((mean(xs) * mean(xs)) - mean(xs * xs)))

    b = mean(ys) - m * mean(xs)

    return m, b


