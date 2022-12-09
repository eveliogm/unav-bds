from typing import List
import pandas as pd
import requests
import urllib
import bs4
from bs4 import BeautifulSoup

class CookieError(Exception):
    pass


GOOGLE_COOKIE_CHECK = ["h1","Uo8X3b OhScic zsYMMe"]
STACKOVERFLOW_COOKIE_CHECK = ["div","answer"]


def error_encode_url(error:str):
    '''
    It takes a string, encodes it, and returns a url
    
    Parameters
    ----------
    error : str
        The error message that you want to search for.
    
    Returns
    -------
        A string that is a url that will search stackoverflow.com for the error in google.
    
    '''
    base_search = "https://www.google.com/search?q="
    web = "stackoverflow.com"
    search = urllib.parse.quote_plus(f'{web} {error}')
    url_base = f'{base_search}{search}'
    return url_base

def get_html_search(query: str):
    '''
    It takes a query string and returns the HTML of the page
    
    Parameters
    ----------
    query : str
        The URL of the website you want to scrape.
    
    Returns
    -------
        A string with the html
    '''
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36', 'Upgrade-Insecure-Requests': '1', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate', 'Cookie':'CONSENT=YES+cb.20210418-17-p0.it+FX+917; '}
    # headers = ""

    res = requests.get(query,headers=headers)
    if res.status_code != 200:
        raise requests.exceptions.RequestException("Cannot procceed only works with 200 status code in response")
    return res

def check_html_mal(soup):
    """
    MALA Solo para sirve para ver el ejemlpo de como ha evolucionado:
    me comlique mucho
    """
    ret = True
    common_button = ["Accept all", "Reject all","Rechazar todo","Aceptar todo"]
    common_title = ['Antes de ir a Google', 'Before you continue to Google']
    title_res = soup.find_all("h1")
    title_str = title_res[0].contents[0]
    button_res = soup.find_all("input",attrs={'class':'basebutton'})

    for b in button_res:
        if b.get_attribute_list("value")[0] in common_button:
            ret = False
    if title_str in common_title:
            ret = False
    return ret 

def is_valid_html(soup:bs4.BeautifulSoup, config:List[str]):
    '''
    This function takes a BeautifulSoup object and a list of two strings as input, and returns True if
    the BeautifulSoup object contains a tag with the name of the first string and the class of the
    second string
    
    Parameters
    ----------
    soup : bs4.BeautifulSoup
        the BeautifulSoup object
    config : List[str]
        a list of strings, where the first string is the tag name and the second string is the class name
    
    Returns
    -------
        A boolean value.
    
    '''
    ret = False
    search_result = soup.find_all(config[0],attrs={'class':config[1]})
    if len(search_result)>0:
        ret = True
    return ret

def parse_html(html: str,config: List[str]):
    '''
    It takes the html of the page and the config list with two string, checks a validation of it there is any cookie 
    problem and returns a BeautifulSoup object
    
    Parameters
    ----------
    html : str
        The HTML of the page you want to parse.
    config : List[str]
        list of strings with configuration of cookie validation proccess
    
    Returns
    -------
        A BeautifulSoup object
    
    '''
    soup = BeautifulSoup(html, 'html.parser')
    if not(is_valid_html(soup,config)):
        raise CookieError("Check the headers of the request, it seems google has update some required fields or its values")
    return soup

def get_search_urls(soup:bs4.BeautifulSoup): 
    '''
    It takes a BeautifulSoup object and returns a list of urls that are in the stackoverflow site
    
    Parameters
    ----------
    soup : bs4.BeautifulSoup
        the BeautifulSoup object that contains the HTML of the page
    
    Returns
    -------
        A list of urls that are in the stackoverflow site
    
    '''
    
    #find all div that have MjjYud == search results class in google search 
    results = soup.find_all('div', attrs={'class':'MjjYud'})

    urls = []
    for result in results:
        #find the first a that contains the href with the url of the solution
        res = result.find("a")
        #Check if the url is in the stackoverflow site
        if "https://stackoverflow.com" in res.attrs["href"]:
            urls.append(res.attrs["href"])
        
    return urls


def get_answers(url:str):
    '''
    It takes a url, gets the html, parses it, finds all the answers, and returns a dataframe with the
    answers
    
    Parameters
    ----------
    url : str
        The url of the question you want to get the answers for.
    
    Returns
    -------
        A dataframe with the following columns:
        votes: number of votes for the answer
        time: time of the answer
        user_name: name of the user who answered
        user_rank: rank of the user who answered
        answer_html: html of the answer
    
    '''
    res = get_html_search(url)
    soup_r = parse_html(res.text,STACKOVERFLOW_COOKIE_CHECK)
    answers = soup_r.find_all('div', attrs={'class':'answer'})
    df = pd.DataFrame({},columns = ["votes","time","answer_html","user_name","user_rank"])

    for answer in answers:
        votes = answer.find('div', attrs={'class':'js-vote-count'})
        exp = answer.find('div', attrs={'class':'s-prose'})
        time = answer.find('div', attrs={'class':'user-action-time'}).find('span', attrs={'class':'relativetime'}).attrs["title"]
        usr_name = answer.find('div', attrs={'class':'user-details'}).find('a').contents[0]
        usr_rank = answer.find('div', attrs={'class':'user-details'}).find('span', attrs={'class':'reputation-score'}).contents[0]
        ans = {'votes': [int(votes.attrs["data-value"])],
               'time': [time],
               'user_name':[usr_name],
               'user_rank':[usr_rank],
               'answer_html': [exp.prettify()]
              }
        df = pd.concat([df, pd.DataFrame(ans)])
    return df

def most_rated_answer(df:pd.DataFrame,sort_by:str):
    '''
    The function takes in a dataframe and a string, and returns the first row of the dataframe sorted
    by the column specified by the string
    
    Parameters
    ----------
    df : pd.DataFrame
        The dataframe that contains the data
    sort_by : str
        "ans" or "ques"
    
    Returns
    -------
        A dataframe with the most rated answer
    '''
    
    if sort_by == "ans":
        df = df.sort_values("votes").reset_index(drop = True)
    
    return df.iloc[[0]]




# # get Stack Overflow Stunning help
# def get_SOS_help(command):
    
#     url = error_encode_url() # TODO encode error str to urlencode
#     get_html_search() # TODO get html with request 
#     parse_html() # parse html with beautiful
#     get_search_classes() # get each search result and check if url start with stack.overflow.com
#     get_first_result_url() #  get_first_result os previous results
#     get_most_rated_answer() # TODO
#     open_chrome_with_url() # Open chrome with previus url
    
#     try:
#         exec(command)
        
#     except:
#         print(stack_overflow_first_link)
#         print(stack_overflow_most_voted_help)
#         prompt_web(stack_overflow_first_link)
#     return