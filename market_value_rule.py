from get_elements import find_geo
from logging_method import define_logging

logger_info, logger_bug = define_logging('dis_market_value_qa_rule/log/market_value.log')
import ast
import json
import time
import spacy

nlp = spacy.load('en_core_web_sm')
import re
import datetime

now = datetime.datetime.now()
# from flask import Flask, request, jsonify

# app = Flask(__name__)

with open('data/currency.json', 'r') as f:
    currency_dict = json.load(f)
currencies = [[i.lower(), len(i)] for i in currency_dict.keys()]
currencies.sort(reverse=True,
                key=lambda x: x[1])  # Sorting to set priority of match ('pound sterling' should come before 'sterling')
currencies = [i[0].lower() for i in currencies]
# currencies = ['new israeli sheqel', 'australian dollar', 'hong kong dollar', 'singapore dollar', 'canadian dollar', 'american dollar', 'pound sterling', 'yuan renminbi', 'russian ruble', 'chinese yuan', 'indian rupee', 'indian rupee', 'u.s. dollar', 'sg dollar', 'us dollar', 'sterling', 'hebrew', 'dollar', 'rupees', 'pound', 'euros', 'rupee', 'rand', 'euro', 'aud', 'au$', 'cad', 'ca$', 'cny', 'cny', 'rmb', 'hkd', 'hk$', 'ils', 'jpy', 'yen', 'krw', 'won', 'rub', 'sgd', 'sg$', 'zar', 'gbp', 'usd', 'us$', 'eur', 'inr', 'a$', 'c$', 's$', 'rs', '¥', '¥', '₩', '₽', '£', '$', '€', '₹']
amount = ['million', 'thousand', 'billion', 'trillion', 'mn', 'bn', 'tn', 'crore', 'kilo', 'mega', 'hectare']
cagr_kw_list = ['cagr', 'compound annual growth rate', 'annual growth rate', 'annual rate of inflation',
                'annual rate of increase', 'annual growth factor']


def text_correction(text):
    # if len(text) > 80:
    # print('Before Processing: ', text)
    text = text.replace('(', '')
    text = text.replace(')', '')
    text = ' ' + text + ' '
    text = text.replace(' emea ', 'Europe, Middle East, Africa')
    text = text.replace('~', '')
    text = text.replace('US$', 'USD')
    # text = text.replace('us$', 'USD')
    text = text.replace('us$', 'USD ')
    text = text.replace('us $', 'USD ')
    text = text.replace('A $', ' AUD ')
    text = text.replace(' R ', ' ZAR ')
    text = text.replace('C $', ' CAD ')
    text = text.replace('S $', ' SGD ')

    text = text.replace('HK $', ' HKD ')
    text = text.replace('CN ¥', ' CNY ')

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

    text = text.replace('SG$', ' SGD ')
    text = text.replace('SG $', ' SGD ')
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

    text = text.replace('au $', 'AUD ')
    text = text.replace('ca $', 'CAD ')
    text = text.replace('s $', 'SGD ')
    # text = text.replace('$', ' $ ')
    # text = text.replace('USD ', 'USD')
    # text = text.replace('usd', 'USD')

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
    text = text.replace('mn,', ' million,')
    text = text.replace('bn,', ' billion,')
    text = text.replace('tn,', ' trillion,')
    text = text.replace('Mn,', ' million,')
    text = text.replace('Bn,', ' billion,')
    text = text.replace('Tn,', ' trillion,')
    text = text.replace('tn,', ' trillion,')
    text = text.replace('mn.', ' million.')
    text = text.replace('bn.', ' billion.')
    text = text.replace('tn.', ' trillion.')
    text = text.replace('Mn.', ' million.')
    text = text.replace('Bn.', ' billion.')
    text = text.replace('Tn.', ' trillion.')
    text = text.replace('tn.', ' trillion.')
    text = text.replace(' $ ', ' USD ')
    text = text.replace(' %', '%')
    text = re.sub('\%+', '%', text)
    text = re.sub(r'[ECMPI]ST|UTC', '', text)
    text = re.sub('\s\s+', ' ', text)

    # if len(text) > 80:
    #     print('after processing: ', text)

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
    # for idx,i in enumerate(chunk_list):
    #     chunk_list[idx][2] = 0
    # print(i,'regex: ',re.findall('[0-9]+\.?[0-9]*', i[0])[0])
    # chunk_list[idx][0] = post_process_values(chunk_list[idx][0])
    # print('chunk list inside:',chunk_list)
    # chunk_list = list(set(chunk_list))
    trillion_numbers = list(set([float(re.findall('[0-9]+\.?[0-9]*', i[0])[0]) for i in chunk_list if
                                 has_num(i[0]) and 'trillion' in i[0].lower()]))
    billion_numbers = list(set([float(re.findall('[0-9]+\.?[0-9]*', i[0])[0]) for i in chunk_list if
                                has_num(i[0]) and 'billion' in i[0].lower()]))
    million_numbers = list(set([float(re.findall('[0-9]+\.?[0-9]*', i[0])[0]) for i in chunk_list if
                                has_num(i[0]) and 'million' in i[0].lower()]))
    thousand_numbers = list(set([float(re.findall('[0-9]+\.?[0-9]*', i[0])[0]) for i in chunk_list if
                                 has_num(i[0]) and 'thousand' in i[0].lower()]))
    crore_numbers = list(set([float(re.findall('[0-9]+\.?[0-9]*', i[0])[0]) for i in chunk_list if
                              has_num(i[0]) and 'crore' in i[0].lower()]))
    # print('trillion,billion,million,thousand', trillion_numbers, billion_numbers, million_numbers,thousand_numbers)
    sorted_amount_list = list()
    sorted_trillion = list()
    sorted_billion = list()
    sorted_million = list()
    sorted_thousand = list()
    sorted_crore = list()
    # print('billion_numbers:',billion_numbers)
    numbers_list = [trillion_numbers, billion_numbers, crore_numbers, million_numbers, thousand_numbers]
    for idx, numbers in enumerate(numbers_list):
        if numbers:
            numbers = sorted(numbers)  # 1.0, 1.2
            # print('numbers; ',numbers)
            #               amount_num = numbers[0]
            for amount_num in numbers:  # 1.2
                for i in chunk_list:  # string of money ($ 1 billion, $ 1.2 billion, etc)
                    # print('amount_num:',amount_num)
                    if str(amount_num).split('.')[1] == str(0) and str(amount_num).split('.')[0] in i[0]:
                        # print('i[0] in 1st:',i[0],idx)
                        if idx == 0 and i[0] not in sorted_trillion:
                            sorted_trillion.extend([i[0]])
                        if idx == 1 and i[0] not in sorted_billion:
                            sorted_billion.extend([i[0]])
                        if idx == 2 and i[0] not in sorted_crore:
                            sorted_crore.extend([i[0]])
                        if idx == 3 and i[0] not in sorted_million:
                            sorted_million.extend([i[0]])
                        if idx == 4 and i[0] not in sorted_thousand:
                            sorted_thousand.extend([i[0]])

                    elif str(amount_num) in i[0]:
                        # print('i[0] in 2nd:', i[0])
                        if idx == 0 and i[0] not in sorted_trillion:
                            sorted_trillion.extend([i[0]])
                        if idx == 1 and i[0] not in sorted_billion:
                            sorted_billion.extend([i[0]])
                        if idx == 2 and i[0] not in sorted_crore:
                            sorted_crore.extend([i[0]])
                        if idx == 3 and i[0] not in sorted_million:
                            sorted_million.extend([i[0]])
                        if idx == 4 and i[0] not in sorted_thousand:
                            sorted_thousand.extend([i[0]])
    print('sorted_million:', sorted_million)
    sorted_amount_list.extend(sorted_thousand)
    sorted_amount_list.extend(sorted_million)
    sorted_amount_list.extend(sorted_billion)
    sorted_amount_list.extend(sorted_crore)
    sorted_amount_list.extend(sorted_trillion)
    return sorted_amount_list


