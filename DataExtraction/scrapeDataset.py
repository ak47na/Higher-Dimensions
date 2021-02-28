import requests

from selenium import webdriver

wd = webdriver.Chrome('C:\Program Files\chromedriver.exe')

def accessUrl(url):
  wd.get(url)
  count = 0
  elems = wd.find_elements_by_xpath("//*[text()='View mode: ']")
  options = wd.find_elements_by_tag("option")
  print(options)
  for elem in elems:
      print(elem)
      count += 1
  print(count)
  exit()
  wd.close()

  exit()
  # all_options = selectorView.find_elements_by_tag_name("option")
  # for option in all_options:
  #   print(option)
  # print(selectorView)

pageLink = 'https://lists.apache.org/list.html?dev@cassandra.apache.org:'
for year in range(2009, 2022):
  for month in range(2, 13):
    if year == 2021 and month == 3:
      break
    url = pageLink + str(year) + '-' + str(month)
    accessUrl(url)
    if year == 2010:
      exit()
