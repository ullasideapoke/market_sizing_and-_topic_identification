import ast
from multiprocessing import Process

from logging_method import define_logging
from functools import partial
from itertools import repeat
from multiprocessing import Pool, freeze_support

logger_info, logger_bug = define_logging('log/market_value.log')
import get_elements
import spacy
from multiprocessing.pool import ThreadPool

nlp = spacy.load('en_core_web_sm')
import nltk
import re
import datetime

now = datetime.datetime.now()
nltk.download('punkt')
import json

from transformers import pipeline

'''
Installation: Ubuntu (https://pytorch.org/get-started/locally/)
pip install torch==1.8.0+cpu torchvision==0.9.0+cpu torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html
pip install transformers
'''

print('Loading Pipeline and Model')
qa_ppl = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')
print('Model Loaded')
with open('data/currency.json', 'r') as f:
    currency_json = json.load(f)


def text_correction(text):
    text = ' ' + text + ' '
    text = text.replace('(', '')
    text = text.replace(')', '')
    text = text.replace(' emea ', 'Europe, Middle East, Africa')
    text = text.replace('~', '')
    text = text.replace('A $', ' AUD ')
    text = text.replace(' R ', ' ZAR ')
    text = text.replace('C $', ' CAD ')
    text = text.replace('S $', ' SGD ')
    text = text.replace('SG $', ' SGD ')
    text = text.replace('HK $', ' HKD ')
    text = text.replace('CN ¥', ' CNY ')
    text = text.replace('$', ' $ ')
    text = text.replace(' one ', '1')
    text = text.replace(' two ', '2')
    text = text.replace(' three ', '3')
    text = text.replace(' four ', '4')
    text = text.replace(' five ', '5')
    text = text.replace(' six ', '6')
    text = text.replace(' seven ', '7')
    text = text.replace(' eight ', ' 8 ')
    text = text.replace(' nine ', '9')
    text = text.replace(' ten ', '10')
    text = text.replace(' eleven ', '11')
    text = text.replace(' twelve ', '12')
    text = text.replace(' thirteen ', '13')
    text = text.replace('percentage', '%')
    text = text.replace('percent', '%')
    text = text.replace('per cent', '%')
    text = text.replace('Pvt.', 'Pvt')
    text = text.replace('- ', '-')
    text = text.replace(' -', '-')
    text = text.replace('–', '-')
    text = text.replace('-', '-')
    text = text.replace('Â', ' ')
    text = text.replace('￦', ' KRW ')
    text = text.replace('₩', ' KRW ')
    text = text.replace('₽', ' RUB ')
    text = text.replace('元', ' CNY ')
    text = text.replace('￡', ' GBP ')
    text = text.replace('GB£', ' GBP ')
    text = text.replace('GB ￡', ' GBP ')
    text = text.replace('UKP', ' GBP ')

    text = text.replace('JP¥', ' JPY ')
    text = text.replace('JP ¥', ' JPY ')
    text = text.replace('元', ' CNY ')
    text = text.replace('руб', ' RUB ')
    text = text.replace('australian dollars', ' AUD ')
    text = text.replace('Australian Dollars', ' AUD ')
    text = text.replace('Australian dollars', ' AUD ')
    text = text.replace('australian dollar', ' AUD ')
    text = text.replace('Australian Dollar', ' AUD ')
    text = text.replace('Australian dollar', ' AUD ')
    text = text.replace('canadian dollar', ' CAD ')
    text = text.replace('Canadian Dollars', ' CAD ')
    text = text.replace('Canadian Dollar', ' CAD ')
    text = text.replace('Canadian dollars', ' CAD ')
    text = text.replace('canadian dollars', ' CAD ')
    text = text.replace('Canadian dollar', ' CAD ')
    text = text.replace('yuan renminbi', ' CNY ')
    text = text.replace('Yuan Renminbi', ' CNY ')
    text = text.replace('Yuan renminbi', ' CNY ')
    text = text.replace('chinese yuan', ' CNY ')
    text = text.replace('Chinese Yuan', ' CNY ')
    text = text.replace('Chinese yuan', ' CNY ')
    text = text.replace('pound sterling', ' GBP ')
    text = text.replace('Pound Sterling', ' GBP ')
    text = text.replace('Pound sterling', ' GBP ')
    text = text.replace('hong kong dollar', ' HKD ')
    text = text.replace('hong kong dollars', ' HKD ')
    text = text.replace('Hong Kong Dollar', ' HKD ')
    text = text.replace('Hong Kong Dollars', ' HKD ')
    text = text.replace('Hong Kong dollars', ' HKD ')
    text = text.replace('Hong Kong dollar', ' HKD ')
    text = text.replace('new israeli sheqel', ' ILS ')
    text = text.replace('New Israeli Sheqel', ' ILS ')
    text = text.replace('New Israeli sheqel', ' ILS ')
    text = text.replace('indian rupee', ' INR ')
    text = text.replace('indian rupees', 'INR')
    text = text.replace('Indian Rupee', ' INR ')
    text = text.replace('Indian rupee', ' INR ')
    text = text.replace('Indian Rupees', ' INR ')
    text = text.replace('Indian rupees', ' INR ')
    text = text.replace('Russian Ruble', ' RUB ')
    text = text.replace('russian rubles', ' RUB ')
    text = text.replace('Russian ruble', ' RUB ')
    text = text.replace('Russian Rubles', ' RUB ')
    text = text.replace('Russian rubles', ' RUB ')
    text = text.replace('Singapore Dollar', ' SGD ')
    text = text.replace('singapore dollars', ' SGD ')
    text = text.replace('Singapore dollar', ' SGD ')
    text = text.replace('Singapore Dollar', ' SGD ')
    text = text.replace('Singapore Dollars', ' SGD ')
    text = text.replace('Singapore dollars', ' SGD ')
    text = text.replace(' usd', ' USD ')
    text = text.replace('American Dollar', ' USD ')
    text = text.replace('American Dollars', ' USD ')
    text = text.replace('American dollars', ' USD ')
    text = text.replace('american dollar', ' USD ')
    text = text.replace('American dollar', ' USD ')
    text = text.replace('american dollars', ' USD ')
    text = text.replace('sg dollar', 'SGD ')
    text = text.replace('sg dollars', 'SGD ')
    text = text.replace('SG Dollar', 'SGD ')
    text = text.replace('SG dollars', 'SGD ')
    text = text.replace('SG Dollars', 'SGD ')
    text = text.replace('SG dollar', 'SGD ')

    text = text.replace('₹', ' INR ')
    text = text.replace(' rs ', 'INR ')
    text = text.replace('r.s', 'INR ')
    # text = text.replace('INR', '₹')
    # text = text.replace('$', 'USD')
    text = text.replace('us$', 'USD ')
    text = text.replace('us $', 'USD ')
    text = text.replace('au $', 'AUD ')
    text = text.replace('ca $', 'CAD ')
    text = text.replace('s$', 'SGD ')
    # text = text.replace('USD ', 'USD')
    # text = text.replace('usd', 'USD')
    # text = text.replace('us$', 'USD')
    # text = text.replace(' us $', ' USD')
    # text = text.replace(' us dollars', ' USD')
    text = text.replace(' cr ', ' crore ')
    # print('cr replace:',text)
    text = text.replace(' Cr ', ' crore ')
    text = text.replace('Crore ', ' crore ')
    text = text.replace('Crores ', ' crore ')
    text = text.replace('crores ', ' crore ')
    text = text.replace('Million ', 'million ')
    text = text.replace('Billion ', ' billion ')
    text = text.replace('Trillion ', ' trillion ')
    text = text.replace('million ', ' million ')
    text = text.replace('billion ', ' billion ')
    text = text.replace('trillion ', ' trillion ')
    text = text.replace('mn ', ' million ')
    text = text.replace('bn ', ' billion ')
    text = text.replace('tn ', ' trillion ')
    text = text.replace('Mn ', ' million ')
    text = text.replace('Bn ', ' billion ')
    text = text.replace('Tn ', ' trillion ')
    text = text.replace('tn ', ' trillion ')
    text = text.replace(' $ ', ' USD ')
    text = text.replace('$', ' USD ')
    text = text.replace(' %', '%')
    text = re.sub('\%+', '%', text)
    text = re.sub(r'[ECMPI]ST|UTC', '', text)
    text = re.sub('\s{2-}', '', text)

    # print('after processing: ', text)

    corrected_words = dict()
    for i in text.split():  # 400mn 330bn

        if re.findall('[0-9]+', i) and not i[0].isalpha():
            if len(re.findall('[a-zA-Z]', i)) < 3:

                if "M" in i:
                    i_new = i.replace("M", " million")
                    corrected_words[i] = i_new
                elif "m" in i:
                    i_new = i.replace("m", " million")
                    corrected_words[i] = i_new
                elif "Mn" in i:
                    i_new = i.replace("Mn", " million")
                    corrected_words[i] = i_new
                elif "mn" in i:
                    i_new = i.replace("mn", " million")
                    corrected_words[i] = i_new

                elif "B" in i:
                    i_new = i.replace("B", " billion")
                    corrected_words[i] = i_new
                elif "b" in i:
                    i_new = i.replace("b", " billion")
                    corrected_words[i] = i_new
                elif "bn" in i:
                    i_new = i.replace("bn", " billion")
                    corrected_words[i] = i_new
                elif "Bn" in i:
                    i_new = i.replace("Bn", " Billion")
                    corrected_words[i] = i_new

                elif "K" in i:
                    i_new = i.replace("K", " thousand")
                    corrected_words[i] = i_new
                elif "k" in i:
                    i_new = i.replace("k", " thousand")
                    corrected_words[i] = i_new
                elif "cr" in i:
                    i_new = i.replace("cr", " crore")
                    corrected_words[i] = i_new
                elif "Cr" in i:
                    i_new = i.replace("Cr", " crore")
                    corrected_words[i] = i_new

    new_text_list = []

    for i in text.split():

        if i in corrected_words.keys():
            new_text_list.append(corrected_words[i])
        else:
            new_text_list.append(i)

    return " ".join(new_text_list).strip()


def has_num(text):
    if re.findall('[0-9]+', text):
        return True
    else:
        return False


def get_sorted_amount(
        chunk_list):  # function that also handles cases with current_value having multi-digit MILLION and projected_value having single digit BILLION, etc
    print('Sorting amounts: ' + str(chunk_list))
    logger_info.info('Sorting amounts: ' + str(chunk_list))
    trillion_numbers = list(set([float(re.findall('[0-9]+\.?[0-9]*', i)[0]) for i in chunk_list if
                                 has_num(i) and 'trillion' in i.lower()]))
    billion_numbers = list(set([float(re.findall('[0-9]+\.?[0-9]*', i)[0]) for i in chunk_list if
                                has_num(i) and 'billion' in i.lower()]))
    million_numbers = list(set([float(re.findall('[0-9]+\.?[0-9]*', i)[0]) for i in chunk_list if
                                has_num(i) and 'million' in i.lower()]))
    thousand_numbers = list(set([float(re.findall('[0-9]+\.?[0-9]*', i)[0]) for i in chunk_list if
                                 has_num(i) and 'thousand' in i.lower()]))
    crore_numbers = list(set([float(re.findall('[0-9]+\.?[0-9]*', i)[0]) for i in chunk_list if
                              has_num(i) and 'crore' in i.lower()]))
    sorted_amount_list = list()
    sorted_trillion = list()
    sorted_billion = list()
    sorted_million = list()
    sorted_thousand = list()
    sorted_crore = list()
    numbers_list = [trillion_numbers, billion_numbers, crore_numbers, million_numbers, thousand_numbers]
    for idx, numbers in enumerate(numbers_list):
        if numbers:
            numbers = sorted(numbers)  # 1.0, 1.2
            #               amount_num = numbers[0]
            for amount_num in numbers:  # 1.2
                for i in chunk_list:  # string of money ($ 1 billion, $ 1.2 billion, etc)
                    if str(amount_num).split('.')[1] == str(0) and str(amount_num).split('.')[0] in i:
                        if idx == 0 and i not in sorted_trillion:
                            sorted_trillion.extend([i])
                        if idx == 1 and i not in sorted_billion:
                            sorted_billion.extend([i])
                        if idx == 2 and i not in sorted_crore:
                            sorted_crore.extend([i])
                        if idx == 3 and i not in sorted_million:
                            sorted_million.extend([i])
                        if idx == 4 and i not in sorted_thousand:
                            sorted_thousand.extend([i])

                    elif str(amount_num) in i:
                        if idx == 0 and i not in sorted_trillion:
                            sorted_trillion.extend([i])
                        if idx == 1 and i not in sorted_billion:
                            sorted_billion.extend([i])
                        if idx == 2 and i not in sorted_crore:
                            sorted_crore.extend([i])
                        if idx == 3 and i not in sorted_million:
                            sorted_million.extend([i])
                        if idx == 4 and i not in sorted_thousand:
                            sorted_thousand.extend([i])
    # print('sorted_million:',sorted_million)
    sorted_amount_list.extend(sorted_thousand)
    sorted_amount_list.extend(sorted_million)
    sorted_amount_list.extend(sorted_billion)
    sorted_amount_list.extend(sorted_crore)
    sorted_amount_list.extend(sorted_trillion)
    print('After sorting amounts: ' + str(chunk_list))
    logger_info.info('After sorting amounts: ' + str(chunk_list))
    return sorted_amount_list


