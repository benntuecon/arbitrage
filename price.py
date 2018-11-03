class Price:
    def __init__(self,host="TW", coin="btc", driver=object()):
        self.host=host
        self.coin=coin   
        self.driver=driver
        self.price_list=[[],[]]       
        if self.host=="TW":            
            self.driver.get("https://max.maicoin.com/markets/%stwd"%(self.coin.lower()))
            self.driver.implicitly_wait(1000)
        elif self.host=="US":                       
            self.driver.get("https://hitbtc.com/exchange/%s-to-USDT"%(self.coin.upper()))
            self.driver.implicitly_wait(1000)
    def update_price(self):
        self.price_list=[[],[]]
        if self.host=="TW":
            MAX_ask = self.driver.find_elements_by_css_selector(r"#order_book_body > div:nth-child(2) > table > tbody > tr")
            MAX_bid = self.driver.find_elements_by_css_selector(r"#order_book_body > div.col-xs-12.col-left > table > tbody > tr")      
            for x in MAX_ask:
                self.price_list[0].append([x.get_attribute("data-price"),
                             x.get_attribute("data-volume")])      
            
            for x in MAX_bid:
                self.price_list[1].append([x.get_attribute("data-price"),
                                 x.get_attribute("data-volume")])
         
        elif self.host=="US":                  
            
            HITBTC_ask = self.driver.find_elements_by_css_selector(
                        r"div.orderBook__containerSell > table > tbody > tr")
            HITBTC_bid = self.driver.find_elements_by_css_selector(
                        r"div.orderBook__containerBuy > table > tbody > tr")      
            if not (HITBTC_ask!=[] and HITBTC_bid!=[]):                
                self.driver.implicitly_wait(1000)
                print("reload elements list")            
            for x in range(len(HITBTC_ask)):
                Y=HITBTC_ask[x].text.split("\n")
                self.price_list[0].append([Y[0],Y[1]])
            for x in range(len(HITBTC_bid)):
                Y=HITBTC_bid[x].text.split("\n")
                self.price_list[1].append([Y[2],Y[1]]) 
        return
    def price_load(coin:str,target_profit_rate=1.07,target_volume=20000):
        print("開始載入 %s 之瀏覽器"%coin)
        driver_for_max = setup_driver()
        TW=Price("TW",coin,driver_for_max)
        TW.update_price()
        driver_for_hitbtc = setup_driver()       
        US=Price("US",coin,driver_for_hitbtc)
        US.update_price()    
        return 
    def test(self):
        self.driver.get("https://hitbtc.com/exchange/%s-to-USDT"%(self.coin.upper()))
        print('page loaded')
        self.driver.implicitly_wait(500)
        print('elements now loading')
        HITBTC_ask = self.driver.find_elements_by_css_selector(
                    r"div.orderBook__containerSell > table > tbody > tr")
        HITBTC_bid = self.driver.find_elements_by_css_selector(
                    r"div.orderBook__containerBuy > table > tbody > tr")      
        print('elements list connected')
        while HITBTC_ask==[]  :
            self.driver.implicitly_wait(1000)
            HITBTC_ask = self.driver.find_elements_by_css_selector(
                    r"div.orderBook__containerSell > table > tbody > tr")
            print("still loading..")
        print("ask list done")
        while HITBTC_bid==[]  :
            self.driver.implicitly_wait(1000)
            HITBTC_bid = self.driver.find_elements_by_css_selector(
                    r"div.orderBook__containerBuy > table > tbody > tr")
            print("still loading..")
        print("bid list done")
        for x in range(1,10):
            Y=HITBTC_ask[x].text.split("\n")
            print(Y[0],Y[1])
    """description of class"""

#price[x][y][z]==>   x=0是賣單價 x=是買單價     y 是價格由好到壞的順序  z=0 是價格 z=1是量