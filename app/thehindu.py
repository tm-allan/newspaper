''' extract articles from thehindu page '''
import os
import re
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


def get_image(date, file_handler, soup):
    ''' download image '''
    try:
        image_src = soup.select('picture')[0].find_all('source')[0]['srcset']
        response = requests.get(image_src, timeout=10, headers=headers)
        # convert the filename into admissible characters
        basename = "".join(x for x in os.path.basename(image_src) if (x.isalnum() or x=='.'))
        # move it to {date}/images folder
        filename = os.path.join(date, 'images', basename)
        with open(filename, 'wb') as handle:
            handle.write(response.content)
        image_alt = soup.select('.lead-img')[0]['alt']
        # change the filename to remove {date} as the path inside .md file is relative
        filename = os.path.join('images', basename)
        file_handler.write(article_image.format(filename, image_alt))
    except Exception as exc:
        # print(f'Error4: {str(exc)}')
        pass


def get_article(date, file_handler, endpoint):
    ''' get one news article '''
    try:
        response = requests.get(endpoint, timeout=10)
        if response.status_code != requests.codes.ok:
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.select('.title')[0].getText().strip()
    except Exception as exc:
        print(f'Error3a: {str(exc)}')

    try:
        oneliner = soup.select('div.hidden-xs:nth-child(8)')[0].getText().strip()
    except Exception as exc:
        # print(f'Error3b: {str(exc)}')
        oneliner = None

    try:
        place = soup.select('.ut-container > span:nth-child(1)')[0].getText().strip().upper()
    except Exception as exc:
        # print(f'Error3b: {str(exc)}')
        place = None

    try:
        value = [int(s) for s in re.findall(r'-?\d+?\d*', os.path.basename(endpoint))][0]
        data = [str(para) for para in soup.select(f'#content-body-{value}')[0]]
        # for para in soup.select(f'#content-body-{value}')[0]:
        #     content = para.getText().strip()
        #     if len(content.split(' ')) < 10:
        #         content = f'### {content}'
        #     data.append(content)
        data = '\n\n'.join(data)
    except Exception as exc:
        print(f'Error3c: {str(exc)}')
        return

    file_handler.write(article_heading.format(title))
    get_image(date, file_handler, soup)
    if oneliner:
        file_handler.write(article_oneliner.format(oneliner))
    if place:
        file_handler.write(f'### {place}\n\n')
    file_handler.write(article_body.format(data))
    file_handler.write('-----\n\n')


def get_section(date, heading, section_link):
    ''' download one section of the page '''
    try:
        filename = os.path.join(date, heading.replace(' ', '-'))
        response = requests.get(section_link, timeout=10, headers=headers)
        # if response.status_code != requests.codes.ok:
        #     return
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        subsections = soup.select('#section_1')[0].select('.archive-list')
        urls = []
        for subsection in subsections:
            # has all the headings and the links
            for tags in subsection.find_all('a'):
                # lists all the <a> tags with the links
                urls += [tags.get('href')]

        with open(f'{filename}.md', 'w') as file_handler:
            file_handler.write(f'# {heading.title()}\n\n')
            for url in tqdm(urls, desc=heading):
                get_article(date, file_handler, url)

        # front_page = soup.select('#section_1')[0].select('.archive-list')[0].find_all('li')
        # front_page = {item.getText().strip(): item.find('a').get('href') for item in front_page}
        # # print(front_page)
        # with open(f'{filename}.md', 'w') as file_handler:
        #     file_handler.write(f'# {heading}\n\n')
        #     for link in tqdm(front_page.values(), desc=heading):
        #         get_article(date, file_handler, link)
        #         # break

    except Exception as exc:
        print(f'Error2: {str(exc)}')
        print(f'Debug Msg: heading: {heading} | section_link: {section_link}')
        return


def ensure_paths(date):
    ''' ensure that these paths exists '''
    if not os.path.exists(date):
        os.makedirs(date)
    image_folder = os.path.join(date, 'images')
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)


def make_main_page(date):
    main_page = os.path.join(date, 'main-page.md')
    with open(main_page, 'w') as handle:
        handle.write('# The Hindu\n\n')
        for filename in sorted(glob(f'{date}/*.md')):
            filename = os.path.basename(filename)
            heading = os.path.splitext(filename)[0].replace('-', ' ').title()
            handle.write(f'[{heading}](./{filename})\n\n')


def get_mainpage(main_link=main_link):
    ''' extract details from the page with today's paper '''
    try:
        date = datetime.datetime.now().strftime("%y%m%d")
        response = requests.get(main_link, timeout=10, headers=headers)
        if response.status_code != requests.codes.ok:
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        header = soup.select('#subnav-tpbar-latest')[0]
        header = {item.getText().strip().lower(): item.get('href') for item in header}
        for heading, link in header.items():
            if heading in not_allowed_sections:
                continue
            ensure_paths(date)
            get_section(date, heading, link)
        make_main_page(date)

    except Exception as exc:
        print(f'Error1: {str(exc)}')
        print(f'header: {header}')
        return


if __name__ == '__main__':
    get_mainpage(main_link)
    # make_main_page('221006')
