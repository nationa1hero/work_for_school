import requests
from bs4 import BeautifulSoup
import csv

def parser(url:str):
    res = requests.get(url = url)
    soup = BeautifulSoup(res.text, 'lxml')
    tasks = soup.find_all('div', class_ = 'nobreak')
    print(tasks)
    for t in tasks:
        name = t.get('probtext')
        print(name)

def create_csv():
    pass

def write_csv():
    pass

if __name__ == '__main__':
    parser(url = 'https://rus6-vpr.sdamgia.ru/test?theme=15')