def combine_results(proj_value_dict, cagr_dict, upper_year_dict, current_year_dict, current_value_dict,
                    current_year_value):
    '''
    Expected :
    {'Germany':{'location':'country','lower_year':2019,'cagr':'2.3%'}, 'Europe':{'location':'continent','upper_year':2019,'cagr':'2.3%'}}
    '''
    print('Comnbingin results...')
    logger_info.info('Comnbingin results...')
    loc_wise_dict = dict()
    dict_list = [proj_value_dict, cagr_dict, upper_year_dict, current_year_dict, current_value_dict, current_year_value]
    for temp_dict_list in dict_list:
        # print('temp_dict_list:',temp_dict_list)
        for dictionary in temp_dict_list:

            if 'continent' in dictionary.keys() and dictionary['continent']:
                loc_wise_dict[dictionary['continent']] = dict()
                loc_wise_dict[dictionary['continent']]['location'] = 'continent'
            if 'country' in dictionary.keys() and dictionary['country']:
                loc_wise_dict[dictionary['country']] = dict()
                loc_wise_dict[dictionary['country']]['location'] = 'country'
    # print('Keys present:',loc_wise_dict,loc_wise_dict.keys())

    for temp_dict_list in dict_list:
        # print('temp_dict_list before inside:', temp_dict_list)
        for key in loc_wise_dict.keys():
            for dictionary in temp_dict_list:
                # print('checking for key: ',key,loc_wise_dict[key]['location'])
                # print(loc_wise_dict[key],' inside dictionary: key:',key,"loc_wise_dict[key]['location'] == 'continent'",loc_wise_dict[key]['location'] == 'continent','---','dictionary',dictionary,'loc_wise_dict',loc_wise_dict)
                if loc_wise_dict[key]['location'] == 'continent' and (
                        'continent' in dictionary.keys() and dictionary['continent'] == key):

                    # print('dictionaries: ',dictionary,key,loc_wise_dict)
                    if 'projected_value' in dictionary.keys() and key in dictionary['continent']:
                        loc_wise_dict[key]['projected_value'] = dictionary['projected_value']
                        loc_wise_dict[key]['score_projected_value'] = dictionary['score_projected_value']
                    if 'current_value' in dictionary.keys() and key in dictionary['continent']:
                        loc_wise_dict[key]['current_value'] = dictionary['current_value']
                        loc_wise_dict[key]['score_current_value'] = dictionary['score_current_value']
                    if 'cagr' in dictionary.keys() and key in dictionary['continent']:
                        loc_wise_dict[key]['cagr'] = dictionary['cagr']
                        loc_wise_dict[key]['score_cagr'] = dictionary['score_cagr']
                    if 'cagr_lower_year' in dictionary.keys() and key in dictionary['continent']:
                        loc_wise_dict[key]['cagr_lower_year'] = dictionary['cagr_lower_year']
                        loc_wise_dict[key]['score_lower_year_cagr'] = dictionary['score_lower_year_cagr']
                    if 'value_lower_year' in dictionary.keys() and key in dictionary['continent']:
                        loc_wise_dict[key]['value_lower_year'] = dictionary['value_lower_year']
                        loc_wise_dict[key]['score_lower_year_value'] = dictionary['score_lower_year_value']
                    if 'upper_year' in dictionary.keys() and key in dictionary['continent']:
                        loc_wise_dict[key]['upper_year'] = dictionary['upper_year']
                        loc_wise_dict[key]['score_upper_year'] = dictionary['score_upper_year']

                elif loc_wise_dict[key]['location'] == 'country' and (
                        'country' in dictionary.keys() and dictionary['country'] == key):
                    # print('elif statements: ',loc_wise_dict[key],dictionary.keys(),key,'projected_value' in list(dictionary.keys()))#,key in dictionary['country'])
                    if 'projected_value' in dictionary.keys() and key in dictionary['country']:
                        loc_wise_dict[key]['projected_value'] = dictionary['projected_value']
                        loc_wise_dict[key]['score_projected_value'] = dictionary['score_projected_value']
                    if 'current_value' in dictionary.keys() and key in dictionary['country']:
                        loc_wise_dict[key]['current_value'] = dictionary['current_value']
                        loc_wise_dict[key]['score_current_value'] = dictionary['score_current_value']
                    if 'cagr' in dictionary.keys() and key in dictionary['country']:
                        loc_wise_dict[key]['cagr'] = dictionary['cagr']
                        loc_wise_dict[key]['score_cagr'] = dictionary['score_cagr']
                    if 'cagr_lower_year' in dictionary.keys() and key in dictionary['country']:
                        loc_wise_dict[key]['cagr_lower_year'] = dictionary['cagr_lower_year']
                        loc_wise_dict[key]['score_lower_year_cagr'] = dictionary['score_lower_year_cagr']
                    if 'value_lower_year' in dictionary.keys() and key in dictionary['country']:
                        loc_wise_dict[key]['value_lower_year'] = dictionary['value_lower_year']
                        loc_wise_dict[key]['score_lower_year_value'] = dictionary['score_lower_year_value']
                    if 'upper_year' in dictionary.keys() and key in dictionary['country']:
                        loc_wise_dict[key]['upper_year'] = dictionary['upper_year']
                        loc_wise_dict[key]['score_upper_year'] = dictionary['score_upper_year']
    print('After combining: ' + str(loc_wise_dict))
    logger_info.info('After combining: ' + str(loc_wise_dict))
    return loc_wise_dict


def process_dict(filtered_dict):
    '''
    Input: {'U s': {'location': 'country', 'projected_value': 'usd 30.2 million',
     'score_projected_value': 0.9407963156700134, 'cagr': '',
     'score_cagr': 0.38772252202033997, 'current_value': '',
      'score_current_value': 0.9242439270019531},
      'China': {'location': 'country', 'cagr': '3.8%',
      'score_cagr': 0.9660698771476746, 'upper_year': '3.8%',
      'score_upper_year': 0.775578498840332}}
    '''
    print('Reformatting dictionary..')
    logger_info.info('Reformatting dictionary..')
    final_dict_list = list()
    for loc in filtered_dict.keys():
        main_keys = ['cagr', 'upper_year', 'cagr_lower_year', 'value_lower_year', 'current_value', 'projected_value']
        loc_dict = dict()
        for key in main_keys:
            loc_dict[key] = ''
        loc_dict[filtered_dict[loc]['location']] = loc
        for key in filtered_dict[loc].keys():
            loc_dict[key] = str(filtered_dict[loc][key]).strip()
        for key in main_keys:
            if 'score_' + key in loc_dict.keys() and loc_dict[key] == '':
                del loc_dict['score_' + key]
        del loc_dict['location']
        final_dict_list.append(loc_dict)
    for each_dict in final_dict_list:
        if 'country' in each_dict.keys():
            country = get_elements.find_geo(each_dict['country'], nlp(each_dict['country']), return_type='processed')

            if country[0]:
                each_dict['country'] = country[0]
        if 'continent' in each_dict.keys():
            continent = get_elements.find_geo(each_dict['continent'], nlp(each_dict['continent']),
                                              return_type='processed')

            if continent[1]:
                each_dict['continent'] = continent[1]

    return final_dict_list


def sort_list_within_list(list_, reverse):
    list_.sort(reverse=reverse, key=lambda x: x[0])
    return list_


def handle_years(in_dict, loc):
    try:
        if 'cagr_lower_year' in in_dict[loc].keys():
            print('Getting Lower Year for CAGR: ' + str(in_dict[loc]))
            logger_info.info('Getting Lower Year for CAGR: ' + str(in_dict[loc]))
            if re.findall('\d{4}', in_dict[loc]['cagr_lower_year'].lower()):
                years = re.findall('\d{4}', in_dict[loc]['cagr_lower_year'].lower())
                year_split = [int(i) for i in years]

                year_split.sort()
                if len(year_split) > 1:
                    in_dict[loc]['cagr_lower_year'] = year_split[0]
                    in_dict[loc]['cagr_lower_year'] = year_split[-1]
                elif len(year_split) == 1:
                    if 'upper_year' in in_dict[loc].keys() and in_dict[loc]['score_upper_year'] > in_dict[loc][
                        'score_lower_year_cagr']:
                        in_dict[loc]['upper_year'] = year_split[0]
                        in_dict[loc]['cagr_lower_year'] = ''
                    else:
                        in_dict[loc]['cagr_lower_year'] = year_split[0]
                        in_dict[loc]['upper_year'] = ''
            elif '%' in in_dict[loc]['cagr_lower_year']:
                in_dict[loc]['cagr_lower_year'] = ''
            else:
                in_dict[loc]['cagr_lower_year'] = ''
        elif 'upper_year' in in_dict[loc].keys():
            print('Getting Upper Year: ' + str(in_dict[loc]))
            logger_info.info('Getting Upper Year: ' + str(in_dict[loc]))
            if re.findall('\d{4}', in_dict[loc]['upper_year'].lower()):
                years = re.findall('\d{4}', in_dict[loc]['upper_year'])
                year_split = [int(i) for i in years]
                year_split.sort()
                if len(year_split) > 1:
                    in_dict[loc]['cagr_lower_year'] = year_split[0]
                    in_dict[loc]['upper_year'] = year_split[-1]
                elif len(year_split) == 1:
                    if 'cagr_lower_year' in in_dict[loc].keys() and in_dict[loc]['score_lower_year_cagr'] > \
                            in_dict[loc][
                                'upper_year']:
                        in_dict[loc]['cagr_lower_year'] = year_split[0]
                        in_dict[loc]['upper_year'] = ''
                    else:
                        in_dict[loc]['upper_year'] = year_split[0]
                        in_dict[loc]['cagr_lower_year'] = ''
            elif '%' in in_dict[loc]['upper_year']:
                in_dict[loc]['upper_year'] = ''
            else:
                in_dict[loc]['upper_year'] = ''
        if 'value_lower_year' in in_dict[loc].keys():
            print('Getting Lower Year for Value: ' + str(in_dict[loc]))
            logger_info.info('Getting Lower Year for Value: ' + str(in_dict[loc]))
            if re.findall('\d{4}', in_dict[loc]['value_lower_year'].lower()):
                years = re.findall('\d{4}', in_dict[loc]['value_lower_year'].lower())
                print('lower year regex: ', re.findall('\d{4}', in_dict[loc]['value_lower_year'].lower()))
                year_split = [int(i) for i in years]

                year_split.sort()
                if len(year_split) > 1:
                    in_dict[loc]['value_lower_year'] = year_split[0]
                    in_dict[loc]['upper_year'] = year_split[-1]
                elif len(year_split) == 1:
                    # print('upper year......', in_dict[loc].keys())
                    if ('upper_year' in in_dict[loc].keys() and 'score_upper_year' in in_dict[loc].keys()) and \
                            in_dict[loc][
                                'score_upper_year'] > in_dict[loc]['score_lower_year_value']:
                        in_dict[loc]['upper_year'] = year_split[0]
                        in_dict[loc]['value_lower_year'] = ''
                    else:
                        in_dict[loc]['value_lower_year'] = year_split[0]
                        in_dict[loc]['upper_year'] = ''
            elif '%' in in_dict[loc]['value_lower_year']:
                in_dict[loc]['value_lower_year'] = ''
            else:
                in_dict[loc]['value_lower_year'] = ''
        elif 'upper_year' in in_dict[loc].keys():
            if re.findall('\d{4}', str(in_dict[loc]['upper_year'])):
                years = re.findall('\d{4}', str(in_dict[loc]['upper_year']))
                year_split = [int(i) for i in years]
                year_split.sort()
                if len(year_split) > 1:
                    in_dict[loc]['value_lower_year'] = year_split[0]
                    in_dict[loc]['upper_year'] = year_split[-1]
                elif len(year_split) == 1:
                    if 'value_lower_year' in in_dict[loc].keys() and in_dict[loc]['score_lower_year_value'] > \
                            in_dict[loc][
                                'upper_year']:
                        in_dict[loc]['value_lower_year'] = year_split[0]
                        in_dict[loc]['upper_year'] = ''
                    else:
                        in_dict[loc]['upper_year'] = year_split[0]
                        in_dict[loc]['value_lower_year'] = ''
            elif '%' in in_dict[loc]['upper_year']:
                in_dict[loc]['upper_year'] = ''
            else:
                in_dict[loc]['upper_year'] = ''
    except Exception as e:
        print('Exception occurred at handle_years(): ' + str(e))
        logger_bug.debug('Exception occurred at handle_years(): ' + str(e))
    return in_dict