def get_fund_amount(doc, text):
    try:
        # print('WITHOUT CORRECTION: ',len(text),text)
        text = text_correction(text)
        # print('corrected text:',len(text),text)
        chunk_list = list()
        chunks = list()
        prev_token = ''
        token_len = len([token.text for token in doc])
        idx = 0
        for token in doc:
            # print('token details: ',token.text,token.ent_type_,token.pos_,token.text.lower() in currencies)
            found_flag = False

            if ((
                        'MONEY' in token.ent_type_ and not token.is_stop and token.text != '-' and 'mark' not in token.text.lower() and 'nearly' not in token.text.lower() and 'estimate' not in token.text.lower() and 'around' not in token.text.lower() and 'approx' not in token.text.lower()) or (
                        (
                                token.pos_ == 'NOUN' or token.pos_ == 'SYM' or token.pos_ == 'PUNCT' or token.pos_ == 'NUM' or token.pos_ == 'PROPN') and (
                                token.lemma_ in amount or token.text.lower() in currencies)) or (
                        (token.pos_ == 'NUM') and (
                        (prev_token and prev_token.text.lower().replace('~', '') in currencies) or (
                        idx + 1 < token_len and doc[idx + 1].text.lower().replace('~', '') in currencies or (
                        idx + 1 < token_len and doc[
                    idx + 1].text.lower().replace('~', '') in amount)))) and (
                        token.text.replace('.', '').replace(',',
                                                            '').isdigit() or token.lemma_.lower() in amount or token.text.lower().replace(
                    '~', '') in currencies)) or token.text.lower().replace('~', '') in currencies:
                found_flag = 'fund'
            if found_flag:
                chunks.append((token.text, found_flag, token.idx))
            else:
                if chunks:
                    entity = ' '.join([i[0] for i in chunks])
                    for amt in amount:
                        if amt in entity:
                            chunk_list.append((entity, chunks[0][1], chunks[0][2]))
                            break
                    chunks = list()
            prev_token = token
            idx += 1
        proj_value = ''
        curr_value = ''
        chunk_list = [[re.sub(',', '', i[0]), i[1], i[2]] for i in chunk_list]
        if chunk_list:
            print('chunk_list:', chunk_list)
            if len(chunk_list) > 1:
                unique_chunk_list = list()
                for i in chunk_list:
                    if not unique_chunk_list:
                        unique_chunk_list.append(i)
                    else:
                        for j in unique_chunk_list:
                            if i[0] not in j[0]:
                                unique_chunk_list.append(i)

                amount_list = get_sorted_amount(unique_chunk_list)
                # amount_list = list(set(amount_list))
                # amount_list = get_sorted_amount(amount_list)
                print('amount_list:', amount_list)
                if amount_list:
                    if len(amount_list) > 1:
                        proj_value = amount_list[-1]
                        curr_value = amount_list[0]
                    elif len(amount_list) == 1:
                        if ('stood' in text.lower() or 'was valued' in text.lower() or 'is valued' in text.lower() or (
                                'worth' in text.lower() and ' in ' in ' ' + text.lower() + ' ')):
                            curr_value = amount_list[0]
                        elif (
                                'worth' in text.lower() and ' by ' in ' ' + text.lower() + ' ') or 'grow' in text.lower() or 'reach' in text.lower() or 'forecast' in text.lower() or 'expect' in text.lower() or 'projected' in text.lower() or 'rise' in text.lower() or 'set to' in text.lower():
                            proj_value = amount_list[0]
                        else:
                            curr_value = amount_list[0]

            else:
                if ('stood' in text.lower() or 'was valued' in text.lower() or 'is valued' in text.lower() or (
                        'worth' in text.lower() and ' in ' in ' ' + text.lower() + ' ')):
                    curr_value = chunk_list[0][0]
                elif (
                        'worth' in text.lower() and ' by ' in ' ' + text.lower() + ' ') or 'grow' in text.lower() or 'reach' in text.lower() or 'forecast' in text.lower() or 'expect' in text.lower() or 'projected' in text.lower() or 'rise' in text.lower() or 'set to' in text.lower():
                    #                 amount_num = chunk_list[0][0]
                    proj_value = chunk_list[0][0]
                else:
                    curr_value = chunk_list[0][0]
    except Exception as e:
        print('Exception at get_fund_amount():' + str(e))
        logger_bug.debug('Exception at get_fund_amount():' + str(e))
    return proj_value, curr_value


