import requests
from datetime import datetime
from datetime import timedelta

pageLinks = ['https://www.eclipse.org/lists/jdt-dev/threads.html']
defaultLink = 'https://www.eclipse.org/lists/jdt-dev/thrd'

edgeFile = open("emailMsgEdges.txt", "w")
detailsFile = open("emailDetails.txt", "wb")
namesFile = open("emailNames.txt", "wb")

for i in range(2, 17):
  pageLinks.append(defaultLink + str(i) + '.html')

def getPageContent(pageLink):
  page = requests.get(pageLink)
  return page.content


from bs4 import BeautifulSoup, NavigableString, Tag, Comment

nrNodes = 0
msgDex = {}
msgDetails = {}

def CheckPage(pageBody):
  cnt = 0
  for child in pageBody:
    dfs(child, (-1, -1))
    cnt += 1

def addEdge(u, v):
   if u[0] != -1 and v[0] != -1:
     edgeFile.write(str(u[0]) + '/\\' + str(v[0]))
  

def dfs(node, par):
  global nrNodes
  if isinstance(node, NavigableString):
    return
  crtEm = node.find('em')
  msgId = node.find('a')['name']
  if msgId in msgDex:
    if str(node) != msgDex[msgId][0]:
      return
  else:
    nrNodes += 1
    if not node.find('li'):
      msgDex[msgId] = (str(node), nrNodes)
    else:
      msgDex[msgId] = (str(node.find('li')), nrNodes)
  
  nodeTuple = (msgId, msgDex[msgId][1])
  if (par[0] != nodeTuple[0]):
      addEdge(par, nodeTuple)
 
  relevantChildren = node.find('ul', recursive = False).find_all('li', recursive = False)
  for son in relevantChildren:
    childStr = str(son)
    sonNode = dfs(son, nodeTuple)    
  return nodeTuple

for pageLink in pageLinks:
  msgDex = {}
  nrNodes = 0
  BS = BeautifulSoup(getPageContent(pageLink), 'html.parser')
  CheckPage(BS.body)
  
  
detailsFile.close()
edgeFile.close()