def filter_answer(in_dict):  # variable = 'year','amount'

    '''Input: {'U s': {'location': 'country', 'projected_value': 0.9407963156700134,
     'cagr': '$30.2 million', 'lower_year': '$30.2 million', 'current_value': '$30.2 million'},
      'China': {'location': 'country', 'cagr': '3.8%', 'upper_year': '3.8%'}}'''
    amount = ['millions', 'thousands', 'billions', 'trillions', 'crores', 'million', 'thousand', 'billion', 'trillion',
              'mn', 'bn', 'tn', 'crore']
    try:
        for loc in in_dict.keys():
            in_dict = handle_years(in_dict, loc)

        currency = set(list(currency_json.values()))
        currency_unprocessed = set(list(currency_json.keys()))
        curr_regex = list()
        for curr in currency:
            curr_regex.append(' ?' + curr.lower() + ' ?\d+\.?\d* ?million ?')
            curr_regex.append(' ?' + curr.lower() + ' ?\d+\.?\d* ?million[s]')
            curr_regex.append(' ?' + curr.lower() + ' ?\d+\.?\d* ?billion')
            curr_regex.append(' ?' + curr.lower() + ' ?\d+\.?\d* ?billion[s]')
            curr_regex.append(' ?' + curr.lower() + ' ?\d+\.?\d* ?trillion')
            curr_regex.append(' ?' + curr.lower() + ' ?\d+\.?\d* ?trillion[s]')

            curr_regex.append(' ?\d+\.?\d* ?million ?' + curr.lower() + ' ')
            curr_regex.append(' ?\d+\.?\d* ?million[s] ?' + curr.lower() + ' ')
            curr_regex.append(' ?\d+\.?\d* ?billion ?' + curr.lower() + ' ')
            curr_regex.append(' ?\d+\.?\d* ?billion[s] ?' + curr + ' ')
            curr_regex.append(' ?\d+\.?\d* ?trillion ?' + curr + ' ')
            curr_regex.append(' ?\d+\.?\d* ?trillion[s] ?' + curr + ' ')

        for loc in in_dict.keys():
            amounts = list()
            # print(in_dict[loc].keys())
            if 'current_value' in in_dict[loc].keys():
                # for word in in_dict[loc]['current_value'].split():
                #   print(word.lower(),word.lower() in amounts, word.lower() in currency_unprocessed, has_num(word.lower()))#[word for word in in_dict[loc]['current_value'].split()]) # if word.lower() in amounts or word.lower() in currency_unprocessed or has_num(word.lower())])
                in_dict[loc]['current_value'] = ' '.join([word for word in in_dict[loc]['current_value'].split()
                                                          if
                                                          word.lower() in amount or word.lower() in currency_unprocessed or has_num(
                                                              word.lower())])

                in_dict[loc]['current_value'] = re.sub('\s+', ' ', text_correction(in_dict[loc]['current_value']))
                for curr in curr_regex:

                    if re.findall(curr, in_dict[loc]['current_value'].lower().replace(',', '')):
                        amounts.extend([i.strip().replace(',', '') for i in
                                        re.findall(curr, in_dict[loc]['current_value'].lower().replace(',', ''))])
                if '%' in in_dict[loc]['current_value']:
                    in_dict[loc]['current_value'] = ''
                    in_dict[loc]['score_current_value'] = 0
                if not has_num(in_dict[loc]['current_value']):
                    in_dict[loc]['current_value'] = ''
                    in_dict[loc]['score_current_value'] = 0
            # print('Extracted Final Current Value:',in_dict[loc]['current_value'])
            if 'projected_value' in in_dict[loc].keys():
                in_dict[loc]['projected_value'] = ' '.join([word for word in in_dict[loc]['projected_value'].split()
                                                            if
                                                            word.lower() in amount or word.lower() in currency_unprocessed or has_num(
                                                                word.lower())])
                in_dict[loc]['projected_value'] = re.sub('\s+', ' ', text_correction(in_dict[loc]['projected_value']))

                for curr in curr_regex:
                    if re.findall(curr, in_dict[loc]['projected_value'].lower().replace(',', '')):
                        # print(curr, in_dict[loc]['projected_value'].lower(),re.findall(curr, in_dict[loc]['projected_value'.lower()]))
                        print('Extracted projected Value:',
                              [i.strip() for i in re.findall(curr, in_dict[loc]['projected_value'].lower())])
                        amounts.extend([i.strip().replace(',', '') for i in
                                        re.findall(curr, in_dict[loc]['projected_value'].lower().replace(',', ''))])
                if '%' in in_dict[loc]['projected_value']:
                    in_dict[loc]['projected_value'] = ''
                    in_dict[loc]['score_projected_value'] = 0
                if not has_num(in_dict[loc]['projected_value']):
                    in_dict[loc]['projected_value'] = ''
                    in_dict[loc]['score_projected_value'] = 0

            amounts = list(set(amounts))
            if len(amounts) > 1:
                for i in amounts:  # Removing duplicates
                    for j in amounts:
                        if i != j:
                            if i in j or j in i:
                                if len(i) > len(j):
                                    amounts.remove(j)
                                else:
                                    amounts.remove(i)

            if len(amounts) == 1:
                '''{'location': 'continent', 'projected_value': '', 'score_projected_value': 0, 
                'cagr': 'above 10%', 'score_cagr': 0.5812923312187195, 'upper_year': '',
                 'score_upper_year': 0.3821554183959961, 'current_value': 'USD 126 billion', 
                 'score_current_value': 0.8688370585441589, 'value_lower_year': 2019,
                  'score_lower_year_value': 0.9636294841766357, 'cagr_lower_year': ''}'''

                if 'score_projected_value' not in in_dict[loc].keys() or (
                        ('score_current_value' in in_dict[loc].keys()) and in_dict[loc]['score_current_value'] >
                        in_dict[loc]['score_projected_value']):

                    in_dict[loc]['projected_value'] = ''
                    in_dict[loc]['current_value'] = amounts[0].replace(',', '').strip()
                    # print('CASE 1', in_dict[loc]['current_value'])
                elif 'score_current_value' not in in_dict[loc].keys() or (
                        ('score_projected_value' in in_dict[loc].keys()) and in_dict[loc]['score_projected_value'] >
                        in_dict[loc]['score_current_value']):
                    in_dict[loc]['current_value'] = ''
                    in_dict[loc]['projected_value'] = amounts[0].replace(',', '').strip()
                    # print('CASE 2', in_dict[loc]['current_value'])
            if ('current_value' in in_dict[loc].keys() and 'projected_value' in in_dict[
                loc].keys()):  # Same projected and current amount
                if (in_dict[loc]['current_value'] == in_dict[loc]['projected_value']):

                    if in_dict[loc]['score_current_value'] > in_dict[loc]['score_projected_value']:
                        # print('CASE 3')
                        in_dict[loc]['projected_value'] = ''
                    else:
                        # print('CASE 4')
                        in_dict[loc]['current_value'] = ''
            if 'projected_value' in in_dict[loc].keys() and in_dict[loc]['projected_value'] and not has_num(
                    in_dict[loc]['projected_value']):
                # print('CASE 5')
                in_dict[loc]['projected_value'] = ''
            if 'projected_value' in in_dict[loc].keys() and in_dict[loc]['projected_value'] and re.findall(
                    '\d+[\W]?\d* +\d+[\W]?\d*', in_dict[loc]['projected_value']):
                # print('CASE 6')
                in_dict[loc]['projected_value'] = ''
            if ('current_value' in in_dict[loc].keys() and in_dict[loc]['current_value'] != '') and (
                    not has_num(in_dict[loc]['current_value'])):
                # print('CASE 7', (('current_value' in in_dict[loc].keys() and in_dict[loc]['current_value'] != '') and (
                #     not has_num(in_dict[loc]['current_value']))), (not has_num(in_dict[loc]['current_value'][0])))
                in_dict[loc]['current_value'] = ''
            if ('current_value' in in_dict[loc].keys() and in_dict[loc]['current_value']) and re.findall(
                    '\d+[\W]?\d* +\d+[\W]?\d*', in_dict[loc]['current_value']):
                # print('CASE 8')
                in_dict[loc]['current_value'] = ''
            if len(amounts) > 1:
                # print('2 AMount after removing duplicates', amounts)
                amounts = get_sorted_amount(amounts)
                # print('Sorted amount:', amounts)
                for idx, i in enumerate(amounts):
                    for j in currency_json.values():
                        if i.lower().endswith(j.lower()):
                            i = i.replace(j, '').strip()
                            i = j + ' ' + i
                            amounts[idx] = i.replace(',', '')
                in_dict[loc]['projected_value'] = amounts[-1]
                in_dict[loc]['current_value'] = amounts[0]

            # Making sure amount, listed currency, amount are present
            if not ('current_value' in in_dict[loc].keys() and '%' not in in_dict[loc]['current_value'] and [i for i in
                                                                                                             amount if
                                                                                                             i.lower() in
                                                                                                             in_dict[
                                                                                                                 loc][
                                                                                                                 'current_value'].lower()] and [
                        i for i in currency
                        if i.lower() in
                           in_dict[loc][
                               'current_value'].lower()] and has_num(
                in_dict[loc]['current_value'])):
                in_dict[loc]['current_value'] = ''
            if not ('projected_value' in in_dict[loc].keys() and '%' not in in_dict[loc]['projected_value'] and [i for i
                                                                                                                 in
                                                                                                                 amount
                                                                                                                 if
                                                                                                                 i.lower() in
                                                                                                                 in_dict[
                                                                                                                     loc][
                                                                                                                     'projected_value'].lower()] and [
                        i for i in currency
                        if i.lower() in
                           in_dict[loc][
                               'projected_value'].lower()] and has_num(
                in_dict[loc]['projected_value'])):
                in_dict[loc]['projected_value'] = ''
                # Normalizing bn, mn, tn etc
            if 'current_value' in in_dict[loc].keys() and in_dict[loc]['current_value']:
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('bn',
                                                                                      ' billion').strip().lower().strip()
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('billions',
                                                                                      ' billion').strip().lower().strip()
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('billion',
                                                                                      ' billion').strip().lower().strip()
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('mn',
                                                                                      ' million').strip().lower().strip()
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('millions',
                                                                                      ' million').strip().lower().strip()
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('million',
                                                                                      ' million').strip().lower().strip()
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('tn',
                                                                                      ' trillion').strip().lower().strip()
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('trillions',
                                                                                      ' trillion').strip().lower().strip()
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('trillion',
                                                                                      ' trillion').strip().lower().strip()
                in_dict[loc]['current_value'] = ' ' + in_dict[loc]['current_value'] + ' '.replace(' k ',
                                                                                                  'thousand').strip().lower().strip()
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('thousands',
                                                                                      ' thousand').strip().lower().strip()
                in_dict[loc]['current_value'] = in_dict[loc]['current_value'].replace('thousand',
                                                                                      ' thousand').strip().lower().strip()
                in_dict[loc]['current_value'] = ' ' + in_dict[loc]['current_value'] + ' '.replace('cr ',
                                                                                                  'crores').strip().lower().strip()
                in_dict[loc]['current_value'] = ' ' + in_dict[loc]['current_value'] + ' '.replace('cr ',
                                                                                                  'crore').strip().lower().strip()
                in_dict[loc]['current_value'] = re.sub('\s{2-}', ' ', in_dict[loc]['current_value'])
            if 'projected_value' in in_dict[loc].keys() and in_dict[loc]['projected_value']:
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('bn',
                                                                                          ' billion').strip().lower().strip()
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('billions',
                                                                                          ' billion').strip().lower().strip()
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('billion',
                                                                                          ' billion').strip().lower().strip()
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('mn',
                                                                                          ' million').strip().lower().strip()
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('millions',
                                                                                          ' million').strip().lower().strip()
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('million',
                                                                                          ' million').strip().lower().strip()
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('tn',
                                                                                          ' trillion').strip().lower().strip()
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('trillions',
                                                                                          ' trillion').strip().lower().strip()
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('trillion',
                                                                                          ' trillion').strip().lower().strip()
                in_dict[loc]['projected_value'] = ' ' + in_dict[loc]['projected_value'] + ' '.replace(' k ',
                                                                                                      'thousand').strip().lower().strip()
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('thousands',
                                                                                          ' thousand').strip().lower().strip()
                in_dict[loc]['projected_value'] = in_dict[loc]['projected_value'].replace('thousand',
                                                                                          ' thousand').strip().lower().strip()
                in_dict[loc]['projected_value'] = ' ' + in_dict[loc]['projected_value'] + ' '.replace('cr ',
                                                                                                      'crores').strip().lower().strip()
                in_dict[loc]['projected_value'] = ' ' + in_dict[loc]['projected_value'] + ' '.replace('cr ',
                                                                                                      'crore').strip().lower().strip()
                in_dict[loc]['projected_value'] = re.sub('\s{2-}', ' ', in_dict[loc]['projected_value'])
        for loc in in_dict.keys():
            if 'cagr' in in_dict[loc].keys() and has_num(in_dict[loc]['cagr']):
                if '%' not in in_dict[loc]['cagr']:
                    in_dict[loc]['cagr'] = ''
                elif [i for i in ['million', 'billion', 'crore', 'thousand', 'crore'] if i in in_dict[loc]['cagr']]:
                    in_dict[loc]['cagr'] = ''
                else:
                    in_dict[loc]['cagr'] = re.sub('\d{4}', '', in_dict[loc]['cagr'])
                    percentage = re.findall("(?:(?:\d+(?:\.\d+)?\-)?(?:(?:\d+(?:\.\d+)?)|100))%",
                                            in_dict[loc]['cagr'])  # https://stackoverflow.com/a/36532849
                    cagr_perc = list()
                    for perc in percentage:
                        if '-' in perc:
                            perc_list = perc.split('-')
                            cagr_perc.extend([i if '%' not in i else i.replace('%', '') for i in perc_list])
                        else:
                            cagr_perc.extend([perc.replace('%', '')])
                    cagr_perc.sort()
                    in_dict[loc]['cagr'] = cagr_perc[0] + '%'
            else:
                in_dict[loc]['cagr'] = ''
        for loc in in_dict.keys():  # score_lower_year_cagr, score_lower_year_value
            # print('year score:',in_dict[loc]['score_lower_year_cagr'],in_dict[loc]['score_lower_year_value'])
            if ('cagr_lower_year' in in_dict[loc].keys() and 'value_lower_year' in in_dict[loc].keys()
                and 'score_lower_year_cagr' in in_dict[loc].keys() and 'score_lower_year_value' in in_dict[
                    loc].keys()) and (in_dict[loc]['cagr_lower_year'] and in_dict[loc]['value_lower_year']):

                if in_dict[loc]['cagr_lower_year'] == in_dict[loc]['value_lower_year']:
                    # print('true1')
                    if in_dict[loc]['score_lower_year_cagr'] > in_dict[loc]['score_lower_year_value']:
                        # print('true2')
                        in_dict[loc]['value_lower_year'] = ''
                    if in_dict[loc]['score_lower_year_cagr'] < in_dict[loc]['score_lower_year_value']:
                        # print('true3')
                        in_dict[loc]['cagr_lower_year'] = ''
            elif ('cagr_lower_year' in in_dict[loc].keys() and 'upper_year' in in_dict[loc].keys()) and (in_dict[loc]['cagr_lower_year'] == in_dict[loc]['upper_year']):
                print('CAME TO ELIF')
                in_dict[loc]['cagr_lower_year'] = ''
    except Exception as e:
        print('exception at filter_answer():' + str(e))
        logger_bug.debug('exception at filter_answer():' + str(e))
    return in_dict


