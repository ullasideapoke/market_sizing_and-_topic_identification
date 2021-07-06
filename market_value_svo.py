import re


from allennlp.predictors.predictor import Predictor
import allennlp_models.tagging
predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/openie-model.2020.03.26.tar.gz")

# OPENIE
from get_elements import find_geo
from market_value_rule import text_correction, has_num, get_cagr, amount, get_amount_units, \
    get_date, logger_bug, logger_info, currencies, cagr_kw_list, currency_dict

stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
             'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
             'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
             'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
             'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but',
             'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
             'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
             'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
             'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
             'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
             "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't",
             'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven',
             "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan',
             "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn',
             "wouldn't"]
pasttense_verbs = ['had', 'accrued', 'valued']
future_tense_verbs = ['project', 'reach', 'attain', 'expect', 'forecast', 'estimate', 'garner', 'total']
# necessary_verbs= ['valued','growing', 'expected']
past_tense_prop = ['from', 'in']
future_tense_prop = ['by', 'to']
# Co-reference Resolution
# coref_predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz")


cagr_keywords = ['cagr', 'compounded annual growth rate', 'annual growth rate', 'annual rate of inflation',
                 'annual growth factor', 'annual rate of increase']


def combine_svos(selected_svo):  # Credit where due: Dinesh, Rakshit
    try:
        for idx, outer_lst in enumerate(selected_svo):
            for id_, sent_verb_obj_lst in enumerate(outer_lst):
                # print("-->", sent_verb_obj_lst)
                if isinstance(sent_verb_obj_lst, str):
                    # print("**>", sent_verb_obj_lst)
                    # verb = sent_verb_obj_lst
                    for i, prv_info in enumerate(selected_svo[idx - 1]):
                        if isinstance(prv_info, str):
                            object_sent = selected_svo[idx - 1][i + 1][0]
                            if sent_verb_obj_lst in object_sent:
                                #     print("--------------------->", object_sent)
                                #     print("----------------------", outer_lst[id_ + 1])
                                for inid, val in enumerate(selected_svo[idx - 1]):
                                    if isinstance(val, str):
                                        selected_svo[idx - 1][inid + 1] = outer_lst[id_ + 1]
                                        # for outer_id, inner_lst in enumerate(listed):
                                        #     if outer_lst[id_ + 1] in inner_lst:
                                        #         del listed[outer_id]
                                        selected_svo.remove(outer_lst)
    except Exception as ex:
        print("Exception in combine_svos(): " + str(ex))
        logger_bug.debug("Exception in combine_svos(): " + str(ex))

    return selected_svo


def handle_split_data(list_text):  # ['a compound annual growth rate CAGR', 'of 5.2%', 'from 2020', 'to 2027']
    # print('BEFORE PROCESSING:',list_text)
    updates_list_text = list()
    try:
        for idx, text in enumerate(list_text):
            # print('texr',text)
            if [i for i in cagr_kw_list if i in text]:
                if idx < len(list_text) - 1 and '%' not in text and '%' in list_text[idx + 1]:
                    updates_list_text.append(' '.join([list_text[idx]] + [list_text[idx + 1]]))
                else:
                    updates_list_text.append(text)
            else:
                if updates_list_text:
                    if text not in updates_list_text[-1]:
                        updates_list_text.append(text)
                else:
                    updates_list_text.append(text)
        # print('After PROCESSING:', updates_list_text)
    except Exception as ex:
        print("Exception in handle_split_data(): " + str(ex))
        logger_bug.debug("Exception in handle_split_data(): " + str(ex))
    return updates_list_text


def process_svo(selected_svo, topics):

    # for i in selected_svo:
    #     print('GOT THIS LIST:',i)
    processed_svo = list()
    try:
        final_processed_svo = list()
        for idx, svo in enumerate(selected_svo):
            # print('svo[0]:',svo[0],idx)
            if svo[0] and (
            [topic for topic in topics if svo[0][-1].lower() in topic or topic.lower() in svo[0][-1].lower()]):
                text_containing_topic = svo[0][-1]
                # print('text_containing_topic:',text_containing_topic,idx)
                processed_svo.append(svo)
                for next_idx, next_svo in enumerate(selected_svo[idx + 1:]):
                    new_idx = idx + 1 + next_idx
                    if not selected_svo[new_idx][0] and any([has_num(i) for i in selected_svo[new_idx][2]]):
                        # print('APPPENDING: ',new_idx,selected_svo[new_idx][0], '...', [[text_containing_topic], selected_svo[new_idx][1], selected_svo[new_idx][2]])
                        processed_svo.append(
                            [[text_containing_topic], selected_svo[new_idx][1], selected_svo[new_idx][2]])
                    else:
                        break
        # print('before adding:',processed_svo)
        for proc_svo in processed_svo:
            print(proc_svo)
            subs = proc_svo[0]
            if subs:
                for i in subs:
                    # print("get_date(i+'.')",get_date(i+'.'))
                    # print("get_amount_units(text+'.'):",get_amount_units(text+'.'))
                    # print("re.findall('\d+\.?\d*%',i):",re.findall('\d+\.?\d*%',i))
                    if get_date(i + '.') != ('', '', 0) or get_amount_units(i + '.') != ('', '') or re.findall(
                            '\d+\.?\d*%', i):
                        proc_svo[2].append(i)
        # print('after adding:', processed_svo)
    except Exception as e:
        print('Exception at process_svo(): ' + str(e))
        logger_bug.debug('Exception at process_svo(): ' + str(e))
    return processed_svo