def get_date(text, doc=None):
    list_years = list()
    lower_year = upper_year = ''
    no_of_unique_years = 0
    try:
        if doc == None:
            doc = nlp(text)
        for ind, ent in enumerate(doc.ents):
            if ent.label_ == 'DATE' or ent.label_ == 'CARDINAL':
                list_years.extend(re.findall('\d{4}', ent.text))
                # print('list_years:',list_years)
                list_years = [int(i) for i in list_years if now.year - 20 < int(i) < now.year + 20]
                # if len(years) > 1:
                #     years = sorted(years)
                #     lower_year = years[0]
                #     upper_year = years[-1]
                # elif len(years) == 1:
                #     if 'reach' in text.lower() or 'forecast' in text.lower() or 'expected' in text.lower() or 'projected' in text.lower() or 'rise' in text.lower():
                #         upper_year = years[0]
                #     else:
                #         lower_year = years[0]
        # if not lower_year or not upper_year:
        years_list = list()
        if re.findall('(\d{4}-\d{4})', text.lower()):  # Handling '2020-2025'
            year_tup = re.findall('(\d{4}-\d{4})', text.lower())  # returns ['2020-2025']
            for tup in year_tup:
                if tup:
                    years_list.extend([tup])
                else:
                    years_list.extend([tup])
        if re.findall('([^$]\d{4}-\d{2}([^W^%]))', ' ' + text.lower() + ' '):  # Handling '2004-10'
            year_tup = re.findall('([^$]\d{4}-\d{2})([^W^%])',
                                  ' ' + text.lower() + ' ')  # returns [('2004-10','.')] from text = '''Experts say this industry is likely to grow at a rate of approximately 30% compounded annual growth (cagr) during the years from 2004-10.'''
            print('year tuple:', re.findall('([^$]\d{4}-\d{2})([^W^%])', ' ' + text.lower() + ' '))
            for tup in year_tup:
                if len(tup[0]) > 1:
                    years_list.extend([tup[0].replace('.', '').strip()])
                else:
                    years_list.extend([tup[1].replace('.', '').strip()])
        if re.findall('([^USD\s?]\d{2}-\d{2}([^W^%]))', ' ' + text.lower() + ' '):  # Handling '2004-10'
            year_tup = re.findall('([^USD\s?]\d{2}-\d{2})([^W^%])',
                                  ' ' + text.lower() + ' ')  # returns [('2004-10','.')] from text = '''Experts say this industry is likely to grow at a rate of approximately 30% compounded annual growth (cagr) during the years from 2004-10.'''
            print('year tuple:', re.findall('([^USD\s?]\d{2}-\d{2})([^W^%])', ' ' + text.lower() + ' '))
            for tup in year_tup:
                if len(tup[0]) > 1:
                    years_list.extend([tup[0].replace('.', '').strip()])
                else:
                    years_list.extend([tup[1].replace('.', '').strip()])
        if re.findall('(fy\d+-?\d+)\.?', text.lower()):
            years_list.extend([i.replace('fy', '') for i in re.findall('(fy\d+-?\d+)\.?', text)])

        print('years_list:', years_list)
        for years in years_list:
            print('years: ', years)
            if '-' in years:  # len(years)==7: # '2004-10'
                split_years = years.split('-')
                for split_year in split_years:
                    if len(split_year) == 2:
                        list_years.extend([int(str(int(now.year / 100)) + split_year)])
                    elif len(split_year) == 4:
                        list_years.extend([split_year])  # int(str(int(now.year / 100)) + split_year))

            #     y1 = re.findall('(\d{4})|(\d{2})', years)
            #     print('y1',y1)
            #     if len(y1) == 1:
            #         # print('str(int(now.year/100))+y1[0]',str(int(now.year/100))+y1[0])
            #         list_years.append(int(str(int(now.year/100))+y1[0]))
            #     elif len(y1)>1:
            #         list_years.extend([int(str(int(now.year/100))+i) for i in y1])
            # else: # 2004-2010
            #     y1 = re.findall('\d{4}', years)
            #     print('y1', y1)
            #     if len(y1) == 1:
            #         # print('str(int(now.year/100))+y1[0]',str(int(now.year/100))+y1[0])
            #         list_years.append(int(str(int(now.year / 100)) + y1[0]))
            #     elif len(y1) > 1:
            #         list_years.extend([int(str(int(now.year / 100)) + i) for i in y1])
        # list_years = list_years.sort()
        print('Years obtained from text:', list_years)
        list_years = [int(i) for i in list_years if now.year - 20 < int(i) < now.year + 20]
        no_of_unique_years = len(set(list_years))
        list_years = list(set(list_years))
        if len(list_years) > 1:
            list_years = sorted(list_years)
            lower_year = list_years[0]
            upper_year = list_years[-1]
        elif len(list_years) == 1:
            if ('stood' in text.lower() or 'was valued' in text.lower() or 'is valued' in text.lower() or (
                    'worth' in text.lower() and ' in ' in ' ' + text.lower() + ' ')):
                lower_year = list_years[0]
            elif int(list_years[0]) > now.year or ((
                                                           'worth' in text.lower() and ' by ' in ' ' + text.lower() + ' ') or 'grow' in text.lower() or 'reach' in text.lower() or 'forecast' in text.lower() or 'expect' in text.lower() or 'projected' in text.lower() or 'rise' in text.lower() or 'set to' in text.lower() or 'estimated to' in text.lower()):
                upper_year = list_years[0]
            else:
                lower_year = list_years[0]
            # if 'reach' in text.lower() or 'forecast' in text.lower() or 'expect' in text.lower() or 'projected' in text.lower() or 'rise' in text.lower() or 'set to' in text.lower():
            #     upper_year = list_years[0]
            # else:
            #     lower_year = list_years[0]

        print("Lower Year: " + str(lower_year) + ' Upper Year: ' + str(upper_year))
        logger_info.info("Lower Year: " + str(lower_year) + ' Upper Year: ' + str(upper_year))
    except Exception as e:
        print('Exception at get_date():', e)
        logger_bug.debug('Exception at get_date():' + str(e))
    return lower_year, upper_year, no_of_unique_years