def pre_process(text):  # To fix years
    text = text.replace(' % ', '%')
    text = text.replace(' %', '%')
    years_list = list()
    years = dict()
    for curr in currency_json.keys():
        if curr in text.lower():
            text = ' ' + text.lower() + ' '.replace(' ' + curr + ' ', ' ' + currency_json[curr] + ' ')
    text = re.sub('\s{2-}', '', text)
    if re.findall('(fy\d+-?\d+)\.?', text.lower()):
        y_list = [i for i in re.findall('(fy\d+-?\d+)\.?', text)]
        for y in y_list:  # fy21-22
            formatted_year_list = list()
            if '-' in y:  # len(years)==7: # '2004-10'
                split_years = y.split('-')  # ['fy21','22']
                for idx, split_year in enumerate(split_years):
                    split_year = split_year.replace('fy', '')
                    if len(split_year) == 2:
                        formatted_year_list.extend([str(int(str(int(now.year / 100)) + split_year))])
                    elif len(split_year) == 4:
                        formatted_year_list.extend([split_year])
            # print('formatted_year_list:', formatted_year_list)
            years[y] = formatted_year_list

    if years:
        for temp_year in years.keys():
            print('temp year:', temp_year, years[temp_year])
            text = text.replace(temp_year, '-'.join(years[temp_year]))

        # years_list.extend(y_list)
    return text


def normalize_currency(sent):
    for curr in currency_json.keys():
        # print("CURRENCY: ",curr)
        if (len(curr) > 1) or ('r' != curr):
            if curr in sent.lower():
                # print("CURRENCY PRESEMT:",curr)
                rep_curr = currency_json[curr]
                if rep_curr:
                    sent = sent.lower().replace(curr, rep_curr)

    sent = re.sub('\s+', ' ', sent).lower()
    return sent


def find_value(sent, con):
    def ques_answer(proj_value_dict, loc, con, curr):
        answer_list = list()
        quest = proj_value_dict[keyword] + ' at ' + loc.lower() + '?'
        ans = qa_ppl(context=sent, question=quest)
        print('Question: ' + quest + '\n' + 'Answer: ' + str(ans))
        logger_info.info('Question: ' + quest + '\n' + 'Answer: ' + str(ans))
        if ans['score'] > 0.35:
            if loc in con[0]:
                if loc.lower() != 'global':
                    country = loc
                    continent = ''
                else:
                    country = ''
                    continent = loc
            elif loc in con[1]:
                country = ''
                continent = loc
            if curr.lower() in ans['answer']:
                answer = ans['answer']
            else:
                answer = curr + ' ' + ans['answer']
            answer_list.append([ans['score'], answer, country, continent, quest])
        return answer_list

    new_out_dict = list()
    curr = ''
    sent = sent.lower()
    proj_value_dict = {'projected': 'what is the projected to reach amount',
                       'reached': 'what is the reached amount',
                       'reaching': 'what is the reaching amount',
                       'reach': 'what is the amount to reach',
                       'estimated': 'what is the estimated amount',
                       'estimate': 'what is the estimate amount',
                       'increased': 'what is the increased amount',
                       'increase': 'what is the increase in amount',
                       'increasing': 'what is the increasing amount',
                       'surged': 'what is the surged amount',
                       'surge': 'what is the surge in amount',
                       'surging': 'what is the surging amount',
                       'expected': 'what is the expected amount',
                       'growing': 'what is the amount growing to',
                       'grew': 'how much has the amount grew to',
                       'grow': 'what will the amount grow to',
                       'expanded': 'what is the expanded amount',
                       'expand': 'what is the amount to expand',
                       'expanding': 'what is the expanding amount',
                       }
    # proj_value_kws = ['reach','estimate','exceed','expand','increase','reach','surge','expected','grow']
    locations = list()
    keyword = ''
    try:
        for currency in currency_json.keys():
            if ' ' + currency + ' ' in ' ' + sent + ' ':
                curr = currency
                break

        for kw in proj_value_dict.keys():
            if kw in sent:
                keyword = kw
                break
        # con = get_elements.find_geo(sent, nlp(sent), return_type='unprocessed')
        locations.extend(con[0])
        locations.extend(con[1])
        loc_dict = dict()
        if keyword:
            if locations:
                answer_list = list()
                for loc in locations:
                    answer_list.extend(ques_answer(proj_value_dict, loc, con, curr))
                '''if len(locations) == 1 or len(locations) > 7:
                    for loc in locations:
                        answer_list.extend(ques_answer(proj_value_dict, loc, con))
                else:
                    if len(locations) == 2:
                        projected_value_pool = ThreadPool(processes=2)
                        th_output_0 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[0],con])
                        th_output_1 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[1],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                    if len(locations) == 3:
                        projected_value_pool = ThreadPool(processes=3)
                        th_output_0 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[0],con])
                        th_output_1 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[1],con])
                        th_output_2 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[2],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                    if len(locations) == 4:
                        projected_value_pool = ThreadPool(processes=4)
                        th_output_0 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[0],con])
                        th_output_1 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[1],con])
                        th_output_2 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[2],con])
                        th_output_3 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[3],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                    if len(locations) == 5:
                        projected_value_pool = ThreadPool(processes=5)
                        th_output_0 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[0],con])
                        th_output_1 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[1],con])
                        th_output_2 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[2],con])
                        th_output_3 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[3],con])
                        th_output_4 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[4],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                    if len(locations) == 6:
                        projected_value_pool = ThreadPool(processes=6)
                        th_output_0 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[0],con])
                        th_output_1 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[1],con])
                        th_output_2 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[2],con])
                        th_output_3 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[3],con])
                        th_output_4 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[4],con])
                        th_output_5 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[5],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                        answer_list.extend(th_output_5.get())
                    if len(locations) == 7:
                        projected_value_pool = ThreadPool(processes=7)
                        th_output_0 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[0],con])
                        th_output_1 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[1],con])
                        th_output_2 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[2],con])
                        th_output_3 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[3],con])
                        th_output_4 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[4],con])
                        th_output_5 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[5],con])
                        th_output_6 = projected_value_pool.apply_async(ques_answer, [proj_value_dict, locations[6],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                        answer_list.extend(th_output_5.get())
                        answer_list.extend(th_output_6.get())'''

                # loc_dict[quest] =
                answer_list = sort_list_within_list(answer_list, reverse=True)
                final_answer_list = list()
                for score, answer, country, continent, quest in answer_list:
                    # print(final_answer_list)
                    present = False
                    if final_answer_list:
                        # print('Truw:',final_answer_list)
                        for idx, fin_ans in enumerate(final_answer_list):
                            if answer == fin_ans[1]:
                                present = True
                                break
                        if present:
                            if score > final_answer_list[idx][0]:
                                final_answer_list.remove(fin_ans[idx])
                                final_answer_list.append([score, answer, country, continent, quest])
                        else:
                            final_answer_list.append([score, answer, country, continent, quest])

                    else:
                        final_answer_list.append([score, answer, country, continent, quest])
                    for final_ans in final_answer_list:
                        loc_dict[final_ans[4]] = [final_ans[0], final_ans[1], final_ans[2], final_ans[3], final_ans[4]]


            else:
                country = continent = ''
                quest = proj_value_dict[keyword] + '?'
                ans = qa_ppl(context=sent, question=quest)
                print('Question: ' + quest)
                print('Answer: ' + str(ans))
                logger_info.info('Question: ' + quest)
                logger_info.info('Answer: ' + str(ans))
                if ans['score'] > 0.35:
                    # answer_list.append([ans['score'],ans['answer'],loc,quest])
                    if curr.lower() in ans['answer']:
                        answer = ans['answer']
                    else:
                        answer = curr + ' ' + ans['answer']
                    loc_dict[quest] = [ans['score'], answer, country, continent, quest]
                new_out_dict = list()
            for ques in loc_dict.keys():
                new_dict = dict()
                new_dict['question'] = ques
                if len(loc_dict[ques][2]) != 0:
                    new_dict['country'] = loc_dict[ques][2]
                elif len(loc_dict[ques][3]) != 0:
                    new_dict['continent'] = loc_dict[ques][3]
                else:
                    new_dict['continent'] = 'Global'
                new_dict['score_projected_value'] = loc_dict[ques][0]
                new_dict['projected_value'] = loc_dict[ques][1]
                new_out_dict.append(new_dict)
        print('RES in funct: ', new_out_dict)
    except Exception as e:
        print('Exception occurred at find_value(): ' + str(e))
        logger_bug.debug('Exception occurred at find_value(): ' + str(e))
    return new_out_dict