def get_mapped_results(predictor, text, topics):
    tags_list = list()
    svo_list = list()
    selected_verbs = list()
    selected_svo = list()
    try:
        print("\nExtracted SVO Triplets:")
        logger_info.info("\nExtracted SVO Triplets:")
        for verb in predictor.predict(text)['verbs']:
            if verb['verb']:  # not in stopwords:
                # sent_tokens = tokenizer.tokenize(text)
                n_r_n = re.findall(r'\[(.*?)\]', verb['description'])
                # print(n_r_n)
                n_before_v = list()
                n_after_v = list()
                verb_word = ''
                v_flag = False
                for i in n_r_n:
                    if i.startswith('V:'):
                        v_flag = True
                        verb_word = text_correction(i).replace(']', '').split(':')[1].strip()
                        continue
                    if not v_flag and has_num(i):
                        n_before_v.append(text_correction(i).replace(']', '').split(':')[1].strip())
                    elif v_flag and has_num(i):
                        n_after_v.append(text_correction(i).replace(']', '').split(':')[1].strip())
                print('[' + str(n_before_v) + ', "' + verb_word + '", ' + str(n_after_v) + '],')
                logger_info.info('[' + str(n_before_v) + ', "' + verb_word + '", ' + str(n_after_v) + '],')
                n_before_v_num_flag = False
                n_after_v_num_flag = False
                select = False
                for topic in topics:
                    for i in n_before_v:
                        if topic.lower() in i.lower() or i.lower() in topic.lower() or has_num(i):
                            select = True
                            break
                for topic in topics:
                    for j in n_after_v:
                        if topic.lower() in j.lower() or j.lower() in topic.lower() or has_num(j):
                            select = True
                            break
                if select:
                    handled_data = handle_split_data(
                        n_after_v)  # combining broken data like: ['a compound annual growth rate CAGR', 'of 5.2%', 'from 2020', 'to 2027']
                    selected_svo.append([n_before_v, verb['verb'], handled_data])
                # if any([has_num(i) or [topic for topic in topics if topic.lower() in i] for i in n_before_v]) or any(
                #         [has_num(i) or [topic for topic in topics if topic.lower() in i] for i in n_after_v]):
                #     selected_verbs.append(verb['verb'])
                #     handled_data = handle_split_data(
                #         n_after_v)  # combining broken data like: ['a compound annual growth rate CAGR', 'of 5.2%', 'from 2020', 'to 2027']
                #     selected_svo.append([n_before_v, verb['verb'], handled_data])
        # print('SELCTED SVO:\n')
        # logger_info.info('SELCTED SVO:\n')
        # for i in selected_svo:
        #     print(i)
        #     logger_info.info(str(i))
        print()
        logger_info.info('')
        processed_svo = process_svo(selected_svo, topics)

        # print('\nProcessed SVOLIST:')
        # for i in processed_svo:
        #     print(i)
        combined_svos = combine_svos(processed_svo)

        # shortlisted_svos = svos_with_topic(combined_svos)
        print('\nSelected SVO LIST:')
        logger_info.info('\nSelected SVO LIST:')
        for i in combined_svos:
            print(i)
            logger_info.info(str(i))
        selected_verbs = [i[1] for i in combined_svos]
        print('Selected verbs: ', selected_verbs)
        logger_info.info('Selected verbs: ' + str(selected_verbs))
    except Exception as e:
        print('Exception at get_mapped_results(): ' + str(e))
        logger_bug.debug('Exception at get_mapped_results(): ' + str(e))
    return combined_svos, selected_verbs
    # if len(n_before_v) == 1 and len(n_after_v) == 1:
    #     if has_num(n_before_v[0]) and not has_num(n_after_v[0]):
    #         tags_list.append([n_before_v[0], [], verb_word])
    #     elif has_num(n_after_v[0]) and not has_num(n_before_v[0]):
    #         tags_list.append([[], n_before_v[0], verb_word])
    #     elif has_num(n_after_v[0]) and has_num(n_before_v[0]):
    #         tags_list.append([n_before_v[0], n_before_v[0], verb_word])
    # elif len(n_after_v) > 1:
    #     for i in n_after_v:
    #         if n_before_v:
    #             tags_list.append([n_before_v[0], i, verb_word])


