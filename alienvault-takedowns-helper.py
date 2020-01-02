#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AlienVault Takedowns Helper - A script to get the registrars of all DNS found from an IP address
Usage:

python3 alienvault-takedowns-helper.py IP_ADDRESS (To find on alienvault the DNS registrars)
python3 alienvault-takedowns-helper.py DNS (To do a whois on the DNS)
'''

import sys
import math
import whois
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

OPTIONS = Options()
OPTIONS.add_argument("--headless")
OPTIONS.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

DRIVER = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=OPTIONS)

def validate_ip(host):
    '''Check if a string is an IP address'''
    parts = host.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        i = int(part)
        if i < 0 or i > 255:
            return False
    return True

def main():
    '''Main Function'''
    if validate_ip(sys.argv[1]):
        print('=== {} ==='.format(sys.argv[1]))
        DRIVER.get('https://otx.alienvault.com/indicator/ip/{}'.format(sys.argv[1]))
        soup = BeautifulSoup(DRIVER.page_source, 'html.parser')

        passive_dns_count = soup.select_one('.count-circle:nth-of-type(1) span').text
        number_pages = math.ceil(int(passive_dns_count) / 10)

        dns_list = []
        for i in range(0, number_pages):
            soup = BeautifulSoup(DRIVER.page_source, 'html.parser')
            soup = soup.find('div', id='passive')
            for link in soup.findAll('a'):
                if link.has_attr('href') and '/indicator/hostname/' in link['href']:
                    dns = link['href'].replace('/indicator/hostname/', '')
                    dns_list.append(dns)
            menu_button = DRIVER.find_element_by_css_selector("a.next")
            menu_button.click()

        for dns in dns_list:
            try:
                domain = whois.query(dns)
                if domain is not None:
                    print('{} - REGISTRAR: {}'.format(dns, domain.registrar))
                else:
                    print('{} - REGISTRAR: NOT FOUND'.format(dns))
            except whois.exceptions.UnknownTld:
                print('{} - REGISTRAR: NOT FOUND'.format(dns))
    else:
        domain = whois.query(sys.argv[1])
        if domain is not None:
            print('NAME: {}'.format(domain.name))
            print('REGISTRAR: {}'.format(domain.registrar))
            print('CREATTION DATE: {}'.format(domain.creation_date))
            print('EXPIRATION DATE: {}'.format(domain.expiration_date))
            print('LAST UPDATED: {}'.format(domain.last_updated))
        else:
            print('WHOIS NOT FOUND')

if __name__ == '__main__':
    main()
