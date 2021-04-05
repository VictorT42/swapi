import requests
from sys import argv


if argv[1] == 'search':
    world = argv[3] == '--world'

    raw_result = requests.get(f'https://www.swapi.tech/api/people/?name={argv[2]}')
    result = raw_result.json()['result']

    if len(result) == 0:
        print('\nThe force is not strong within you')
        exit(0)

    else:
        character = result[0]['properties']

        output = '\n' + \
            f'Name: {character["name"]}\n' + \
            f'Height: {character["height"]}\n' + \
            f'Mass: {character["mass"]}\n' + \
            f'Birth Year: {character["birth_year"]}'

        if world:
            raw_result = requests.get(character['homeworld'])
            result = raw_result.json()['result']

            homeworld = result['properties']

            year_ratio = '{0:.2f}'.format(int(homeworld["orbital_period"])/365)
            day_ratio = '{0:.2f}'.format(int(homeworld["rotation_period"])/24)

            output += '\nHomeworld\n----------------\n' + \
                f'Name: {homeworld["name"]}\n' + \
                f'Population: {homeworld["population"]}\n\n' + \
                f'On {homeworld["name"]}, 1 year on earth is {year_ratio} years and 1 day is {day_ratio} days'

        print(output)