def detect_future_past(amount, text, verb, verbs_list):
    future = False
    text = ' ' + text + ' '
    try:
        num_list = [i.strip('.') for i in re.findall(r'\d+\.?\d*', amount)]
        print('Numbers Found: ', num_list, ' in ', amount, 'verb:', verb)
        index = text.find(num_list[0])
        dist_dict = dict()
        for word in pasttense_verbs:
            past_index = text.find(word)
            if past_index != -1:
                dist = index - past_index
                dist_dict[dist] = word
        for word in future_tense_verbs:
            future_index = text.find(word)
            if future_index != -1:
                dist = index - future_index
                dist_dict[dist] = word
        if verb in future_tense_verbs:
            future = False
            for i in verbs_list:
                if i == verb:
                    break
                else:
                    if i in future_tense_verbs:
                        future = False

        print('dist dict:', dist_dict, list(dist_dict.keys()), dist_dict[sorted(list(dist_dict.keys()))[0]])
        nearest_word = dist_dict[sorted(list(dist_dict.keys()))[0]].strip()
        # print('nearest_word.strip in future_tense:','by' in future_tense)
        if nearest_word.strip() in future_tense_verbs:
            future = True
        # print("PROJECTED VALUE?:",future)
    except Exception as e:
        print('Exception occurred at detect_curr_or_proj() :' + str(e))
        logger_bug.debug('Exception occurred at detect_curr_or_proj() :' + str(e))
    return future


def get_selected_svo_verbs(text, topic):
    res_list = list()
    topic_status = False
    empty_topic = False
    selected_svo = list()
    selected_verbs = list()
    try:
        text = text_correction(text)
        svo_list = get_mapped_results(predictor, text,
                                      topic)  # Returns [[[sub_1_1,sub_1_2,...],verb_1,[obj_1_1,obj_1_2,...]],
        # [sub_2_1,sub_2_2,...],verb_2,[obj_2_1,obj_2_2,...]]]

        for each_svo in svo_list:
            # print('each_svo: ',each_svo)
            if each_svo[0]:
                for expected_topic in each_svo[0]:
                    if topic.lower() in expected_topic.lower() or expected_topic.lower() in topic.lower():
                        topic_status = True
                        empty_topic = False
                        print('HERE 2: ', each_svo)
                        if any([has_num(i) for i in each_svo[0]]) or any([has_num(i) for i in each_svo[1]]):
                            selected_verbs.append(each_svo[1])
                            selected_svo.append(each_svo)
                        break
                if topic_status == False:
                    continue
            else:
                empty_topic = True
                if topic_status == True:
                    # print('HERE 1: ', each_svo)
                    if any([has_num(i) for i in each_svo[0]]) or any([has_num(i) for i in each_svo[1]]):
                        selected_verbs.append(each_svo[1])
                        selected_svo.append(each_svo)
                    continue
                else:
                    topic_status = False
        # print('\nSVOLIST:')
        # for i in selected_svo:
        #     print(i)
        # print('selected_verbs: ', selected_verbs)

    except Exception as e:
        print('Exception at get_selected_svo_verbs(): ' + str(e))
        logger_bug.debug('Exception at get_selected_svo_verbs(): ' + str(e))
    return selected_svo, selected_verbs


