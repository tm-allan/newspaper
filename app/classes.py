
class Image():
    ''' a datastructure to store the details of an image '''
    def __init__(self, filename, alt_text, raw):
        self.filename = filename
        self.alt_text = alt_text
        self.raw = raw


class Article():
    ''' a datastructure to store the details of an article '''
    def __init__(self, heading, oneliner, place, body):
        self.heading = heading
        self.oneliner = oneliner
        self.place = place
        self.body = body


class Section():
    ''' a datastructure to store the details of an article '''
    def __init__(self, name, link, articles):
        self.name = name
        self.link = link
        self.articles = articles
