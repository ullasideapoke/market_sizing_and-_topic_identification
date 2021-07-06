import re
import time
import spacy
import pandas as pd
from nltk.tokenize import sent_tokenize

nlp = spacy.load('en_core_web_sm')

bk_df = pd.read_csv("data/business_keywords.csv")
sk_df = pd.read_csv("data/statistic_keywords.csv")
in_df = pd.read_csv("data/industry_name.csv")
n_df = pd.read_csv("data/numbers.csv")

busines_keyword = list(set(bk_df['word']))
statistic_keyword = list(set(sk_df['word']))
industry_name = list(set(in_df['word']))
numbers = list(set(n_df['word']))

stopwords = ['frequently asked questions', 'faqs', 'faq']


def text_cleaning(text):
    all_sent = list()

    for each_sent in sent_tokenize(text):
        if "table of content" in each_sent.lower() or "the content of the study subjects" in each_sent.lower() or "list of tables" in each_sent.lower():
            break
        else:
            each_sent = re.sub('<[^>]+>', '', each_sent)

            if "cagr" not in each_sent.lower():
                each_sent = " ".join([i for i in each_sent.split("\n") if len(i.split()) > 6])

            else:
                each_sent = each_sent.replace("\n", " ")

            each_sent = post_proc_clean(punct_numbers(each_sent))
            each_sent = " ".join([i for i in each_sent.split() if len(i) > 0])
            all_sent.append(each_sent)

    return all_sent


def post_proc_clean(text):
    text = str(text).replace("#", " ")
    text = str(text).replace("*", " ")
    text = str(text).replace("@", " ")

    return text


def punct_numbers(string):
    punc_pattern = re.compile("["
                              u"\U0000007B-\U0000FFFF"  # {|}~
                              "]+", flags=re.UNICODE)

    string = punc_pattern.sub(r' ', string)
    return string


def get_ent_count(text):
    entity_count = 0
    entity_word = []
    doc = nlp(text)
    for ent in doc.ents:
        entity_count += 1
        entity_word.append(ent.text)

    return [entity_count, entity_word]


def valid_sent_ele(each_sent, validation_count=0, validation_word=[], ent_count=0, ent_word=[]):
    valid_sent = dict()
    each_sent = [i for i in each_sent.split() if len(i) > 0]
    each_sent = " ".join(each_sent)
    each_sent = post_proc_clean(each_sent)

    valid_sent['imp_sent'] = each_sent.capitalize()
    valid_sent['val_count'] = validation_count
    valid_sent['val_word'] = validation_word
    valid_sent['ent_count'] = ent_count
    valid_sent['ent_word'] = ent_word

    return valid_sent


def imp_sent_ext_pipeline(sentences):
    constant_bigram = ["this report", "report gives", "research report"]
    constant_word = ["cagr", "compound annual growth rate"]
    list_valid_dict = list()

    for each_sent in sentences:
        stop_word_flag = False

        for word in stopwords:
            if word in each_sent.lower():
                stop_word_flag = True
                break

        if len(
                each_sent.split()) < 60 and not stop_word_flag or "cagr" in each_sent.lower() or "compound annual growth rate" in each_sent.lower():
            validation_count = 0
            valid_sent = dict()
            validation_word = []
            each_sent_list = str(each_sent).lower().split()
            sent_flag = "N"

            if sent_flag == "N":
                for i in constant_word:
                    if i in each_sent_list:
                        validation_count += 1
                        validation_word.append(i)

                for i in constant_bigram:
                    if i in each_sent.lower():
                        validation_count += 1
                        validation_word.append(i)

                if validation_count > 0:
                    valid_sent = valid_sent_ele(each_sent, validation_count, validation_word)
                    valid_sent['total_count'] = 0
                    # imp_sent["0"] = valid_sent
                    sent_flag = "Y"

            if sent_flag == "N":
                for i in busines_keyword:
                    if i in each_sent_list:
                        validation_count += 1
                        validation_word.append(i)

                for i in statistic_keyword:
                    if i in each_sent_list:
                        validation_count += 1
                        validation_word.append(i)

                for i in industry_name:
                    if i in each_sent_list:
                        validation_count += 1
                        validation_word.append(i)

                for i in numbers:
                    if i in each_sent_list:
                        validation_count += 1
                        validation_word.append(i)

                ent = get_ent_count(each_sent)
                ent_count = ent[0]
                ent_word = ent[1]
                total_count = validation_count + ent_count

                if (50 >= total_count >= 5) and (validation_count > 0):
                    valid_sent = valid_sent_ele(each_sent, validation_count, validation_word, ent_count, ent_word)
                    valid_sent["total_count"] = total_count
                    # imp_sent[str(total_count)] = valid_sent

            if valid_sent:
                list_valid_dict.append(valid_sent)

    return list_valid_dict


def imp_ext_main(text):
    clean_text = text_cleaning(text)
    imp_sent_dict = imp_sent_ext_pipeline(clean_text)
    imp_sentetences = [each_imp_sent['imp_sent'] for each_imp_sent in imp_sent_dict]
    imp_sentetences = list(set(imp_sentetences))

    return imp_sentetences


if __name__ == '__main__':
    text = "The Plant Based Protein Supplement market size was valued at $4.2 billion in 2018 and is expected to reach $7.0 billion by 2026, registering a CAGR of 6.7% from 2019 to 2026.. The global Plant Based Protein Supplement market is segmented based on price, end user and distribution channel. Based on price, the global Plant Based Protein Supplement market is further segmented into $50 – $100, $100 – $200 and Above $200. According to the Vegan Society, in 2019, there were 600,000 vegans around the globe. The rise in awareness about the health benefits associated with the consumption of vegan food products has led majority of population adopting into vegan diet. This has led to burgeon demand for different types of vegan food products from its health-conscious target customers. This similar kind of trend has been enduring even from the sports segments. Professional sports personnel and athletes are now adopting into vegan diet owing to increase in awareness about the associated benefits. This consumer perception all together has triggered demand for plant-based protein supplement products. According to the U.S. Census Bureau, millennials are on the verge of surpassing baby boomers in the country. Similarly, in Asia-Pacific, millennials account for a larger population, especially in countries such as China, India, and Australia as compared to other population groups."
    print(imp_ext_main(text))