def get_results_svo(text, selected_svo, selected_verbs):
    res_dict = {'cagr': '', 'value_lower_year': '', 'cagr_lower_year': '', 'percentage': '', 'upper_year': '',
                'projected_value': '',
                'current_value': '', 'country': [], 'continent': [], 'sentence': text, 'approach': 'rule',
                'match': 'partial', 'manual_verification': False}
    try:
        for each_svo in selected_svo:
            for each in each_svo[0]:
                print('sending for location', each)
                countries, continents = find_geo(each, return_type='processed')
                res_dict['country'].extend(countries)
                res_dict['continent'].extend(continents)
            verb = each_svo[1]
            for s_v_o in each_svo:
                if type(s_v_o) == list and s_v_o:  # Else its a verb
                    for text in s_v_o:
                        # print("s_v_o text: ", text)
                        if has_num(text):
                            if not res_dict['cagr'] and [i for i in cagr_keywords if i in text.lower()]:
                                res_dict['cagr'] = get_cagr(text)
                            if [i for i in amount if i in text]:
                                amounts = get_amount_units(text + '.', doc=None)
                                # print('Got amount: ', amounts, text)
                                if amounts[0] and amounts[1]:
                                    if not res_dict['projected_value']:
                                        if amounts[0] not in res_dict['current_value']:
                                            res_dict['projected_value'] = amounts[0]
                                    if not res_dict['current_value']:
                                        if amounts[0] not in res_dict['projected_value']:
                                            res_dict['current_value'] = amounts[1]
                                    # if 'current_value' not in res_dict.keys() or not res_dict['current_value']:
                                    #     res_dict['current_value'] = amounts[1]
                                elif amounts[0] and not res_dict['projected_value']:
                                    res_dict['projected_value'] = amounts[0]
                                elif amounts[1]:
                                    value_bool = detect_future_past(amounts[1], text, verb,
                                                                    selected_verbs)  # True: Projected Value, False: Current Value
                                    # print(value_bool)
                                    if value_bool:
                                        res_dict['projected_value'] = amounts[1]
                                    else:
                                        res_dict['current_value'] = amounts[1]
                            if not res_dict['upper_year'] or not res_dict['value_lower_year']:
                                years = get_date(text + '.')
                                if years[0] and years[1]:
                                    res_dict['value_lower_year'] = years[0]
                                    res_dict['upper_year'] = years[1]

                            print(res_dict)
    except Exception as e:
        print('Exception at get_results_svo():' + str(e))
        logger_bug.debug('Exception at get_results_svo():' + str(e))
    return res_dict


def handle_currencies(unique_amounts, obj_list):
    curr_to_append = ''
    try:
        for idx, amt in enumerate(unique_amounts):
            if not [i for i in currencies if ' ' + i + ' ' in ' ' + amt.lower() + ' ']:
                for obj in obj_list:
                    if amt.lower() in obj.lower():
                        for curr in currencies:
                            if curr.lower() in obj.lower():
                                print("CURRENCY PRESENT IS :",curr.lower(), obj.lower())
                                curr_to_append = currency_dict[curr]
                                break
                        unique_amounts[idx] = curr_to_append.upper() + ' ' + amt
    except Exception as e:
        print('Exception at handle_currencies():' + str(e))
        logger_bug.debug('Exception at handle_currencies():' + str(e))
    return unique_amounts


def get_proj_curr(collected_amount, res_dict, object_list, selected_svo):
    try:
        unique_amounts = [collected_amount[0]]
        for amt1 in collected_amount:
            presence = False
            for u_amt in unique_amounts:
                if amt1.lower().strip() in u_amt.lower().strip() or u_amt.lower().strip() in amt1.lower().strip():
                    presence = True
                    break
                else:
                    continue
            if not presence:
                unique_amounts.append(amt1)

        unique_amounts = handle_currencies(unique_amounts, object_list)
        if len(unique_amounts) == 1 and res_dict['projected_value'] and not res_dict['current_value']:
            res_dict['current_value'] = collected_amount[0]
        elif len(unique_amounts) == 2 and res_dict['projected_value'] and not res_dict['current_value']:
            for amount1 in unique_amounts:
                if amount1 in res_dict['projected_value']:
                    unique_amounts.remove(amount1)
            res_dict['current_value'] = unique_amounts[0]
        elif len(unique_amounts) == 2 and not res_dict['projected_value'] and not res_dict['current_value']:
            res_dict['current_value'] = unique_amounts[0]
            res_dict['projected_value'] = unique_amounts[1]
        elif len(unique_amounts) == 1:

            for each_svo in selected_svo:
                if [i for i in pasttense_verbs if i in each_svo[1]]:
                    res_dict['current_value'] = unique_amounts[0]
                    break
                elif [i for i in future_tense_verbs if i in each_svo[1]]:
                    res_dict['projected_value'] = unique_amounts[0]
                    break
            if not res_dict['current_value'] or not res_dict['projected_value']:
                for idx, obj in enumerate(object_list):
                    if re.findall('\d+\.?\d+', unique_amounts[0]) and idx < len(object_list):
                        for value in re.findall('\d+\.?\d+', unique_amounts[0]):
                            # print('----',object_list[idx])
                            # print(value in obj)
                            # print([i for i in pasttense_verbs if i in obj])
                            # print((idx < len(object_list) and [i for i in pasttense_verbs if i in obj]))
                            if (not res_dict['current_value']) and value in obj and (
                                    [i for i in pasttense_verbs if i in obj] or (
                                    idx < len(object_list) and [i for i in past_tense_prop if
                                                                i in object_list[idx + 1]])):
                                res_dict['current_value'] = unique_amounts[0]
                                break
                            if (not res_dict['projected_value']) and value in obj and (
                                    [i for i in future_tense_verbs if i in obj] or (
                                    idx < len(object_list) and [i for i in future_tense_prop if
                                                                i in object_list[idx + 1]])):
                                res_dict['projected_value'] = unique_amounts[0]
                                break
    except Exception as e:
        print('Exception at get_proj_curr(): ' + str(e))
        logger_bug.debug('Exception at get_proj_curr(): ' + str(e))
    return res_dict


