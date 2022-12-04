import sys
#sys.path.append('C:\\Users\\pablo\\OneDrive\\UNAV\\Local_Deployment')
#sys.path.append('C:\\Users\\pablo\\Anaconda3\\Lib\\site-packages')
#sys.path.append('C:\\Users\\pablo\\Anaconda3\\lib')

print(sys.path)
'''
from pip._internal import main as pipmain
pipmain(['install', "--user", "--upgrade", 'pip'])
pipmain(['install', "--user", 'azure-storage-blob==2.1.0'])
pipmain(['install', "--user", 'requests'])
pipmain(['install', "--user", 'pandas'])
pipmain(['install', "--user", '--upgrade', 'pandas'])
pipmain(['install', "--user", 'bs4'])
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd

from io import StringIO
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings

def blob_to_container(container_name, file_name):
    blockblob_service.create_blob_from_path(
        container_name, #container1/folder1/folder1
        file_name, #blob name
        file_name, #blob to upload from local
        content_settings=ContentSettings(content_type='application/CSV')
                )

r = requests.get('https://www.nytimes.com/interactive/2017/06/23/opinion/trumps-lies.html')
soup = BeautifulSoup(r.text, 'html.parser')

results = soup.find_all('span', attrs={'class':'short-desc'})
records = []
for result in results:
    date = result.find('strong').text[0:-1] + ', 2017'
    lie = result.contents[1][1:-2]
    explanation = result.find('a').text[1:-1]
    url = result.find('a')['href']
    records.append((date, lie, explanation, url))
    
df = pd.DataFrame(records, columns=['date', 'lie', 'explanation', 'url'])

p_account_name = 'YOUR_STORAGE_ACCOUNT_NAME_HERE'
p_account_key =  'YOUR_STORAGE_ACCOUNT_KEY_HERE'
blockblob_service = BlockBlobService(account_name = p_account_name, account_key = p_account_key)

file_name = 'pruebas.csv'
df.to_csv(file_name,  header = False, sep= ',', encoding = 'utf-8', index = False)
blob_to_container(container_name = 'landing/file1', file_name = file_name)