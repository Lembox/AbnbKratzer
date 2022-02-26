from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

desired_path = ""
base_url = "https://airbnb.de"
search_url = "https://www.airbnb.de/s/Bayreuth/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_dates%5B%5D=april&flexible_trip_dates%5B%5D=march&flexible_trip_lengths%5B%5D=weekend_trip&date_picker_type=calendar&query=Bayreuth&place_id=ChIJGQMtqMWioUcRNOfR0gnfhto&checkin=2022-03-12&checkout=2022-03-19&adults=2&source=structured_search_input_header&search_type=autocomplete_click"

options = Options()
options.add_argument('--blink-settings=imagesEnabled=false')
driver = webdriver.Chrome(options=options)
driver.get(search_url)
time.sleep(3)
page_detailed = driver.page_source
detail_soup = BeautifulSoup(page_detailed, features="html.parser")
search_listings = detail_soup.find_all('div', 'cm4lcvy dir dir-ltr')

def extract_element(listing_html, params):
    # 1. Find the right tag
    if 'class' in params:
        elements_found = listing_html.find_all(params['tag'], params['class'])
    else:
        elements_found = listing_html.find_all(params['tag'])

    # 2. Extract the right element
    tag_order = params.get('order', 0)
    element = elements_found[tag_order]

    # 3. Get text
    if 'get' in params:
        output = element.get(params['get'])
    else:
        output = element.get_text()

    if 'split' in params:
        if ('check-before-split' in params) and (params.get('check-before-split', 0) in output):
            output = output.split(params['split'])[params.get('pos', 0) - 1].replace(' ', '')
        else:
            output = output.split(params['split'])[params.get('pos', 0)].replace(' ', '')

    if 'number' in params:
        output = output.replace(',', '.')

    if 'check-for' in params:
        output = output.split(params.get('check-for', 0))[0]

    if 'bool_check' in params:
        output = int(params.get('bool_check', 0) in output)

    if 'exc_bool' in params:
        if output == 'Studio':
            output = 1

    if 'replace' in params:
        output = str(output).replace(params.get('replace', 0), '')

    if 'replace2' in params:
        output = str(output).replace(params.get('replace2', 0), '')
    return output

SEARCH_PAGE = {
    'url': {'tag': 'a', 'get': 'href'},
    'number_of_listings': {'tag': 'div', 'class': '_1h559tl'}
}

LISTING_PAGE = {
    'name': {'tag': 'h1', 'class': '_fecoyn4'},
    'room_type': {'tag': 'h2', 'class': '_14i3z6h', 'split': ' ', 'pos': 0},
    'city': {'tag': 'span', 'class': '_8vvkqm3', 'split': ',', 'pos': 0},
    'state': {'tag': 'span', 'class': '_8vvkqm3', 'split': ',', 'pos': 1},
    'country': {'tag': 'span', 'class': '_8vvkqm3', 'split': ',', 'pos': 2},
    'number_of_guests': {'tag': 'ol', 'class': '_194e2vt2', 'split': ' ', 'pos': 0},
    'bedrooms': {'tag': 'ol', 'class': '_194e2vt2', 'split': ' ', 'pos': 3, 'exc_bool': 'Studio'},
    'beds': {'tag': 'ol', 'class': '_194e2vt2', 'split': ' ', 'pos': 6, 'check-before-split': 'Studio'},
    'bathrooms': {'tag': 'ol', 'class': '_194e2vt2', 'split': ' ', 'pos': 9, 'number': 1, 'check-before-split': 'Studio'},
    'bathrooms_shared': {'tag': 'ol', 'class': '_194e2vt2', 'split': ' ', 'pos': 10, 'bool_check': 'emeins', 'check-before-split': 'Studio'},
    'overall_rating': {'tag': 'span', 'class': '_17p6nbba', 'split' : ' ', 'pos': 0, 'number': 1},
    'number_of_reviews': {'tag': 'span', 'class': '_s65ijh7', 'split' : ' ', 'pos': 0, 'check-for': '\xa0'},
    'superhost': {'tag': 'span', 'class': '_1puzr7bb', 'bool': 1},
    'price': {'tag': 'span', 'class': '_tyxjp1', 'replace': '€'},
    'cleaning_fee': {'tag': 'span', 'class': '_1k4xcdh', 'order': 1, 'replace': '€'},
    'service_fee': {'tag': 'span', 'class': '_1k4xcdh', 'order': 2, 'replace': '€'},
    'total_price': {'tag': 'span', 'class': '_1k4xcdh', 'order': 3, 'replace': '€', 'replace2': '.'},
    'weekly_discount': {'tag': 'span', 'class': '_swukpu', 'replace': '€'},
    'cleanliness': {'tag': 'span', 'class': '_4oybiu', 'order': 0, 'number': 1},
    'communication': {'tag': 'span', 'class': '_4oybiu', 'order': 1, 'number': 1},
    'check-in': {'tag': 'span', 'class': '_4oybiu', 'order': 2, 'number': 1},
    'accuracy': {'tag': 'span', 'class': '_4oybiu', 'order': 3, 'number': 1},
    'location': {'tag': 'span', 'class': '_4oybiu', 'order': 4, 'number': 1},
    'value': {'tag': 'span', 'class': '_4oybiu', 'order': 5, 'number': 1},
    'host_id': {'tag': 'a', 'class': '_9bezani', 'get': 'href', 'split': '/', 'pos': -1},
    'host_name': {'tag': 'h2', 'class': '_14i3z6h', 'split': '\xa0', 'pos': -1},
}

