from sys import argv
import requests
import sqlitedict
import datetime


SEARCH_HISTORY = 0


def character_format(character):
    return '\n' + \
        f'Name: {character["name"]}\n' + \
        f'Height: {character["height"]}\n' + \
        f'Mass: {character["mass"]}\n' + \
        f'Birth Year: {character["birth_year"]}'


def homeworld_format(homeworld):
    year_ratio = '{0:.2f}'.format(int(homeworld["orbital_period"]) / 365)
    day_ratio = '{0:.2f}'.format(int(homeworld["rotation_period"]) / 24)

    return '\n\n\nHomeworld\n----------------\n' + \
        f'Name: {homeworld["name"]}\n' + \
        f'Population: {homeworld["population"]}\n\n' + \
        f'On {homeworld["name"]}, 1 year on earth is {year_ratio} years and 1 day is {day_ratio} days'


def search(search_string, world=False, search_cache=None, homeworld_cache=None):
    timestamp = datetime.datetime.now()

    if search_cache is not None:
        try:
            search_cache[SEARCH_HISTORY] += [(search_string, world, timestamp)]
        except KeyError:
            search_cache[SEARCH_HISTORY] = [(search_string, world, timestamp)]
        search_cache.commit()

    if search_cache is not None and search_string in search_cache:
        character = search_cache[search_string]['character']
        last_search_timestamp = search_cache[search_string]['time']

    else:
        last_search_timestamp = None

        raw_result = requests.get(f'https://www.swapi.tech/api/people/?name={search_string}')
        result = raw_result.json()['result']

        if len(result) == 0:
            print('\nThe force is not strong within you')
            return

        character = result[0]['properties']

        if search_cache is not None:
            search_cache[search_string] = {'time': timestamp, 'character': character}
            search_cache.commit()

    character_output = character_format(character)

    if world:
        if homeworld_cache is not None and character['homeworld'] in homeworld_cache:
            homeworld = homeworld_cache[character['homeworld']]

        else:
            raw_result = requests.get(character['homeworld'])
            result = raw_result.json()['result']

            homeworld = result['properties']

            if homeworld_cache is not None:
                homeworld_cache[character['homeworld']] = homeworld
                homeworld_cache.commit()

        homeworld_output = homeworld_format(homeworld)

    else:
        homeworld_output = ''

    print(character_output+homeworld_output)

    if last_search_timestamp:
        print(f'\n\ncached: {last_search_timestamp}')


def print_cache(search_cache, homeworld_cache):
    try:
        search_history = search_cache[SEARCH_HISTORY]
    except KeyError:
        print('Cache has been cleared since the last search')
        return

    for search_string, world, timestamp in search_history:
        output = '#'*120 + \
                 f'\nSEARCH:\n\n{search_string}\n' + \
                 f'\nTIME:\n\n{timestamp}\n' + \
                 f'\nRESULT:\n'

        if search_string in search_cache:
            character = search_cache[search_string]['character']
            character_output = character_format(character)

            if world:
                homeworld_output = homeworld_format(homeworld_cache[character['homeworld']])
            else:
                homeworld_output = ''

            output += character_output+homeworld_output

        else:
            output += 'The force is not strong within you'

        output += '\n\n'+'#'*120
        print(output)


def main():
    try:
        subcommand = argv[1]
    except IndexError:
        message = f'Usage:\n' + \
            f'\t{argv[0]} search \'character name\' [--world]\n' + \
            f'\t{argv[0]} cache (prints all searches)\n' + \
            f'\t{argv[0]} cache --clean (clears cache)'

        print(message)
        return

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
        try:
            if args_to_parse[0] == '--clean':
                search_cache.clear()
                search_cache.commit()
                homeworld_cache.clear()
                homeworld_cache.commit()
        except IndexError:
            print_cache(search_cache, homeworld_cache)

    search_cache.close()
    homeworld_cache.close()


if __name__ == '__main__':
    main()
