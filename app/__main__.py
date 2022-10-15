''' acts as a package '''
import datetime
# import logger
from .thehindu import TheHindu

if __name__ == '__main__':
    main_link = 'https://www.thehindu.com/todays-paper/'
    date = datetime.datetime.now().strftime("%y%m%d")
    thehindu = TheHindu(date, main_link)
    for section in thehindu.section:
        print(section.name)
        for article in section.articles:
            print(f'\t{article.content.heading}')
