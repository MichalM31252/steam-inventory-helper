import requests
import time
import datetime
import praw
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import mysql.connector

#patch notes
# - liczenie czy title nie przekracza 300 znaków
# - usuwanie przedmiotów z bazy danych jeżeli nie ma ich w ekwipunku podczas wymiany
# - naprawienie reklamy na steam z naklejkami 
# - usunięcie niepotrzebnych spacji w reklamie steam
# - usunięcie niepotrzebnych bibliotek 



mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="przedmioty_cs"
)

mycursor = mydb.cursor(buffered=True)

session = requests.Session()

def get_title_reddit(x, y, title_list, Want_reddit):
    global title_reddit
    Have = str(x) + " items worth around: " + str(y) + "$"
    baza = "[H] " + Have + "(" + ")" + " [W] " + Want_reddit
    title_string = ''.join(title_list)
    title_reddit = "[H] " + Have + "(" + title_string, ")" + " [W] " + Want_reddit #nie zmieniaj
    title_reddit = ''.join(title_reddit)
    if(len(title_reddit) > 300): 
        pom_list = []
        for element in title_list:
            if(len(baza) + len(element) + 2 > 300):
                pom_string = "".join(pom_list)
                title_reddit = "[H] " + Have + "(" + pom_string + ")" + " [W] " + Want_reddit #nie zmieniaj
                title_reddit = ''.join(title_reddit)
            else:
                pom_list.append(element)

