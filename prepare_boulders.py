import sqlite3
import json
import codecs

import os


#From the SQLite database gets the information about boulders and create .js file
#that is later used to create HTML page with map of the boulders

conn = sqlite3.connect('boulders.sqlite')
cur = conn.cursor()


cur.execute('SELECT * FROM Boulders')

#.js file for boulders locations and all important info
fhand = codecs.open('locations.js','w', "utf-8")
fhand.write("myData = [\n")

#counter just to distinguish between first and next boulders
count = 0

for row in cur :

    #get latitude and longtitude
    lat = row[5]
    lng = row[6]

    #url of the original page describing details of the boulder
    url = row[1]
    name=row[2]

    #french difficulty of the boulder
    french=row[4]
    description=row[8]
    rules=row[9]
    type=row[10]

    # Check how many pictures we have for the problem
    #path in the format .\Photos\1\, where the number reflects boulder's id
    DIR = os.getcwd()+'\\Photos\\'+str(row[0])+''

    #list of files in the chosen folder = all pictures
    list = os.listdir(DIR)
    pictures = len(list)

    #We skip the process for an entry in the database that is missing GPS location
    #However, there should not be such an entry
    if lat == 0 or lng == 0 : continue

    #create the info that is displayed when mouseover at the point
    #contains name of the boulder, french difficulty, and type
    info = str(row[2])+", "+str(row[4])+", "+str(row[10])


    #A little bit of cleaning
    #clean reamining html tags left in the texts
    info = info.replace("<br />"," ... ")
    description = description.replace("<br />"," ... ")
    rules = rules.replace("<br />"," ... ")

    #replace some special symbols with javascript syntax for the strings
    info = info.replace("\n"," \\n ")
    description = description.replace("\n"," \\n ")
    rules = rules.replace("\n"," \\n ")

    info = info.replace("\'"," \\' ")
    description = description.replace("\'"," \\' ")
    rules = rules.replace("\'"," \\' ")



    #prepare javascript file will all the data for google maps
    try :
        count = count + 1
        #end of the line, if there is already some line in the file
        if count > 1 : fhand.write(",\n")
        #all our information separated by commas
        output = "["+str(lat)+","+str(lng)+", '"+info+"', '"+url+"', '"+name+"', '"+french+"', '"+description+"', '"+rules+"', '"+type+"', "+str(pictures)+"]"
        fhand.write(output)
    except:
        continue

#finishing the .js file
fhand.write("\n];\n")
cur.close()
fhand.close()

print("{} records written to where.js".format(count))
print ("Open Map.html to view the data in a browser")
