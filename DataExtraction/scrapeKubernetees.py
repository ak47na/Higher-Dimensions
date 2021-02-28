from selenium import webdriver


PATH = 'C:\Program Files\chromedriver.exe'

def navigatePagesAndGetData(pageLink):
    wd.get(pageLink)
    times = 1
    while times > 0:
        nextArrow = wd.find_elements_by_class_name('uArJ5e.Y5FYJe.cjq2Db.YLAhbd')[1]
        messages = wd.find_elements_by_class_name('uVccjd.aiSeRd.DQoTwe')
        for message in messages:
            print(message)
        nextArrow.click()
        times -= 1

wd = webdriver.Chrome(PATH)
pageLink = "https://groups.google.com/g/kubernetes-dev"
navigatePagesAndGetData(pageLink)