class CSGO_item():
    def __init__(self,item_id,market_hash_name,market_hash_name_short,market_hash_name_shorter,price,inspect_link,sticker_list,sticker_1,sticker_2,sticker_3,sticker_4,sticker_5,has_expensive_stickers,screenshot,screenshot_requestId,item_float,exterior,tradeable,tradeable_date):
        self.item_id = item_id
        self.market_hash_name = market_hash_name
        self.market_hash_name_short = market_hash_name_short
        self.market_hash_name_shorter = market_hash_name_shorter
        self.price = price
        self.inspect_link = inspect_link
        self.sticker_list = sticker_list
        self.sticker_1 = sticker_1
        self.sticker_2 = sticker_2
        self.sticker_3 = sticker_3
        self.sticker_4 = sticker_4
        self.sticker_5 = sticker_5
        self.has_expensive_stickers = has_expensive_stickers
        self.screenshot = screenshot
        self.screenshot_requestId = screenshot_requestId
        self.item_float = item_float
        self.exterior = exterior
        self.tradeable = tradeable
        self.tradeable_date = tradeable_date

    def screenshot_post(self,inspect_link):
        url = "https://market-api.swap.gg/v1/screenshot"
        data = {
        'limit': 25,
        "inspectLink": self.inspect_link
        } 
        headers = {
            'content-type': 'application/json',
            'Authorization': '441c4839-be5b-4731-8710-781d761d804a' #bardzo możliwe, że to powinno być w auth header
        }
        response_screenshot = session.post(url=url, json=data, headers=headers) # dorób time.sleep(5)
        if(response_screenshot.json()['status'] == "OK"):
            print(response_screenshot.json())
            if(response_screenshot.json()['result']["state"] == "COMPLETED"):
                self.screenshot = response_screenshot.json()['result']["imageLink"]
                self.item_float = str(response_screenshot.json()['result']["itemInfo"]["floatvalue"])[:9] #usuń pobieranie tylko 8 pierwszych znakow

                mycursor.execute("INSERT INTO items (item_id, market_hash_name, market_hash_name_short, market_hash_name_shorter, price, inspect_link, has_expensive_stickers, exterior, item_float, screenshot, tradeable, tradeable_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (objekt.item_id, objekt.market_hash_name, objekt.market_hash_name_short, objekt.market_hash_name_shorter, objekt.price, objekt.inspect_link, objekt.has_expensive_stickers, objekt.exterior, objekt.item_float, objekt.screenshot, objekt.tradeable, objekt.tradeable_date))
                mydb.commit() 

                stickers = response_screenshot.json()['result']["itemInfo"]["stickers"]
                if stickers:
                    if(len(stickers) >= 1):
                        objekt.sticker_1 = response_screenshot.json()['result']["itemInfo"]["stickers"][0]["name"]
                        if(len(stickers) >= 2):
                            objekt.sticker_2 = response_screenshot.json()['result']["itemInfo"]["stickers"][1]["name"]
                            if(len(stickers) >= 3):
                                objekt.sticker_3 = response_screenshot.json()['result']["itemInfo"]["stickers"][2]["name"]
                                if(len(stickers) >= 4):
                                    objekt.sticker_4 = response_screenshot.json()['result']["itemInfo"]["stickers"][3]["name"]
                                    if(len(stickers) >= 5):
                                        objekt.sticker_5 = response_screenshot.json()['result']["itemInfo"]["stickers"][4]["name"]

                    mycursor.execute("INSERT INTO stickers_applied (item_id, sticker_1, sticker_2, sticker_3, sticker_4, sticker_5) VALUES (%s, %s, %s, %s, %s, %s)", (objekt.item_id, objekt.sticker_1, objekt.sticker_2, objekt.sticker_3, objekt.sticker_4, objekt.sticker_5))
                    mydb.commit()

                print("melon")
                #for sticker in stickers:
                    #val3.append(sticker)
            elif(response_screenshot.json()['result']["state"] == "IN_QUEUE"):
                print("IN_QUEUE \n")
                time.sleep(180)
                self.screenshot_post(inspect_link)
            elif(response_screenshot.json()['result']["state"] == "FAILED"):
                print("FAILED \n")              
            elif(response_screenshot.json()['result']["state"] == "ERROR"):
                print("error")
                time.sleep(300)  #program na discordzie ktory mnie pinguje## #############################################################
                self.screenshot_post(inspect_link)
            time.sleep(3)
val = []
black_list = []
normal_text = []
sticker_normal_text = []
prices_list = []
title_list = []
reddit_text = ""
objekty = {}
duplicates = []
banned_words = ["G2A"]
id_list = []

url = "http://steamcommunity.com/profiles/76561198231636540/inventory/json/730/2"

steamid = 76561198231636540

params = {
    'l': 'english',
    'key': '492EE6A0BD7968AFE46FEC5CCC84666D',
    'steamid': steamid
}    

r = requests.get(url=url, params=params)

paczka_json = r.json()
print(paczka_json)

try:
    success = str(paczka_json["success"])
except TypeError:
    print("Występują problemy z api steama. Spróbuj ponownie poźniej")
    raise SystemExit(0)

paczka_inv_dict = paczka_json["rgInventory"]

paczka_des_dict = paczka_json["rgDescriptions"]

paczka_inv_list = list(paczka_inv_dict)

paczka_des_list = list(paczka_des_dict)

if(success == "True"): # pokazuje czy poprawnie wykonano zapytanie
    print("Wykonano poprawne zapytanie")
else:
    print("Wykonano nie poprawne zapytanie")  #Zrób tu powiadomienie na telefon
    raise SystemExit(0)

print("\n \n")

go = 0
j = 0
i = 0
x = 0
y = 0
many = False

for element1 in paczka_inv_dict:
    sticker_list = []
    screenshot = "This item is too cheap"
    item_float = "This item is too cheap"
    tradeable_date = ""
    has_expensive_stickers = 0
    price = 0
    sticker_1 = ""
    sticker_2 = ""
    sticker_3 = ""
    sticker_4 = ""
    sticker_5 = ""

    class_id_inv = paczka_inv_dict[element1]['classid']
    instance_id_inv = paczka_inv_dict[element1]['instanceid']
    item_id = paczka_inv_dict[element1]['id']
    

    for element2 in paczka_des_dict:
        item_type = paczka_des_dict[element2]['tags'][0]['name']
        if(item_type == "Container" or item_type == "Sticker" or item_type == "Agent" or item_type == "Collectible" or item_type == "Tool" or item_type == "Music Kit"):
            continue
            
        if(item_type == "Rifle" or item_type == "Pistol" or item_type == "SMG" or item_type == "Sniper Rifle" or item_type == "Gloves" or item_type == "Knife"):
            class_id_des = paczka_des_dict[element2]['classid']
            instance_id_des = paczka_des_dict[element2]['instanceid']

            if(class_id_inv == class_id_des and instance_id_inv == instance_id_des):

                id_list.append(tuple((item_id,)))

                name = paczka_des_dict[element2]['name']
                market_hash_name = paczka_des_dict[element2]['market_hash_name']
                market_hash_name_short = market_hash_name.replace(' | ',' ')

                print(item_id,"\n")
                val_pom = (item_id,)
                print(val_pom,"\n")
                val.append(val_pom,)
                print(val,"\n")

                mycursor.execute("SELECT item_id, COUNT(*) FROM items WHERE item_id = %s GROUP BY item_id", (item_id,)) ######
                mycursor.fetchall()
                row_count = mycursor.rowcount ######
                if(row_count == 1):
                    print("continue")
                    continue
                
                if(market_hash_name not in black_list):

                    market_hash_name_shorter = market_hash_name_short.replace("(Factory New)","FN")
                    market_hash_name_shorter = market_hash_name_shorter.replace("(Minimal Wear)","MW")
                    market_hash_name_shorter = market_hash_name_shorter.replace("(Field-Tested)","FT")
                    market_hash_name_shorter = market_hash_name_shorter.replace("(Well-Worn)","WW")
                    market_hash_name_shorter = market_hash_name_shorter.replace("(Battle-Scarred)","BS")
                    market_hash_name_shorter = market_hash_name_shorter.replace("StatTrak\u2122","ST")

                    inspectlink_alfa = paczka_des_dict[element2]['actions'][0]['link']
                    print(inspectlink_alfa)
                    inspectlink_beta = inspectlink_alfa.replace('%owner_steamid%',str(steamid))
                    inspectlink_gamma = inspectlink_beta.replace(" ", "%20")
                    inspect_link = inspectlink_gamma.replace('%assetid%',str(element1))
                    print(inspect_link)

                    tradeable = paczka_des_dict[element2]['tradable'] 
                    if('cache_expiration' in paczka_des_dict[element2]):
                        cache_expiration = paczka_des_dict[element2]['cache_expiration']
                        tradeable_date = datetime.datetime.strptime(cache_expiration,"%Y-%m-%dT%H:%M:%SZ")

                    if('cache_expiration' not in paczka_des_dict[element2]):
                        tradeable = paczka_des_dict[element2]['tradable']  
                        tradeable_date = ""             
                    
                    descriptions_length = len(paczka_des_dict[element2]['descriptions'])
                    sticker_response = paczka_des_dict[element2]['descriptions'][descriptions_length-1]['value'] #to jest string napewno
                    exterior = paczka_des_dict[element2]['tags'][5]['name']

                    mycursor.execute("SELECT name FROM stickers",)
                    myresult = mycursor.fetchall() 
                    print(myresult)
                    for lista in myresult:
                        for element in lista:
                            if(element in sticker_response):
                                sticker_list.append(element)
                                has_expensive_stickers = 1
                    
                    marketable = paczka_des_dict[element2]['marketable']
                    if(marketable==1):
                        time.sleep(3)
                        url = "https://steamcommunity.com/market/priceoverview/"
                        params = {
                            'currency': 1,
                            'appid': 730,
                            'market_hash_name': market_hash_name
                        } 
                        s = requests.get(url=url, params=params)
                        cena_json = s.json()
                        if(cena_json['success'] == True):
                            try:
                                cena = cena_json["median_price"].replace("$","")
                                price = round(float(cena),2)
                            except:
                                cena = cena_json["lowest_price"].replace("$","")
                                price = round(float(cena),2)
                            
                        elif(cena_json['success'] == False):
                            print("Nie udalo sie pobrac ceny")
                            pass
                            
                        time.sleep(4)

                        screenshot_requestId = ""
                        if(market_hash_name in objekty.keys()):
                            objekty[market_hash_name].append(CSGO_item(item_id, market_hash_name, market_hash_name_short, market_hash_name_shorter, price, inspect_link, sticker_list, sticker_1, sticker_2, sticker_3, sticker_4, sticker_5, has_expensive_stickers, screenshot, screenshot_requestId, item_float, exterior, tradeable, tradeable_date))
                            break
                        objekty[market_hash_name] = [CSGO_item(item_id, market_hash_name, market_hash_name_short, market_hash_name_shorter, price, inspect_link, sticker_list, sticker_1, sticker_2, sticker_3, sticker_4, sticker_5, has_expensive_stickers, screenshot, screenshot_requestId, item_float, exterior, tradeable, tradeable_date)]         

for name, lista_obj in objekty.items():
    for objekt in lista_obj:
        objekt.screenshot_post(objekt.inspect_link)

mycursor.execute("SELECT `item_id` FROM items",)
myresult = mycursor.fetchall() 
for element in myresult:
    if element not in id_list:
        mycursor.execute("DELETE FROM items WHERE item_id = %s", element)
        mydb.commit()

mycursor.execute("SELECT `market_hash_name` FROM items WHERE has_expensive_stickers = 0 AND price > 1 AND tradeable = 1 ORDER BY price ASC",)
myresult = mycursor.fetchall() 
print(myresult)
print(set(myresult))
if(len(myresult) != len(set(myresult))):
    many = True
    print("many = True")

if(many == True):
    reddit_text = "Amount | Market Name | Float | Screenshot | Inspectlink | \n :--|:--:|:--:|:--:|--: \n"
if(many == False):
    reddit_text = "Market Name | Float | Screenshot | Inspectlink | \n :--|:--:|:--:|:--:|--: \n"
        
melon = 0
mycursor.execute("SELECT *, count(market_hash_name) as name_count FROM items WHERE has_expensive_stickers = 0 AND tradeable = 1 GROUP BY market_hash_name having name_count = 1 ORDER BY price ASC",)
myresult = mycursor.fetchall() 
for xyz in myresult:
    print(xyz[0]) #item_id
    print(xyz[1]) #market_hash_name
    print(xyz[2]) #market_hash_name_short
    print(xyz[3]) #market_hash_name_shorter
    print(xyz[4]) #price 
    print(xyz[5]) #inspect_link 
    print(xyz[6]) #has_expensive_stickers
    print(xyz[7]) #exterior
    print(xyz[8]) #item_float
    print(xyz[9]) #screenshot
    print(xyz[10])#tradeable
    print(xyz[11])#tradeable_date
    print(xyz[12])#itemcount
    print("")

    y += xyz[4]
    x += 1
    if(many == True):
        reddit_text += str(xyz[12]) + "x | " + xyz[2] + " | " + str(xyz[8]) + " | [screenshot](" + xyz[9] + ") | [inspectlink](" + xyz[5] + ") \n"
        normal_text.append("[H] " + str(xyz[12]) + "x " +  xyz[3] + " \n")
    if(many == False):
        reddit_text += xyz[2] + " | " + str(xyz[8]) + " | [screenshot](" + xyz[9] + ") | [inspectlink](" + xyz[5] + ") \n"
        normal_text.append("[H] " + xyz[3] + " \n")

    if(melon == 0):
        if(xyz[12] == 1):
            title_list.append(xyz[3])
        if(xyz[12] != 1):
            title_list.append(xyz[12] + "x " + xyz[3])

    if(melon != 0):
        if(xyz[12] == 1):
            title_list.append(", " + xyz[3])
        if(xyz[12] != 1):
            title_list.append(xyz[12] + "x " + xyz[3])
            
    melon += 1

expensive_stickers = mycursor.execute("SELECT name FROM stickers",)
stickers_a = mycursor.fetchall() 
mycursor.execute("SELECT stickers_applied.sticker_1, stickers_applied.sticker_2, stickers_applied.sticker_3, stickers_applied.sticker_4, stickers_applied.sticker_5, items.market_hash_name_shorter FROM stickers_applied JOIN items ON (stickers_applied.item_id = items.item_id AND items.has_expensive_stickers = 1 AND items.tradeable = 1) ORDER BY items.price ASC",)
myresult = mycursor.fetchall() 
print("Myresultaaaaaa: ",myresult)
for xyz in myresult:
    print(xyz[0]) #sticker_1
    print(xyz[1]) #sticker_2
    print(xyz[2]) #sticker_3
    print(xyz[3]) #sticker_4
    print(xyz[4]) #sticker_5
    print(xyz[5]) #market_hash_name_shorter
    print("")

    sticker_names = []
    first = True
    for n in range(0,5):
        pom = str(xyz[n])
        if pom != "":
            for element in stickers_a:
                if pom in element:
                    pom = pom.replace("Katowice","Kato")
                    pom = pom.replace("20","")
                    pom = pom.replace(" | "," ")
                    if first == True:   
                        sticker_names.append(pom)
                        first = False
                    elif first == False:
                        sticker_names.append(", " + pom)

        else:
            continue
    sticker_names = ''.join(sticker_names) 
    sticker_normal_text += "[H] " + xyz[5] + " w/ " + sticker_names + "\n"
                    
normal_text = ''.join(normal_text)
sticker_normal_text = ''.join(sticker_normal_text)
    
#if(y<=25): #sprawdza czy jest sens robić posty i czy wartość wszystkich przedmiotów jest większa lub równa 30$
    #print("Niestety przedmioty nie spełniają warunku aby zostać zareklamowane")
    #raise SystemExit(0)

bo = "Crown Foil on an Ak-47 Redline Any Pos <0.20 Float Any Wear Not Scratched"
Want_normal = "Katowice 2014 Normal/Holo, Katowice 2015, Crown, Howling Dawn Stickers Applied On Guns "
Want_reddit = Want_normal + "B/O " + bo #nie zmieniaj
buyout = "\n \n B/O " + bo + "\n \n" #dodać program
ending = "\nYou can add me if you want I don't bite :D \n \ntradelink: https://steamcommunity.com/tradeoffer/new/?partner=271370812&token=eHAwcnd9" #nie zmieniaj
selftext_reddit = buyout + reddit_text + ending + "\n \nThe prices are negotiable"#nie zmieniaj

if(normal_text == ""):
    selftext_normal = sticker_normal_text + ending
elif(sticker_normal_text == ""):
    selftext_normal = normal_text + ending
else:
    selftext_normal = normal_text + "\n" + sticker_normal_text + ending

title_reddit = ""
get_title_reddit(x, y, title_list, Want_reddit)

title_normal = "[W] "+ Want_normal + "\n \n"

def advertisment_reddit(title_reddit,selftext_reddit):
    reddit = praw.Reddit(client_id='lIA2AeFihJSYfw',
                        client_secret='F-s_pg3PYM0KDd896dZruXPl1tM',
                        user_agent='my user agent',
                        username='szun3',
                        password='C~HQ6<K84~zb7g(')
                        
    reddit.validate_on_submit = True
    reddit.subreddit('test').submit(title=title_reddit, selftext=selftext_reddit) #GlobalOffensiveTrade test
    time.sleep(4)
    print("Reddit post has been created")

def advertisment_discussion_tab(title,selftext):
    try:
        driver.get("https://steamcommunity.com/app/730/tradingforum/")
        time.sleep(random.uniform(5.1, 10.0))
        driver.find_element_by_class_name("responsive_OnClickDismissMenu").click()
        time.sleep(1)
        topic = driver.find_element_by_class_name("forum_topic_input")
        topic.click()
        topic.send_keys(title)
        description = driver.find_element_by_class_name("forumtopic_reply_textarea")
        description.click()
        description.send_keys(selftext)
        button = driver.find_element_by_class_name("btn_green_white_innerfade")
        button.click()
    except:
        print("Wystąpił błąd z publikacją posta w sekcji dyskusji")

def advertisment_steam_groups(title,selftext,url):
    try:
        time.sleep(random.uniform(5.1, 8.0))
        driver.get(url)
        comments_other = driver.find_elements_by_tag_name("bdi")
        for element in comments_other:
            element = element.get_attribute('innerHTML')
            if(element == "The Rice Dealer"):
                return 
        comment_area = driver.find_element_by_class_name("commentthread_textarea")
        comment_area.click()
        comment_area.send_keys(title,selftext)
        submit = driver.find_element_by_class_name("btn_green_white_innerfade")
        submit.click()
    except:
        print("Wystąpił błąd w linijce z url: "+url)

#advertisment_reddit(title_reddit,selftext_reddit)
time.sleep(5)

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument(r"user-data-dir=C:\Users\Michal\AppData\Local\Google\Chrome\User Data\Profile 1")
driver = webdriver.Chrome(executable_path=r'C:\Users\Michal\Desktop\projekty\chromedriver.exe', chrome_options = chrome_options)

advertisment_discussion_tab(title_normal,selftext_normal)
time.sleep(5)

advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/tradecenter2016")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/CSGOTrader")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/csgolounge")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/katowicestickerclub")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/csmoneytrade")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/katowice2014stickercollectors")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/ibuypower")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/Original_Traders_Group")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/SGTTB")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/CykaKatowice")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/TeamKato14")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/Katowice2014")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/CsDealsOfficial")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/freeetrade")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/CSGOTRADEme")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/BibanatorCommunity")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/1BUYPOWER")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/polandgotrade")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/Trading-Lounge")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/gergelyszabotrading")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/WorldTradersGroup")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/theglobalparadise")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/steamanalyst")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/iTraders")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/TradingRevolution")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/CSGOFGT")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/SkinProfit")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/OpiumPulsesTrading")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/csgointernationaltradings")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/csgotradeherre")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/CSGOSellCom")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/LitTrading")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/CSGOSkinTradingAndMore")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/casedropeu")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/tradesmart")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/skinport")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/tdm_jesus")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/realCSGO64")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/SkinTrade")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/globaltradeandplay")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/Trade-City")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/LitNetwork")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/csgotradesss")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/community_market")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/csgotradebot")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/rewardsgg")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/titan")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/CSGOTradesGroup")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/csgotradeskinscaseWorld")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/CSGOTradeHub")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/FACEITcom")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/thetradingmasters")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/TheTradeCenter")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/otrade")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/CABUYSELLOfficial")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/csgo_traders")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/csgosum")
advertisment_steam_groups(title_normal,selftext_normal,"https://steamcommunity.com/groups/wymieniamy-skiny")

driver.quit()