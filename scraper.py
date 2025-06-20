from bs4 import BeautifulSoup
import requests
import pandas as pd
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
url=input("Enter the URL: ")
page=requests.get(url,headers=headers)
data = []
soup = BeautifulSoup(page.text,'html.parser')
list_header = []
header = soup.find_all("table")[4].find("tr")
for items in header:
    try:
        list_header.append(items.get_text())
    except:
        continue
del list_header[6:]
HTML_data = soup.find_all("table")[4].find_all("tr")[1:]
for element in HTML_data:
    sub_data = []
    x=0
    for sub_element in element:
        try:
            if x != 9:
                sub_data.append(sub_element.get_text())
                x+=1
            else:
                x=0
                break
        except:
            continue
    sub_data.pop()
    del sub_data[-2:]
    data.append(sub_data)
del data[0:2]
dft = pd.DataFrame(data = data, columns = list_header)
dft.iloc[0,0]="Promoter"
dft.iloc[1,0]="Public"
dft.iloc[2,0]="Others"
dft.iloc[3,0]="Others"
dft.iloc[4,0]="Others"
df= dft[['Category of shareholder', 'No. of shareholders', 'Total no. shares held', 'Shareholding as a % of total no. of shares (calculated as per SCRR, 1957)As a % of (A+B+C2)']]
name= url.split('=')[1].split('&')[0]+'.csv'
df.to_csv(name)
