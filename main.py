import urllib.request
from PIL import Image,ImageDraw,ImageFont,ImageColor,ImageEnhance
import json
import os
import tweepy
import datetime
import threading
import subprocess
import sys
import time
import requests
import textwrap
import schedule


auth = tweepy.OAuthHandler(os.environ["key"],os.environ["sec"])
auth.set_access_token(os.environ["token"],os.environ["token_sec"])

api = tweepy.API(auth)

def tweet(tweetText,image):
        for status in tweepy.Cursor(api.user_timeline,screen_name=api.me().screen_name,tweet_mode="extended").items(1):
                if tweetText not in status.full_text:
                        media_ids = []
                        #now = datetime.datetime.utcnow()
                        #date = str(now.day)+"/"+str(now.month)
                        resp = api.media_upload(image)
                        media_ids.append(resp.media_id)
                        api.update_status(status=tweetText + " #Fortnite",media_ids=media_ids)




def text_wrap(text, font, max_width):
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text) 
    else:
        # split the line by spaces to get words
        words = text.split(' ')  
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ''         
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:                
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word, 
            # add the line to the lines array
            lines.append(line)    
    return lines


font1 = ImageFont.truetype("TitleFont.ttf",45)
font2 = ImageFont.truetype("DescFont.ttf",30)

def writeToFile():
    exists = os.path.isfile("News.json")
    resp = requests.get("https://fortnitecontent-website-prod07.ol.epicgames.com/content/api/pages/fortnite-game")
    if resp.status_code == 200:
        jsonResp = resp.json()
        brNews = jsonResp["battleroyalenews"]["news"]["messages"]
        if not exists:
            newsFile = open("News.json","x")
            newsFile.close()
        newsFile = open("News.json","r+")
        data = newsFile.read()
        if json.dumps(brNews) not in data:
            print("writing")
            newsFile.write(json.dumps(brNews))
            newsFile.close()
            downloadImages()
        else:
            print("Not writing")
            return
       

def downloadImages():
    brNews = json.loads(open("News.json","r").read())
    left = brNews[0]
    mid = brNews[1]
    right = brNews[2]
    leftImg = left["image"]
    midImg = mid["image"]
    rightImg = right["image"]
    urllib.request.urlretrieve(leftImg, "Left.png")
    urllib.request.urlretrieve(midImg, "Mid.png")
    urllib.request.urlretrieve(rightImg, "Right.png")
    makeImage(left=left,mid=mid,right=right)
def makeImage(left,mid,right):
    offset = 50
    leftFile = Image.open("Left.png")
    midFile = Image.open("Mid.png")
    rightFile = Image.open("Right.png")
    backFile = Image.open("ImageBackground.png")
    rectangle = Image.new("RGBA",(555,766),(99,99,99,210))
    rectangle1 = rectangle.copy()
    rect1Draw = ImageDraw.ImageDraw(rectangle1)
    line1 = text_wrap(left["body"],font2,rectangle1.size[0])
    rectangle1.save("Test.png")
    resizedLeft = leftFile.resize((555,265),Image.ANTIALIAS)
    resizedMid = midFile.resize((555,265),Image.ANTIALIAS)
    resizedRight = rightFile.resize((555,265),Image.ANTIALIAS)
    backFile.paste(resizedLeft,(36,285))
    backFile.paste(resizedMid,(684,285))
    backFile.paste(resizedRight,(1335,285))
    d = ImageDraw.ImageDraw(backFile)
    d.text((36,549),left["title"],fill=(0,0,0),font=font1,anchor=None,spacing=4,align="center")
    d.text((684,549),mid["title"],fill=(0,0,0),font=font1,anchor=None,spacing=4,align="center")
    d.text((1335,549),right["title"],fill=(0,0,0),font=font1,anchor=None,spacing=4,align="center")
    d.multiline_text((36,667),left["body"],fill="black",font=font2)
    d.multiline_text((684,667),left["body"],fill="black",font=font2)
    d.multiline_text((1335,667),left["body"],fill="black",font=font2)
   
    
    backFile.save("News.png")
    #tweet()
    #os.remove("News.png")
    

def checkForStarterPack():
    baseUrl = "https://store.playstation.com/valkyrie-api/en/AU/999/resolve/EP1464-CUSA07669_00-"
    resp = requests.get(baseUrl+"RMPA070000000000")
    respJson = resp.json()
    if "FORTNITETESTING" in respJson["data"]["relationships"]["children"]["data"]["id"]:
        print("redirected")
        return
    else:
        image = respJson["included"][0]["attributes"]["thumbnail-url-base"]
        desc = respJson["included"][0]["attributes"]["long-description"]
        desc = desc.replace("<br>","").split("V-Bucks")
        urllib.request.urlretrieve(image,"StarterPack.png")
        finishedDesc = desc[0].replace(":-",":\n-").replace("600","600 Vbucks")+desc[1].replace("-","\n-")
        tweet(finishedDesc,"StarterPack.png")
        schedule.clear("bot-tasks")

schedule.every(1).seconds.do(checkForStarterPack).tag("bot-tasks")

while True:
    schedule.run_pending()
    time.sleep(1)