def sort_list_within_list(list_, reverse):
    list_.sort(reverse=reverse, key=lambda x: x[0])
    return list_


def find_cagr(text):  # Function to get cagr% nearest to the keywords list
    perc = ''
    try:
        kw_idx = 0
        cagr_indices = list()
        cagr_perc = re.findall('\d+.?\d*%', text)
        cagr_kw_list = ['cagr', 'compound annual growth rate', 'annual growth rate', 'annual rate of inflation',
                        'annual rate of increase', 'annual growth factor']
        for perc in cagr_perc:
            cagr_indices.append([text.index(perc), perc])
        for kw in cagr_kw_list:
            if kw in text.lower():
                kw_idx = text.index(kw)
        ind_diff = [[abs(kw_idx - i[0]), i[1]] for i in cagr_indices]
        ind_diff = sort_list_within_list(ind_diff, reverse=False)
        perc = ind_diff[0][1]
    except Exception as e:
        print('Exception at find_cagr(): ' + str(e))
        logger_bug.debug('Exception at find_cagr(): ' + str(e))
    return perc


def get_cagr(text, doc=None):
    if doc == None:
        doc = nlp(text)
    print('get_cagr:', text)
    cagr_perc = ''
    try:
        cagr = ''
        chunks = list()
        for chunk in doc.noun_chunks:
            chunks.append(chunk)

        for ind, chunk in enumerate(chunks):
            if [i for i in cagr_kw_list if i.lower() in chunk.text.lower() or chunk.text.lower() in i.lower()]:
                if ind < len(chunks) - 1 and '%' in chunks[ind + 1].text:
                    print('Detected CAGR % after noun chunk: ', chunks[ind + 1].text)
                    logger_info.info('Detected CAGR % after noun chunk: ' + str(chunks[ind + 1].text))
                    cagr = chunks[ind + 1].text
                elif ind != 0 and '%' in chunks[ind - 1].text:
                    print('Detected CAGR % before noun chunk: ', chunks[ind - 1].text)
                    logger_info.info('Detected CAGR % before noun chunk: ' + str(chunks[ind - 1].text))
                    cagr = chunks[ind - 1].text
                elif '%' in chunk.text:
                    print('Detected CAGR % in noun chunk: ' + str(chunk.text))
                    logger_info.info('Detected CAGR % in noun chunk: ' + str(chunk.text))
                    cagr = chunk.text
                try:
                    # print('cagr---',cagr)
                    cagr_perc = re.findall('\d+.?\d*%', cagr)[0]
                except Exception as e:
                    print('Exception at get_cagr(): ' + str(e))
                    logger_bug.debug('Exception at get_cagr(): ' + str(e))
                    cagr_perc = find_cagr(text)
                print("CAGR:" + str(cagr_perc))
                logger_info.info("CAGR:" + str(cagr_perc))

        if not cagr_perc:
            for ind, ent in enumerate(doc.ents):
                if ent.label_ == 'PERCENT':
                    cagr = ent.text
                    if 'x' not in cagr:
                        cagr_perc = re.findall('\d+.?\d*%', cagr)[0]
                        print("CAGR: " + str(cagr_perc))
                        logger_info.info("CAGR: " + str(cagr_perc))
                        break
        if not cagr_perc and [i for i in cagr_kw_list if i.lower() in text.lower() or text.lower() in i.lower()]:
            numbers = re.findall(r'\d+\.*\d*\%', text)
            if numbers:
                if has_num(numbers[0]):
                    cagr = numbers[0]
                    if 'x' not in cagr:
                        cagr_perc = numbers[0]
                        print("Percentage: " + str(cagr_perc))

    except Exception as e:
        print('Exception at get_cagr():' + str(e))
        logger_info.info('Exception at get_cagr():' + str(e))
        cagr_perc = ''
    return cagr_perc


