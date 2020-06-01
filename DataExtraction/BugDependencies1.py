import bugzilla

b = bugzilla.Bugzilla(url="https://bugs.eclipse.org/bugs/rest/", api_key="Hf6q2p8asdXNHe99brQpGZoeV6IRwCMhdn1v9gNP")

f = open("/content/BugDex2020.txt", "r")
g = open("/BugDependency.txt", "w")

while (True):
  crtL = f.readline()
  if not crtL:
    break
  lst = crtL.split()
  bug = b.get_bug(int(lst[0][2:-1]))
  g.write(lst[0][2:-1] + str(' ') + str(len(bug["depends_on"])) + '\n')
  g.write(str(bug["depends_on"]) + '\n')
  
  
f.close()
g.close()
