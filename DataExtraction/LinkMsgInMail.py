import requests

pageLinks = ['https://www.eclipse.org/lists/jdt-dev/threads.html']
defaultLink = 'https://www.eclipse.org/lists/jdt-dev/thrd'
FF = False

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
  if not(msgId in msgDex):
    nrNodes += 1
    if not node.find('li'):
      msgDex[msgId] = (str(node), nrNodes)
    else:
      msgDex[msgId] = (str(node.find('li')), nrNodes)
  
  nodeTuple = (msgId, msgDex[msgId][1])
  if (par[0] != nodeTuple[0]):
      addEdge(par, nodeTuple)
  if (not node.find('ul', recursive = False)):
    return nodeTuple
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
  print(len(BS.find_all('em')), nrNodes)
  

edgeFile.close()
