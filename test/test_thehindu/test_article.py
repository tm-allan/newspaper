''' unit test for thehindu.py 
    source: https://realpython.com/python-testing/

    to run this file: python3 -m test.test_thehindu.test_article
'''
import os
import re
import datetime
import requests
import unittest
from glob import glob
from tqdm.auto import tqdm
from bs4 import BeautifulSoup

from app.thehindu import TheHinduArticle, Article, Image

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
}


class Test(unittest.TestCase):
    ''' unit test '''
    def setUp(self):
        ''' equivalent to __init__(). unittest calls setUp first '''
        self.article_link = 'https://www.thehindu.com/todays-paper/centre-to-grant-oil-psus-rs-22000-crore-to-cover-lpg-losses/article66003291.ece'

    def get_raw_article(self):
        ''' downloads and saves an articles as .html file '''
        response = requests.get(self.article_link, timeout=10, headers=headers)
        if response.status_code != requests.codes.ok:
            return None
        with open('test/test_thehindu/article-page.html', 'w') as handle:
            handle.write(response.text)

    def get_saved_article_values(self):
        ''' returns saved article values to compare '''
        title = 'Centre to grant oil PSUs Rs. 22,000 crore to cover LPG losses'
        oneliner = 'Move will help OMCs cover losses they have faced over the past two years'
        place = 'NEW DELHI'
        body = '''<p><span>W</span>ith global prices for liquefied petroleum gas (LPG) surging, the Union Cabinet on Wednesday approved a Rs. 22,000-crore ‘one-time grant’ to public sector oil marketing firms to make good the losses they have faced over the past two years in domestic LPG cylinder supplies.</p>\n\n<p>Domestic LPG cylinders are supplied at regulated prices to consumers by the public sector oil marketing players Indian Oil Corporation, Bharat Petroleum and Hindustan Petroleum Corporation, which will get the grant.</p>\n\n<p>Though international prices for LPG have risen by 300% between June 2020 and June 2022, the increased costs have not been fully passed on to domestic LPG users to insulate them from fluctuations in global prices, as per an official communique from the government. “Accordingly, domestic LPG prices have [been] raised by only 72% during this period. This has led to significant losses for these oil marketing companies (OMCs),” the statement said.</p>\n\n<p>The prices for domestic LPG cylinders were last hiked in July by about Rs. 50 for a 14.2 kg cylinder, taking the cost to Rs. 1,068.5 in Chennai and Rs. 1,053 in New Delhi.</p>'''
        filename = 'TH12PTIGovtt2BGK8ACS5A4.3.jpg.jpg'
        alt_text = 'The Centre says the global prices of LPG have risen 300%.KAMAL NARANG'
        raw = None
        article = Article(title, oneliner, place, body)
        image = Image(filename, alt_text, raw)
        return article, image

    def test_article(self):
        ''' test the TheHinduArticle class '''
        with open('test/test_thehindu/article-page.html', 'r') as handle:
            response = handle.read()
            soup = BeautifulSoup(response, 'html.parser')
            extracted_article = TheHinduArticle(None)
            extracted_article.content = extracted_article.get_content(soup, self.article_link)
            extracted_article.image = extracted_article.get_image(soup)
            saved_article_data, saved_article_image = self.get_saved_article_values()
            self.assertEqual(saved_article_data.heading, extracted_article.content.heading)
            self.assertEqual(saved_article_data.oneliner, extracted_article.content.oneliner)
            self.assertEqual(saved_article_data.place, extracted_article.content.place)
            self.assertEqual(saved_article_data.body, extracted_article.content.body)
            self.assertEqual(saved_article_image.filename, extracted_article.image.filename)
            self.assertEqual(saved_article_image.alt_text, extracted_article.image.alt_text)
            self.assertIsNotNone(extracted_article.image.alt_text)


if __name__ == '__main__':
    unittest.main()
