import requests
import urllib.request
from PIL import Image,ImageDraw,ImageFont
import json
import os
import tweepy
import datetime
import threading



auth = tweepy.OAuthHandler(os.environ["key"],os.environ["sec"])
auth.set_access_token(os.environ["token"],os.environ["token_sec"])

api = tweepy.API(auth)


def tweet():
    if os.path.exists("News.png"):
        media_ids = []
        now = datetime.datetime.utcnow()
        date = str(now.day)+"/"+str(now.month)
        resp = api.media_upload("News.png")
        media_ids.append(resp.media_id)
        api.update_status(status="Fortnite BR News " + date,media_ids=media_ids)

def set_interval(func, sec): 
    def func_wrapper():
        set_interval(func, sec) 
        func()  
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def wrap_text(text, width, font):
    text_lines = []
    text_line = []
    text = text.replace('\n', ' [br] ')
    words = text.split()
    font_size = font.getsize(text)

    for word in words:
        if word == '[br]':
            text_lines.append(' '.join(text_line))
            text_line = []
            continue
        text_line.append(word)
        w, h = font.getsize(' '.join(text_line))
        if w > width:
            text_line.pop()
            text_lines.append(' '.join(text_line))
            text_line = [word]

    if len(text_line) > 0:
        text_lines.append(' '.join(text_line))

    return text_lines


font1 = ImageFont.truetype("TitleFont.ttf",50)
font2 = ImageFont.truetype("DescFont.ttf",45)
def writeToFile():
    exists = os.path.isfile("News.json")
    resp = requests.get("https://fortnitecontent-website-prod07.ol.epicgames.com/content/api/pages/fortnite-game")
    if resp.status_code == 200:
        jsonResp = resp.json()
        brNews = jsonResp["battleroyalenews"]["news"]["messages"]
        if not exists:
            newsFile = open("News.json","x")
            newsFile.close()
        newsFile = open("News.json","r")
        if json.dumps(brNews) not in newsFile.read():
            print("writing")
            newsFile = open("News.json","w")
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
    leftFile.thumbnail((600,337.5),Image.ANTIALIAS)
    midFile.thumbnail((600,337.5),Image.ANTIALIAS)
    rightFile.thumbnail((600,337.5),Image.ANTIALIAS)
    backFile.paste(leftFile,(14,314))
    backFile.paste(midFile,(660,314))
    backFile.paste(rightFile,(1308,314))
    d = ImageDraw.ImageDraw(backFile)
    d.multiline_text((14+offset,652),left["title"],fill=(0,0,0),font=font1,anchor=None,spacing=4,align="center")
    d.multiline_text((660+offset,652),mid["title"],fill=(0,0,0),font=font1,anchor=None,spacing=4,align="center")
    d.multiline_text((1308+offset,652),right["title"],fill=(0,0,0),font=font1,anchor=None,spacing=4,align="center")
    line_height = font2.getsize('hg')[1]
    lines1 = wrap_text(left["body"],650,font2)
    lines2 = wrap_text(mid["body"],650,font2)
    lines3 = wrap_text(right["body"],650,font2)
    left_coords = [14+(offset/2),735]
    mid_coords = [660+(offset/2),735]
    right_coords = [1308+(offset/2),735]
    for line in lines1:
        d.text((left_coords[0],left_coords[1]),line,(0,0,0),font2)
        left_coords[1] = left_coords[1] + line_height
    for line in lines2:
        d.text((mid_coords[0],mid_coords[1]),line,(0,0,0),font2)
        mid_coords[1] = mid_coords[1] + line_height
    for line in lines3:
        d.text((right_coords[0],right_coords[1]),line,(0,0,0),font2)
        right_coords[1] = right_coords[1] + line_height
    backFile.save("News.png")
    tweet()
    os.remove("News.png")
set_interval(writeToFile,1)