import ast

from imp_sent_ext import imp_ext_main
from market_value_qa import wrapper_market_value_qa
from market_value_rule import wrapper_market_value_rule
from get_elements import find_geo
from logging_method import define_logging
from market_value_svo import wrapper_market_value_svo
from topic_extraction import get_topic_results
from pprint import pprint
from get_elements import remove_geo_in_topic

logger_info, logger_bug = define_logging('log/market_value.log')
import re
import spacy
import time

nlp = spacy.load('en_core_web_sm')


def has_num(text):
    if re.findall('[0-9]+', text):
        return True
    else:
        return False


def preprocess_text(each_text):
    # Replacing all locations mentioned in brackets (Syndicate Reports)

    each_text = re.sub('country ?\(.*\)', '', each_text.lower())
    each_text = re.sub('countries ?\(.*\)', '', each_text.lower())
    each_text = re.sub('continents ?\(.*\)', '', each_text.lower())
    each_text = re.sub('continent ?\(.*\)', '', each_text.lower())
    each_text = re.sub('regions ?\(.*\)', '', each_text.lower())
    each_text = re.sub('region ?\(.*\)', '', each_text.lower())
    each_text = re.sub('regional analysis ?\(.*\)', '', each_text.lower())
    each_text = re.sub('regional ?\(.*\)', '', each_text.lower())
    each_text = re.sub('geography ?\(.*\)', '', each_text.lower())
    each_text = re.sub('geographies ?\(.*\)', '', each_text.lower())
    each_text = re.sub('countries covered ?\(.*\)', '', each_text.lower())
    each_text = re.sub('countries analyzed ?\(.*\)', '', each_text.lower())
    return each_text


def get_loc_count(each_text):
    loc_count = 0
    loc = ([], [])
    try:
        each_text = each_text.lower()
        loc_count = 0
        doc = nlp(each_text)
        loc = find_geo(each_text, doc, return_type='unprocessed')
        all_loc = loc[0] + loc[1]

        print('All locations present:', all_loc)
        for sent in doc.sents:

            loc_count_sent = 0
            for loc in all_loc:
                if loc.lower() in sent.text.lower():
                    loc_count_sent += 1
            if loc_count_sent and not has_num(sent.text):  # A sentence containing more than 3 locations
                print('Removing sentence "' + sent.text + '" as it does not contain numbers but contains locations')
                logger_info.info(
                    'Removing sentence "' + sent.text + '" as it does not contain numbers but contains locations')
                each_text = each_text.replace(sent.text, '')  # Remove the text
        for loc in all_loc:
            if '(' + loc + ')' in each_text:
                each_text.replace('(' + loc + ')', '')
        print('After replacing: ', len(each_text), each_text)
        loc = find_geo(each_text, doc, return_type='unprocessed')

        # all_loc = loc[0] + loc[1]
        global_flag = False
        if loc[0]:
            for country in loc[0]:
                if country.lower() != 'global':
                    loc_count += 1
                elif not global_flag:
                    global_flag = True
                    loc_count += 1
        if loc[1]:
            for continent in loc[1]:
                if continent.lower() != 'global':
                    loc_count += 1
                elif not global_flag:
                    global_flag = True
                    loc_count += 1
    except Exception as e:
        print('Exception occurred at get_loc_count(): ' + str(e))
        logger_bug.debug('Exception occurred at get_loc_count(): ' + str(e))
    return each_text, loc, loc_count


def perc_count(text):
    percentage = re.findall("(?:(?:\d+(?:\.\d+)?\-)?(?:(?:\d+(?:\.\d+)?)|100))%",
                            text)
    unique_perc = list(set(percentage))
    return unique_perc, len(unique_perc)


def get_text(text):  # Depending on number of percentage values
    selected_sentence = ''
    imp_sentences = ''
    try:
        print('BEFORE ')
        text = preprocess_text(text)  # Remove locations in brackets
        text, loc, loc_count = get_loc_count(text)
        text = text.replace('percentage', '%')
        text = text.replace('per cent', '%')
        text = text.replace('percent', '%')
        text = text.replace('%%', '%')
        text = text.replace(' %', '%')
        percentage, percentage_count = perc_count(text)

        if percentage_count == 1:
            important_sentences = imp_ext_main(text)
            print('length of imp:', len(important_sentences))
            for i in important_sentences:
                print('Obtained Important Sentences: ', i)
            imp_sentences = '. '.join(imp_ext_main(text))
            if imp_sentences:
                imp_sentences = re.sub('\.+', '.', imp_sentences)
                return imp_sentences, percentage_count
        elif percentage_count > 1:
            return text, percentage_count

        #
        #
        #
        #
        # if type(imp_sentences) == str:
        #     imp_sentences = ast.literal_eval(imp_sentences)
        # if perc_count == 1:
        #     for sent in imp_sentences:
        #         print('PERCENTAGE FOUND: ', re.findall('\d+.?\d*%', sent))
        #
        #         if re.findall('\d+.?\d*%', sent):
        #             perc = re.findall('\d+.?\d*%', sent)
        #
        #             if perc[0] in text:
        #                 selected_sentence = sent
    except Exception as e:
        print("Exception occurred at decide_sent_or_para(): " + str(e))
        logger_bug.info("Exception occurred at decide_sent_or_para(): " + str(e))
    return ''