def get_amounts_app_1(text):
    text = ' ' + text + ' '
    stopwords_mat = stopwords + ['amount']
    curr_flag = False
    num_flag = False
    amount_flag = False
    set_curr = False
    try:
        for i in stopwords_mat:
            text = text.replace(' '+i+' ', ' ')
        text = re.sub('\s\s+', ' ', text)


        for curr in currencies:
            if text.count(' ' + curr + ' ') == 1:
                curr_flag = True
                print('currency present:', curr)
                break

        for amt in amount:
            if text.count(' ' + amt + ' ') == 1:
                amount_flag = True
                print('amount present:', amt)
                break

        if has_num(text):
            print('has num:', text)
            num_flag = True

        if num_flag and curr_flag and amount_flag:
            set_curr = True

    except Exception as e:
        print('Exception at get_amounts_app_1(): ' + str(e))
        logger_bug.debug('Exception at get_amounts_app_1(): ' + str(e))
    return text.strip(), set_curr


def get_cagr_from_list(res_dict, collected_cagr):
    try:
        unique_cagr = [i for i in collected_cagr if i != '']
        res_dict['cagr'] = list(set(unique_cagr))[0]
    except Exception as e:
        print('Exception at get_cagr_from_list(): ' + str(e))
        logger_bug.debug('Exception at get_cagr_from_list(): ' + str(e))
    return res_dict


