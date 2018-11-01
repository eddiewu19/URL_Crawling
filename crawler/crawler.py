# external import
from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.request
import time
from PIL import ImageFile
import re
from newspaper import Article
import newspaper
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

# function definitions
def simple_get(url):
    """
    Transforms URL into a Soup object
    :param url: URL
    :rtype: BeautifulSoup Object
    """
    if valid_url(url):
        if url_is_alive(url):
            page = urlopen(url)
            soup = BeautifulSoup(page,"lxml")  #html.parser, html5lib, lxml
            return soup
        else:
            return "Bad URL"
    else:
        return "Bad URL"
    
def get_title(soup):
    """
    Extracts the title from the website
    :param soup: BeautifulSoup Object
    :rtype: String
    """
    return soup.title

def get_pictures(soup):
    """
    Takes first 4 valid image URL's from website and chooses the best picture by IMG size.
    :param soup: BeautifulSoup Object
    :rtype: Image URL of the selected IMG
    """
    image_tags = soup.findAll('img')
    counter = 0
    urls = []
    sizes = []
    # print out image urls
    for image_tag in image_tags:
            if valid_url(image_tag.get('src')) and counter < 4:
                counter += 1
                urls.append(image_tag.get('src'))
                sizes.append(getsizes(image_tag.get('src'))[0])
    return urls[sizes.index(max(sizes))]
        
def url_is_alive(url):
    """
    Checks that a given URL is reachable.
    :param url: A URL
    :rtype: bool
    """
    request = urllib.request.Request(url)
    request.get_method = lambda: 'HEAD'

    try:
        urllib.request.urlopen(request)
        return True
    except urllib.request.HTTPError:
        return False

def valid_url(url):
    """
    Checks if a URL is malformed
    :param url: A URL
    :rtype: bool
    """
    regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None   # True

def getsizes(url):
    """
    Takes a image URL and returns its size 
    :param url: A URL
    :rtype: Int
    """
    file = urlopen(url)
    size = file.headers.get("content-length")
    if size: size = int(size)
    p = ImageFile.Parser()
    while 1:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            return size, p.image.size
            break
    file.close()
    return size, None

def get_article_links(url):
    """
    Takes a URL with articles and returns a list of URLs of all the contained articles.
    :param url: A URL
    :rtype: list
    """
    links = newspaper.build(url, memoize_articles=False, language = 'zh')
    return [article.url for article in links.articles]

def recommend_article(article_feed_url, tag):
    """
    Takes a URL with articles as well as a tag and returns the recommended article title 
    (for now) from this URL based on the tag. Currently selects the article with highest
    tag occurrences in its main text. 
    :param article_feed_url: A URL
    :param tag: String
    :rtype: String
    """

    list_of_article_titles = []
    all_text = []
    key_words = []
    english_check = re.compile(r'[a-z]')
    if english_check.match(tag): # english
        print("This is a english website")
        if valid_url(article_feed_url) and url_is_alive(article_feed_url):
            article_urls = get_article_links(article_feed_url) 
            try:
                for article_url in article_urls: 
                    if valid_url(article_url) == False or url_is_alive(article_url) == False: 
                        continue
                    cur_article = Article(article_url, language = 'zh')
                    cur_article.download()
                    cur_article.parse()
                    list_of_article_titles.append(cur_article.title)
                    tag_frequency.append(cur_article.text.lower().count(tag))
                    all_text.append(cur_article.text.lower())
                print("there are in total of {0} articles collected".format(len(list_of_article_titles)))
            except:
                print("download limit exceeded... but the result so far is returned...")
                print("there are in total of ", len(list_of_article_titles), ' articles collected')
        else:
            return 'Bad URL'
        
    else: # chinese
        print("this is a chinese website")
        soup = simple_get(article_feed_url)
        try:
            for article in soup.findAll('a', href=True):
                if article.text and article['href'] and len(article.text.replace(' ', '')) >= 15:
                    cur_article = Article(article_feed_url + article['href'][1:], language = 'zh')
                    cur_article.download()
                    cur_article.parse()
                    cur_article.nlp()
                    list_of_article_titles.append(cur_article.title)
                    all_text.append(cur_article.text.lower())
                    key_words.append(cur_article.keywords)

            print("there are in total of ", len(list_of_article_titles), ' articles collected')
            print("These are the titles of found articles: ", list_of_article_titles)

        except:
            print("download limit exceeded... but the result so far is returned...")
            print("there are in total of ", len(list_of_article_titles), ' articles collected')


        if not all_text:
            return None

    # create vector representation of our articles
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(all_text)

    # create binary target variable (whether or not the tag is in the keywords)
    y = []
    for keywords in key_words:
        check = False
        for keyword in keywords:
            if tag in keyword:
                check = True
                break
        if check:
            y.append(1)
        else:
            y.append(0)

    # build logistic regression model to find article with highest probability
    clf = LogisticRegression().fit(X, y)
    article_probs = clf.predict_proba(X)[:, 1]
    return list_of_article_titles[np.argmax(article_probs)]
