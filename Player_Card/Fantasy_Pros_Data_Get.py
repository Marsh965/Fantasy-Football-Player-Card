import pandas as pd
import time
from my_functions import make_soup, pos_make_soup, ADP_make_soup, stats_make_soup, snap_count, projections_make_soup
import sys

start = time.time()

# Constants
SUPPORTED_YEARS = ['2015', '2016', '2017', '2018', '2019']

# User Inputs
while True:
    year = input('Enter the year you would like to analyze... \n(2015 to present)\nYear: ')
    if year in SUPPORTED_YEARS:
        break
    elif year == 'x':
        print('\n\n\nGoodbye.\n\n\n')
        sys.exit()
    else:
        print("\nYou can type 'x' to kill the program at any time...\n")
        continue


# Iterates through the weeks and creates a csv page for each individual week with points scored that week
for week in range(1, 18):
    print(f'Week {week} Fantasy Leaders...')
    soup = make_soup('https://www.fantasypros.com/nfl/reports/leaders/half-ppr.php?', year, week, week)  # week 1-1, 2-2, 3-3, etc.
    table = soup.find_all('table')[0]
    df = pd.read_html(str(table))[0]
    df.to_csv(f'FF_{year}_Week{week}.csv', index=False)


# Grabs the Fantasy Leaders data for the year
print(f'{year} Fantasy Leaders')
soup = make_soup('https://www.fantasypros.com/nfl/reports/leaders/half-ppr.php?', year, 1, 17)
table = soup.find_all('table')[0]
df = pd.read_html(str(table))[0]
df.to_csv(f'FF_{year}.csv', index=False)


# Grabs the targets by team data for the year
print(f'{year} Targets by Team')
soup = make_soup('https://www.fantasypros.com/nfl/reports/targets-distribution/?', year, 1, 17)
table = soup.find_all('table')[0]
df = pd.read_html(str(table))[0]
df.to_csv(f'FF_{year}_Team_Targets.csv', index=False)


position_list = ['qb', 'rb', 'wr', 'te']
for pos in position_list:
    # Grabs the projections for all positions for the upcoming year
    print(f'Projections_{pos}')
    soup = projections_make_soup(pos, 'HALF')
    table = soup.find_all('table')[0]
    df = pd.read_html(str(table))[0]
    df.to_csv(f'FF_{year}_Projections_{pos}.csv',  index=False)
    # Grabs the snap counts for the selected year
    print(f'{year}_{pos}_Snap Counts')
    soup = snap_count(pos, year)
    table = soup.find_all('table')[0]
    df = pd.read_html(str(table))[0]
    df.to_csv(f'FF_{year}_Snaps_{pos}.csv', index=False)
    # Grabs the Stats for the selected year
    print(f'{year}_{pos}_Stats')
    soup = stats_make_soup(pos, year)
    table = soup.find_all('table')[0]
    df = pd.read_html(str(table))[0]
    df.to_csv(f'FF_{year}_Stats_{pos}.csv', index=False)

# Grabs the positional target data by team
position_list = ['rb', 'wr', 'te']
for pos in position_list:
    print(f'{year}_Targets_by_team_{pos}')
    soup = pos_make_soup(2019, pos)
    table = soup.find_all('table')[0]
    df = pd.read_html(str(table))[0]
    df.to_csv(f'FF_{year}_Targets_{pos}.csv', index=False)


# Grabs the ADP rank of the players for the upcoming years draft
print('ADP Values')
soup = ADP_make_soup()
table = soup.find_all('table')[0]
df = pd.read_html(str(table))[0]
df.to_csv('FF_2020_ADP.csv',  index=False)


end = time.time()
print('\nIt took ' + str(round((end - start), 2)) + ' seconds to gather your data.')