def get_date_from_muliple_dates(res_dict, collected_years, selected_svo, object_list):
    try:
        # stopwords_year = stopwords+['year']
        # for idx, obj in enumerate(object_list):
        #     for stop in stopwords_year:
        #         obj = obj.replace(stop,'')
        #     object_list[idx] = obj

        # object_list = list()
        # projected_value = res_dict['projected_value']
        # current_value = res_dict['current_value']
        # object_list = [i[2] for i in selected_svo]
        if len(collected_years) == 2:
            res_dict['value_lower_year'] = sorted(collected_years)[0]
            res_dict['upper_year'] = sorted(collected_years)[1]
            print('approach 6')
        elif len(collected_years) > 2:
            for idx_obj, obj in enumerate(object_list):
                print('OBJ:', obj)
                count_of_years = 0
                for year in collected_years:
                    if str(year) in obj:
                        count_of_years += 1
                detected_year = [i for i in collected_years if str(i) in obj]
                if count_of_years == 1:

                    if res_dict['current_value'] and re.findall('\d+.?\d*', res_dict['current_value'])[0] in obj:
                        res_dict['value_lower_year'] = detected_year[0]
                    elif res_dict['projected_value'] and re.findall('\d+.?\d*', res_dict['projected_value'])[0] in obj:
                        res_dict['upper_year'] = detected_year[0]
                    elif len(obj) <= 19 and [i for i in past_tense_prop if
                                             i in obj]:  # 'from' in obj:  # and '-'+str(i)[-2:] not in obj: # 'from 2012', 'from the year 2012'
                        if [kw for kw in cagr_kw_list if kw.lower() in obj.lower() or (
                                idx_obj < len(object_list) and kw.lower() in object_list[idx_obj - 1].lower())]:
                            res_dict['cagr_lower_year'] = detected_year[0]
                        else:
                            res_dict['value_lower_year'] = detected_year[0]
                        print('approach 1')
                    elif len(obj) <= 15 and [i for i in past_tense_prop if i in obj]:  # 'in 2012', 'in the year 2013'
                        if [kw for kw in cagr_kw_list if kw.lower() in obj.lower() or (
                                idx_obj < len(object_list) and kw.lower() in object_list[idx_obj - 1].lower())]:
                            res_dict['cagr_lower_year'] = detected_year[0]
                        else:
                            res_dict['value_lower_year'] = detected_year[0]
                        print('approach 2')
                    elif len(obj) <= 15 and [i for i in future_tense_prop if i in obj]:  # 'to 2012'
                        res_dict['upper_year'] = detected_year[0]
                        print('approach 3', detected_year[0])
                    elif len(obj) <= 15 and [i for i in future_tense_prop if i in obj]:  # 'to 2012'
                        res_dict['upper_year'] = detected_year[0]
                        print('approach 4', detected_year[0])
                    elif '-' + str(detected_year[0])[-2:] in obj:  # To handle 2012-19
                        res_dict['upper_year'] = detected_year[0]  # 19
                        print('approach 5', detected_year[0])
                if count_of_years == 2:
                    if (res_dict['current_value'] and re.findall('\d+.?\d*', res_dict['current_value'])[0] in obj) or \
                            (res_dict['projected_value'] and re.findall('\d+.?\d*', res_dict['projected_value'])[
                                0] in obj):
                        res_dict['value_lower_year'] = sorted(detected_year)[0]
                        res_dict['upper_year'] = sorted(detected_year)[1]
        if len(collected_years) == 1:
            result_set = False
            for obj in object_list:
                detected_year = [i for i in collected_years if str(i) in obj]
                print('len is 1  :', detected_year)
                if detected_year:
                    if res_dict['current_value'] and re.findall('\d+.?\d*', res_dict['current_value'])[0] in obj:
                        res_dict['value_lower_year'] = detected_year[0]
                    elif res_dict['projected_value'] and re.findall('\d+.?\d*', res_dict['projected_value'])[0] in obj:
                        res_dict['upper_year'] = detected_year[0]
                    elif len(obj) <= 19 and [i for i in past_tense_prop if
                                             i in obj]:  # 'from' in obj:  # and '-'+str(i)[-2:] not in obj: # 'from 2012', 'from the year 2012'
                        res_dict['value_lower_year'] = detected_year[0]
                        print('approach 1')
                    elif len(obj) <= 15 and [i for i in past_tense_prop if i in obj]:  # 'in 2012', 'in the year 2013'
                        res_dict['value_lower_year'] = detected_year[0]
                        print('approach 2')
                    elif len(obj) <= 15 and [i for i in future_tense_prop if i in obj]:  # 'to 2012'
                        res_dict['upper_year'] = detected_year[0]
                        print('approach 3', detected_year[0])
                    elif len(obj) <= 15 and [i for i in future_tense_prop if i in obj]:  # 'to 2012'
                        res_dict['upper_year'] = detected_year[0]
                        print('approach 4', detected_year[0])
                    elif '-' + str(detected_year[0])[-2:] in obj:  # To handle 2012-19
                        res_dict['upper_year'] = detected_year[0]  # 19
                        print('approach 5', detected_year[0])

        print('YEAR RES_DICT: ', res_dict)
    except Exception as e:
        print('Exception at get_date_from_muliple_dates(): ' + str(e))
        logger_bug.debug('Exception at get_date_from_muliple_dates(): ' + str(e))
    return res_dict


def get_results_svo_2(text, selected_svo, selected_verbs):
    res_dict = {'cagr': '', 'value_lower_year': '', 'cagr_lower_year': '', 'percentage': '', 'upper_year': '',
                'projected_value': '',
                'current_value': '', 'country': [], 'continent': [], 'sentence': text, 'approach': 'rule',
                'match': 'partial', 'manual_verification': False}
    try:
        # print('entering loopp:')
        for each_svo in selected_svo:
            # print('loop')
            for each in each_svo[0]:
                print('sending for location', each)
                countries, continents = find_geo(each, return_type='processed')
                res_dict['country'].extend(countries)
                res_dict['continent'].extend(continents)
        all_chunks = list()
        collected_years = list()
        collected_amount = list()
        collected_cagr = list()
        object_list = list()
        for i in selected_svo:
            all_chunks.extend(i[2])
        for i in selected_svo:
            object_list.extend(i[2])
        print('OBJECTS FROM SELECTED SVOs: ', object_list)
        for i in all_chunks:
            print("COLLECTING FROM CHUNK:" + i)

            dates = get_date(i + '.')
            if dates[0]:
                collected_years.append(dates[0])
            if dates[1]:
                collected_years.append(dates[1])
            set_flag = False
            # func_amounts = ''
            # if len(i) < 17:
            #     func_amounts,set_flag = get_amounts_app_1(i)  # 'at USD 2 billion'
            # if set_flag and func_amounts:
            #     amounts = ('',func_amounts)
            if not set_flag:
                amounts = get_amount_units(i + '.')
            print('Amounts:', amounts)
            if amounts[0] and amounts[1]:
                print('Projected and Current values found: ' + amounts[0] + ' ' + amounts[1])
                res_dict['projected_value'] = amounts[0]
                res_dict['current_value'] = amounts[1]
            elif amounts[0]:
                print('Projected value found: ' + amounts[0])
                res_dict['projected_value'] = amounts[0]
            elif amounts[1]:
                print(amounts[1])
                collected_amount.append(amounts[1])

            cagr = get_cagr(i)
            collected_cagr.append(cagr)
        print('Collected CAGRs: ', collected_cagr)
        print('Collected Amounts: ', collected_amount)
        print('Collected Years: ', collected_years)
        res_dict = get_cagr_from_list(res_dict, collected_cagr)
        res_dict = get_proj_curr(collected_amount, res_dict, object_list, selected_svo)

        collected_years = list(set(collected_years))
        print('RES DICT before mapping:', res_dict)
        print('Collected Years: ' + str(collected_years))
        res_dict = get_date_from_muliple_dates(res_dict, collected_years, selected_svo, object_list)
        if res_dict['country']:
            res_dict['country'] = list(set(res_dict['country']))
        else:
            res_dict['country'] = ''
        if res_dict['continent']:
            res_dict['continent'] = list(set(res_dict['continent']))
        else:
            res_dict['continent'] = ''
    except Exception as e:
        print('Exception occurred at get_results_svo_2(): ' + str(e))
        logger_bug.debug('Exception occurred at get_results_svo_2(): ' + str(e))
    return res_dict


