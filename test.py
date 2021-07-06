from gingerit.gingerit import GingerIt
import json
import logging
import re
import pycountry
from nltk import ngrams, word_tokenize
import country_converter as coco
import spacy

parser = GingerIt()


nlp = spacy.load('en_core_web_sm')
with open('data/state+country.json') as f:
    state_country_data = json.load(f)
with open('data/nationality.json') as f:
    nationality_dict = json.load(f)

cnt_lst = []
for i in range(len(state_country_data)):
    for key, value in state_country_data[i].items():
        cnt_lst.append(value.lower())
extra_conts = ["South Korea", 'Global', "Vietnam", "Russia", "Taiwan", "Czech Republic", "Curacao", "Venezuela",
               "Macedonia",
               "Hercegovina", "Bosnia", 'UK', 'USA', "Bolivia", 'Zealand', 'Saudi', 'republic of korea', 'korea', 'u s',
               'u.s.', 'u.k.']  # ,'Middle East','Latin America','Middle East and Africa']
continent_dict = {'Europe': 'Europe', 'LATAM': 'Latin America', 'Africa': "Africa", 'African': 'Africa',
                  "North American": "North America", "European": "Europe", "South American": "South America",
                  "Asian": "Asia", "Asia-Pacific": "Asia-Pacific", "Asia Pacific": "Asia-Pacific",
                  'Middle East': 'Middle East', 'Latin America': 'Latin America', 'North America': 'North America',
                  'South America': 'South America'}
cnt_lst = cnt_lst + extra_conts
cnt_lst = set(cnt_lst)


