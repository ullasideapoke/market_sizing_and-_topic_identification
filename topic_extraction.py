from allennlp.predictors.predictor import Predictor

from get_elements import find_geo
from market_value_rule import text_correction, has_num
import re
import allennlp_models.tagging

predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/openie-model.2020.03.26.tar.gz")
# print(predictor.predict(
#     sentence="In December, John decided to join the party.."
# ))

import pandas as pd

verb_list = pd.read_csv("data/market_verbs.csv")
proj_value = verb_list['verbs'].tolist()


def get_topic_results(text):
    tags_list = list()
    svo_list = list()
    selected_verbs = list()
    selected_svo = list()
    topic_verb = list()
    print("\nExtracted SVO Triplets:")
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
            # print('[' + str(n_before_v) + ', "' + verb_word + '", ' + str(n_after_v) + '],')
            topic_verb.append([n_before_v, verb_word, n_after_v])
            # print(verb_word)
    # print(topic_verb)
    final_list = list()
    for i in topic_verb:
        if i[0]:
            if i[1] in proj_value:
                final_list.append(i[0][0])
    # print(final_list)
    # final_list = list(set(final_list))
    final_list = set(final_list)

    # is_locations = find_geo(final_list)
    # # print(is_locations)
    # # print(len(is_locations))
    # for i in range(len(is_locations)):
    #     # print(len(is_locations[i]))
    #     if len(is_locations[i])>=1:
    #         output = {""}
    #
    #     else:
    #
    #         output = final_list

    return final_list


if __name__ == '__main__':
    text = "what is the market size for electric vehicle in united states in 2027"
    result = get_topic_results(text)
    print("result", result)
