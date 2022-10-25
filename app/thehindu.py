''' extract articles from thehindu page '''
import os
import re
import sys
import logging
import datetime
import requests
from tqdm.auto import tqdm
from bs4 import BeautifulSoup

sys.path.append('.')
sys.path.append('app')

import logger
from classes import *


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
}
main_link = 'https://www.thehindu.com/todays-paper/'

LOGGER = logging.getLogger('newspaper.thehindu')


class TheHinduArticle():
    ''' download an article from thehindu '''
    def __init__(self, link):
        ''' initialize the class variables '''
        self.link = link
        if link is None or link == '':
            self.content = None
            self.image = None
        else:
            soup = self.get_page(link)
            self.content = self.get_content(soup, link)
            self.image = self.get_image(soup)

    def get_page(self, endpoint):
        ''' get a page '''
        try:
            response = requests.get(endpoint, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception as exc:
            LOGGER.error(str(exc))
            return None
        return soup

    def get_image(self, soup):
        ''' download image '''
        try:
            image_src = soup.select('picture')[0].find_all('source')[0]['srcset']
            response = requests.get(image_src, timeout=10, headers=headers)
            response.raise_for_status()
            # convert the filename into admissible characters
            filename = "".join(x for x in os.path.basename(image_src) if (x.isalnum() or x == '.'))
            # move it to {date}/images folder
            image_alt = soup.select('.lead-img')[0]['alt']
            return Image(filename, image_alt, response.content)
        except Exception as exc:
            LOGGER.debug(str(exc))
            return None

    def get_content(self, soup, link):
        ''' get one news article '''
        heading = oneliner = place = body = None
        try:
            heading = soup.select('.title')[0].getText().strip()
        except Exception as exc:
            LOGGER.error(str(exc))

        try:
            oneliner = soup.select('div.hidden-xs:nth-child(8)')[0].getText().strip()
        except Exception as exc:
            LOGGER.debug(str(exc))

        try:
            place = soup.select('.ut-container > span:nth-child(1)')[0].getText().strip().upper()
        except Exception as exc:
            LOGGER.debug(str(exc))

        try:
            value = [int(s) for s in re.findall(r'-?\d+?\d*', os.path.basename(link))][0]
            body = [str(para) for para in soup.select(f'#content-body-{value}')[0]]
            body = '\n\n'.join(body)
        except Exception as exc:
            LOGGER.error(str(exc))

        return Article(heading, oneliner, place, body)


class TheHindu():
    ''' class to download the day's paper '''
    def __init__(self, date, link):
        ''' initialize '''
        # TODO: add date
        self.date = date
        self.link = link
        self.section = self.get_mainpage(link)

    def fetch_page(self, link):
        try:
            response = requests.get(link, timeout=10, headers=headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as exc:
            LOGGER.error(exc)
            return None

    def get_articles_from_section(self, heading, section_link):
        ''' download all articles from this section '''
        try:
            soup = self.fetch_page(section_link)
            subsections = soup.select('#section_1')
            # handle cases where a subsection has no articles
            if subsections:
                subsections = subsections[0].select('.archive-list')
            else:
                return []
            urls = []
            for subsection in subsections:
                # has all the headings and the links
                for tags in subsection.find_all('a'):
                    # lists all the <a> tags with the links
                    urls += [tags.get('href')]
            # return the list of articles
            return [TheHinduArticle(url) for url in tqdm(urls, desc=heading)]
        except Exception as exc:
            LOGGER.exception(exc)
            LOGGER.debug(f'heading: {heading} | section_link: {section_link}')
            return []

    def get_sections_list(self, link):
        ''' extract details from the page with today's paper '''
        try:
            soup = self.fetch_page(link)

            header = soup.select('#subnav-tpbar-latest')[0]
            return {item.getText().strip().title(): item.get('href') for item in header}

        except Exception as exc:
            LOGGER.error(exc)
            return None

    def get_mainpage(self, link=main_link):
        ''' extract details from the page with today's paper '''
        try:
            sections_link = self.get_sections_list(link)
            if sections_link is None:
                LOGGER.error("Cound not get today's paper")
                return None
            # section = []
            # for heading, link in sections_link.items():
            #     if heading != 'Others':
            #         continue
            #     section += [Section(heading, link, self.get_articles_from_section(heading, link))]
            #     break
            # return section
            return [Section(heading, link, self.get_articles_from_section(heading, link)) for heading, link in sections_link.items()]

        except Exception as exc:
            LOGGER.error(exc)
            return


if __name__ == '__main__':
    date = datetime.datetime.now().strftime("%y%m%d")
    thehindu = TheHindu(date, main_link)
    if thehindu.section is None:
        sys.exit(1)
    for section in thehindu.section:
        print(section.name)
        for article in section.articles:
            print(f'\t{article.content.heading}')
