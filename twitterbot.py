import os
import re
import time
from twython import Twython
import random
import configparser as ConfigParser
from selenium import webdriver


# dann machen wir mal einen blanken browser auf
def browser_aufmachen():
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--start-maximized")
    prefs= {'profile.managed_default_content_settings.javascript': 2}
    chromeOptions.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome('c:\\Python36\chromedriver.exe',chrome_options=chromeOptions)
    return (driver)

# passende antworte von google news holen und formatieren
def suche_antworten(begriff):
    antworten=[]
    driver = browser_aufmachen()
    url="https://news.google.com/news/search/section/q/" + begriff + "?hl=de&gl=DE&ned=de"
    driver.get(url)
    els=driver.find_elements_by_xpath('//a[@role="heading"]')
    for el in els:
        s=el.text.split(" - ")
        # den dickeren happen bei spiegelstrichen
        if len(s)>1 and len(s[1])>len(s[0]):
            a=s[1]
        else:
            a=s[0]
        # wen interessieren schon quellen
        p=a.find(":")
        if p>0:
            a=a[p+1:]
        # ein paar zeichen brauchen wir nicht
        p=a.find("...")
        if p>0:
            a=""
        a=a.replace('"','')
        a=a.replace("“","")
        a=a.replace("„","")
        a=a.strip()
        # ausrufezeichen sind wichtig bei twitter
        if a!="":
            a=a+"!"
            antworten.append(a)
    driver.quit()
    return antworten



# config laden
config = ConfigParser.RawConfigParser()
configfile=(os.path.expanduser("~/twitterbot.ini"))
config.read(configfile)

# letzte tweets laden
twitter = Twython(config.get('twitter', 'APP_KEY'), config.get('twitter', 'APP_SECRET'),
                  config.get('twitter', 'OAUTH_TOKEN'), config.get('twitter', 'OAUTH_TOKEN_SECRET'))
sid=config.get('twitter', 'ID')
timeline = twitter.get_home_timeline(since_id=sid)
if len(timeline)==0:
    exit(0)
lastEntry = timeline[0]
sid = str(lastEntry['id'])

# config aktualisieren
cfg = open(configfile,'w')
config.set('twitter','ID',sid)
config.write(cfg)
cfg.close()

# alle neue tweets durchgehen
for tweet in timeline:
    user = tweet['user']['screen_name']
    text = tweet['text']
    id = str(tweet['id'])
    print("*** ID:",id, "***")
    print("User:",user)
    print("Tweet:",text)
    # hashtags mit regex filtern und auswahl
    hashtags=re.findall(r"#(\w+)",text)
    print ("Hashtags:",hashtags)
    if len(hashtags) > 0:
        hashtag=random.choice(hashtags)
        antworten=suche_antworten(hashtag)
        # antwort zum hashtag tweeten
        if len(antworten) > 0:
            antwort="@"+user+" "+random.choice(antworten)
            print ("Reply:",antwort)
            # tweet und pause um twitter nicht zu stressen
            twitter.update_status(status=antwort,in_reply_to_status_id=id)
            time.sleep(60)


