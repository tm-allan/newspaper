''' extract articles from thehindu page '''
import os
import re
import logging
import datetime
import requests
from glob import glob
from tqdm.auto import tqdm
from bs4 import BeautifulSoup


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
}
main_link = 'https://www.thehindu.com/todays-paper/'
article_heading ='## <span style="color:blue"> {} </span>\n\n'
article_oneliner = '### <div style="text-align: justify"> *{}* </div>\n\n'
article_body = '<div style="text-align: justify"> \n\n{} </div>\n\n'
article_image = '![alt text]({} "{}")\n\n'
not_allowed_sections = [
    # 'Front Page',
    # 'national',
    'tamil nadu',
    'karnataka',
    # 'kerala',
    'andhra pradesh',
    'telangana',
    # 'new delhi',
    # 'international',
    # 'opinion',
    # 'business',
    # 'sport',
    # 'miscellaneous',
    # 'education plus',
    # 'others',
]

LOGGER = logging.getLogger('newspaper.thehindu')


class Image():
    ''' a datastructure to store the details of an image '''
    def __init__(self, filename, alt_text, raw):
        self.filename = filename
        self.alt_text = alt_text
        self.raw = raw


class Article():
    ''' a datastructure to store the details of an article '''
    def __init__(self, title, oneliner, place, body):
        self.title = title
        self.oneliner = oneliner
        self.place = place
        self.body = body


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
            if response.status_code != requests.codes.ok:
                return None
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
            if response.status_code != requests.codes.ok:
                return None
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
        try:
            title = soup.select('.title')[0].getText().strip()
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

        return Article(title, oneliner, place, body)


if __name__ == '__main__':
    test_article_link = 'https://www.thehindu.com/todays-paper/centre-to-grant-oil-psus-rs-22000-crore-to-cover-lpg-losses/article66003291.ece'
    article = TheHinduArticle(test_article_link)
    print(f'title: {article.content.title}')
    print(f'oneliner: {article.content.oneliner}')
    print(f'place: {article.content.place}')
    print(f'body: {article.content.body}')
    print(f'filename: {article.image.filename}')
    print(f'alt_text: {article.image.alt_text}')
    # print(article.image.raw)
