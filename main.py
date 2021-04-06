from sys import argv
import requests
import sqlitedict
import datetime


def search(search_string, world=False, search_cache=None, homeworld_cache=None):

    last_search_timestamp = None

    if search_cache and search_string in search_cache:
        character = search_cache[search_string]['character']
        last_search_timestamp = search_cache[search_string]['time']

    else:
        raw_result = requests.get(f'https://www.swapi.tech/api/people/?name={search_string}')
        result = raw_result.json()['result']

        if len(result) == 0:
            print('\nThe force is not strong within you')
            exit(0)

        character = result[0]['properties']

        if search_cache is not None:
            search_cache[search_string] = {'time': datetime.datetime.now(), 'character': character}
            search_cache.commit()

    character_output = '\n' + \
        f'Name: {character["name"]}\n' + \
        f'Height: {character["height"]}\n' + \
        f'Mass: {character["mass"]}\n' + \
        f'Birth Year: {character["birth_year"]}'

    if world:
        if homeworld_cache and character['homeworld'] in homeworld_cache:
            homeworld = homeworld_cache[character['homeworld']]

        else:
            raw_result = requests.get(character['homeworld'])
            result = raw_result.json()['result']

            homeworld = result['properties']

            if homeworld_cache is not None:
                homeworld_cache[character['homeworld']] = homeworld
                homeworld_cache.commit()

        year_ratio = '{0:.2f}'.format(int(homeworld["orbital_period"])/365)
        day_ratio = '{0:.2f}'.format(int(homeworld["rotation_period"])/24)

        homeworld_output = '\n\n\nHomeworld\n----------------\n' + \
            f'Name: {homeworld["name"]}\n' + \
            f'Population: {homeworld["population"]}\n\n' + \
            f'On {homeworld["name"]}, 1 year on earth is {year_ratio} years and 1 day is {day_ratio} days'

    else:
        homeworld_output = ''

    print(character_output+homeworld_output)

    if last_search_timestamp:
        print(f'\n\ncached: {last_search_timestamp}')


subcommand = argv[1]
args_to_parse = argv[2:]

search_cache = sqlitedict.SqliteDict('./.cache', tablename='searches')
homeworld_cache = sqlitedict.SqliteDict('./.cache', tablename='worlds')

if subcommand == 'search':
    try:
        args_to_parse.remove('--world')
        world = True
    except ValueError:
        world = False

    if len(args_to_parse) != 1:
        print('Please give the name of one character to search')

    search(args_to_parse[0], world, search_cache, homeworld_cache)
elif subcommand == 'cache':
    if args_to_parse[0] == '--clean':
        search_cache.clear()
        search_cache.commit()
        homeworld_cache.clear()
        homeworld_cache.commit()

search_cache.close()
homeworld_cache.close()