def find_cagr(text, con):
    new_out_dict = list()
    text = text.lower()
    keyword = ''
    cagr_kws = {'cagr': 'What is the cagr',
                'compound annual growth rate': 'what is the compound annual growth rate',
                'annual growth rate': 'what is the annual growth rate',
                'annual rate of increase': 'what is the annual rate of increase',
                'annual growth factor': 'what is the annual growth factor'}

    def ques_answer(cagr_kws, loc, con):
        answer_list = list()
        # print(loc)
        quest = cagr_kws[keyword] + ' in ' + loc.lower() + '?'
        # print(quest)
        ans = qa_ppl(context=text, question=quest)
        print('Question: ' + quest + '\n' + 'Answer: ' + str(ans))
        logger_info.info('Question: ' + quest + '\n' + 'Answer: ' + str(ans))

        if ans['score'] > 0.35:
            if loc in con[0]:
                if loc.lower() != 'global':
                    country = loc
                    continent = ''
                else:
                    country = ''
                    continent = loc

            elif loc in con[1]:
                country = ''
                continent = loc
            answer_list.append([ans['score'], ans['answer'], country, continent, quest])
        return answer_list

    try:
        for kw in cagr_kws.keys():
            if kw in text:
                # print('kw present:', kw)
                keyword = kw
        print('KW resent for extracting CAGR: ', keyword)
        logger_info.info('KW resent for extracting CAGR: ' + keyword)
        locations = list()
        # con = get_elements.find_geo(text, nlp(text), return_type='unprocessed')
        locations.extend(con[0])
        locations.extend(con[1])
        # print('locations:',locations)
        loc_dict = dict()
        if keyword:
            # print('Keyword:',keyword,' present in:',text )
            if locations:
                answer_list = list()
                for loc in locations:
                    answer_list.extend(ques_answer(cagr_kws, loc, con))
                '''if len(locations) == 1 or len(locations) > 7:
                    for loc in locations:
                        answer_list.extend(ques_answer(cagr_kws, loc, con))
                else:
                    if len(locations) == 2:
                        cagr_pool = ThreadPool(processes=2)
                        th_output_0 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[0],con])
                        th_output_1 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[1],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                    if len(locations) == 3:
                        cagr_pool = ThreadPool(processes=3)
                        th_output_0 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[0],con])
                        th_output_1 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[1],con])
                        th_output_2 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[2],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                    if len(locations) == 4:
                        cagr_pool = ThreadPool(processes=4)
                        th_output_0 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[0],con])
                        th_output_1 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[1],con])
                        th_output_2 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[2],con])
                        th_output_3 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[3],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                    if len(locations) == 5:
                        cagr_pool = ThreadPool(processes=5)
                        th_output_0 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[0],con])
                        th_output_1 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[1],con])
                        th_output_2 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[2],con])
                        th_output_3 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[3],con])
                        th_output_4 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[4],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                    if len(locations) == 6:
                        cagr_pool = ThreadPool(processes=6)
                        th_output_0 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[0],con])
                        th_output_1 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[1],con])
                        th_output_2 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[2],con])
                        th_output_3 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[3],con])
                        th_output_4 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[4],con])
                        th_output_5 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[5],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                        answer_list.extend(th_output_5.get())
                    if len(locations) == 7:
                        cagr_pool = ThreadPool(processes=7)
                        th_output_0 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[0],con])
                        th_output_1 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[1],con])
                        th_output_2 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[2],con])
                        th_output_3 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[3],con])
                        th_output_4 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[4],con])
                        th_output_5 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[5],con])
                        th_output_6 = cagr_pool.apply_async(ques_answer, [cagr_kws, locations[6],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                        answer_list.extend(th_output_5.get())
                        answer_list.extend(th_output_6.get())'''

                # loc_dict[quest] =
                answer_list = sort_list_within_list(answer_list, reverse=True)
                # print('answer_list: ', answer_list)
                final_answer_list = list()
                for score, answer, country, continent, quest in answer_list:
                    # print(final_answer_list)
                    present = False
                    if final_answer_list:
                        # print('Truw:',final_answer_list)
                        for idx, fin_ans in enumerate(final_answer_list):
                            if answer == fin_ans[1]:
                                present = True
                                break
                        if present:
                            if score > final_answer_list[idx][0]:
                                final_answer_list.remove(fin_ans[idx])
                                final_answer_list.append([score, answer, country, continent, quest])
                        else:
                            final_answer_list.append([score, answer, country, continent, quest])

                    else:
                        final_answer_list.append([score, answer, country, continent, quest])
                    for final_ans in final_answer_list:
                        loc_dict[final_ans[4]] = [final_ans[0], final_ans[1], final_ans[2], final_ans[3], final_ans[4]]
            else:
                country = continent = ''
                # print(kw)
                quest = cagr_kws[keyword] + ' ?'
                ans = qa_ppl(context=text, question=quest)
                print('Question: ' + quest)
                print('Answer: ' + str(ans))
                logger_info.info('Question: ' + quest)
                logger_info.info('Answer: ' + str(ans))
                if ans['score'] > 0.35:
                    loc_dict[quest] = [ans['score'], ans['answer'], country, continent, quest]
            # print(qa_ppl(context = text, question='annual growth rate at european union'))
            print('RES: ', loc_dict)
            new_out_dict = list()
            for ques in loc_dict.keys():
                new_dict = dict()
                new_dict['question'] = ques
                if len(loc_dict[ques][2]) != 0:
                    new_dict['country'] = loc_dict[ques][2]
                elif len(loc_dict[ques][3]) != 0:
                    new_dict['continent'] = loc_dict[ques][3]
                else:
                    new_dict['continent'] = 'Global'
                new_dict['score_cagr'] = loc_dict[ques][0]
                new_dict['cagr'] = loc_dict[ques][1]
                new_out_dict.append(new_dict)
        print('RES: ', new_out_dict)
        logger_info.info('RES: ' + str(new_out_dict))
    except Exception as e:
        print('Exception occurred at find_cagr(): ' + str(e))
        logger_bug.debug('Exception occurred at find_cagr(): ' + str(e))
    return new_out_dict


def find_forecast_year(text, con):
    new_out_dict = list()
    text = text.lower()
    keyword = ''
    cagr_keyword = ''
    cagr_kws = {'cagr': 'What is the cagr',
                'compound annual growth rate': 'what is the compound annual growth rate',
                'annual growth rate': 'what is the annual growth rate',
                'annual rate of increase': 'what is the annual rate of increase',
                'annual growth factor': 'what is the annual growth factor'}
    # text = 'According to one widely publicized projection, the storage market could reach more than USD 26 billion in annual sales by 2022, a compound annual growth rate (cagr) of 46.5%..'
    forecast_year = {'reached': '<keyword> is reached in which year',
                     'reaching': '<keyword> will be reaching in which year',
                     'reach': 'when will the <keyword> reach by',
                     'estimated': 'when is the <keyword> estimated to reach',
                     'estimate': 'when is the estimate year for <keyword>',
                     'increased': 'when will the <keyword> be increased to',
                     'increase': 'when will the <keyword> increase',
                     'increasing': 'when will the <keyword> be increasing to',
                     'surged': 'when will the <keyword> surged',
                     'surge': 'when will the <keyword> surge',
                     'surging': 'when will the <keyword> be surging to',
                     'expected': 'when is the <keyword> expected',
                     'growing': 'when is the <keyword> be growing to',
                     'grew': 'when did the <keyword> grow',
                     'grow': 'when will the <keyword> grow',
                     'expanded': 'when did the <keyword> expand',
                     'expand': 'when will the <keyword> expand',
                     'expanding': 'when is the <keyword> expanding to',
                     'forecast': 'when is the <keyword> forecasted to grow',
                     'expecting': 'when is the <keyword> expecting to reach by',
                     'expect': 'when is the <keyword> expected to reach by'

                     }

    def ques_answer(cagr_keyword, forecast_year, loc, con):
        # print(loc)
        print('keyword to replace in function:', cagr_keyword)
        if cagr_keyword:
            replace_word = forecast_year[keyword].replace('<keyword>', cagr_keyword)
        else:
            replace_word = forecast_year[keyword].replace('<keyword>', 'amount')
        quest = replace_word + ' in ' + loc.lower() + '?'

        # print(quest)
        ans = qa_ppl(context=text, question=quest)
        print('Question: ' + quest + '\n' + 'Answer: ' + str(ans))
        logger_info.info('Question: ' + quest + '\n' + 'Answer: ' + str(ans))
        # print('ans: ',ans)
        if ans['score'] > 0.35:
            if loc in con[0]:
                if loc.lower() != 'global':
                    country = loc
                    continent = ''
                else:
                    country = ''
                    continent = loc

            elif loc in con[1]:
                country = ''
                continent = loc
            answer_list.append([ans['score'], ans['answer'], country, continent, quest])
        return answer_list

    try:
        for kw in cagr_kws.keys():
            if kw in text:
                # print(kw,' in text')
                cagr_keyword = kw

        for kw in forecast_year.keys():
            if kw in text:
                keyword = kw
        print('KW present in text for forecast year: ' + keyword)
        logger_info.info('KW present in text for forecast year: ' + keyword)
        locations = list()
        # con = get_elements.find_geo(text, nlp(text), return_type='unprocessed')
        # # print('Find forecast year: ', con)
        locations.extend(con[0])
        locations.extend(con[1])
        # print('locations:',locations)
        loc_dict = dict()
        if keyword:
            # print('Keyword:',keyword,' present in:',text )
            if locations:
                answer_list = list()
                for loc in locations:
                    answer_list.extend(ques_answer(cagr_keyword, forecast_year, loc, con))
                '''if len(locations) == 1 or len(locations) > 7:
                    for loc in locations:
                        answer_list.extend(ques_answer(cagr_kws, loc,con))
                else:
                    if len(locations) == 2:
                        forecast_year_pool = ThreadPool(processes=2)
                        th_output_0 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[0],con])
                        th_output_1 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[1],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                    if len(locations) == 3:
                        forecast_year_pool = ThreadPool(processes=3)
                        th_output_0 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[0],con])
                        th_output_1 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[1],con])
                        th_output_2 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[2],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                    if len(locations) == 4:
                        forecast_year_pool = ThreadPool(processes=4)
                        th_output_0 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[0],con])
                        th_output_1 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[1],con])
                        th_output_2 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[2],con])
                        th_output_3 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[3],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                    if len(locations) == 5:
                        forecast_year_pool = ThreadPool(processes=5)
                        th_output_0 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[0],con])
                        th_output_1 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[1],con])
                        th_output_2 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[2],con])
                        th_output_3 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[3],con])
                        th_output_4 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[4],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                    if len(locations) == 6:
                        forecast_year_pool = ThreadPool(processes=6)
                        th_output_0 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[0],con])
                        th_output_1 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[1],con])
                        th_output_2 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[2],con])
                        th_output_3 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[3],con])
                        th_output_4 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[4],con])
                        th_output_5 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[5],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                        answer_list.extend(th_output_5.get())
                    if len(locations) == 7:
                        forecast_year_pool = ThreadPool(processes=7)
                        th_output_0 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[0],con,con])
                        th_output_1 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[1],con,con])
                        th_output_2 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[2],con,con])
                        th_output_3 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[3],con,con])
                        th_output_4 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[4],con,con])
                        th_output_5 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[5],con,con])
                        th_output_6 = forecast_year_pool.apply_async(ques_answer, [cagr_keyword, forecast_year, locations[6],con,con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                        answer_list.extend(th_output_5.get())
                        answer_list.extend(th_output_6.get())'''

                answer_list = sort_list_within_list(answer_list, reverse=True)
                # print('answer_list: ', answer_list)
                final_answer_list = list()
                for score, answer, country, continent, quest in answer_list:
                    # print(final_answer_list)
                    present = False
                    if final_answer_list:
                        # print('Truw:',final_answer_list)
                        for idx, fin_ans in enumerate(final_answer_list):
                            if answer == fin_ans[1]:
                                present = True
                                break
                        if present:
                            if score > final_answer_list[idx][0]:
                                final_answer_list.remove(fin_ans[idx])
                                final_answer_list.append([score, answer, country, continent, quest])
                        else:
                            final_answer_list.append([score, answer, country, continent, quest])

                    else:
                        final_answer_list.append([score, answer, country, continent, quest])
                    for final_ans in final_answer_list:
                        loc_dict[final_ans[4]] = [final_ans[0], final_ans[1], final_ans[2], final_ans[3], final_ans[4]]
            else:
                country = continent = ''
                # print(kw)
                print('keyword to replace:', cagr_keyword)
                if cagr_keyword:
                    replace_word = forecast_year[keyword].replace('<keyword>', cagr_keyword)
                else:
                    replace_word = forecast_year[keyword].replace('<keyword>', 'amount')
                quest = replace_word + ' ?'

                ans = qa_ppl(context=text, question=quest)
                print('Question: ' + quest)
                print('Answer: ' + str(ans))
                logger_info.info('Question: ' + quest)
                logger_info.info('Answer: ' + str(ans))
                if ans['score'] > 0.35:
                    loc_dict[quest] = [ans['score'], ans['answer'], country, continent, quest]
            new_out_dict = list()
            for ques in loc_dict.keys():
                new_dict = dict()
                new_dict['question'] = ques
                if len(loc_dict[ques][2]) != 0:
                    new_dict['country'] = loc_dict[ques][2]
                elif len(loc_dict[ques][3]) != 0:
                    new_dict['continent'] = loc_dict[ques][3]
                else:
                    new_dict['continent'] = 'Global'
                new_dict['score_upper_year'] = loc_dict[ques][0]
                new_dict['upper_year'] = loc_dict[ques][1]
                new_out_dict.append(new_dict)
        print('RES: ', new_out_dict)
        logger_info.info('RES: ' + str(new_out_dict))
    except Exception as e:
        print('Exception occurred at find_forecast_year(): ' + str(e))
        logger_bug.debug('Exception occurred at find_forecast_year(): ' + str(e))
    return new_out_dict