def get_amount(text, doc=None):
    proj_value = curr_value = ''
    try:
        if doc == None:
            doc = nlp(text)
        proj_value = ''
        curr_value = ''
        amounts = get_fund_amount(doc, text)
        if amounts:
            amt_to_sort = [[i, '', 0] for i in amounts]
            print('Before sorting', amounts)
            amounts = get_sorted_amount(amt_to_sort)
            print('After sorting:', amounts)
            proj_value = amounts[0]
            curr_value = amounts[1]
        print('Projected Value: ' + str(proj_value) + ' Current Value: ' + str(curr_value))
        logger_info.info('Projected Value: ' + str(proj_value) + ' Current Value: ' + str(curr_value))
    except Exception as e:
        logger_info.info('Exception at get_amount():' + str(e))
        print('Exception at get_amount():' + str(e))
    return proj_value, curr_value


def get_cagr_sentences(summary_list):
    selected_sentences = list()
    try:
        print('Obtained Summary: ' + str(summary_list))
        logger_info.info('Obtained Summary: ' + str(summary_list))
        if '[' in summary_list and ']' in summary_list:
            summary = ast.literal_eval(summary_list)
        else:
            summary = [summary_list]
        if summary:
            for i in summary:
                i = text_correction(i)
                if (
                        'cagr' in i.lower() or 'compound annual growth rate' in i.lower() or 'annual growth rate' in i.lower() or 'annual rate of inflation' in i.lower() or 'annual growth factor' in i.lower() or 'annual rate of increase' in i.lower()) and '%' in i:
                    # if ('cagr' in i.lower() or 'compound annual growth rate' in i.lower()) and '%' in i:
                    selected_sentences.append(i)
        print('Selected Sentences: ' + str(selected_sentences))
        logger_info.info('Selected Sentences: ' + str(selected_sentences))
    except Exception as e:
        print('error at cagr', e)
    return selected_sentences


def get_units_sentences(summary_list):
    # currencies = ['£', '$', '€', '¥', '₹', 'Rs', 'USD', 'US$', 'AUD']
    units = ['million', 'thousand', 'billion', 'trillion', 'mn', 'bn', 'tn', 'crore', 'kilo', 'mega', 'hectare']
    #     print('Obtained Summary: ',summary_list)
    if '[' in summary_list and "]" in summary_list:
        summary = ast.literal_eval(summary_list)
    else:
        summary = [summary_list]
    selected_sentences = list()

    if summary:
        for i in summary:
            i = text_correction(i)
            if 'cagr' not in i.lower() and 'compounded annual growth rate' not in i.lower() and 'annual growth rate' not in i.lower() and 'annual rate of inflation' not in i.lower() and 'annual growth factor' not in i.lower() and 'annual rate of increase' not in i.lower():
                curr_flag = False
                i = ' ' + i + ' '
                for keyword in units:
                    if ' ' + keyword + ' ' in i.lower() and ' cagr ' not in i.lower():
                        selected_sentences.append(i)
                        break
                locations = find_geo(i)
                if locations[0] or locations[1]:
                    if '%' in i or [curr for curr in currencies if curr in i]:
                        selected_sentences.append(i)
    return list(set(selected_sentences))


# def get_quantity(text):
#
#     except Exception as e:
#         print('Exception at get_quantity(): '+str(e))
#         logger_bug.debug('Exception at get_quantity(): '+str(e))
#     return proj_value, curr_value

def post_process_values(proj_value, curr_value):
    try:

        proj_value = proj_value.replace('bn', 'billion')
        proj_value = proj_value.replace('billion', ' billion')
        proj_value = proj_value.replace('mn', 'million')
        proj_value = proj_value.replace('million', ' million')
        proj_value = proj_value.replace('tn', 'trillion')
        proj_value = proj_value.replace('trillion', ' trillion')
        proj_value = ' ' + proj_value + ' '.replace(' k ', 'thousand')
        proj_value = proj_value.replace('thousand', ' thousand')
        proj_value = ' ' + proj_value + ' '.replace('cr ', 'crore').strip().lower().strip()
        # print('proj_value:', proj_value)
        for currency in currencies:
            # print('currency:',currency)
            if currency in proj_value.lower():
                print('currency present:', currency, proj_value, currency_dict[currency],
                      proj_value.strip().lower().endswith(currency.lower()))
                if proj_value.strip().lower().endswith(currency.lower()):
                    proj_value = proj_value.lower().replace(currency.lower(), '')
                    proj_value = (currency_dict[currency] + ' ' + proj_value.lower()).strip()
                elif not proj_value.strip().lower().startswith(currency.lower()):
                    proj_value = proj_value.strip().lower().replace(currency, '')
                    proj_value = (currency_dict[currency] + ' ' + proj_value.lower()).strip()

                else:
                    proj_value = (
                        proj_value.lower().replace(currency.lower(), currency_dict[currency.lower()] + ' ')).strip()
                break
            # tok = currency_dict[currencies[currencies.index(token.text.lower())]]
        proj_value_correction = proj_value.split()
        proj_value = ' '.join(
            [i for i in proj_value_correction if has_num(i) or i.lower() in amount or i.lower() in currencies])

        if re.findall('^\d+', proj_value) and proj_value.split()[
            1] not in amount:  # Removing unnecessary numbers in beginning
            proj_value = proj_value.replace(re.findall('^\d+', proj_value)[0], '')
        proj_value = re.sub('\s+', ' ', proj_value)

        curr_value = curr_value.replace('bn', ' billion')
        curr_value = curr_value.replace('billion', ' billion')
        curr_value = curr_value.replace('mn', ' million')
        curr_value = curr_value.replace('million', ' million')
        curr_value = curr_value.replace('tn', ' trillion')
        curr_value = curr_value.replace('trillion', ' trillion')
        curr_value = ' ' + curr_value + ' '.replace(' k ', 'thousand')
        curr_value = curr_value.replace('thousand', ' thousand')
        curr_value = ' ' + curr_value + ' '.replace('cr ', 'crore').strip().lower().strip()
        for currency in currencies:
            # print('currency:', currency)
            if currency in curr_value.lower():
                if curr_value.strip().lower().endswith(currency.lower()):
                    print('currency present:', currency, curr_value, currency_dict[currency])
                    curr_value = curr_value.lower().replace(currency.lower(), '')
                    curr_value = (currency_dict[currency.lower()] + ' ' + curr_value.lower()).strip()
                elif not curr_value.strip().lower().startswith(currency.lower()):
                    curr_value = curr_value.strip().lower().replace(currency, '')
                    curr_value = (currency_dict[currency] + ' ' + curr_value.lower()).strip()

                else:
                    curr_value = (
                        curr_value.lower().replace(currency.lower(), currency_dict[currency.lower()] + ' ')).strip()
                break
        curr_value_correction = curr_value.split()
        curr_value = ' '.join(
            [i for i in curr_value_correction if has_num(i) or i.lower() in amount or i.lower() in currencies])
        # extra_num = re.findall('^\d+', curr_value)
        if re.findall('^\d+', curr_value) and curr_value.split()[1] not in amount:
            curr_value = curr_value.replace(re.findall('^\d+', curr_value)[0], '')
        curr_value = re.sub('\s+', ' ', curr_value)
    except Exception as e:
        print('Exception in post_process_values: ' + str(e))
        logger_bug.debug('Exception in post_process_values: ' + str(e))
    return proj_value, curr_value