def wrapper_market_value(text, topics):
    res_list = list()
    input_text = text = re.sub('\.+', '.', text)  # Replace .. with . in case double .. are present
    # text= get_text(text)
    if re.findall('x+\.\d+%',
                  text) or 'xx%' in text.lower() or '...%' in text.lower() or 'xx %' in text.lower() or 'x.x%' in text.lower() or 'xx.xx%' in text.lower() or 'x.xx%' in text.lower():  # Do not process if text contains unknown values
        return [{'cagr': '', 'percentage': '', 'upper_year': '', 'cagr_lower_year': '', 'current_value': '',
                 'value_lower_year': '', 'projected_value': '', 'continent': '', 'country': '', 'sentence': input_text,
                 'manual_verification': False}]
    try:
        if text.startswith('[') and text.endswith(']'):
            text_list = ast.literal_eval(text)
            text_list = list(set(text_list))
        else:
            text_list = [text]
        # print('Received text list: ',text.startswith('['),text.endswith(']'),text_list)
        for each_text in text_list:
            orig_text = each_text
            each_text = each_text.strip()
            each_text = each_text.replace('percentage', '%')
            each_text = each_text.replace('per cent', '%')
            each_text = each_text.replace('percent', '%')
            each_text = each_text.replace('%%', '%')
            each_text = each_text.replace(' %', '%')

            each_text, percentage_count = get_text(each_text)
            print('Received Text: ', each_text[:100] + '....')
            logger_info.info('Received Text: ' + each_text[:100] + '....')
            total_time = time.time()

            each_text, loc, loc_count = get_loc_count(each_text)
            print('EACH TEXT:', percentage_count, loc, loc_count, each_text)

            # res_list = wrapper_market_value_qa(text,loc)
            # count_of_perc = perc_count(text)
            # QA Model
            if percentage_count > 1:
                if loc_count == 0 or loc_count == 1:
                    print('No of unique percentages: ' + str(percentage_count) + ', Extracting using SVO Model')
                    logger_info.info('No of percentages: ' + str(percentage_count) + ', Extracting using SVO Model')
                    result = wrapper_market_value_svo(each_text, topics)
                    if result:
                        for i in result:
                            i['sentence'] = orig_text
                    res_list.extend(result)
                elif (15 > loc_count):
                    print('No of unique percentages: ' + str(percentage_count) + ', Extracting using QA Model')
                    logger_info.info('No of percentages: ' + str(percentage_count) + ', Extracting using QA Model')
                    result = wrapper_market_value_qa(each_text, loc, topics)
                    if result:
                        for i in result:
                            i['sentence'] = orig_text
                    res_list.extend(result)

            # Rule Based Approach
            else:
                print('No of unique percentages: ' + str(percentage_count) + ', Extracting using Rule based Approach')
                logger_info.info(
                    'No of unique percentages: ' + str(percentage_count) + ', Extracting using Rule based Approach')
                result = wrapper_market_value_rule(each_text)
                if result:
                    for i in result:
                        i['sentence'] = orig_text
                res_list.extend(result)

            # if res_list:
            #     print("RES LIST: ",orig_text)
            #     for each_dict in res_list:
            #         each_dict[
            #             'sentence'] = orig_text  # As sentences from here are being shown in UI, User expects unprocessed text
            # res_list = list(set(res_list))
            print(res_list)
            print('Total Time taken: ' + str(time.time() - total_time))
            logger_info.info('Total Time taken: ' + str(time.time() - total_time))

    except Exception as e:
        print('Exception occurred at wrapper_market_value(): ' + str(e))
        logger_bug.debug('Exception occurred at wrapper_market_value(): ' + str(e))
    return res_list


cagr_kw_list_new = ['cagr', 'compound annual growth rate', 'annual growth rate', 'annual rate of inflation',
                    'annual rate of increase', 'annual growth factor']


def paragraph_to_cagr_sentence(paragraph):
    new_text = paragraph.splitlines()
    new_text_lower = list()
    text_list_final = list()
    for i in range(len(new_text)):
        new_text_lower.append(new_text[i].lower())
        if any(word in new_text_lower[i] for word in cagr_kw_list_new):
            text_list_final.append(new_text[i])

    return text_list_final


def market_sizing_main_function(sentence):
    final_dict = {}
    final_list =list()
    is_locations =()
    sent = paragraph_to_cagr_sentence(sentence)
    for i in range(len(sent)):
        extacted_topic = get_topic_results(sent[i])
        topics = ['space robotics']
        list_dict = wrapper_market_value(sent[i], extacted_topic)
        print("list_dict",list_dict)
        for list1 in list_dict:
            extacted_topic = remove_geo_in_topic(extacted_topic)
            extacted_topic = set(extacted_topic)
            final_dict = {'topic': extacted_topic, 'values': list1}
            final_list.append(final_dict)

    return final_list


