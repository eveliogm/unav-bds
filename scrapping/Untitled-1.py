


def get_bound_box():
    timeout = time.time() +  60 * 2 # to mins timeout
    options = Options()
    # options.add_experimental_option("detach", True)
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options)
    url = "http://bboxfinder.com/#0.000000,0.000000,0.000000,0.000000"
    driver.get(url)
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    cont_w = True 
    while (cont_w and (time.time() < timeout)):
        if len(soup.find('span', attrs={'id':'boxbounds'}).contents) > 0:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            bbox = soup.find('span', attrs={'id':'boxbounds'}).contents[0]
            if bbox != '0.000000,0.000000,0.000000,0.000000':
                cont_w = False
    driver.close()
    return bbox