def find_cagr_for_topic(each_dict,topics):
    print('Checking Topic for the CAGR...')
    text = each_dict['sentence'].lower()
    keyword = topic_keyword = ''
    topic_ques = {'project': 'what <market_keyword> is projected to reach <cagr_keyword> of <cagr_value>?',
                     'reached': 'what <market_keyword> has reached <cagr_keyword> of <cagr_value>?',
                     'reaching': 'what <market_keyword> is reaching <cagr_keyword> of <cagr_value>?',
                     'reach': 'what <market_keyword> will reach <cagr_keyword> of <cagr_value>?',
                     'estimated': 'what <market_keyword> is estimated at <cagr_keyword> of <cagr_value>?',
                     'estimate': 'what <market_keyword> is the estimate <cagr_keyword> of <cagr_value>?',
                     'increased': 'what <market_keyword> has increased to <cagr_keyword> of <cagr_value>?',
                     'increase': 'what <market_keyword> will increase to <cagr_keyword> of <cagr_value>?',
                     'increasing': 'what <market_keyword> is increasing to <cagr_keyword> of <cagr_value>?',
                     'surged': 'what <market_keyword> has surged to <cagr_keyword> of <cagr_value>?',
                     'surge': 'what <market_keyword> will surge to <cagr_keyword> of <cagr_value>?',
                     'surging': 'what <market_keyword> is surging to <cagr_keyword> of <cagr_value>?',
                     'expected': 'what <market_keyword> is expected to grow <cagr_keyword> of <cagr_value>?',
                     'growing': 'what <market_keyword> is growing to <cagr_keyword> of <cagr_value>?',
                     'grew': 'what <market_keyword> grew to <cagr_keyword> of <cagr_value>?',
                     'grow': 'what <market_keyword> will grow to <cagr_keyword> of <cagr_value>?',
                     'expanded': 'what <market_keyword> has expanded to <cagr_keyword> of <cagr_value>?',
                     'expand': 'what <market_keyword> will expand to <cagr_keyword> of <cagr_value>?',
                     'expanding': 'what <market_keyword> is expanding to <cagr_keyword> of <cagr_value>?',
                     'forecast': 'what <market_keyword> will forecast to <cagr_keyword> of <cagr_value>?',
                     'expecting': 'what <market_keyword> is expecting to grow <cagr_keyword> of <cagr_value>?',
                     'expect': 'what <market_keyword> will expect to grow <cagr_keyword> of <cagr_value>?',

                     }
    cagr_kws = {'compound annual growth rate': 'what is the compound annual growth rate',
                'annual growth rate': 'what is the annual growth rate',
                'annual rate of increase': 'what is the annual rate of increase',
                'annual growth factor': 'what is the annual growth factor',
                'cagr': 'What is the cagr'}

    def ques_answer(text,keyword,topic_keyword,topics):
        # answer_list = list()
        # print(loc)
        if 'market' in text:
            quest = topic_ques[topic_keyword].replace('<market_keyword>', 'market')
            quest = quest.replace('<cagr_keyword>', keyword)
        else:
            quest = topic_ques[topic_keyword].replace('<market_keyword>', '')
            quest = quest.replace('<cagr_keyword>', keyword)
            quest = re.sub('\s{2}',' ',quest)
        # print(quest)
        ans = qa_ppl(context=text, question=quest)
        print('Question: ' + quest + '\n' + 'Answer: ' + str(ans))
        logger_info.info('Question: ' + quest + '\n' + 'Answer: ' + str(ans))
        mv_flag = True
        if ans['score'] > 0.20:
            mv_flag = False
            for topic in topics:
                if topic in ans['answer']:
                    # answer_list.append([ans['score'], ans['answer'], quest])
                    mv_flag = False
                    break
        if not mv_flag:
            print('Manual Verification: ' + ans['answer'] + ' with score: '+str(ans['score'])+' for topic: ' + str(topic))
            logger_info.info('Manual Verification: ' + ans['answer'] + ' with score: '+str(ans['score'])+' for topic: ' + str(topic))
        return mv_flag

    mv_flag = True
    try:
        for kw in cagr_kws.keys():
            if kw in text:
                # print('kw present:', kw)
                keyword = kw
        for t_kw in topic_ques.keys():
            if t_kw in text:
                # print('kw present:', kw)
                topic_keyword = t_kw
        print('KW sent for MV using CAGR: ', keyword)
        logger_info.info('KW sent for MV using CAGR: ' + keyword)


        if keyword:
            mv_flag = ques_answer(text,keyword,topic_keyword,topics)
        else:
            mv_flag = False
    except Exception as e:
        print('Exception occurred at find_cagr_for_topic(): ' + str(e))
        logger_bug.debug('Exception occurred at find_cagr_for_topic(): ' + str(e))
    return mv_flag


def find_current_value(sent, con):
    new_out_dict = list()
    curr_value_dict = dict()
    sent = sent.lower()
    sent = normalize_currency(sent)

    def ques_answer(replace_word, loc, con):
        quest = replace_word + ' in ' + loc.lower() + '?'
        # print('Question:', quest)
        ans = qa_ppl(context=sent, question=quest)
        print('Question: 1 time' + quest + '\n' + 'Answer: ' + str(ans))
        logger_info.info('Question: ' + quest + '\n' + 'Answer: ' + str(ans))

        if ans['score'] > 0.35:
            if loc in con[0]:
                if loc.lower() != 'global':
                    country = loc
                    continent = ''
                else:
                    country = ''
                    continent = loc

            elif loc in con[1]:
                country = ''
                continent = loc
            if curr.lower() in ans['answer']:
                answer = ans['answer']
            else:
                answer = curr + ' ' + ans['answer']
            answer_list.append([ans['score'], answer, country, continent, quest])
        return answer_list

    try:
        for curr in currency_json.keys():
            if ' ' + curr + ' ' in ' ' + sent + ' ':
                curr_value_dict[' '] = 'what is the initial amount in ' + curr
                break
            else:
                curr_value_dict[' '] = 'what is the initial amount '

        locations = list()

        # con = get_elements.find_geo(sent, nlp(sent), return_type='unprocessed')
        # # print('Find current value: ', con)
        locations.extend(con[0])
        locations.extend(con[1])
        # print(locations)
        loc_dict = dict()
        replace_word = list(curr_value_dict.values())[0]
        # if keyword:
        if replace_word:
            # print('Keyword:',keyword,' present in:',sent )
            if locations:
                answer_list = list()
                mul_loc = list()
                answer_list = list()
                for loc in locations:
                    answer_list.extend(ques_answer(replace_word, loc, con))
                '''if len(locations) == 1 or len(locations) > 7:
                    for loc in locations:
                        answer_list.extend(ques_answer(replace_word, loc,con))
                else:
                    if len(locations) == 2:
                        current_value_pool = ThreadPool(processes=2)
                        th_output_0 = current_value_pool.apply_async(ques_answer, [replace_word, locations[0],con])
                        th_output_1 = current_value_pool.apply_async(ques_answer, [replace_word, locations[1],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                    if len(locations) == 3:
                        current_value_pool = ThreadPool(processes=3)
                        th_output_0 = current_value_pool.apply_async(ques_answer, [replace_word, locations[0],con])
                        th_output_1 = current_value_pool.apply_async(ques_answer, [replace_word, locations[1],con])
                        th_output_2 = current_value_pool.apply_async(ques_answer, [replace_word, locations[2],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                    if len(locations) == 4:
                        current_value_pool = ThreadPool(processes=4)
                        th_output_0 = current_value_pool.apply_async(ques_answer, [replace_word, locations[0],con])
                        th_output_1 = current_value_pool.apply_async(ques_answer, [replace_word, locations[1],con])
                        th_output_2 = current_value_pool.apply_async(ques_answer, [replace_word, locations[2],con])
                        th_output_3 = current_value_pool.apply_async(ques_answer, [replace_word, locations[3],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                    if len(locations) == 5:
                        current_value_pool = ThreadPool(processes=5)
                        th_output_0 = current_value_pool.apply_async(ques_answer, [replace_word, locations[0],con])
                        th_output_1 = current_value_pool.apply_async(ques_answer, [replace_word, locations[1],con])
                        th_output_2 = current_value_pool.apply_async(ques_answer, [replace_word, locations[2],con])
                        th_output_3 = current_value_pool.apply_async(ques_answer, [replace_word, locations[3],con])
                        th_output_4 = current_value_pool.apply_async(ques_answer, [replace_word, locations[4],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                    if len(locations) == 6:
                        current_value_pool = ThreadPool(processes=6)
                        th_output_0 = current_value_pool.apply_async(ques_answer, [replace_word, locations[0],con])
                        th_output_1 = current_value_pool.apply_async(ques_answer, [replace_word, locations[1],con])
                        th_output_2 = current_value_pool.apply_async(ques_answer, [replace_word, locations[2],con])
                        th_output_3 = current_value_pool.apply_async(ques_answer, [replace_word, locations[3],con])
                        th_output_4 = current_value_pool.apply_async(ques_answer, [replace_word, locations[4],con])
                        th_output_5 = current_value_pool.apply_async(ques_answer, [replace_word, locations[5],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                        answer_list.extend(th_output_5.get())
                    if len(locations) == 7:
                        current_value_pool = ThreadPool(processes=7)
                        th_output_0 = current_value_pool.apply_async(ques_answer, [replace_word, locations[0],con])
                        th_output_1 = current_value_pool.apply_async(ques_answer, [replace_word, locations[1],con])
                        th_output_2 = current_value_pool.apply_async(ques_answer, [replace_word, locations[2],con])
                        th_output_3 = current_value_pool.apply_async(ques_answer, [replace_word, locations[3],con])
                        th_output_4 = current_value_pool.apply_async(ques_answer, [replace_word, locations[4],con])
                        th_output_5 = current_value_pool.apply_async(ques_answer, [replace_word, locations[5],con])
                        th_output_6 = current_value_pool.apply_async(ques_answer, [replace_word, locations[6],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                        answer_list.extend(th_output_5.get())
                        answer_list.extend(th_output_6.get())'''
                answer_list = sort_list_within_list(answer_list, reverse=True)
                # print('answer_list: ', answer_list)
                final_answer_list = list()
                for score, answer, country, continent, quest in answer_list:
                    # print(final_answer_list)
                    present = False
                    if final_answer_list:
                        # print('Truw:',final_answer_list)
                        for idx, fin_ans in enumerate(final_answer_list):
                            if answer == fin_ans[1]:
                                present = True
                                break
                        if present:
                            if score > final_answer_list[idx][0]:
                                final_answer_list.remove(fin_ans[idx])
                                final_answer_list.append([score, answer, country, continent, quest])
                        else:
                            final_answer_list.append([score, answer, country, continent, quest])

                    else:
                        final_answer_list.append([score, answer, country, continent, quest])
                    for final_ans in final_answer_list:
                        loc_dict[final_ans[4]] = [final_ans[0], final_ans[1], final_ans[2], final_ans[3], final_ans[4]]


            else:
                country = continent = ''
                # replace_word = curr_value_dict[keyword].replace('<keyword>','')
                quest = replace_word + '?'
                ans = qa_ppl(context=sent, question=quest)
                print('Question: ' + quest)
                print('Answer: ' + str(ans))
                logger_info.info('Question: ' + quest)
                logger_info.info('Answer: ' + str(ans))
                if ans['score'] > 0.35:
                    if curr.lower() in ans['answer']:
                        answer = ans['answer']
                    else:
                        answer = curr + ' ' + ans['answer']

                    # answer_list.append([ans['score'],ans['answer'],loc,quest])
                    loc_dict[quest] = [ans['score'], answer, country, continent, quest]
            # print('RES: ',loc_dict)
            new_out_dict = list()
            for ques in loc_dict.keys():
                new_dict = dict()
                new_dict['question'] = ques
                if len(loc_dict[ques][2]) != 0:
                    new_dict['country'] = loc_dict[ques][2]
                elif len(loc_dict[ques][3]) != 0:
                    new_dict['continent'] = loc_dict[ques][3]
                else:
                    new_dict['continent'] = 'Global'
                new_dict['score_current_value'] = loc_dict[ques][0]
                new_dict['current_value'] = loc_dict[ques][1]
                new_dict['sentence'] = sent
                new_out_dict.append(new_dict)

        print('RES: ', new_out_dict)
        logger_info.info('RES: ' + str(new_out_dict))
    except Exception as e:
        print('Exception occurred at current_value():' + str(e))
        logger_bug.debug('Exception occurred at current_value():' + str(e))
    return new_out_dict


