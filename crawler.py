import requests
from bs4 import BeautifulSoup
from urlparse import urlparse
from multiprocessing import Pool
import re

#list for already parsed urls
parsed = []
#list for external urls
external = []
#ip regex
reip = re.compile('(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}')

#crawler, open url, search links in html and send to other functions
def crawl(url, maxlevel):
    results = open('results.txt', 'a')
    if(maxlevel == 0):
        return
    cleanurl = url.strip()
    cleanurl = 'http://' + cleanurl
    domain = urlparse(cleanurl).netloc
    try:
        r = requests.get(cleanurl, timeout=5)
    except:
        return
    parsed.append(cleanurl)
    teex(cleanurl, r.text)
    jsex(cleanurl, r.text)
    frex(cleanurl, r.text)
    soup = BeautifulSoup(r.text, 'lxml')
    for a in soup.find_all('a', href=True):
        hurl = a['href']
        if '://' in hurl:
            hdomain = urlparse(hurl).netloc
            if domain not in hdomain:
                if hurl not in external:
                    if '.ru' in urlparse(hurl).netloc:
                        results.write(domain.encode('utf-8') + "," + hurl.encode('utf-8') + "\n")
                    if reip.match(urlparse(hurl).netloc):
                        results.write(domain.encode('utf-8') + "," + hurl.encode('utf-8') + "\n")
                    external.append(hurl)
            else:
                if hurl not in parsed:
                    parsed.append(hurl)
                    teex(hurl, r.text)
                    jsex(hurl, r.text)
                    frex(hurl, r.text)
                    crawl(hurl, maxlevel - 1)
    results.close()

#parse text and search for suspicious keywords
def teex(url, source):
    terms = ['hack', 'h4ck', 'deface', 'd3f4c3', 'l33t', 'h4xor']
    textresults = open('textresults.txt', 'a')
    for term in terms:
        termr = re.escape(term)
        if re.search(termr, source, re.IGNORECASE):
            textresults.write("term " + term + " found in " + url + "\n")
    textresults.close()



#parse scripts
def jsex(url, source):
    jsresults = open('jsresults.txt', 'a')
    soup = BeautifulSoup(source, 'lxml')
    scripts = soup.findAll('script',{'src':True})
    for script in scripts:
            #check if there is .ru domain in script src url
            if  '://' in script['src'] and '.ru' in script['src']:
                jsresults.write(url.encode('utf-8') + "," + urlparse(script['src']).netloc + ","  + script['src'].encode('utf-8') + '\n')
            #check if there is ip in script src url
            if reip.match(urlparse(script['src']).netloc):
                jsresults.write(url.encode('utf-8') + "," + urlparse(script['src']).netloc + ","  + script['src'].encode('utf-8') + '\n')
            else:
                return

    jsresults.close()

#parse frames
def frex(url, source):
    frameresults = open('frameresults.txt', 'a')
    soup = BeautifulSoup(source, 'lxml')
    iframes = soup.findAll('iframe',{'src':True})
    for frame in iframes:
            #check if there is .ru domain in script src url
            if  '://' in frame['src'] and '.ru' in frame['src']:
                frameresults.write(url.encode('utf-8') + "," + urlparse(frame['src']).netloc + ","  + frame['src'].encode('utf-8') + '\n')
            #check if there is ip in script src url
            if reip.match(urlparse(frame['src']).netloc):
                rameresults.write(url.encode('utf-8') + "," + urlparse(frame['src']).netloc + ","  + frame['src'].encode('utf-8') + '\n')
            else:
                return
    frameresults.close()

def job(line):
    maxlevel = 1
    crawl(line, maxlevel)

if __name__ == "__main__":
    pool = Pool(100)
    with open('list.txt') as source_file:
        # chunk the work into batches of 4 lines at a time
        result = pool.map(job, source_file, 4)
