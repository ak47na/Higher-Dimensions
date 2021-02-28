import requests
from bs4 import BeautifulSoup

from selenium import webdriver

wd = webdriver.Chrome('C:\Program Files\chromedriver.exe')
msgDex = {}

def printMsgDex():
    print('Succesfull write dict')
    f = open('D:\AKwork2020-2021\Higher-Dimensions\GraphConstruction\Data\msgDictPerl.txt', 'w')
    for msg in msgDex:
        f.write(str(msg) + '/\\' + str(msgDex[msg][0]) + '/\\' + str(msgDex[msg][1]) + '\n')
    f.close()


def getMessageDetails():
    msgId = wd.current_url.rsplit('/')[-1][:-5]
    if msgId in msgDex:
        # The message has already been processed.
        return
    header = wd.find_elements_by_id("article_header")
    if (len(header) == 0):
        print('Some error with message page', wd.current_url)
        return
    msgSender = header[0].find_element_by_tag_name('b').text
    res = requests.get(wd.current_url).content
    soup = BeautifulSoup(res, 'html.parser')
    articleHeader = soup.find("div", {"id": "article_header"})
    if not articleHeader:
        print('The page is', wd.current_url, wd.page_source)
        exit()
    text = soup.find("div", {"id": "article_header"}).find_all(text=True)
    msgDate = ''
    canBeDate = False
    for textEl in text:
        if ('Date:' in textEl):
            canBeDate = True
        else:
            if canBeDate and len(textEl) > 3:
                msgDate = textEl
                break

    msgDex[msgId] = (msgSender, msgDate)

def findAllMsgDetails():
    ulElems = wd.find_elements_by_tag_name("ul")
    if len(ulElems) == 0:
        print('Some error with list of messages in page', wd.current_url)
        return
    msgs = wd.find_element_by_tag_name("ul").find_elements_by_tag_name('li')
    msgsLinks = []
    count = 0
    for msg in msgs:
        hasLink = msg.find_elements_by_tag_name('a')
        if (len(hasLink) == 0):
            #print('The message ', msg, msg.text, ' has no link!!')
            count += 1
            continue
        msgsLinks.append(hasLink[0].get_attribute('href'))
    assert count <= 1
    for msgLink in msgsLinks:
        wd.get(msgLink)
        getMessageDetails()


def dfs(msgSender, ulElem):
    allChildren = ulElem.find_elements_by_xpath("./*")
    sender = ''
    for child in allChildren:
        if child.tag_name == 'li':
            msgLink = child.find_elements_by_tag_name('a').get_attribute('href')
            # print(msgLink)


def getMessagesFromPage(url):
    wd.get(url)
    elems = wd.find_elements_by_tag_name("tr")
    messagesLinks = []
    for elem in elems:
        messageEl = elem.find_element_by_tag_name("td")
        messageLink = messageEl.find_element_by_tag_name("a")
        messagesLinks.append(messageLink.get_attribute("href"))

    for messageLink in messagesLinks:
        wd.get(messageLink)
        getMessageDetails()
        findAllMsgDetails()
        # msgSender = wd.find_element_by_id("article_header").find_element_by_tag_name('b').text
        # dfs(msgSender, ulElem)

    # print(len(elem))

def accessUrl(url):
  print(url)
  wd.get(url)
  pElems = wd.find_elements_by_tag_name("p")
  assert (len(pElems) <= 4)
  getMessagesFromPage(url)
  if (len(pElems) == 4):
      #The page has multiple pages.
      pages = pElems[1].find_elements_by_tag_name("a")
      assert len(pages) > 0
      lastPage = int(pages[-2].text)
      for page in range(2, lastPage + 1):
          pageLink = url[:-5] + '/page' + str(page) + '.html'
          print(pageLink)
          getMessagesFromPage(pageLink)


pageLink = 'https://www.nntp.perl.org/group/perl.perl5.porters/'
for year in range(1999, 2003):
  for month in range(1, 13):
    if year == 2021 and month == 3:
      break
    if year == 1999 and month < 9:
        continue
    monthStr = str(month)
    if month < 10:
        monthStr = '0' + monthStr
    url = pageLink + str(year) + '/' + monthStr +'.html'
    accessUrl(url)

printMsgDex()