def check_manual_verification_match_approach(result):
    try:
        result['approach'] = 'svo'
        year_flag = False
        value_flag = False
        cagr_flag = False
        if result['cagr_lower_year'] or result['value_lower_year'] or result['upper_year']:
            year_flag = True
        if result['cagr']:
            cagr_flag = True
        if result['current_value'] or result['projected_value']:
            value_flag = True
        if year_flag and cagr_flag and value_flag:
            result['match'] = 'complete'
        else:
            result['match'] = 'partial'
        if year_flag and not cagr_flag and not value_flag:
            result['manual_verification'] = True
    except Exception as e:
            print('Exception occurred at check_manual_verification_match_approach(): ' + str(e))
            logger_bug.debug('Exception occurred at check_manual_verification_match_approach(): ' + str(e))

    return result


def wrapper_market_value_svo(text, topics):
    try:
        print('Received Text: ' + text)
        print('Received Topics: ' + str(topics))
        logger_info.info('Received Text: ' + text)
        logger_info.info('Received Topics: ' + str(topics))
        selected_svo, selected_verbs = get_mapped_results(predictor, text, topics)
        result = get_results_svo_2(text, selected_svo, selected_verbs)
        result = check_manual_verification_match_approach(result)
        print("Final Results: "+str(result))
        logger_info.info("Final Results: " + str(result))
    except Exception as e:
        print('Exception occurred at wrapper_market_value_svo(): '+str(e))
        logger_bug.debug('Exception occurred at wrapper_market_value_svo(): ' + str(e))
    return [result]


if __name__ == '__main__':
    text = '''- Amid the COVID-19 crisis, the global market for Space Robotics estimated at US$3.2 Billion in the year 2020, is projected to reach a revised size of US$5.2 Billion by , growing at aCAGR of 7.2% over the period 2020-. Services, one of the segments analyzed in the report, is projected to record 7.6% CAGR and reach US$3.9 Billion by the end of the analysis period. After an early analysis of the business implications of the pandemic and its induced economic crisis, growth in the Products segment is readjusted to a revised 6.1% CAGR for the next 7-year period.'''
    topic = ['space robotics']
    print(wrapper_market_value_svo(text, topic))

    # import pandas as pd
    # # import get_elements
    # import time
    #
    # # text = '''Within Europe, growth of cagr in Germany is 14%, while the rest of Europe the projected value is $13 million dollars.'''
    # # doc = nlp(text)
    # input_df = pd.read_excel('Space Robotics.xlsx')#, sheet_name='final_test_data')
    # # input_df['proj_result_new'] = ''
    # # input_df['cagr_result_new'] = ''
    # # input_df['forecast_value_new'] = ''
    # # input_df['current_value_new'] = ''
    # # input_df['current_year_new'] = ''
    # input_df['all_result'] = ''
    #
    # for row, sent in enumerate(input_df['sentence']):
    #     if type(sent) != float and sent != '' and str(sent) != 'nan' and len(sent) > 1:
    #         # print('Sent: ',input_df.at[row,'priority'])
    #         if True:  # input_df.at[row,'priority'] == 1:
    #             # sent = input_df.at[row,'Sentence']
    #             print('----------',row, ': ', sent)
    #             # curr = time.time()
    #             final_res = wrapper_market_sizing_svo(sent,'space robotics')
    #             # for final_dict in final_res:
    #             #     final_dict['time'] = time.time() - curr
    #
    #             # loc_dict = find_value(sent) # Projected Value
    #             # cagr_dict = find_cagr(sent) # CAGR
    #             # forecast_dict = find_forecast_year(sent) # Upper Year
    #             # current_value_dict = find_current_value(sent) # Current Value
    #             # current_year_dict = find_current_year(sent) # Lower Year
    #             print('ROW:', row, ' Result: ', final_res)  # ,loc_dict,' and ',cagr_dict)
    #             input_df.at[row, 'all_result'] = final_res
    #             # input_df.at[row,'cagr_result_new'] = cagr_dict
    #             # input_df.at[row,'forecast_result_new'] = forecast_dict
    #             # input_df.at[row,'current_value_new'] = current_value_dict
    #             # input_df.at[row,'current_year_new'] = current_year_dict
    #
    #     if row % 20 == 0 or row % 233 == 0:
    #         input_df.to_csv('CAGR_Market_Research_QA_Model_final.csv', index=False)
