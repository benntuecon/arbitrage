# -*- coding: utf-8 -*-
"""
Created on Fri May 25 11:04:37 2018

@author: CHEN
"""
import os 
import time
from selenium import webdriver
from collections import deque
from price import Price
from login import login_MAX
import multiprocessing as mp
import queue
import datetime 
import requests

#price[x][y][z]==>   x=0是賣單價 x=1是買單價     y 是價格由好到壞的順序  z=0 是價格 z=1是量
def setup_driver(headless=False):    
    option=webdriver.ChromeOptions()
    
    prefs = {"profile.managed_default_content_settings.images":2} 
    option.add_experimental_option("prefs",prefs)    
    
    option.add_argument("--window-size=900,780")    
    driver = webdriver.Chrome(  executable_path=os.getcwd()+"\chromedriver.exe",options=option)    
    return driver


def price_load(coin:str):
    print("開始載入 %s 之瀏覽器"%coin)
    driver_for_max = setup_driver()
    TW=Price("TW",coin,driver_for_max)
    TW.update_price()
    driver_for_hitbtc = setup_driver()       
    US=Price("US",coin,driver_for_hitbtc)
    US.update_price()
    runtimes=0
    keep_arbitrage(US,TW,coin,runtimes)
    
    return 
   
    ##################################################### critical point############################## 
def arbitrage(US,TW,coin,runtimes,target_profit_rate=1.025,target_volume=20000):    
    try:
        profit_of_sell_coin_in_us=float(US.price_list[1][0][0])*30  / (float(TW.price_list[0][0][0]))        
        if profit_of_sell_coin_in_us>target_profit_rate:
            print("價格已達標，驗證量",coin,"profit= ", profit_of_sell_coin_in_us, "\n",US.price_list[1][0][0] ,TW.price_list[0][0][0] )
            buyside_volume =float(US.price_list[1][0][0])*30  * (float(US.price_list[1][0][1]))
            sellside_volume = float(TW.price_list[0][0][0]) *  float(TW.price_list[0][0][1])
            print("buyside volume     sellside volume\n",buyside_volume,sellside_volume)
            i=0
            while buyside_volume<target_volume:
                i+=1
                buyside_volume+=float(US.price_list[1][i][0])*30  * (float(US.price_list[1][i][1]))
                print("第%s 買方深度為%s"%(i,buyside_volume))
            j=0
            while sellside_volume<target_volume:
                print("第%s 賣方深度為%s"%(i,sellsside_volume))
                j+=1
                sellside_volume+=float(TW.price_list[0][i][0])  * (float(TW.price_list[0][i][1]))
            
            if (float(US.price_list[1][i][0])*30  / (float(TW.price_list[0][j][0])))>target_profit_rate-0.005:
                send_line(coin,
                            profit_of_sell_coin_in_us,
                            "HITBTC",
                            US.price_list[1][0],
                            TW.price_list[0][0]
                            )
                time.sleep(30)
       
        else:
            print("ROR of selling %s in us =  %s"%(coin, profit_of_sell_coin_in_us),TW.price_list[0][0],US.price_list[1][0])
            profit_of_sell_coin_in_tw=float(TW.price_list[1][0][0]) / (float(US.price_list[0][0][0])*30)
            if profit_of_sell_coin_in_tw>target_profit_rate:
                print("價格已達標，驗證量",coin,"profit= ", profit_of_sell_coin_in_tw, "\n",TW.price_list[1][0][0] ,US.price_list[0][0][0] )
                buyside_volume =float(TW.price_list[1][0][0]) * (float(TW.price_list[1][0][1]))
                print("台灣可買之深度為",TW.price_list[1][0][0]," * ",TW.price_list[1][0][1],"=",buyside_volume)
                sellside_volume = float(US.price_list[0][0][0])*30 *  float(US.price_list[0][0][1])
                print("美國可賣之深度為",US.price_list[0][0][0]," * 30 * ",US.price_list[0][0][1],"=",sellside_volume)
                i=0
                while buyside_volume<target_volume:
                    i+=1
                    buyside_volume+=float(TW.price_list[1][i][0]) * (float(TW.price_list[1][i][1]))
                j=0
                while sellside_volume<target_volume:
                    j+=1
                    sellside_volume+=float(US.price_list[0][j][0])*30 *  float(US.price_list[0][j][1])
                if (float(TW.price_list[1][i][0])  / (float(US.price_list[0][j][0])*30))>target_profit_rate-0.005:
                    send_line(coin,
                                profit_of_sell_coin_in_tw,
                                "MAX",
                                TW.price_list[1][0],
                                US.price_list[0][0]
                                )
                    time.sleep(30)
            else:    
                print("ROR of selling %s in tw =  %s"%(coin, profit_of_sell_coin_in_tw),TW.price_list[1][0],US.price_list[0][0])
                    
            ############################################################################################
            
            US.update_price()
            TW.update_price()
                
            
        
             

            
    except :
        pass
        