# Logging Methods
def log_load_info():
    logging.basicConfig(filename='log/market_value.log',
                        level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    return logging


def log_load_debug():
    logging.basicConfig(filename='log/market_value.log',
                        level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    return logging


logger_info = log_load_info()
logger_bug = log_load_debug()


def remove_punctuation(text):
    text = text.replace('USD', '$')
    text = text.replace('US$', '$')
    text = text.replace('usd', '$')
    text = text.replace('us$', '$')
    query = re.sub(r'[^A-Za-z0-9]+', ' ', text).strip()  # punctuations
    # query = re.sub(r'(?:^| )\w(?:$| )', ' ', query).strip()  # single letters
    query = re.sub(r'\s\s+', ' ', query).strip()
    # logger_info.info("Punctuation removal is completed."+query)
    return query


def normalize_location(loc):
    standard_country_name = coco.convert(names=loc, to='name_short')
    if standard_country_name != "not found":
        loc = standard_country_name
    return loc


def find_country(ad_1, source='pycountry'):
    # print('soutce:',source)
    ad_1 = remove_punctuation(ad_1)
    ad_1 = ' ' + ad_1.lower() + ' '
    country_list = list()
    if source == 'pycountry':
        for country in pycountry.countries:
            if ' ' + country.name.lower() + ' ' in ad_1:
                country_list.append(country.name)
    elif source == 'json':
        for country in cnt_lst:
            if ' ' + country.lower() + ' ' in ad_1:
                country_list.append(country)
        for nationality in nationality_dict.keys():
            if ' ' + nationality.lower() + ' ' in ad_1 and ' north american ' not in ad_1 and ' south amrican ' not in ad_1:
                country_list.append(list(nationality_dict.values())[list(nationality_dict.keys()).index(nationality)])
    elif source == 'eu':
        if ' eu 6 ' in ad_1 or ' eu-6 ' in ad_1 or 'eu6 ' in ad_1:
            country_list.extend(['eu 6', 'Belgium', 'France', 'Germany', 'Italy', 'Luxembourg', 'Netherlands'])
        elif ' eu 18 ' in ad_1 or ' eu-18 ' in ad_1 or ' eu 18 ' in ad_1:
            country_list.extend(
                ['eu 18', 'Austria', 'Belgium', 'Cyprus', 'Estonia', 'Finland', 'France', 'Germany', 'Greece',
                 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands', 'Portugal',
                 'Slovakia', 'Slovenia', 'Spain'])

    return country_list


def get_ngrams(text, n):
    n_grams_list = []
    n_grams = ngrams(word_tokenize(text), n)
    n_grams_list.extend([' '.join(grams).strip() for grams in n_grams])
    #     print('n_grams_list',n_grams_list)
    return n_grams_list


def get_country(ad_1, doc):
    # ad_1 = ad_1.replace('Zealand', 'New Zealand')
    # country_list = []
    # ad_1 = ' '.join(ad_1.split('-'))
    country_list = find_country(ad_1, source='pycountry')
    country_list.extend(find_country(ad_1, source='json'))
    country_list.extend(find_country(ad_1, source='eu'))
    entities_list = ['LOC', 'GPE']
    for ent in doc.ents:
        if ent.label_ in entities_list:
            txt = re.sub('[\W]', ' ', ' ' + ent.text.lower() + ' ')
            if ('u' in txt and 's' in txt and len(txt.strip()) == 2) or ('united' in txt and 'states' in txt):
                country_list.extend([ent.text])
    country_list = [i.lower() for i in country_list]
    # country_list = list(set(country_list))
    for i in country_list:
        ad_1 = ad_1.replace(i, '')
    # country_list = ['new Zealand' if i.lower() in 'zealand' else i for i in country_list]
    country_list = ['Saudi Arabia' if i.lower() in 'saudi' else i for i in country_list]
    country_list = list(set(country_list))

    if not country_list:
        bigrams = get_ngrams(ad_1, 2)
        for gram in bigrams:
            country_list = find_country(gram, source='pycountry')
            country_list.extend(find_country(gram, source='json'))
            country_list = [i.lower() for i in country_list]
            # country_list = list(set(country_list))
            for i in country_list:
                ad_1.replace(i, '')
            # country_list = ['new Zealand' if i.lower() in 'zealand' else i for i in country_list]
            country_list = ['Saudi Arabia' if i.lower() in 'saudi' else i for i in country_list]
            country_list = list(set(country_list))

    country_list = [i.capitalize() for i in country_list]
    return country_list


def get_continent(text):
    continent_list = []
    text = remove_punctuation(text)
    text = ' ' + text.lower() + ' '
    continents = ['Europe', 'Asia', 'Africa', 'North America', 'South America', 'Global']
    for continentality in continent_dict.keys():
        if ' ' + continentality.lower() + ' ' in text:
            continent_list.append(list(continent_dict.values())[list(continent_dict.keys()).index(continentality)])
    if not continent_list:
        for continent in continents:
            if ' ' + continent.lower() + ' ' in ' ' + str(text).lower() + ' ':
                continent_list.append(continent)

    return continent_list


def remove_geo_in_topic(text, doc=None, return_type='processed'):
    if doc == None:
        doc = nlp(text)
    url_s = ' ' + text.lower() + ' '
    url_s = str(url_s.lower())
    print("text:", url_s)
    final_text = list()
    normalized_countries = continent = list()
    location_list = list()
    try:
        geo = get_country(url_s, doc)
        continent = get_continent(url_s)
        # print("continent",continent)
        # print("geo",geo)
        country_list = geo
        continent_list = continent
        location_list = country_list + continent_list
        location_list = [x.lower() for x in location_list]
        # print("location_list",location_list)

        final_text = re.sub('|'.join("(?<=\s){}(?=\s)".format(i) for i in location_list), "", url_s)
        print("before",final_text)
        final_text = parser.parse(final_text)
        final_text = dict((k, final_text[k]) for k in ['result'] if k in final_text)
        final_text= " ".join(final_text.values())
        final_text = [final_text]
    except Exception as e:
        print('Exception at find_geo_tag_topic', e)
        logger_bug.exception('Exception at find_geo_tag_topic' + str(e))

    return final_text


if __name__ == '__main__':
    # url_dict = dict()
    # url = 'https://www.strategymrc.com/report/agricultural-biologicals-market-united-states'
    # url_s = "Country-Bosnia-Zealand-US-Saudi-Hercegovina-November-13799257"
    # # url_s = url_s.lower()
    # url_dict['rem_url'] = url_s.replace("-", " ")
    # print(find_geo_tag_topic(url_dict))
    text = '''Asia-Pacific was the highest revenue contributor, accounting for $84.84 billion in 2019 '''

    print(remove_geo_in_topic(text))
