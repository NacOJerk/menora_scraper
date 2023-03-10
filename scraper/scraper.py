from bs4 import BeautifulSoup
from bs4 import element
import requests
from typing import List, Tuple, Dict
from datetime import datetime

PHONE_USER_AGENT = 'Mozilla/5.0 (Linux; Android 9; ASUS_X00TD; Flow) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/359.0.0.288 Mobile Safari/537.36'
EVENTS_URL = 'https://www.sportpalace.co.il/menora-mivtachim/%D7%9C%D7%95%D7%97-%D7%90%D7%A8%D7%95%D7%A2%D7%99%D7%9D/'
EVENT_CLASS = 'mc-events'
TIME_CLASS  ='time'
DESC_CLASS = 'desc'

Element = element.Tag
Elements = List[Element]

def get_website_content(url=EVENTS_URL) -> BeautifulSoup: 
    response = requests.get(url, headers={'user-agent': PHONE_USER_AGENT})

    assert response.status_code == 200, "Response code is not success full"

    return BeautifulSoup(response.text, features="html.parser")

def get_all_events_elements(soup: BeautifulSoup) -> Elements:    
    return soup.find_all('li', {"class": "mc-events"})

def get_next_month_link(soup: BeautifulSoup) -> Elements:    
    return soup.find('li', {"class": "my-calendar-next"}).find('a')['href']

def to_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        assert False, "Value (%s) isn't an int" % value

def find_exatly_one(element: Element, typ: str, filter: Dict[str, str]) -> Element:
    found = element.find_all(typ, filter)
    assert len(found) == 1, "There isn't a single element, %s - %s - %s" % (typ, str(filter), str(found))

    return found[0]

def get_single_event_info(element: Element, year: str, month: str, day: str) -> Tuple[str, datetime]:

    hour_minute = find_exatly_one(element, 'span', {'class': TIME_CLASS}).text.split(':')

    assert len(hour_minute) == 2, "Time element isn't composed with hour and minute, %s" % hour_minute
    hour, minute = hour_minute

    year, month, day, hour, minute = [to_int(val) for val in [year, month, day, hour, minute]]

    desc = find_exatly_one(element, 'span', {'class': DESC_CLASS}).text
    return (desc, datetime(year, month, day, hour, minute))

def get_event_info(element: Element) -> List[Tuple[str, datetime]]:
    
    assert element.has_attr('id'), "Element doesn't have id attribute"
    id_splitted_vals = element.get('id').split('-')

    assert len(id_splitted_vals) == 4, "Not enough values in id, %s" % str(id_splitted_vals)
    year, month, day = id_splitted_vals[1:]

    return [get_single_event_info(elem, year, month, day) for elem in element.find_all("div", {'class': 'game'})]


def get_all_events_info() -> List[Tuple[str, datetime]]:
    website_content = get_website_content()
    events = []
    for event_list in [get_event_info(element) for element in get_all_events_elements(website_content)]:
        events += event_list

    next_month_link = get_next_month_link(website_content)

    for event_list in [get_event_info(element) for element in get_all_events_elements(get_website_content(next_month_link))]:
        events += event_list

    return events

if __name__ == "__main__":
    elements_info = get_all_events_info()
    print("All elements: ")
    for desc, date in elements_info:
        print("%d-%d-%d %d:%d: %s" % (date.day, date.month, date.year, date.hour, date.minute, desc))