def keep_arbitrage(US,TW,coin,runtimes,target_profit_rate=1.025,target_volume=20000):
    runtimes=0
    while True:
        arbitrage(US,TW,coin,runtimes,target_profit_rate=1.025,target_volume=20000)
        time.sleep(3)
        runtimes+=1
        if runtimes%50==1:
            print(datetime.datetime.now(),coin ,"running well")
        if runtimes%500==0:
            send_line(s, coin,profit_of_sell_coin_in_tw,profit_of_sell_coin_in_us)
       



def send_line(coin:str, rate_of_return:float,  buy_at,buyside:list,sellside:list):
    date=datetime.datetime.now()
    token = "g73iZv83YPCFLvWlOPwITmToICDxUmY2vn7Q7mPd9sr"
    if not coin=="s":
        msg="TARGET:     %s\n Rate of return =    %s\n =============\n sellside  =  %s \n P and Q  =  %s \n buy at the oppsite= \n %s  "%(coin,rate_of_return,buy_at,buyside,sellside)
    else:
        msg="每500次運算 常規報價： \n %s在台灣賣之報酬：\n %s 在美國賣之報酬：\n %s"%(coin,rate_of_return,buy_at)
   
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    
    payload = {'message': msg}
    r = requests.post(url, headers = headers, params = payload)
    return r.status_code




def multi_arbitrage():
    print("setup pool")
    P=mp.Pool(processes=5)
    for x in ['mith','eth','ltc']:
        print(x,"    started")
        res=P.apply_async(price_load,(x,))


def fluctuation_notify(coin:str,exchange_name,Maxlen=120,amplitude=0.02):
    ring = deque(maxlen=Maxlen)
    
    driver_for_max = setup_driver()
    exchange=Price(exchange_name,coin,driver_for_max)
    exchange.update_price()
    new_value=float(exchange.price_list[1][0][0])
    ring.append(new_value)
    while True:
        new_value=float(exchange.price_list[1][0][0])
        top=max(ring)
        bottom=min(ring)
       
        if new_value<top*(1-amplitude):
            rate=(top-new_value)/top
            send_line_fluc(coin,exchange.host,amplitude,rate)      

        if new_value>bottom*(1+amplitude):
            rate=(bottom-new_value)/bottom
            send_line_fluc(coin,exchange.host,amplitude,rate)        
        ring.append(new_value)
        print("新增價格",coin,exchange.host,new_value)
        exchange.update_price()

def keep_fluc_noti():
    print("setup pool")
    P=mp.Pool(processes=6)
    for x in ['mith','eth','ltc']:
        for y in ['US','TW']:            
            print(x,y,"    started")
            res=P.apply_async(fluctuation_notify,(x,y,))


    
        

def send_line_fluc(coin:str,exchange,rate):
    date=datetime.datetime.now()
    token = "g73iZv83YPCFLvWlOPwITmToICDxUmY2vn7Q7mPd9sr"
    side="向上"if rate>0 else "向下"
    msg="%s 在 %s 有超過%s幅度的 %s波動 "%(coin,exchange,amp,side)   
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    
    payload = {'message': msg}
    r = requests.post(url, headers = headers, params = payload)
    return r.status_code

    

if __name__ == "__main__":
    #keep_fluc_noti()
    multi_arbitrage()
    #fluctuation_notify("eth","US")
    

    





    



    