def find_current_year_cagr(sent, con):
    new_out_dict = list()
    sent = sent.lower()
    cagr_keyword = ''
    cagr_kws = {'cagr': 'What is the cagr',
                'compound annual growth rate': 'what is the compound annual growth rate',
                'annual growth rate': 'what is the annual growth rate',
                'annual rate of increase': 'what is the annual rate of increase',
                'annual growth factor': 'what is the annual growth factor'}

    def ques_answer(curr_value_dict, loc, con):
        # if cagr_keyword:
        #   replace_word = curr_value_dict[keyword].replace('<keyword>',cagr_keyword)
        # else:
        replace_word = curr_value_dict[keyword].replace('<keyword>', 'amount')
        quest = replace_word + ' in ' + loc.lower() + '?'

        ans = qa_ppl(context=sent, question=quest)
        print('Question: ' + quest + '\n' + 'Answer: ' + str(ans))
        logger_info.info('Question: ' + quest + '\n' + 'Answer: ' + str(ans))

        if ans['score'] > 0.35:
            if loc in con[0]:
                if loc.lower() != 'global':
                    country = loc
                    continent = ''
                else:
                    country = ''
                    continent = loc

            elif loc in con[1]:
                country = ''
                continent = loc
            answer_list.append([ans['score'], ans['answer'], country, continent, quest])
        return answer_list

    try:
        for kw in cagr_kws.keys():
            if kw in sent:
                # print(kw,' in text')
                cagr_keyword = kw
                break

        curr_value_dict = {' ': 'when is the initial year for <keyword>'}
        # proj_value_kws = ['reach','estimate','exceed','expand','increase','reach','surge','expected','grow']
        locations = list()
        keyword = ''

        # print(row)
        for kw in curr_value_dict.keys():
            if kw in sent:
                keyword = kw
                break
        # con = get_elements.find_geo(sent, nlp(sent), return_type='unprocessed')
        # # print('Find current year: ', con)
        locations.extend(con[0])  # country
        locations.extend(con[1])  # continent
        locations = [i for i in locations if i.lower() != 'global']
        # print(locations)
        loc_dict = dict()
        if keyword:
            # print('Keyword:',keyword,' present in:',sent )
            if locations:
                answer_list = list()
                mul_loc = list()
                for loc in locations:
                    answer_list.extend(ques_answer(curr_value_dict, loc, con))
                '''if len(locations) == 1 or len(locations) > 7:
                    for loc in locations:
                        answer_list.extend(ques_answer(curr_value_dict, loc,con))
                else:
                    if len(locations) == 2:
                        current_year_cagr_pool = ThreadPool(processes=2)
                        th_output_0 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[0],con])
                        th_output_1 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[1],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                    if len(locations) == 3:
                        current_year_cagr_pool = ThreadPool(processes=3)
                        th_output_0 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[0],con])
                        th_output_1 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[1],con])
                        th_output_2 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[2],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                    if len(locations) == 4:
                        current_year_cagr_pool = ThreadPool(processes=4)
                        th_output_0 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[0],con])
                        th_output_1 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[1],con])
                        th_output_2 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[2],con])
                        th_output_3 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[3],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                    if len(locations) == 5:
                        current_year_cagr_pool = ThreadPool(processes=5)
                        th_output_0 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[0],con])
                        th_output_1 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[1],con])
                        th_output_2 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[2],con])
                        th_output_3 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[3],con])
                        th_output_4 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[4],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                    if len(locations) == 6:
                        current_year_cagr_pool = ThreadPool(processes=6)
                        th_output_0 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[0],con])
                        th_output_1 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[1],con])
                        th_output_2 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[2],con])
                        th_output_3 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[3],con])
                        th_output_4 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[4],con])
                        th_output_5 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[5],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                        answer_list.extend(th_output_5.get())
                    if len(locations) == 7:
                        current_year_cagr_pool = ThreadPool(processes=7)
                        th_output_0 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[0],con])
                        th_output_1 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[1],con])
                        th_output_2 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[2],con])
                        th_output_3 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[3],con])
                        th_output_4 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[4],con])
                        th_output_5 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[5],con])
                        th_output_6 = current_year_cagr_pool.apply_async(ques_answer, [curr_value_dict, locations[6],con])
                        answer_list.extend(th_output_0.get())
                        answer_list.extend(th_output_1.get())
                        answer_list.extend(th_output_2.get())
                        answer_list.extend(th_output_3.get())
                        answer_list.extend(th_output_4.get())
                        answer_list.extend(th_output_5.get())
                        answer_list.extend(th_output_6.get())'''

                answer_list = sort_list_within_list(answer_list, reverse=True)
                # print('answer_list for current year: ', answer_list)
                final_answer_list = list()
                for score, answer, country, continent, quest in answer_list:
                    # print(final_answer_list)
                    present = False
                    if final_answer_list:
                        # print('Truw:',final_answer_list)
                        for idx, fin_ans in enumerate(final_answer_list):
                            if answer == fin_ans[1]:
                                present = True
                                break
                        if present:
                            if score > final_answer_list[idx][0]:
                                final_answer_list.remove(fin_ans[idx])
                                final_answer_list.append([score, answer, country, continent, quest])
                        else:
                            final_answer_list.append([score, answer, country, continent, quest])

                    else:
                        final_answer_list.append([score, answer, country, continent, quest])
                    for final_ans in final_answer_list:
                        loc_dict[final_ans[4]] = [final_ans[0], final_ans[1], final_ans[2], final_ans[3], final_ans[4]]


            else:
                country = continent = ''
                if cagr_keyword:
                    replace_word = curr_value_dict[keyword].replace('<keyword>', cagr_keyword)
                    # replace_word = curr_value_dict[keyword].replace('<keyword>','780.71 Million')
                    quest = replace_word + '?'
                    # print('Question:', quest)
                    ans = qa_ppl(context=sent, question=quest)
                    print('Question: ' + quest)
                    print('Answer: ' + str(ans))
                    logger_info.info('Question: ' + quest)
                    logger_info.info('Answer: ' + str(ans))
                    if ans['score'] > 0.35:
                        # answer_list.append([ans['score'],ans['answer'],loc,quest])
                        loc_dict[quest] = [ans['score'], ans['answer'], country, continent, quest]

                    new_out_dict = list()
                    for ques in loc_dict.keys():
                        new_dict = dict()
                        new_dict['question'] = ques
                        if len(loc_dict[ques][2]) != 0:
                            new_dict['country'] = loc_dict[ques][2]
                        elif len(loc_dict[ques][3]) != 0:
                            new_dict['continent'] = loc_dict[ques][3]
                        else:
                            new_dict['continent'] = 'Global'
                        new_dict['score_lower_year_cagr'] = loc_dict[ques][0]
                        new_dict['cagr_lower_year'] = loc_dict[ques][1]
                        new_out_dict.append(new_dict)

        print('RES: ', new_out_dict)
        logger_info.info('RES: ' + str(new_out_dict))
    except Exception as e:
        print('Exception at cagr_lower_year():' + str(e))
        logger_bug.debug('Exception at cagr_lower_year():' + str(e))
    return new_out_dict


def find_current_year_value(sent, input_value_dict):
    # print('input_value_dict before processing:', input_value_dict)
    sent = sent.lower()
    sent = normalize_currency(sent)
    try:
        for each_dict in input_value_dict:
            if 'current_value' in each_dict.keys():
                if 'continent' in each_dict.keys():
                    ques = 'when is the initial year for ' + each_dict['current_value'] + ' in ' + each_dict[
                        'continent'] + '?'
                elif 'country' in each_dict.keys():
                    ques = 'when is the initial year for ' + each_dict['current_value'] + ' in ' + each_dict[
                        'country'] + '?'
                else:
                    ques = 'when is the initial year for ' + each_dict[
                        'current_value'] + '?'  # in '+each_dict['country']+'?'
                ans = qa_ppl(context=sent, question=ques)
                print('Question: ' + ques)
                print('Answer: ' + str(ans))
                logger_info.info('Question: ' + ques)
                logger_info.info('Answer: ' + str(ans))
                if ans['score'] > 0.35:
                    each_dict['value_lower_year'] = ans['answer']
                    each_dict['score_lower_year_value'] = ans['score']
                else:
                    ques = 'when is the initial year for ' + each_dict['current_value'] + '?'
                    ans = qa_ppl(context=each_dict['sentence'], question=ques)
                    if ans['score'] > 0.35:
                        each_dict['value_lower_year'] = ans['answer']
                        each_dict['score_lower_year_value'] = ans['score']
                each_dict['question'] += ' and ' + ques
        # print('input_value_dict after processing:', input_value_dict)
    except Exception as e:
        print('Exception occurred at lower_year_value(): ' + str(e))
        logger_bug.debug('Exception occurred at lower_year_value(): ' + str(e))
    return input_value_dict


def partial_complete_approach_sentence(dict_list, text):
    changed_dict_list = list()
    for idx,each_dict in enumerate(dict_list):
        each_dict['approach'] = 'qa'
        each_dict['sentence'] = text
        value_flag = cagr_flag = year_flag = False
        if 'cagr' in each_dict.keys() and each_dict['cagr']:
            cagr_flag = True
        if ('cagr_lower_year' in each_dict.keys() and each_dict['cagr_lower_year']) or \
                ('value_lower_year' in each_dict.keys() and each_dict['value_lower_year']) or \
                ('upper_year' in each_dict.keys() and each_dict['upper_year']):
            year_flag = True
        if ('current_value' in each_dict.keys() and each_dict['current_value']) or \
                ('current_value' in each_dict.keys() and each_dict['current_value']):
            value_flag = True
        if value_flag and cagr_flag and year_flag:
            each_dict['match'] = 'complete'
        else:
            each_dict['match'] = 'partial'
        if not value_flag and not cagr_flag and not year_flag:
            continue
        else:
            changed_dict_list.append(each_dict)


    return changed_dict_list


def check_manual_verification(processed_dict,topics):
    mv_flag = False
    year_mv_flag = False # Check MV using only Year Flag
    topic_mv_flag = False
    # Manual Verification if only Year is present but no value or cagr accompanying the Year
    for each_dict in processed_dict:
        value_flag = cagr_flag = year_flag = False
        if 'cagr' in each_dict.keys() and each_dict['cagr']:
            cagr_flag = True
        if ('cagr_lower_year' in each_dict.keys() and each_dict['cagr_lower_year']) or \
                ('value_lower_year' in each_dict.keys() and each_dict['value_lower_year']) or \
                ('upper_year' in each_dict.keys() and each_dict['upper_year']):
            year_flag = True
        if ('current_value' in each_dict.keys() and each_dict['current_value']) or \
                ('current_value' in each_dict.keys() and each_dict['current_value']):
            value_flag = True
        print(year_flag,value_flag,cagr_flag)
        if year_flag and not value_flag and not cagr_flag: # If a dictionary contains only location and year value
            year_mv_flag = True
            break

    # Manual Verification if no Year present in any dictionary.
    if not year_mv_flag:
        year_flag = False
        for each_dict in processed_dict:
            if ('cagr_lower_year' in each_dict.keys() and each_dict['cagr_lower_year']) or \
                    ('value_lower_year' in each_dict.keys() and each_dict['value_lower_year']) or \
                    ('upper_year' in each_dict.keys() and each_dict['upper_year']):
                year_flag = True
        if not year_flag:
            year_mv_flag = True

    if year_mv_flag:
        for each_dict in processed_dict:
            each_dict['manual_verification'] = True
    if year_mv_flag:
        for each_dict in processed_dict:
            if find_cagr_for_topic(each_dict,topics):
                topic_mv_flag = True
                break
    if year_mv_flag and topic_mv_flag:
        for each_dict in processed_dict:
            each_dict['manual_verification'] = True

    return processed_dict


def ensure_keys(processed_dict):
    all_keys = ['cagr', 'percentage', 'upper_year', 'cagr_lower_year', 'current_value', 'value_lower_year',
                'projected_value', 'continent', 'country', 'sentence','manual_verification']
    for each_dict in processed_dict:
        for key in all_keys:
            if key not in each_dict.keys():
                print('ensuring keys: ',each_dict)
                if key == 'manual_verification':
                    each_dict[key] = False
                else:
                    each_dict[key] = ''
    return processed_dict


def get_results(sent, country_continents,topics):
    processed_dict = list()
    input_text = sent
    try:
        print('---Pre Processing')
        logger_info.info('---Pre Processing')
        sent = pre_process(sent)
        # procs = []
        # proc = Process(target=find_value)  # instantiating without any argument
        # procs.append(proc)
        # proc.start()
        # pool = Pool()
        # print('Calling all the threads... ')
        # logger_info.info('Calling all the threads... ')
        # pool = ThreadPool(processes=4)
        # th_output_0 = pool.map_async(find_value, [sent, country_continents])  # Projected Value
        # th_output_1 = pool.map_async(find_cagr, [sent, country_continents])  # CAGR
        # th_output_2 = pool.map_async(find_forecast_year, [sent, country_continents])  # Upper Year
        # th_output_3 = pool.map_async(find_current_value, [sent, country_continents])  # Current Value
        # proj_value_dict = th_output_0.get()
        # cagr_dict = th_output_1.get()
        # upper_year_dict = th_output_2.get()
        # current_value_dict = th_output_3.get()

        print('---Finding Projected Value')
        logger_info.info('---Finding Projected Value')
        proj_value_dict = find_value(sent, country_continents)  # Projected Value
        print(' Projected Value: ', proj_value_dict)
        logger_info.info(' Projected Value: ' + str(proj_value_dict))

        print('---Finding CAGR')
        logger_info.info('---Finding CAGR')
        cagr_dict = find_cagr(sent, country_continents)  # CAGR
        print(' CAGR: ', cagr_dict)
        logger_info.info(' CAGR: ' + str(cagr_dict))

        print('---Finding Upper Year')
        logger_info.info('---Finding Upper Year')
        upper_year_dict = find_forecast_year(sent, country_continents)  # Upper Year
        print(' Upper Year: ', upper_year_dict)
        logger_info.info(' Upper Year: ' + str(upper_year_dict))

        print('---Finding Current Value')
        logger_info.info('---Finding Current Value')
        current_value_dict = find_current_value(sent, country_continents)  # Current Value
        print(' Current Value: ', current_value_dict)
        logger_info.info(' Current Value: ' + str(current_value_dict))

        print('---Finding Lower Year for CAGR')
        logger_info.info('---Finding Lower Year CAGR Year')
        current_year_dict = find_current_year_cagr(sent, country_continents)  # Lower Year
        print(' Current CAGR Year:', current_year_dict)
        logger_info.info(' Current CAGR Year: ' + str(current_year_dict))

        print('---Finding Lower Year for Current Value')
        logger_info.info('---Finding Lower Year for Current Value')
        current_year_value = find_current_year_value(sent, current_value_dict)
        print(' Current Value Year:', current_year_dict)
        logger_info.info(' Current Value Year:' + str(current_year_dict))

        unprocessed_dict = combine_results(proj_value_dict, cagr_dict, upper_year_dict, current_year_dict,
                                           current_value_dict, current_year_value)
        print('Unprocessed Dict:', unprocessed_dict)
        logger_info.info('Unprocessed Dict:' + str(unprocessed_dict))
        filtered_dict = filter_answer(unprocessed_dict)
        processed_dict = process_dict(filtered_dict)
        processed_dict = partial_complete_approach_sentence(processed_dict, input_text)  # Adding more keys for tracking
        processed_dict = ensure_keys(processed_dict)
        processed_dict = check_manual_verification(processed_dict,topics)

    except Exception as e:
        print('Exception occurred at get_results(): ' + str(e))
        logger_bug.debug('Exception occurred at get_results(): ' + str(e))
    return processed_dict


