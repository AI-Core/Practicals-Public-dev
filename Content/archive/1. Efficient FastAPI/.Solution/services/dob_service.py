import requests
from bs4 import BeautifulSoup
import json
import re

def get_dob(first_name: str, last_name: str, city: bool=False):
    infobox_data = get_infobox(first_name, last_name)
    if not infobox_data:
        return None
    birthday = infobox_data.find('span', {'class': 'bday'})

    report = {'First name': first_name,
              'Last_name': last_name,
              'Date of Birth': birthday.text}
    if city:
        birthplace = infobox_data.find('div', {'class': 'birthplace'})
        report['City'] = birthplace.text

    return report

def get_infobox(first_name: str, last_name: str):
    r = requests.get(f'https://en.wikipedia.org/wiki/{first_name}_{last_name}')
    soup = BeautifulSoup(r.text, 'html.parser')
    if soup.find_all('b', text=re.compile('Wikipedia does not have an article with this exact name')):
        return None
    celeb_infobox = soup.find('table', {'class': 'infobox biography vcard'})
    return celeb_infobox.find('td', {'class': 'infobox-data'})