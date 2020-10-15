import re
import requests

import bs4


GROUP_NUMBER = re.compile(r'Group (\d+).*')


CONVERSION = {
    'All Adjectives': 'alladjectives',
    'Arts, Entertainment, & Literature': 'artsentlit',
    'Crime & the Law': 'crimelaw',
    'Feelings, Qualities, & States': 'feelqualstates',
    'Food & Eating': 'foodeat',
    'Health & the Body': 'healthbody',
    'Money & Work': 'moneywork',
    'The Natural World': 'natworld',
    'Lots of Nouns': 'lotsnouns',
    'Nouns? Verbs? Both!': 'nounsverbs',
    'Phrasal Verbs': 'phrasalverbs',
    'The Political World': 'poliworld',
    'Basic Science & Academia': 'scienceaca',
    'The Social World': 'socialworld',
    'Structures, Places, & Objects': 'structplaobj',
    'Transitions': 'transitions',
    'Verbs, Verbs, Verbs': 'verbsverbs',
    'War, Violence, & Conflict': 'warviocon',
}


def parse_words(category):

    if category not in CONVERSION:
        raise ValueError(f'{category} provided incorrect.')
    words = {}

    with open('gerry_website/general/page.html') as f:
        text = bs4.BeautifulSoup(f.read(), 'html.parser')

    category_tag = text.find('h3', id=CONVERSION[category])

    group_divs = category_tag.find_next_siblings('div')

    different_group_1 = False

    for div in group_divs:
        if 'sublist' in div.get('class', [])[0]:

            p_tags = div.find_all('p')

            for tag in p_tags:
                if not tag.strong:
                    continue

                if (match := GROUP_NUMBER.match(tag.strong.text)):
                    group = match.group(1)

                if group == '1' and different_group_1:
                    return words

                words[group] = [t.text.strip() for t in tag.find_all('a')]

                different_group_1 = True

    return words
