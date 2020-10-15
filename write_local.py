import json
import pprint
import time

import requests

import words
import exercise

CONVERSIONS = [
    'Food & Eating',
    'Transitions',
    'Crime & the Law',
    'The Social World',
    'Health & the Body',
    'Arts, Entertainment, & Literature',
    'All Adjectives',
    'Basic Science & Academia',
    'Lots of Nouns',
    'The Natural World',
    'Verbs, Verbs, Verbs',
    'Nouns? Verbs? Both!',
    'Money & Work',
    'Structures, Places, & Objects',
    'War, Violence, & Conflict',
    'The Political World',
    'Feelings, Qualities, and States',
    'Phrasal Verbs'
]

DICT = 'https://api.dictionaryapi.dev/api/v1/entries/en/{}'.format

def get_definition(word, sleep=1):
    data = requests.get(DICT(word))
    data = data.json()
    if isinstance(data, list):
        return data

    if data.get('title') == 'API Rate Limit Exceeded':
        if sleep % 5 == 0:
            print(f'Retrying {word}, now resting for {sleep} seconds.')
        time.sleep(sleep)
        return get_definition(word, sleep=sleep+1)

    if data.get('title') == 'No Definitions Found':
        return None



if __name__ == '__main__':
    current = ''
    content = {}

    aa = content.setdefault(current, {})

    for group, _words in words.parse_words(current).items():
        print(group)
        aa[group] = {}
        for word in _words:
            word_info = aa[group].setdefault('words', {})
            info = word_info.setdefault(
                word, {'customDefinition': '', 'dictionaryUrl': '', 'apiDefinitions': []}
            )

            query = get_definition(word)
            if query is None:
                print(f"Couldn't get definition for {word} of group {group}))")
            else:

                api_definitions = info['apiDefinitions']
                for q in query:
                    api_definitions.append({'definitions': []})
                    info_object = api_definitions[-1]

                    for word_type, definitions in q['meaning'].items():
                        for _definition in definitions:
                            _definition.update({'selected': True, 'type': word_type})
                            if 'example' not in _definition:
                                _definition.update({'example': ''})
                            if 'synonyms' not in _definition:
                                _definition.update({'synonyms': None})
                            info_object['definitions'].append(_definition)

                    info_object['phonetics'] = q['phonetics']
                    info_object['word'] = word
    print()

    for group, _exercise in exercise.parse_exercises(current).items():
        exercises = aa[group].setdefault('exercises', {})
        for subgroup, subexercise in _exercise.items():
            print(subexercise)
            exercises[subgroup] = {'questions': subexercise}

    with open('', 'w+') as f:
        json.dump(content, f)