#
#     new_list = list()
#     for row,data in enumerate(input_df['sentence']):
#       if input_df.at[row,'all_result']:
#         len_res = len(input_df.at[row,'all_result'])
#         if len_res==0:
#           new_list.append([input_df.at[row,'URL'],data,input_df.at[row,'all_result'],''
#                            ,'','','','','','','','','','','','',0])
#         else:
#           for res in input_df.at[row,'all_result']:
#             print(res.keys())
#             locations = list()
#             if 'country' not in res.keys():
#               res['country'] = ''
#             else:
#               locations.append(res['country'])
#             if 'continent' not in res.keys():
#               res['continent'] = ''
#             else:
#               locations.append(res['continent'])
#             print('RESULT:',res)
#             new_list.append([input_df.at[row,'list of paragraphs'],data,res,res['cagr'],res['percentage'],
#                              res['upper_year'],res['cagr_lower_year'],res['current_value'],
#                              res['value_lower_year'],res['projected_value'],
#                              res['continent'],res['country'],locations,res['match'],res['approach'],res['manual_verification'],res['time']])
#     out_df = pd.DataFrame(new_list,columns=['URL','Sentence','Result','cagr','percentage','upper_year','cagr_lower_year','current_value','value_lower_year','projected_value','continent','country','locations','match','approach','manual_verification','time'])
#     out_df.to_excel('out_data_after_test.xlsx',index=False)
#
#     verb_filtered_svo = list()
#     for idx,each_svo in enumerate(selected_svo):
#
#         if idx < len(selected_svo):
#             curr_verb_index = selected_verbs.index(each_svo[1])
#             print('Current Index and current verb:',idx,curr_verb_index,selected_verbs[curr_verb_index])
#             curr_verb_index = selected_verbs.index(each_svo[1])
#             verb_presence = False
#             for verb in selected_verbs[curr_verb_index+1:len(selected_verbs)-1]:
#                 print('next svos:', verb, selected_svo[idx][2][0], '....',
#                       selected_verbs[curr_verb_index + 1:len(selected_verbs) - 1])
#                 if verb in selected_svo[idx][2][0]:
#                     verb_presence = True
#                     # selected_verbs.pop(curr_verb_index)
#                     curr_verb_index = selected_verbs.index(verb)
#                     print('Updated Index and Updates verb in loop:', curr_verb_index, selected_verbs[curr_verb_index],selected_svo[idx][2][0])
#
#                 else:
#                     verb_presence = False
#                     print('breaking: ',idx)
#                     break
#             print('Updated Index and Updates verb:', curr_verb_index, selected_verbs[curr_verb_index])
#             verb_filtered_svo.append(
#                 [selected_svo[idx][0], selected_verbs[curr_verb_index], selected_svo[curr_verb_index][2]])
#             print('ADDED TO LIST:',verb_filtered_svo)
#             # if updated_verb_index > curr_verb_index:
#             #     verb_filtered_svo.append([selected_svo[idx][0],selected_verbs[updated_verb_index],selected_svo[updated_verb_index][2]])
#             # else:
#             #     verb_filtered_svo.append(
#             #         [selected_svo[idx][0], selected_verbs[updated_verb_index], selected_svo[updated_verb_index][2]])
#
#     print('VERB FILTERED:',verb_filtered_svo)
# print(get_cagr('at a CAGR of 6%'))
# print(get_amount_units('at USD 3.89 billion.'))
# print(get_cagr('over 8.6% from 2019 to 2025.'))
