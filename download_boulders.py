import sqlite3
import urllib.error
import ssl
from urllib.request import urlopen

import os

#function to download images of the boulders
from image_dl import getImages


#######################################FUNCTIONS##################################

#Function to open the site with description of the boulder and get additional information
#such as description and rules.
#Also downloads and saves images of the boulders if it gets pics=True
#it returns type of the boulder(category), description, rules
def getDetails(url, id, pics):

    f = urlopen(url)
    content = f.read()
    content_str = content.decode("utf8")
    f.close()

    #Finding part with the description of the boulder
    try:
        before_descr = content_str.split("<div class=\"clearfix text-formatted field field--name-field-beschreibung field--type-text-long field--label-above\">")[1]
        descr = before_descr.split("<div class=\"field__item\"><p>")[1]
        #sometimes there is missing end of <p> tag, so we use </div> to find end of the description
        descr = descr.split("</div")[0]
        #if there is properly ended paragraph. then we can clear leftovers
        descr = descr.split("</p")[0]
    #If the site doesn't contain description of the boulder, the previous section will fail to run
    except:
        descr = "No description"

    #Finding rules of the boulder
    try:
        before_rules = content_str.split("<div class=\"clearfix text-formatted field field--name-field-rules field--type-text-long field--label-above\">")[1]
        rules = before_rules.split("<div class=\"field__item\"><p>")[1]
        #sometimes there is missing end of <p> tag, so we use </div> to find end of the description
        rules = rules.split("</div")[0]

        rules = rules.split("</p")[0]
    #if the rules are missing
    except:
        rules = "No rules"

    #Finding category of the boulder
    try:
        before_type = content_str.split("<div class=\"field field--name-boulder-kategorie field--type-entity-reference field--label-hidden field__items\">")[1]
        type = before_type.split("de\">")[1]
        #works as a link, so it is easy to find end of the category name
        type = type.split("</a")[0]
    except:
        type = "No type"

    #if we are asked to download pictures
    if pics:
        print("got information, going to get images for problem {}".format(id))
        # input()
        #We provide the code and our id of the boulder and it will download all pictures into folder named by the id
        getImages(content_str,id)

    #returning obtained information - description, rules, and boulder type
    return descr, rules, type



#################################### MAIN CODE ##################################################x


#creating directory for photos. Photos/id
path = os.getcwd()
path = path+"\\Photos"
try:
    os.mkdir(path)
    print("Photo folder created")
    # input()
except:
    print("Not possible to create Photos folder. It probably exists already.")

#Database to save information about boulders
conn = sqlite3.connect('boulders.sqlite')
cur = conn.cursor()

#Table in the boulders database, including url with desctiption, name, difficulty 1-100,
#french difficulty, GPS location, date when it was posted, description, rules to climb, and category
cur.execute('''CREATE TABLE IF NOT EXISTS Boulders
    (id INTEGER NOT NULL PRIMARY KEY UNIQUE,
     url TEXT UNIQUE,
     name TEXT,
     difficulty INT,
     french TEXT,
     lat FLOAT,
     lon FLOAT,
     posted TEXT,
     description TEXT,
     rules TEXT,
     type TEXT)''')

#Page with the list of urban boulders and their locations used as the data source in this project
web = "http://www.urban-boulder.com/de/map"
site = "http://www.urban-boulder.com"
f = urlopen(web)
content = f.read()
content_str = content.decode("utf8")
f.close()


#Preparing transformation from 0-100 score to French grade
FrGrade = {
    "20":"2",
    "30":"2+",
    "40":"4",
    "50":"5A",
    "55":"5B",
    "60":"6C",
    "70":"6B",
    "75":"6B+",
    "80":"6C/6C+",
    "85":"7A",
    "90":"7B"}


#Split string into list of specific boulders
splitted = content_str.split("<div class=\"geolocation\"")
#print(splitted[1])
#we get rid of the first item that just conatins page introduction
boulders = splitted[1:]

#let's extract all the information about the boulder
#our id for boulders
id = 1

for boulder in boulders:

    #get URL of the site with boulder description
    after_url = boulder.split("ocation-title\"><a href=\"")[1]
    url = site + after_url.split("\"")[0]

    #check if this url is already in our database, then no need to scrape it:
    cur.execute('SELECT id FROM Boulders WHERE url = ? ', (url, ))
    row = cur.fetchone()
    if row is not None:
        print("skipping problem {} because it was saved before.".format(id))
        id+=1
        continue

    #getting latitude and longtitude
    after_lat = boulder.split("data-lat=\"")[1]
    latitude = after_lat.split("\"")[0]

    after_lon = boulder.split("data-lng=\"")[1]
    longtitude = after_lon.split("\"")[0]

    #get the name
    name = after_url.split(">")[1].split("<")[0]
    print("Working on the problem: {} with ID: {}".format(name,id))

    #get the grade on the 0-100 scale
    gradestart = after_url.split("Grade 1-100: </span><span class=\"field-content\">")[1]
    grade = gradestart.split("<")[0]

    #French grade. Some boulders have weird number on the scale and weird French grade
    #In that case, we don't asign French grade and just keep the 0-100 score
    try:
        french = FrGrade[grade]
    except:
        french = grade

    #when was the route posted
    beforedate = after_url.split("posted: </span><span class=\"field-content\">")[1]
    posted = beforedate.split("<")[0]

    #Now we want to get description and rules and also download images
    #last parameter must be true to download images
    description, rules, type = getDetails(url, id, True)

    #let's save obtained data into database
    cur.execute('''INSERT OR IGNORE INTO Boulders
        (
         id,
         url,
         name,
         difficulty,
         french,
         lat,
         lon,
         posted,
         description,
         rules,
         type
        )
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )''',
        ( id, url, name, grade, french, latitude, longtitude, posted, description, rules, type ) )

    conn.commit()


    print("Problem: {} with ID: {} saved in database".format(name,id))
    # input()
    #Increase ID for next boulder
    id+=1

print("Database of boulders finished. Run prepare_boulders.py to prepare obtained data for map creation.")
