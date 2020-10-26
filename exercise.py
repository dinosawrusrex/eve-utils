import os
import re
import string

import bs4

GENERAL_CONVERSION = {
    'Food & Eating': 'food_eat',
    'Transitions': 'transitions',
    'Crime & the Law': 'crime_law',
    'The Social World': 'socialworld',
    'Health & the Body': 'health_body',
    'Arts, Entertainment, & Literature': 'arts_ent_lit',
    'All Adjectives': 'adjectives',
    'Basic Science & Academia': 'science_academia',
    'Lots of Nouns': 'nouns',
    'The Natural World': 'naturalworld',
    'Verbs, Verbs, Verbs': 'verbsverbsverbs',
    'Nouns? Verbs? Both!': 'nounverb',
    'Money & Work': 'money_work',
    'Structures, Places, & Objects': 'structures',
    'War, Violence, & Conflict': 'war_conflict',
    'The Political World': 'politics',
    'Feelings, Qualities, and States': 'feelings',
    'Phrasal Verbs': 'phrasalverbs'
}

ACADEMIC_CONVERSION = {
    'Sublist 1': 'sublist1',
    'Sublist 2': 'sublist2',
    'Sublist 3': 'sublist3',
    'Sublist 4': 'sublist4',
    'Sublist 5': 'sublist5',
    'Sublist 6': 'sublist6',
    'Sublist 7': 'sublist7',
    'Sublist 8': 'sublist8',
    'Sublist 9': 'sublist9',
    'Sublist 10': 'sublist10',
}

GENERAL_NAME_FILTER = filter(lambda f: GENERAL_CONVERSION[category] in f.lower(), os.listdir('gerry_website/general'))

def files_filter(category, conversion):

    if 'Sublist' not in category:
        return filter(lambda f: conversion[category] in f.lower(), os.listdir('gerry_website/general'))

    sublist, _, group = category.partition(' ')
    if len(group) == 1:
        group = '0' + group
    return filter(lambda f: sublist+group in f, os.listdir('gerry_website/academic'))


GENERAL_DIRECTORY = 'gerry_website/general/{}'.format
ACADEMIC_DIRECTORY = 'gerry_website/academic/{}'.format


def parse_exercises(category):

    if category not in GENERAL_CONVERSION and category not in ACADEMIC_CONVERSION:
        raise ValueError(f'{category} provided incorrect')
    exercises = {}

    CONVERSION = GENERAL_CONVERSION if category in GENERAL_CONVERSION else ACADEMIC_CONVERSION
    DIRECTORY = GENERAL_DIRECTORY if category in GENERAL_CONVERSION else ACADEMIC_DIRECTORY

    for name in sorted(files_filter(category, CONVERSION)):

        group, subgroup = _get_group_subgroup(name)

        try:
            questions_and_answers = _parse_htm(DIRECTORY(name))
        except TypeError:
            try:
                questions_and_answers = _parse_htm(DIRECTORY(name), certain_phrasal_verbs=True)
            except TypeError:
                raise TypeError(f'Failed to parse {name}')

        subcategory = exercises.setdefault(group, {})
        subcategory[subgroup] = questions_and_answers

    return exercises


CATEGORY_GROUP = re.compile(r'EngVocEx_\D+_(\d+).*')
CATEGORY_SUBGROUP = re.compile(r'EngVocEx_\D+_\d+[-_](\d+).htm')

PHRASAL_VERB_GROUP = re.compile(r'PhrasalVerbsGroup(\d+).*')
PHRASAL_VERB_SUBGROUP = re.compile(r'PhrasalVerbsGroup\d+-(\d+).htm')

ACADEMIC_GROUP_SUBGROUP = re.compile(r'AWLSublist\d+-Ex(\d)([a-e]).htm')
ACADEMIC_SUBGROUP_CONVERSION = string.ascii_letters[:5]


def _get_group_subgroup(file_name):

    if file_name.lower().startswith('phrasalverbs'):
        return PHRASAL_VERB_GROUP.match(file_name).group(1), PHRASAL_VERB_SUBGROUP.match(file_name).group(1)

    group_match = CATEGORY_GROUP.match(file_name)
    subgroup_match = CATEGORY_SUBGROUP.match(file_name)

    if 'phrasalverbs' in file_name.lower():
        return group_match.group(1), subgroup_match.group(1)
    if group_match:
        if not subgroup_match:
            return '1', group_match.group(1)
        return group_match.group(1), subgroup_match.group(1)

    if 'AWLSublist' in file_name:
        if (match := ACADEMIC_GROUP_SUBGROUP.match(file_name)):
            return match.group(1), ACADEMIC_SUBGROUP_CONVERSION.index(match.group(2))+1

    raise ValueError(f'Could not get name or group for {file_name}')


def _parse_htm(file_name, certain_phrasal_verbs=False):

    answer_id = 's0_0' if not certain_phrasal_verbs else 'R_0'
    default_option_value = 'x' if not certain_phrasal_verbs else '-1'

    with open(file_name) as f:
        text = bs4.BeautifulSoup(f.read(), 'html.parser')

    questions = text.find_all('td', class_='LeftItem')
    answer_options = text.find('select', id=answer_id)

    answers = {}
    for answer in answer_options:
        if isinstance(answer, bs4.element.Tag) and answer.get('value') != default_option_value:
            answers[int(answer.get('value'))] = answer.text

    questions_and_answers = []
    for question in questions:
        index, statement = _split_id_and_question(question, certain_phrasal_verbs=certain_phrasal_verbs)
        questions_and_answers.append({'answer': answers[index], 'question': statement})

    return questions_and_answers


ANSWER_FROM_INDEX = re.compile(r's(\d+)_\d+')

def _split_id_and_question(question, certain_phrasal_verbs=False):

    if not certain_phrasal_verbs:
        if (match := ANSWER_FROM_INDEX.match(question.next_sibling.contents[0].get('id'))):
            index = int(match.group(1))
    else:
        index = int(question.get('id').split('_')[-1])

    question = question.text.partition('.')[-1].lstrip()
    return index, question.lstrip()
