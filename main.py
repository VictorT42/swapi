import requests
from sys import argv

if argv[1] == 'search':
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
        print(output)