def get_amount_units(text, doc=None):
    proj_value = ''
    curr_value = ''
    try:
        if doc == None:
            doc = nlp(text)

        amounts = get_fund_amount(doc, text)
        # print('eecued here: ')
        if amounts:
            if amounts[0] and has_num(amounts[0]) and 'x' not in amounts[0]:
                proj_value = amounts[0]
            else:
                proj_value = ''
            if amounts[1] and has_num(amounts[1]) and 'x' not in amounts[1]:
                curr_value = amounts[1]
            else:
                curr_value = ''
        if not proj_value and not curr_value:  # In case of values other than currencies: Eg: 11 million Kilos, 12 thousand hectares, etc
            text = re.sub(',', '', text)
            unfiltered_numbers = re.findall(
                r'\$?(\d+\.?\d+\s?(million|thousand|billion|units|trillion|mn|bn|tn|crore|kilo|mega|hectare)\s?[a-z]*)',
                text.lower())
            numbers = list()
            for i in unfiltered_numbers:  # 339.3 million in, # 80.4 million subscribers
                i_split = i[0].split()
                filtered_string = ''
                for split_text in i_split:
                    if (split_text.replace(',', '').replace('.', '').isnumeric()) or (split_text in amount):
                        filtered_string = filtered_string + ' ' + split_text
                numbers.append([filtered_string.strip(), 0])  # '0' is a dummy placeholder

            if numbers:
                numbers = get_sorted_amount(numbers)
                print('numbers:', numbers)
                if ('stood' in text.lower() or 'was valued' in text.lower() or 'is valued' in text.lower() or (
                        'worth' in text.lower() and ' in ' in ' ' + text.lower() + ' ')) and len(numbers) == 1:
                    curr_value = numbers[0]
                elif (
                        'worth' in text.lower() and ' by ' in ' ' + text.lower() + ' ') or 'grow' in text.lower() or 'reach' in text.lower() or 'forecast' in text.lower() or 'expect' in text.lower() or 'projected' in text.lower() or 'rise' in text.lower() or 'set to' in text.lower() or 'estimated to' in text.lower():
                    if len(numbers) > 1:
                        proj_value = numbers[-1]
                        curr_value = numbers[0]
                    else:
                        curr_value = numbers[0]

                else:
                    curr_value = numbers[0]
                    if len(numbers) > 1:
                        proj_value = numbers[-1]
        proj_value, curr_value = post_process_values(proj_value, curr_value)

    except Exception as e:
        print('Exception at get_amount_units(): ', e)
        logger_bug.debug('Exception at get_amount_units(): ' + str(e))
    return proj_value, curr_value


def get_perc(doc, text):
    try:
        percentage = ''
        percentage_num = ''
        chunks = list()
        for chunk in doc.noun_chunks:
            chunks.append(chunk)
        for ind, chunk in enumerate(chunks):

            if 'cagr' not in text and 'x' not in chunk.text.lower():
                # print('Chunk:',chunk.text.lower())
                if ind < len(chunks) - 1 and '%' in chunks[ind + 1].text:
                    print('Detected % after noun chunk: ', chunks[ind + 1].text)
                    #                     logger_info.info('Detected CAGR % after noun chunk: '+str(chunks[ind + 1].text))
                    percentage = chunks[ind + 1].text
                elif ind != 0 and '%' in chunks[ind - 1].text:
                    print('Detected % before noun chunk: ', chunks[ind - 1].text)
                    #                     logger_info.info('Detected CAGR % before noun chunk: '+str(chunks[ind - 1].text))
                    percentage = chunks[ind - 1].text
                elif '%' in chunk.text:
                    print('Detected % in noun chunk: ' + str(chunk.text))
                    #                     logger_info.info('Detected CAGR % in noun chunk: ' +str(chunk.text))
                    percentage = chunk.text
                if percentage:
                    percentage_num = re.findall('\d+.?\d*%', percentage)[0]

                    logger_info.info("Percentage: " + str(percentage_num))

        if not percentage_num and 'cagr' not in text:
            for ind, ent in enumerate(doc.ents):
                if ent.label_ == 'PERCENT':
                    percentage = ent.text
                    if 'x' not in percentage:
                        percentage_num = re.findall('\d+.?\d*%', percentage)[0]
                        logger_info.info("Percentage: " + str(percentage_num))
                        break
        if not percentage_num and 'cagr' not in text:
            numbers = re.findall(r'\d+\.*\d*\%', text)
            if numbers:
                if has_num(numbers[0]):

                    if 'x' not in percentage:
                        percentage_num = numbers[0]
                        print("Percentage: " + str(percentage_num))
    except Exception as e:
        print('Exception at get_perc():' + str(e))
        logger_bug.debug('Exception at get_perc():' + str(e))
        percentage_num = percentage = ''
    return percentage_num