if __name__ == '__main__':
    # text = 'The U.S. Market is Estimated at $30.2 Million, While China is Forecast to Grow at 3.8% CAGR'
    # text = pre_process(text)
    # unprocessed_dict = get_results(text)

    # print('filtered_dict:',filtered_dict)
    # sentence = '''INDIA ELECTRIC VEHICLE (EV) MARKET - GROWTH, TRENDS, COVID-19 IMPACT, AND FORECASTS (2021 - 2026) \nThe India Electric Vehicle (EV) Market is Segmented by Vehicle Type (Passenger Cars, Commercial Vehicles, Two- and Three-wheelers) and Power Source Type (Battery Electric Vehicle, Plug-in Electric Vehicle and Hybrid Electric Vehicle). The report offers market size and forecast for India Electric Vehicle in value (USD billion) for all the above segments. \nMarket Overview \nThe India and asia Electric Vehicle Market was valued at USD 5 billion in 2020 and is expected to reach USD 47 billion by 2026 registering a CAGR of above 44% during the forecast period (2021 - 2026). \nThe India Electric Vehicle Market has been impacted by the outbreak of COVID-19 pandemic due to supply chain disruptions and halt of manufacturing units due to continuous lockdowns and travel restrictions across the county. However, as electric vehicle (EV) market is still in its nascent stage in India. It is expected to grow at a much faster rate during the forecast period due to various government initiatives and policies. \nE-Commerce companies (Amazon, for example) are launching initiatives to use e-Mobility for last-mile deliveries to reduce carbon footprint. India is experimenting with e-Mobility for public transport and has deployed electric inter-city buses across some of the major cities. In addition, state governments are also playing active role in deployment of policies encouraging EV. For instance,Kerala aims to put one million EV units on the road by 2022 and 6,000 e-buses in public transport by 2025. \nTelangana aims to have EV sales targets for 2025 to achieve 80% 2- and 3-wheelers (motorcycles, scooters, auto-rickshaws), 70% commercial cars (ride-hailing companies, such as Ola and Uber), 40% buses, 30% private cars, 15% electrification of all vehicles. \nThe EV market in India has gained significant momentum after the implementation of FAME India scheme with its aim of shifting towards e-mobility in wake of growing international policy commitments and environmental challenges. Moreover, India offers the world’s largest untapped market, especially in the Electric two-wheeler segment and as 100 percent foreign direct investment is allowed in this sector under the automatic route market is expected to gain momentum during forecast period. \nScope of the Report \nAn Electric vehicle is one that operates on an electric motor, instead of an internal-combustion engine which generates power by burning a mix of fuel and gases. Therefore, Electric vehicle is seen as a possible replacement for the current-generation automobile in near future to address environmental challenges. The report covers the latest trends and technologies followed by COVID-19 impact on the market. \nThe India Electric Vehicle Market is segmented by Vehicle Type and Power Source. By Vehicle type, the market is segmented into Passenger Cars, Commercial Vehicles, Two- and Three-wheelers and By Power Source Type, the market is segmented into Battery Electric Vehicle, Plug-in Electric Vehicle and Hybrid Electric Vehicle. For each segment market sizing and forecast has been done on basis of value (USD billion). \nKey Market Trends \nGrowing Adoption Of Electric Buses During Forecast Period. \nIndia is the second most populated country in the world after China, and just like China, which has the largest electric bus fleet in the world, India is also pushing hard for the electrification of buses. Many state governments have already started the procurement of electric buses from Chinese and local electric bus manufacturers. \nWith growing need for controlling GHG (Greenhouse gases) emissions emitted by vehicles, the government is encouraging the use of electric powered vehicles across various states, which is boosting the demand for electric buses in India. The market is being driven by factors such as increase in domestic manufacturing, rapid urbanization, and rise in environmental awareness. \nFor instance, \nIn February 2020, Union transport minister inaugurated India's first inter-city electric bus service, these buses are manufactured by Mitra Mobility Solution which has the range of 300 km on a full charge. \nMany local bus manufacturers are in collaboration with some Chinese manufacturers are trying to catch the rising demand of the electric buses in India. For Instance, \nIn 2019, Foton PMI announced that it was planning to invest around INR 500 crore on a joint venture with Beiqi Foton Motor Co. of China to manufacture electric buses in India. The company has already given five electric buses to one of the airlines for internal operations. \nElectric Two Wheeler Vehicles Likely To Have Optimistic Growth \nWith transportation still being a challenge in India, a lot of people in these segments look forwards to the 2-Wheeler Industry in India. As a result of the surging pollution, the national government has launched stringent policies to curb vehicular emissions. In particular, the jump from Bharat Stage V (BSV) to BSVI emission standards is expected to benefit the Indian electric scooter and motorcycle market, by raising the prices of petrol-driven two-wheelers by 7–15%. From 1st April 2020 onward, automakers are only allowed to sell BSVI-compliant vehicles in the nation, which is driving the push toward electric variants. \nFor extracting the maximum revenue from the rapidly growing Indian electric scooter and motorcycle market, original equipment manufacturers (OEMs) are expanding their facilities. For instance, \nIn January 2020, Ather Energy Pvt. Ltd. announced intentions to build a 400,000-square-foot factory in Hosur, Tamil Nadu, which would have an annual output of 1 lakh units. Currently, the company operates one manufacturing plant in Bengaluru, which has a capacity of 25,000 units. The idea of the company behind an additional facility is meeting the rising demand for electric two-wheelers in India. \nIn the same vein, Okinawa AutoTech Pvt. Ltd. invested 28.4 million (INR 200 crore) for its second manufacturing plant in May 2019. To be developed for electric two-wheeler vehicles in Rajasthan and planned to be commissioned in early 2020–21, the manufacturing plant will have an annual output of 10 lakh units. \nFurthermore, the availability of a considerable number of electric two wheeler models, their low cost, as well as their availability as a substitute for conventional fuel-based vehicles and these are fueling the demand in the India Electric vehicle market. \nCompetitive Landscape \nThe India EV market is consolidated due to presence of major players active in the market owing to cheap and readily available manpower. However, established players in the market are introducing their new model's, product launches to gain competitive edge over other players. For instance, \nIn January 2020, Morris Garages Motor India launched the d ZS EV, which is the first electric internet SUV in India, the car has a driving range of 340 km on a full charge. The ZS EV vehicle has been awarded five stars at the Euro NCAP crash tests. \nIn 2019, Tata Motors announced its electric vehicle technology ZIPTRON, which will power all future Tata electric cars. This technology consists of a highly efficient permanent magnet AC motor, providing excellent performance on demand. It will also offer a dust and waterproof battery system meeting IP67 standards. \nThe startups are expanding their presence by raising funds from investors, tapping in new and unexplored cities. Companies are investing a tremendous amount on R&D and launching new models to mark their presence in the market.'''
    sentence = ''' Electric Vehicle Market Size to Hit Around US$ 802.8 Bn by 2027\nAccording to Precedence Research, the electric vehicle market size is expected to hit around US$ 802.81 billion by 2027, growing at a CAGR of 40.7% from 2020 to 2027.\nJune 30, 2021 19:00 ET\nPrecedence Research\nPune,\nINDIA\nOTTAWA, June\n30, 2021\n(GLOBE NEWSWIRE) -- The electric vehicle market size\nsurpassed US$ 165 billion in 2020. Electric vehicles use one or more than one electric motors or traction motors for propulsion. The electric vehicles are powered either by a collector system through electricity from charging station deployments or can be charged by self-charging devices such as regenerative braking systems and turbochargers. They have shown attractive growth over the past decade and their adoption rate is still prospering in double digit growth.\nAn electric vehicle operates on electricity unlike its counterpart, which runs on fuel. Instead of internal combustion engine, these vehicles run on an electric motor that requires constant supply of energy from batteries. There are a variety of batteries used in these vehicles. These include lithium ion, molten salt, zinc-air, and various nickel-based designs. Electric vehicles were primarily designed to replace conventional ways of travel as they lead to environmental pollution. Electric vehicles have gained popularity owing to numerous technological advancements. The electric vehicle outperforms the conventional vehicle providing higher fuel economy, low carbon emission & maintenance, convenience of charging at home, smoother drive, and reduced sound from engine. There are three types of electric vehicles-battery, hybrid, and plug-in hybrid electric vehicles. In addition, electric vehicles require no engine oil changes but are slightly expensive than their gasoline equivalents.\nGet the Sample Pages of Report for More Understanding@ https://www.precedenceresearch.com/sample/1009\nOn the basis of product they are categorized into Battery Electric Vehicle (BEV) and Plug-in Hybrid Electric Vehicle (PHEV). Presently, BEV dominated the sale of electric vehicles across globe. However, PHEVs are anticipated to flourish significantly over the coming years. The growth of PHEV is attributed to its benefits over BEV and driver-friendly features. Some of the attractive features of PHEV are extended driving range due to presence of liquid fuel tank & internal combustion engine, low battery cost and size, and charging flexibility at any gas station.\nGrowth Factors\nEven though the oil prices have declined prominently, electric vehicles adoption is increasing day by day. Rising environmental concern for pollution and CO2 emission, favorable government policies for adoption of electric vehicles, and significant investment by EV manufacturers are some of the major factors driving the global electric vehicle market. Some of the manufacturers are also promoting workplace and residential charging stations to over the charging constraints. For instance, in December 2017, Electrify America LLC announced to install more than 2,800 residential and workplace charging stations by June 2019 in 17 different metropolitan cities of U.S.\nHowever, lack of global standard for the charging infrastructure is one of the major reasons that hinder the market growth. Nonetheless, technological advancement in electric vehicle charging stations powered by renewable energy open up new opportunities in the market growth.\nReport Highlights\nAsia Pacific was the dominant region in 2020 and expected to be the most attractive market during the forecast period. China, India, Indonesia, and Korea are some of the most lucrative regions for the electric vehicle growth. Rising investments and government initiatives are the major factors for its significant growth.\nNorth America and Europe are the significant revenue contributors in the global electric vehicle market with considerable growth. Rising environmental concern and heavy incentives offered by the government have increased the adoption of electric vehicles massively in these regions.\nBattery Electric Vehicles (BEV) led the product segment with approximately 67% of the global market share. However, Plug-in Hybrid Electric Vehicles (PHEVs) are considered to register fastest growth during forecast period owing to being driver-friendly coupled with several benefits over the BEV.\nGet Customization on this Research Report@ https://www.precedenceresearch.com/customization/1009\nRegional Snapshots\nAsia-Pacific was the highest revenue contributor, accounting for $84.84 billion in 2019, and is estimated to reach $357.81 billion by 2027, with a CAGR of 20.1%. North America is estimated to reach $194.20 billion by 2027, at a significant CAGR of 27.5%.\nAsia-Pacific and Europe collectively accounted for around 74.8% share in 2019, with the former constituting around 52.3% share.\nAutonomous vechile are expected to witness considerable CAGRs of 27.5% and 25.3%, respectively, during the forecast period.\nAsia Pacific seeks the most lucrative growth over the forecast period owing to rising adoption of electric and zero-emission vehicles in the region. The government of various Asian countries has issued stringent regulations for the CO2 and greenhouse gas (GHG) emission. This has forced the auto-manufacturers to move their production towards more efficient and environment-friendly vehicles. In June 2019, Japan had issued a new CO2 emission standard for 2030, according to this car manufacturing must focus in reducing the CO2 emission by 32% by 2030 in comparison to 2016. Other countries are also taking significant initiative for controlling the vehicle emission. For instance, in 2020, China made huge investment in electric car infrastructure to promote e-mobility. Volkswagen AG, one of the leading electric vehicle manufacturers has signed a joint venture with China and planned to invest USD 11.30 Bn for industrialization of e-mobility in China.\nEurope and North America are the prominent electric vehicles market with around 45% combined revenue share globally. Europe after Asia Pacific is the second most lucrative EV market owing to various governments plan for zero emission on-road fleet by 2030. In June 2020, the government of Germany announced to double the subsidies on electric vehicles. The initiative has taken to promote electric vehicle sales and restrict diesel vehicle sales. Similarly, in July 2016, the U.S. government planned to accelerate electric vehicle adoption by announcing some private sector and federal actions such as launch of FAST act process and loan guarantees up to USD 4.5 Bn for the deployment of electric vehicle charging station.\nBrowse more Automotive Industry Research Reports@ https://www.precedenceresearch.com/industry/automotive\nKey Players & Strategies\nThe global electric vehicle market is consolidated and highly competitive owing to the presence of large number of players. Market players are significantly involved in merger, acquisition, partnership, regional expansion and other marketing strategies to retain their position in the global market. For instance, in March 2020, Nikola Corporation, a zero-emission truck startup announced its merger with VectoIQ, dedicated for the development of mobility as a service and autonomous fleet.\nSome of the key players of the market are BYD Company Ltd., Ford Motor Company, Daimler AG, General Motors Company, Mitsubishi Motor Corporation, Groupe Renault, Nissan Motor Company, Toyota Motor Corporation, Tesla Inc., and Volkswagen Group, among others.\nBuy this Premium Research Report@ https://www.precedenceresearch.com/checkout/1009\nYou can place an order or ask any questions, please feel free to contact at sales@precedenceresearch.com | +1 9197 992 333\nAbout Us\nPrecedence Research is a worldwide market research and consulting organization. We give unmatched nature of offering to our customers present all around the globe across industry verticals. Precedence Research has expertise in giving deep-dive market insight along with market intelligence to our customers spread crosswise over various undertakings. We are obliged to serve our different client base present over the enterprises of medicinal services, healthcare, innovation, next-gen technologies, semi-conductors, chemicals, automotive, and aerospace & defense, among different ventures present globally.\nFor Latest Update Follow Us:'''
    # sent = '''['The space robotics market is estimated to be USD 2.58 billion in 2017 and is projected to reach USD 4.36 billion by 2023, at a CAGR of 8.64% during the forecast period. Some of the major companies providing space robotics solutions include Altius Space Machines (US), Maxar Technologies (US), Motiv Space Systems (US), Space Systems/Loral (US), Honeybee Robotics (US), Astrobotic Technology (US), Made In Space (US), Effective Space Solutions Limited (UK) and Northrop Grumman (US). These key market players offer various space robotics solutions and robotics & subsystems, sensors & autonomous systems, software and robotic services, such as satellite servicing, on-orbit assembly and manufacturing, surface mobility, and de-orbiting services, among others. New product developments, partnerships, and contracts are the major growth strategies adopted by these players to enhance their positions in the space robotics market.In-flight Entertainment & Connectivity Market by End User (OEM, Aftermarket), Aircraft Type (NBA, WBA, VLA, Business Jets), Product (IFE Hardware, Ife Connectivity, IFE Content), and Region - Global Forecast to 2023']'''
    # sent = '''Space Robotics Market Size Worth $5.7 Billion By 2027 | CAGR: 5.2%: Grand View Research, Inc.Jan 14, 2021, 03:35 ET'''
    # sent = '''Published Date: Apr 2019 | Report ID: GMI3219 | Authors: Preeti Wadhwani, Prasenjit Saha Industry Trends Space Robotics Market size valued at USD 2 billion in 2018 and will grow at a CAGR of 6% from 2019 to 2025.High investments in the space exploration projects and launch of several satellites by various countries is expected to drive the industry growth.'''
    # sent = '''["While we have looked at a few robot stocks like iRobot (NASDAQ:IRBT) and Cognex (NASDAQ:CGNX), there is actually an ETF available called the Robo Global Robotics & Automation Index ETF (NASDAQ:ROBO). ABB stock comes with the caveat that robotics represents only 21% of their corporate revenue. Eshel has a. Top penny stocks today to find best penny stocks to buy for January 2021. Walmart Inc. In this article we present the top 10 robotics and artificial intelligence stocks to buy. Adjusted for one-time factors, earnings per share (EPS) declined 26%. Location: Boulder, Colorado. The 2 year Welding Engineering Technician - Robotics Ontario College Diploma Program at Conestoga College students will acquire comprehensive welding skills through hands-on practical labs, using the latest equipment. Cellula Robotics is a world leading engineering solutions company that specializes in the turnkey design and production of subsea robotic systems. The Indxx Global Robotics and Artificial Intelligence Thematic Index (IBOTZNT) is designed to provide exposure to exchange-listed companies in developed markets that are expected to benefit from the adoption and utilization of robotics and/or artificial intelligence, including companies involved in developing industrial robots and production systems, automated inventory management, unmanned. Since then, BOTZ shares have increased by 88. SPECULATIVE BUY. The global robotics market is expected to see a CAGR of 25% between 2019 and 2024 on increased human and machine interaction. Company: Boston-based Rethink Robotics is the much-anticipated follow-up to Rodney Brooks' first startup, iRobot. Canadian Robotics Ltd. Robotic Process Automation has become a fast-growing offering in every business for automation and support. 71 billion by 2027, registering a CAGR of 5. The global space robotics market size is expected to reach $5. The Company's world-renowned space robotics and on-orbit servicing capabilities span more than 30 years, including 91 on-orbit servicing missions with the Space Shuttle program plus continuing robotic operations to build and maintain the International Space Station (ISS). The contract, worth $40 million, is the biggest one to date for the company, which has offices in St. Here are the 12 Canadian dividend stocks in the tech space Absolute Software CEO John Livingston.3 Canadian Stocks with Large Insider Buying Over the Past Two Weeks", "14, 2021 /PRNewswire/ -- The global space robotics market size is expected to reach USD 5. In addition to Element AI, a German startup with Canadian roots, Twenty Billion Neurons (TwentyBN) was also named to CB Insights’ AI 100. Toronto Stock Exchange Horizons ETFs Management (Canada) Inc. TR-1: Standard form for notification of major holdings NOTIFICATION OF MAJOR HOLDINGS (to be sent to the relevant issuer and to the FCA in Microsoft Word format if possible)i 1a. The contract, worth $40 million, is the biggest one to date for the company, which has offices in St. Ramakanth covers the Healthcare sector, focusing on stocks such as Zomedica Pharmaceuticals Corp, IntelGenx Technologies, and Gritstone Oncology Inc. specializes in providing cost effective solutions with exceptional services in supporting an increasingly demanding robotic automation industry in North America. Cevian hasn't said what it has in store. Construct a pivoting robotic laboratory arm with gripper claw. The news is out that Canada has become an artificial intelligence hotbed. com Phone: +1-903-453-0802 Fax: +1-214-722-1284 US Sales and Support hours are Monday - Friday, 7am - 5pm CT Technical Support E-Mail: [email\xa0protected] 32; market cap: US$45. This amendment relates to MDA’s August. - January 25, 2021) - KWESST Micro Systems Inc. The global space robotics market size is expected to reach $5.06 billion in assets under management, remains a force in this category. ( WMT ) WMT is a discount store and supermarket major that operates more than 11,500 retail and wholesale stores in 27 countries worldwide, selling grocery and a. 8 billion by 2024, growing at a CAGR of 58% from 2017-2024. Search Name or Symbol. publicly traded Robotics companies. The best penny stocks today shows the biggest penny stock gainers and losers sorted by percentage. Satellite industry giant Maxar is selling MDA, its subsidiary focused on space robotics, for $1 billion CAD (around $765.All-In-One Screener Buffett-Munger Screener Industry Overview Undervalued Predictable Benjamin Graham Net-Net 52-week/3Y/5Y Lows 52-week/3Y/5Y Highs Magic Formula(Greenblatt) Dividend Stocks Peter Lynch Screen S&P500 Grid Predictable Companies Spin Off List Historical Low P/B List Historical Low P/S List High Short Interest Upcoming Special. 0% stake (later boosted to 5. Ottawa, Ontario--(Newsfile Corp. 1,118 likes · 2 talking about this. The goal of robotics is to. A new partnership between heavy metal fabricator Miller Fabrication Solutions, Brookville, Pa. Build a vertical three-fingered claw that can lift a cup up off the table keeping it level. MZOR Description — Mazor Robotics Ltd. The Company's molecular modeling, simulation, and informatics software are used extensively in the area of nanotechnology. Barron's also provides information on historical stock ratings, target prices, company earnings, market valuation and. 640 Bridge Street West, Waterloo, Ontario N2K 4M9. Flippy, from Miso Robotics. Brendan Riley, President of GreenPower commented, “We are seeing a dramatic increase in autonomous vehicle demand and this vehicle demonstrates the compelling marriage of. Got to love Dividend Growth Investing. This year, three Canadian robotics companies made the list, including relative new-comer, Clearpath Robotics. AeroVironment Acquires Telerob, a Leader in Ground Robotic Solutions, to Expand Multi-Domain Unmanned Systems Offering and Global Presence (Graphic: Business Wire) SIMI VALLEY: AeroVironment Inc. Investors can select from stocks traded directly on Canadian and US exchanges or purchase over-the-counter shares from international companies. The global space robotics market size is expected to reach $5. AeroVironment (NASDAQ: AVAV) 3. Robotics stocks follow a cyclical pattern of ups and downs along with the movement of economic cycles. Click on the tabs below to see more information on Robotics ETFs, including historical performance, dividends, holdings, expense ratios, technical indicators, analysts reports and more. Publicly traded Canadian robotics stocks. 71 billion by 2027, registering a compound annual growth rate of 5. In the third quarter , iRobot's revenue increased 22% year over year, powered by 34% revenue growth in the U.", "All-In-One Screener Buffett-Munger Screener Industry Overview Undervalued Predictable Benjamin Graham Net-Net 52-week/3Y/5Y Lows 52-week/3Y/5Y Highs Magic Formula(Greenblatt) Dividend Stocks Peter Lynch Screen S&P500 Grid Predictable Companies Spin Off List Historical Low P/B List Historical Low P/S List High Short Interest Upcoming Special. 0% stake (later boosted to 5. Ottawa, Ontario--(Newsfile Corp. 1,118 likes · 2 talking about this. The goal of robotics is to. A new partnership between heavy metal fabricator Miller Fabrication Solutions, Brookville, Pa. Build a vertical three-fingered claw that can lift a cup up off the table keeping it level. MZOR Description — Mazor Robotics Ltd. The Company's molecular modeling, simulation, and informatics software are used extensively in the area of nanotechnology. Barron's also provides information on historical stock ratings, target prices, company earnings, market valuation and. 640 Bridge Street West, Waterloo, Ontario N2K 4M9. Flippy, from Miso Robotics. Brendan Riley, President of GreenPower commented, “We are seeing a dramatic increase in autonomous vehicle demand and this vehicle demonstrates the compelling marriage of. Got to love Dividend Growth Investing. This year, three Canadian robotics companies made the list, including relative new-comer, Clearpath Robotics. AeroVironment Acquires Telerob, a Leader in Ground Robotic Solutions, to Expand Multi-Domain Unmanned Systems Offering and Global Presence (Graphic: Business Wire) SIMI VALLEY: AeroVironment Inc. Investors can select from stocks traded directly on Canadian and US exchanges or purchase over-the-counter shares from international companies. The global space robotics market size is expected to reach $5. AeroVironment (NASDAQ: AVAV) 3. Robotics stocks follow a cyclical pattern of ups and downs along with the movement of economic cycles. Click on the tabs below to see more information on Robotics ETFs, including historical performance, dividends, holdings, expense ratios, technical indicators, analysts reports and more. Publicly traded Canadian robotics stocks. 71 billion by 2027, registering a compound annual growth rate of 5. In the third quarter , iRobot's revenue increased 22% year over year, powered by 34% revenue growth in the U.VEX Robotics, Inc. The tire producer / manufacturer and Canadian Tire use this fee to pay for the collection, transportation and processing of used tires. SPECULATIVE BUY. Posted by 3 years ago. A credit card (or PayPal) will be required to pay for shipping for orders under $49. July 14, 2020. Big dollars are being spent on new startups and the devices are becoming more commonplace each day. 71 billion by 2027, registering a CAGR of 5. stock news by MarketWatch. This voucher cannot be used towards shipping fees or Candian brokerage fees. To help provide a sense of the short to long-term trend, included is an interactive Corindus Vascular Robotics stock chart which you can easily adjust to the time frame of your choosing (e. Today, we are leaders in providing this wide range of high-performance solutions, from coatings, fillers, and adhesives to robotics, parts, and engineering. The two tiers are known as Bellwether holdings and Non-Bellwether holdings. 3 Top Robotic-Surgery Stocks to Consider Buying Now If scalpel-wielding robots no longer frighten you, here are three stocks you might want to buy now, and one more to keep your eyes on. GoPro went public in early 2014 and sold approximately $427 million worth of stock, making it the biggest consumer-electronics IPO since battery company Duracell International Inc. Don Burnette and Paz Eshel are Silicon Valley, through and through. The NSERC Canadian Robotics Network (NCRN) is a national partnership that builds upon the highly successful NSERC Canadian Field Robotics Network (NCFRN) , with a broader mandate, wider domain. Reiser (Canada) Co. 1-844-465-7684."]'''
    # sent = '''Space Robotics Market Size Worth $5.7 Billion By 2027 | CAGR: 5.2%: Grand View Research, Inc.Space Robotics Market Size Worth $5.7 Billion By 2027 | CAGR: 5.2%: Grand View Research, Inc.'''
    # sent = '''- Amid the COVID-19 crisis, the global market for Space Robotics estimated at US$3.2 Billion in the year 2020, is projected to reach a revised size of US$5.2 Billion by 2027, growing at a CAGR of 7.2% over the period 2020-2027. Services, one of the segments analyzed in the report, is projected to record 7.6% CAGR and reach US$3.9 Billion by the end of the analysis period. After an early analysis of the business implications of the pandemic and its induced economic crisis, growth in the Products segment is readjusted to a revised 6.1% CAGR for the next 7-year period.'''
    # sent = '''The global Space Robotics market is valued at US$ 2704 million in 2020 is expected to reach US$ 3793.6 million by the end of 2026, growing at a CAGR of 4.9% during 2021-2026. Global Space Robotics Market: Drivers and Restrains'''
    # sent = '''The global plant-based protein market size is projected to grow from USD 10.3 billion in 2020 to USD 14.5 billion by 2025, in terms of value, recording a compound annual growth rate (CAGR) of 7.1% during the forecast period. Some of the major factors driving the growth of the plant-based protein market include growing demand in the food industry, increasing demand for pea-based protein and the opportunity to expand in high growth potential markets.'''
    # imp_sentences = ['The Europe Robotics technology market is expected to reach $46.5 billion by 2022, growing at a CAGR of 10.3% during the forecast period (2016–2022).']
    # print(sent)
    # sent = '''['Amid the COVID-19 crisis, the global market for Space Robotics estimated at US$3.2 Billion in the year 2020, is projected to reach a revised size of US$5.2 Billion by 2027, growing at aCAGR of 7.2% over the period 2020-2027. Services, one of the segments analyzed in the report, is projected to record 7.6% CAGR and reach US$3.9 Billion by the end of the analysis period.', 'The Space Robotics market in the U.S. is estimated at US$948.1 Million in the year 2020. China, the world`s second largest economy, is forecast to reach a projected market size of US$911 Million by the year 2027 trailing a CAGR of 6.7% over the analysis period 2020 to 2027. Among the other noteworthy geographic markets are Japan and Canada, each forecast to grow at 6.7% and 5.8% respectively over the 2020-2027 period. Within Europe, Germany is forecast to grow at approximately 5.9% CAGR. Select Competitors (Total 35 Featured) -']'''
    import time

    curr = time.time()
    result = market_sizing_main_function(sentence)
    print("**************************************************************************************")
    pprint(result)
    # sent = paragraph_to_cagr_sentence(sentence)
    # for i in range(len(sent)):
    #     extacted_topic = get_topic_results(sent[i])
    #     topics = ['space robotics']
    #     list_dict = wrapper_market_value(sent[i], topics)
    #     for list1 in list_dict:
    #         print('Processed Dictionary:', list1)
    #         print("extacted_topic", extacted_topic)
    print('Total time:', time.time() - curr)

    # import pandas as pd
    # import get_elements
    # import time
    #
    # # text = '''Within Europe, growth of cagr in Germany is 14%, while the rest of Europe the projected value is $13 million dollars.'''
    # # doc = nlp(text)
    # input_df = pd.read_excel('Electric Vehicle1.xlsx', sheet_name='final_test_data')
    # # input_df['proj_result_new'] = ''
    # # input_df['cagr_result_new'] = ''
    # # input_df['forecast_value_new'] = ''
    # # input_df['current_value_new'] = ''
    # # input_df['current_year_new'] = ''
    # input_df['all_result'] = ''
    #
    # for row, sent in enumerate(input_df['list of paragraphs']):
    #     if type(sent) != float and sent != '' and str(sent) != 'nan' and len(sent) > 1:
    #         # print('Sent: ',input_df.at[row,'priority'])
    #         if True:  # input_df.at[row,'priority'] == 1:
    #             # sent = input_df.at[row,'Sentence']
    #             print('----------',row, ': ', sent)
    #             curr = time.time()
    #             final_res = wrapper_market_value(sent)
    #             for final_dict in final_res:
    #                 final_dict['time'] = time.time() - curr
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
    #     # if row % 20 == 0 or row % 233 == 0:
    #     #     input_df.to_csv('CAGR_Market_Research_QA_Model_final.csv', index=False)
    # #
    # new_list = list()
    # for row,data in enumerate(input_df['list of paragraphs']):
    #   if input_df.at[row,'all_result']:
    #     len_res = len(input_df.at[row,'all_result'])
    #     if len_res==0:
    #       new_list.append([input_df.at[row,'URL'],data,input_df.at[row,'all_result'],''
    #                        ,'','','','','','','','','','','','',0])
    #     else:
    #       for res in input_df.at[row,'all_result']:
    #         print(res.keys())
    #         locations = list()
    #         if 'country' not in res.keys():
    #           res['country'] = ''
    #         else:
    #           locations.append(res['country'])
    #         if 'continent' not in res.keys():
    #           res['continent'] = ''
    #         else:
    #           locations.append(res['continent'])
    #         print('RESULT:',res)
    #         new_list.append([input_df.at[row,'list of paragraphs'],data,res,res['cagr'],res['percentage'],
    #                          res['upper_year'],res['cagr_lower_year'],res['current_value'],
    #                          res['value_lower_year'],res['projected_value'],
    #                          res['continent'],res['country'],locations,res['match'],res['approach'],res['manual_verification'],res['time']])
    # out_df = pd.DataFrame(new_list,columns=['URL','Sentence','Result','cagr','percentage','upper_year','cagr_lower_year','current_value','value_lower_year','projected_value','continent','country','locations','match','approach','manual_verification','time'])
    # out_df.to_excel('out_data_after_test.xlsx',index=False)