def extract_amenities(features_dict, soup):
    features_dict['WLAN'] = int('WLAN' in soup)
    features_dict['free_parking'] = int('Kostenloser Parkplatz' in soup)
    features_dict['laundry'] = int('Waschmaschine' in soup)
    features_dict['kitchen'] = int('Küche' in soup)
    features_dict['garden'] = int("M16 1a5 5 0 0 1 5 5 5 5 0 0 1 0 10" in soup)
    features_dict['balcony'] = int("M23 1a2 2 0 0 1 1.995 1.85L25" in soup)
    features_dict['working_area'] = int('Arbeitsplatz' in soup)

def extract_page_features(features_dict, soup, rules):
    for feature in rules:
        try:
            features_dict[feature] = extract_element(soup, rules[feature])
        except:
            features_dict[feature] = None

        if 'bool' in rules[feature]:
            features_dict[feature] = int(features_dict[feature] is not None)
    return features_dict

def determine_amount_prices(soup):
    st = str(soup)
    amount = 0
    if "Reinigungsgebühr" in st:
        amount += 1
    if "Service-Gebühr" in st:
        amount += 10
    return amount

out = []
count = 0
limit = 10
while search_listings and limit > 0:
    driver.get(search_url + "&items_offset=" + str(20 * count))
    time.sleep(2)
    page_detailed = driver.page_source
    detail_soup = BeautifulSoup(page_detailed, features="html.parser")
    search_listings = detail_soup.find_all('div', 'cm4lcvy dir dir-ltr')
    for x in search_listings:
        features_dict = {}
        url = extract_element(x, SEARCH_PAGE['url'])
        features_dict['url'] = base_url + url.split('?')[0]
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(base_url + url)
        time.sleep(4)
        page_detailed = driver.page_source
        detail_soup = BeautifulSoup(page_detailed, features="html.parser")
        detail_soup_price = detail_soup.find_all('span', '')
        price_details = detail_soup.find_all('div', '_1bgajnx')
        amount_prices = determine_amount_prices(price_details)
        tmp = dict(LISTING_PAGE)
        if amount_prices == 0:
            tmp.pop('cleaning_fee')
            tmp.pop('service_fee')
            tmp['total_price']['order'] = 1
        elif amount_prices == 1:
            tmp.pop('service_fee')
            tmp['total_price']['order'] = 2
        elif amount_prices == 10:
            tmp.pop('cleaning_fee')
            tmp['service_fee']['order'] = 1
            tmp['total_price']['order'] = 2
        else:
            tmp['cleaning_fee']['order'] = 1
            tmp['service_fee']['order'] = 2
            tmp['total_price']['order'] = 3
        amenities = detail_soup.find_all('div', '_19xnuo97')
        extract_amenities(features_dict, str(amenities))
        features_dict['id'] = features_dict['url'].split('/')[-1]
        out.append(extract_page_features(features_dict, detail_soup, tmp))
        answer_rate = detail_soup.find_all('li', 'f19phm7j dir dir-ltr')
        for tag in answer_rate:
            st = str(tag)
            if 'Antwortrate' in st:
                features_dict['answer_rate'] = st.split("<span>")[1].split("</span")[0].replace('%', '')
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)
    count += 1
    limit -= 1

driver.quit()
df = pd.DataFrame(out)
df.to_csv(desired_path + time.strftime("%Y%m%d-%H%M%S") + ".csv", index=False, encoding='utf-8')