def segment_no_cagr(text):
    input_text = text
    res_dict = {'country': [], 'continent': [], 'percentage': '', 'cagr': '', "projected_value": '',
                "current_value": '', 'lower_year': '', 'upper_year': '', 'sentence': '', 'approach': '2',
                'match': 'partial'}
    location_flag = False
    value_flag = False
    year_flag = False
    perc_flag = False

    if not text.endswith('.'):
        text = text + '.'
    text = text_correction(text)

    doc = nlp(text)
    locations = find_geo(text)
    if locations[0]:
        res_dict['country'] = locations[0]
        location_flag = True
    if locations[1]:
        res_dict['continent'] = locations[1]
        location_flag = True

    if 'cagr' not in text and 'compound annual growth rate' not in text:
        percentage = get_perc(doc, text)
        if percentage:
            res_dict['percentage'] = percentage
            perc_flag = True
    # if cagr:
    #     res_dict['cagr'] = cagr
    #     perc_flag = True

    proj_value, curr_value = get_amount_units(text, doc)
    if proj_value.strip():
        res_dict['projected_value'] = proj_value.strip()
        value_flag = True
    if curr_value.strip():
        res_dict['current_value'] = curr_value.strip()
        value_flag = True

    dates = get_date(text, doc)
    if dates[0]:
        res_dict['lower_year'] = dates[0]
        year_flag = True
    if dates[1]:
        res_dict['upper_year'] = dates[1]
        year_flag = True
    no_of_unique_years = dates[2]
    res_dict['sentence'] = input_text
    if value_flag and perc_flag and year_flag:
        res_dict['match'] = 'complete'
    else:
        if not (location_flag and not perc_flag and not value_flag and not year_flag) and not (
                perc_flag and not location_flag and not value_flag and not year_flag) and not (
                value_flag and not perc_flag and not location_flag and not year_flag) and not (
                year_flag and not perc_flag and not value_flag and not location_flag):
            res_dict['match'] = 'partial'
    if no_of_unique_years > 3:
        res_dict['manual_verification'] = True
    # return_flag = False
    # if value_flag and not (location_flag and year_flag and perc_flag):
    #     return_flag = True
    # elif location_flag and (perc_flag or value_flag):
    #     return_flag = True
    # elif year_flag and (perc_flag or value_flag):
    #     return_flag = True
    # elif perc_flag and (location_flag or year_flag):
    #     return_flag = True

    # if return_flag:
    #     return res_dict
    # else:
    #     return {}
    return res_dict


def get_company_sentences(summary_list):
    companies_keywords = ["industry participants", "top players", "key market players", "leading market players",
                          'leading players', 'key players', 'major players', 'market leaders', 'leading companies',
                          'key companies', 'major companies', 'companies']
    print('Obtained Summary for companies: ' + str(summary_list))
    logger_info.info('Obtained Summary for companies: ' + str(summary_list))
    if '[' in summary_list and "]" in summary_list:
        summary = ast.literal_eval(summary_list)
    else:
        summary = [summary_list]
    selected_sentences = list()
    if summary:
        for i in summary:
            for keyword in companies_keywords:
                if ' ' + keyword + ' ' in i:
                    selected_sentences.append(i)
                    break
    print('Selected Sentences: ' + str(selected_sentences))
    logger_info.info('Selected Sentences: ' + str(selected_sentences))
    return selected_sentences


def get_companies(text_list):
    entity_list = ['ORG', 'GPE', 'PERSON']
    selected_sentences = get_company_sentences(text_list)
    #     selecetd_sentences= [text_list]
    companies_list = list()
    res_list = list()
    for text in selected_sentences:
        input_text = text
        text = text_correction(text)
        res_dict = dict()
        res_dict['sentence'] = input_text
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in entity_list:
                companies_list.append(ent.text)
        res_dict['companies'] = companies_list
        # res_dict['sentence'] = text
        res_list.append(res_dict)
    #     print('res_list:',res_list)
    return res_list


