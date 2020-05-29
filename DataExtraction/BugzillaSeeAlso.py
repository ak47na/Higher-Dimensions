import bugzilla

b = bugzilla.Bugzilla(url="https://bugs.eclipse.org/bugs/rest/", api_key="Hf6q2p8asdXNHe99brQpGZoeV6IRwCMhdn1v9gNP")

f = open("/BugDex2020.txt", "r")
g = open("Bug2Gerrit.txt", "w")
while (True):
  crtL = f.readline()
  if not crtL:
    break
  lst = crtL.split()
  bug = b.get_bug(int(lst[0][2:-1]))
  g.write(lst[0][2:-1] + str(' ') + str(len(bug["see_also"])) + '\n')
  g.write(str(bug["see_also"]) + '\n')
  
f.close()
g.close()