def wrapper_market_value_qa(text, loc,topics):
    result_list = list()
    if text.startswith('[') and text.endswith(']'):
        text_list = ast.literal_eval(text)
    else:
        text_list = [text]

    for each_text in text_list:
        print('Recieved text')
        result_list.extend(get_results(each_text, loc,topics))
    return result_list


if __name__ == '__main__':
    # text = "More recently, the question around the impact of a changing automotive environment had a muting effect on valuations > while european and north american suppliers trade at similar valuation levels, japanese companies continue to trade at a discount, reflecting the stagnation in their home market japanese suppliers3) european suppliers4) north american suppliers5) 10-y-= 5.8x2) 10-y-= 4.4x2) impacted by the economic crisis evolution of automotive supplier valuations 1) ntm = next twelve months; 2) excluding the distorting impact of the economic crisis (jan-dec 2009 multiples); 3) aisin seiki, bridgestone, calsonic kansei, denso, exedy, jtekt, keihin, koito, mitsuba, nhk spring, nsk, stanley electric, showa, sumitomo riko, takata, tokai rika, toyoda gosei, toyota boshoku and ts tech; 4) american axle, borgwarner, cummins, dana, delphi, federal-mogul, iochpe maxion, johnson controls, lear, magna, martinrea, meritor, tenneco, tower, visteon and wabco; 5) autoliv, autoneum, brembo, cie, continental, elringklinger, faurecia, georg fischer, grammer, haldex, hella, leoni, norma, plastic omnium, pwo, shw, skf, stabilus, and valeo 11 global automotive supplier study 2018.pptx financial performance of suppliers varies greatly depending on region, company size, product focus and business model source: company information, lazard, roland berger > chinese-based suppliers currently achieve the highest margins with 9% ebit > nafta-based suppliers profit from their previous restructuring efforts and re-focusing on technology > european supplier margins have increased only marginally and are currently close to the average supplier universe values > japanese/korean suppliers remain at a low margin level of 6% ebit > large suppliers with >eur 10 billion revenues maintain strong margins of 7.5% ebit > midsized suppliers (eur 1.0 to 2.5 billion revenues) show strong and very profitable growth > upper midsized suppliers (eur 2.5 to 5 billion revenues) below average regarding profitability > small suppliers (below eur 0.5 billion revenues) lag behind in terms of growth and profitability > chassis suppliers clearly improved margins to 8% ebit driven by adas and active safety > tire suppliers maintained strong margins due to favorable raw material costs > powertrain suppliers gradually lost ground and achieve below-average margins in the meantime > interior suppliers still trail their peers, with recently even lower margins > product innovators are strongly growing and generating stable above-average margins of >7% ebit based on technology leadership translated into higher prices > process specialists continue to face below average margins of 6-7% ebit due to a lower innovation level and higher competitive pressure region company size product focus business model 1 2 3 4 profitability trends in the global automotive supplier industry 2010 vs. 2017e 12 global automotive supplier study 2018.pptx 11.7 8.7 8.3 7.2 6.5 6.3 china-and nafta-based suppliers are currently more profitable than the average china-based suppliers recently on the decline source: company information, lazard, roland berger japan south korea europe nafta china revenue cagr 2010-2017e ebit margin 2010-2017e 1 region 2017e = 7.3 11.9% 3.0% 6.9% 7.2% 5.1% > china-based suppliers have seen a decline in margins in recent years from a very high level due to intensified competition in their home market, but still achieve above average growth and profitability > nafta-based suppliers are still leveraging the effects from their substantial restructuring during the 2008/2009 auto crisis and the subsequent re-focusing on technology > europe-based suppliers largely benefit from leading technology positions in many segments and a favorable customer mix > south-korea-based suppliers' margins have come under pressure recently > japan-based suppliers have seen a slight recovery in terms of profitability, reducing the gap to other regions key supplier performance indicators by region, 2010 vs. 2017e [%] 13 global automotive supplier study 2018.pptx 5.5 7.2 8.6 6.9 6.6 7.5 2 company size source: company information, lazard, roland berger > large multinational suppliers (above eur 10 billion revenues) grew in line with the average, but have been able to achieve above average profitability > large suppliers (eur 2.5-5 billion revenues) gave up profitability to continue strong revenue growth > midsize suppliers (eur 1.0-2.5 billion revenues) increased profitability, mostly on the back of a very focused and technology-enabled product portfolio > very small suppliers lag behind in terms of growth and profitability due to limited resources for innovation and expansion >10.0 tire suppliers grew at a slower rate, but benefited from recently favorable raw material costs > chassis suppliers clearly improved margins over time development increasingly driven by advanced driver assistance and active safety > powertrain margins pressurized by intensified competition, the cost of (multiple) innovations and the rise of electric vehicles > exterior suppliers have been strongly growing while continuing to be profitable above average due to growing lightweight focus > electrics/infotainment suppliers face changing customer requirements and increased competition, reducing profitability > interior suppliers' margins continue to stay under pressure electrics/ infotainm.exterior chassis power-train interior tires 2.9% 4.9% 6.0% 7.4% 5.6% 5.6% revenue cagr 2010-2017e ebit margin 2010-2017e 2017e = 7.3 key supplier performance indicators by product focus, 2010 vs. 2017e [%] 15 global automotive supplier study 2018.pptx 7.2 6.7 product innovators outpace process specialists in terms of profitability and growth source: company information, lazard, roland berger 4 business model > on average, innovative products feature higher differentiation potential and greater oem willingness to pay higher prices > high entry barriers through intellectual property in many innovation-driven segments > competitive structure more consolidated in innovation-driven segments > higher fragmentation in many process-driven segments puts pressure on prices > product innovators grow slightly above process specialist due to increasing demand for innovative products and solutions process specialists2) product innovators1) 6.4% 5.5% revenue cagr 2010-2017e ebit margin 2010-2017e key supplier performance indicators by business model, 2010 vs. 2017e [%] note: analysis excludes tire suppliers; 1) business model based on innovative products with differentiation potential; 2) business model based on process expertise (while product differentiation potential is limited) 16 global automotive supplier study 2018.pptx margins of top-performing suppliers expected to stay at previously high levels low-performing peers still significantly lagging behind 8.2 8.0 8.3 8.3 revenue growth [2010=100] ebit2) margin [%] source: company information, lazard, roland berger 2010 2011 2012 2013 2014 2015 2016 2017e 2010 2011 2012 2013 2014 2015 2016 2017e key performance indicators of top vs. low performing suppliers1) 1) top (low) performance based on above-(below-) average revenue growth 2010-2016, roce 2010-2016 and roce 2016; 2) ebit after restructuring items 17 global automotive supplier study 2018.pptx however, top performance is not necessarily related to (product) innovation only source: company information, lazard, roland berger low product innovators top process specialists low process specialists top product innovators avg."
    # print(wrapper_market_value_qa(text))
    dict1 = [{'cagr': '', 'upper_year': '2027', 'cagr_lower_year': '2019', 'value_lower_year': '', 'current_value': '', 'projected_value': '', 'continent': ['Asia-Pacific'], 'score_upper_year': '0.431206613779068', 'approach': 'qa', 'sentence': 'Global EEG Devices Market to Reach US$ 2,198.0 Million by 2027 – Coherent   Market Insights  Business Wire  SEATTLE -- December 16, 2019  The global EEG devices market was valued at US$ 1,125.6 million in 2018, and is projected to exhibit a CAGR of 7.8 % over the forecast period (2019-2027).  EEG devices are used to detect brain waves and amplify the signals. These devices are used in the diagnosis and treatment of various disorders such as brain tumor, brain damage from head injury, encephalitis, stroke, and sleep disorders.  The global EEG (Electroencephalography) devices market is estimated to account for US$ 2,198.0 Mn in terms of value by the end of 2027.  Request your sample copy @ https://www.coherentmarketinsights.com/insight/request-sample/1665  Market Drivers  Increasing prevalence of sleep disorders is expected to boost growth of the global EEG devices market over the forecast period. For instance, according to a research published in Asian Journal of Psychiatry in February 2018, sleep disorders were found in 83.4% of the study population.  Moreover, EEG offers several benefits such as measurement during mute epochs, semantic integration, selective attention, and semantic integration. These advantages are expected to further propel growth of the market over the forecast period.  Market Opportunities  Increasing R&D in neuroscience is expected to offer lucrative growth opportunities for market players. For instance, in December 2019, researchers from University of Manchester published a research ‘Spatial Neglect in Stroke: Identification, Disease Process and Association with Outcome during Inpatient Rehabilitation’ to increase their understanding on spatial neglect in inpatient stroke survivors.  Increasing awareness programs related to aging and neurodegenerative diseases is also expected to boost growth of the market. For instance, in September 2019, The European Calcium Society (ECS) organized the eighth ECS workshop around the theme of “Calcium Signaling in Aging and Neurodegenerative Diseases” in Coimbra (Portugal).  Market Restraints  In EEG, availability of deep or small lesions may lead to abnormality in EEG outcome. EEG is also associated with other drawbacks such as false localization of epileptogenic zone, influence by hypoglycemia and alertness, and limited time sampling. Such disadvantages are expected to hamper growth of the market.  Key Takeaways:  Diagnostic Centers segment dominated the global EEG (Electroencephalography) devices market in 2018, accounting for 60.9% share in terms of value, followed by hospitals. The major driver attributing to the growth of the segment during the forecast period constitutes of increasing patient population and increasing demand for minimally invasive procedures.  Standalone (Fixed Devices) segment dominated the global EEG (Electroencephalography) devices market in 2018, accounting for 47.1% share in terms of value, followed by portable devices segment. Reason increasing product approvals is a major factor attributing to the growth of the segment during the forecast period  Market Trends  Key players in the market are focused on launching continuous EEG monitoring devices to enhance their market share. For instance, in December 2019, Ceribell launched rapid response EEG system ‘Clarity’ that offers continuous bedside EEG monitoring with instantaneous seizure detection and alert.  Key players in the market are also focused on gaining contracts to enhance their market share. For instance, in September 2018, BrainScope received a research contract of US$ 4.5 million from the U.S. Department of Defense (DOD) to create and integrate ocular capabilities into its handheld, multi-parameter mild Traumatic Brain Injury (mTBI) and concussion products.  Major players operating in the global EEG (Electroencephalography) devices market include Cadwell Laboratories Inc., Compumedics Limited, Natus Medical Incorporated, Neurosoft Ltd., Elekta AB, Electrical Geodesics, Inc., NeuroWave Systems Inc., EB Neuro S.p.A., and Nihon Kohden Corporation.  Key Developments  Key players in the market are focused on raising funding to expand their product portfolio. For instance, in September 2018, Ceribell, Inc. completed a US$ 35 million Series B financing led by new investors Optimas Capital Partners Fund and The Rise Fund to expand the commercialization of its innovative Rapid Response EEG system ‘Clarity’.  Key players in the market are also focused on product development and launch to expand their product portfolio. For instance, in November 2019, Rhythmlink International, LLC launched two new products, the BrainHealth Headset and the RLI EEG Template. BrainHealth Headset can be used to offer rapid EEG recordings.  Buy this Report (Single User License) @ https://www.coherentmarketinsights.com/insight/buy-now/1665  Taxonomy (Scope, segments)    *\xa0EEG (Electroencephalography) Devices Market, By Device Type:         *\xa08-Channel EEG        *\xa021-Channel EEG        *\xa032-Channel EEG        *\xa040-Channel EEG        *\xa08-Channel EEG        *\xa0Multi-Channel    *\xa0EEG (Electroencephalography) Devices Market, By Modality:         *\xa0Standalone        *\xa0Portable    *\xa0EEG (Electroencephalography) Devices Market, By End User:         *\xa0Hospitals        *\xa0Diagnostic Centers    *\xa0EEG (Electroencephalography) Devices Market, By Region:         *\xa0North America        *\xa0Latin America        *\xa0Europe        *\xa0Asia Pacific        *\xa0Middle East        *\xa0Africa \xa0 View source version on businesswire.com: https://www.businesswire.com/news/home/20191216005270/en/  Contact:  Mr. Raj Shah Coherent Market Insights 1001 4th Ave. #3200 Seattle, WA 98154 Tel: +1-206-701-6702 Email: sales@coherentmarketinsights.com', 'match': 'partial', 'percentage': '', 'country': '', 'manual_verification': False}]
    print(check_manual_verification(dict1))