def get_market_value(text):
    out_dict = {'cagr': '', 'value_lower_year': '', 'cagr_lower_year': '', 'percentage': '', 'upper_year': '',
                'projected_value': '',
                'current_value': '', 'country': '', 'continent': '', 'sentence': text, 'approach': 'rule',
                'match': 'partial', 'manual_verification': False}
    location_flag = False
    value_flag = False
    year_flag = False
    perc_flag = False
    no_of_unique_years = 0
    try:
        input_text = text
        print('Received Text for getting CAGR and Value: ' + str(text))
        logger_info.info('Received Text: ' + str(text))
        out_dict['sentence'] = input_text
        print('Pre-Processing')
        logger_info.info('Pre-Processing')
        if not text.endswith('.'):
            text = text + '.'
        text = text_correction(text)
        # print('corrected text:',text)
        doc = nlp(text)

        print('Fetching CAGR')
        logger_info.info('Fetching CAGR')
        cagr_perc = get_cagr(text, doc)
        if cagr_perc:
            out_dict['cagr'] = cagr_perc
            perc_flag = True

        print('Fetching Forecast/Current Year')
        logger_info.info('Fetching Date')
        dates = get_date(text, doc)
        if dates[0]:
            out_dict['value_lower_year'] = dates[0]
            year_flag = True
        if dates[1]:
            out_dict['upper_year'] = dates[1]
            year_flag = True
        no_of_unique_years = dates[2]
        print('Fetching Current and Projected Value')
        logger_info.info('Fetching Current and Projected Value')
        proj_value, curr_value = get_amount_units(text, doc)
        if proj_value.strip():
            out_dict['projected_value'] = proj_value.strip()
            value_flag = True
        if curr_value.strip():
            out_dict['current_value'] = curr_value.strip()
            value_flag = True

        print('Fetching Locations')
        logger_info.info('Fetching Locations')
        locations = find_geo(text, doc)
        print('Countries Found: ' + str(locations[0]) + ' Continents Found:' + str(locations[1]))
        if locations[0]:
            out_dict['country'] = locations[0]
            location_flag = True
        if locations[1]:
            out_dict['continent'] = locations[1]
            location_flag = True
        # print('out_dict:',out_dict)
        if value_flag and perc_flag and year_flag:
            out_dict['match'] = 'complete'
        else:
            out_dict['match'] = 'partial'
        if no_of_unique_years > 3:
            out_dict['manual_verification'] = True

        # return_flag = False
        # if value_flag and not (location_flag and year_flag and perc_flag):
        #     return_flag = True
        # elif location_flag and (perc_flag or value_flag):
        #     return_flag = True
        # elif year_flag and (perc_flag or value_flag):
        #     return_flag = True
        # elif perc_flag and (location_flag or year_flag):
        #     return_flag = True

        # if return_flag:
        #     print('Final Result: ' + str(out_dict))
        #     logger_info.info('Final Result: ' + str(out_dict))
        #     return out_dict
        # else:
        #     print('Final Result: {}')
        #     logger_info.info('Final Result: {}')
        #     return {}
        return out_dict

    except Exception as e:
        logger_bug.debug('Exception at get_market_value():' + str(e))
        print('Exception at get_market_value():' + str(e))

    return out_dict


def wrapper_market_value_rule(summary_list):
    result_list = list()
    try:
        if summary_list.startswith('[') and summary_list.endswith(']'):
            summary = get_cagr_sentences(summary_list)
            # summary_no_cagr = get_units_sentences(summary_list)
        else:
            summary = [i for i in [summary_list] if
                       'cagr' in i.lower() or 'compounded annual growth rate' in i.lower() or 'annual growth rate' in i.lower() or 'annual rate of inflation' in i.lower() or 'annual growth factor' in i.lower() or 'annual rate of increase' in i.lower()]
            # summary_no_cagr = [i for i in [summary_list] if 'cagr' not in i.lower() and 'compounded annual growth rate' not in i.lower() and 'annual growth rate' not in i.lower() and 'growth rate' not in i.lower() and 'annual rate of inflation' not in i.lower() and 'annual growth factor' not in i.lower() and 'annual rate of increase' not in i.lower()]
        if summary:
            for i in summary:
                result_list.append(get_market_value(i))  # CAGR related sentences
        # if summary_no_cagr:
        #     for j in summary_no_cagr:
        #         result_list.append(segment_no_cagr(j))
    except Exception as e:
        logger_bug.debug('Exception at wrapper_get_market_value():' + str(e))
        print('Exception at wrapper_get_market_value():' + str(e))
    return result_list


# @app.route('/market_growth', methods=["GET", "POST"])
def get_market_value_api(text):
    out_dict = []  # {'cagr': '', 'lower_year': '', 'upper_year': '', 'projected_value': '', 'current_value': '',
    # 'country': '', 'continent': ''}
    try:
        if True:  # request.method == "POST":
            # req_json = ast.literal_eval(request.get_data(as_text=True))
            # text = req_json["text"].lower()
            api_time = time.time()
            out_dict = wrapper_market_value_rule(text)
            total_time = time.time() - api_time
            print('Final Result: ' + str(out_dict))
            logger_info.info('Final Result: ' + str(out_dict))
            print('Total Time Consumption: ' + str(total_time))
            logger_info.info('Total Time Consumption: ' + str(total_time))
    except Exception as e:
        logger_bug.debug('Exception in main function: ' + str(e))
        print('Exception at main function: ' + str(e))
    return out_dict

if __name__ == '__main__':
    print(get_cagr('a compound annual growth rate of 5.2%'))
#     #loans, leases, ependiture, expense, spend
#     # app.run(port='6030', host='0.0.0.0')
#     text = '''From 2007 through 2018, the real compound annual growth rate for the capital expenditure per mile of new electric transmission infrastructure was eight percent.'''
#     res = get_market_value_api(str(text))

# import pandas as pd
# df = pd.read_excel('cagr_context_based_p1_data.xlsx')
# df['cagr_program'] = ''
# df['lower_year_program'] = ''
# df['upper_year_program'] = ''
# df['current_value_program'] = ''
# df['projected_value_program'] = ''
# df['country_program'] = ''
# df['continent_program'] = ''
# for row,sentence in enumerate(df['sentence']):
#     if type(sentence)!=float:
#         res = get_market_value_api(sentence)
#         if len(res) == 1:
#             df.at[row,'cagr_program'] = res[0]['cagr']
#             df.at[row,'lower_year_program'] = res[0]['lower_year']
#             df.at[row,'upper_year_program'] = res[0]['upper_year']
#             df.at[row,'current_value_program'] = res[0]['current_value']
#             df.at[row,'projected_value_program'] = res[0]['projected_value']
#             df.at[row,'country_program'] = res[0]['country']
#             df.at[row,'continent_program'] = res[0]['continent']
# df.to_csv('context.csv',index=False)
