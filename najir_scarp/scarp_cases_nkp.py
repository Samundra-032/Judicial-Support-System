import requests
from bs4 import BeautifulSoup

import warnings
warnings.filterwarnings('ignore')

notdownloads = []

def textFromRequest(req, fileName):
    soup = BeautifulSoup(req.content, "html.parser")
    try:
        res = soup.article.div(id="faisala_detail ")[0]
        title = soup.find_all("div", id="decision_summary")[0].h1.text
        try:
            name = "cases/"+str(title)+'.txt'.replace("/","-")
            f = open(name, 'wt')
            f.write(res.text)
            f.close()
        except AttributeError:
            print(fileName)
            pass
    except:
        print(fileName)
        notdownloads.append(fileName)
        pass 

for index in range(2,9):
    req = requests.get("https://nkp.gov.np/full_detail/0"+str(index), verify=False)
    title = "case_0"+str(index)
    textFromRequest(req=req, fileName=title)
    
for index in range(10, 10078):
    req = requests.get("https://nkp.gov.np/full_detail/"+str(index), verify=False)
    title = "case_"+str(index)
    textFromRequest(req=req, fileName=title)