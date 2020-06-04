import requests

pref = 'https://www.eclipse.org/lists/jdt-dev/msg'
pageLinks = ['https://www.eclipse.org/lists/jdt-dev/threads.html']
defaultLink = 'https://www.eclipse.org/lists/jdt-dev/thrd'
detailsFile = open("details.txt", "wb")
errorFile = open("errors.txt", "wb")
edgeFile = open("msgEdges.txt", "w")
for i in range(2, 17):
  pageLinks.append(defaultLink + str(i) + '.html')

def getPageContent(pageLink):
  page = requests.get(pageLink)
  return page.content


from bs4 import BeautifulSoup, NavigableString, Tag

nrNodes = 0
msgDex = {}

def CheckPage(pageBody):
  global nrNodes
  allLists = pageBody.find_all('li')
  for lst in allLists:
    Link = lst.find('a')
    if Link and ('msg' in Link['href']):
      msg = Link['name']
      if not(msg in msgDex):
        nrNodes += 1
        msgDex[msg] = (lst.find('em'), nrNodes)
      else:
        if (msgDex[msg][0] != lst.find('em')):
          print(msgDex[msg], lst.find('em'))
          msgDex[msg] = (lst.find('em'), msgDex[msg][1])
        print(msgDex[msg], lst.find('em'))
      
  print(len(pageBody.find_all('em')), nrNodes)

def addEdge(u, v):
   if u[0] != -1 and v[0] != -1:
     edgeFile.write(str(u[0]) + '/\\' + str(v[0]))

for pageLink in pageLinks:
  msgDex = {}
  nrNodes = 0
  BS = BeautifulSoup(getPageContent(pageLink), 'html.parser')
  CheckPage(BS.body)
  
  
for key in msgDex:
  #print(pref + key + '.html') 
  BSi = BeautifulSoup(getPageContent(pref + key + '.html'), 'html.parser')
  #print(BSi.find_all(text=lambda text: (isinstance(text, Comment)) and 'X-Date' in text))
  allLists = BSi.find_all('li')
  cnt = 0
  msgDetails[key] = {}
  for lst in allLists:
    Em = lst.find('em')
    if Em:
      Em = str(Em)
      if ('Date' in Em):
        msgDetails[key]['date'] = getDateFromList(str(lst))
        cnt += 1
      elif ('From' in Em):
        strList = str(lst)
        msgDetails[key]['name'] = ''
        if (' &lt;' in strList):
          msgDetails[key]['name'] = getNameFromList(str(strList))
        msgDetails[key]['email'] = getIDFromEmail(lst.find('a')['href'])
        cnt += 1
    if cnt == 2:
      break
  if not 'email' in msgDetails[key]:
    print(key)
  else:
    detailsFile.write((str(msgDetails[key]['name']) +'/\\' + str(msgDetails[key]['email']) + '/\\' + str(msgDetails[key]['date']) + '\n').encode())

detailsFile.close()
errorFile.close()
edgeFile.close()
