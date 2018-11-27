import requests
import time
import multiprocessing as mp
from bs4 import BeautifulSoup

###################################################################################################
# This is a distributed crawler which can help you crawl steam reviews from www.steam.com
# Include user_name, review_attitude, play_hour, link, review  (split by '\t')
# Usage: modified game_name and game_id to whatever game you interest in steam
#        game id can be found on the steam website
#        e. https://steamcommunity.com/app/646910/reviews/?browsefilter=toprated&snr=1_5_reviews_
###################################################################################################

game_name = 'portal2'
game_id = '620'

base_url = 'http://steamcommunity.com/app/' + game_id + '/homecontent/'
file_path = 'steam_' + game_name + '.txt'
page_params = {'userreviewsoffset': 0, 'p': 0, 'workshopitemspage': 0, 'readytouseitemspage': 0,
               'mtxitemspage': 0, 'itemspage': 0, 'screenshotspage': 0, 'videospage': 0, 'artpage': 0,
               'allguidepage': 0, 'webguidepage': 0, 'integratedguidepage': 0, 'discussionspage': 0}
basic_params = {'numperpage': 10, 'browsefilter': 'toprated', 'appid': '433850', 'appHubSubSection': '10',
                'l': 'english', 'filterLanguage': 'default', 'forceanon': '1'}


def write_callback(array):
    with open(file_path, 'a+', encoding='utf-8') as f:
        for i in array:
            f.writelines(i + '\n')


def crawl(start):
    htmls = []
    for i in range(start, start + 20):
        for key in page_params.keys():
            page_params[key] = str(i)
        page_params['userreviewsoffset'] = str(10 * (i - 1))
        html = requests.get(base_url, dict(basic_params.items() | page_params.items())).text
        htmls.append(html)
    return htmls


def parse(htmls):
    review_list = []
    for html in htmls:
        if html == '':
            continue
        soup = BeautifulSoup(html, 'html.parser')
        reviews = soup.find_all('div', {'class': 'apphub_Card'})

        for review in reviews:
            nick = review.find('div', {'class': 'apphub_CardContentAuthorName'})
            title = review.find('div', {'class': 'title'}).text
            hour = review.find('div', {'class': 'hours'}).text.split(' ')[0]
            link = nick.find('a').attrs['href']
            comment = review.find('div', {'class': 'apphub_CardTextContent'}).text

            if "Early Access Review" in comment:
                comment = comment.split('\n')[3].replace('\t', '')
            else:
                comment = comment.split('\n')[2].replace('\t', '')
            line = nick.text + '\t' + title + '\t' + hour + '\t' + link + '\t' + comment
            review_list.append(line)
    return review_list


if __name__ == '__main__':

    pool = mp.Pool()
    t1 = time.time()

    print('\nDistributed Crawling...')
    crawl_jobs = [pool.apply_async(crawl, args=(start,)) for start in [0, 20, 40, 60, 80, 100]]
    html_s = [j.get() for j in crawl_jobs]

    print('\nDistributed Parsing...')
    res = []
    for html_arr in html_s:
        res.append(pool.apply_async(parse, (html_arr,), callback=write_callback))

    pool.close()
    pool.join()
    t2 = time.time()
    print('End...\n' + 'time used:' + str(float(t2 - t1)) + 's')
