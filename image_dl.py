from urllib.request import urlopen

import requests
import os



#######################################FUNCTIONS##################################
#function to download boulder images from the boulder description page
#sitecontent - it gets string with the html code of the page
#id - id of the boulder, to name the picture folder after
def getImages(sitecontent,id):

    #Folder for specific boulder
    path = os.getcwd()
    path = path+"\\Photos"+"\\"+str(id)

    #creating folder
    try:
        os.mkdir(path)
        print("Created subfolder for boulder problem {}".format(id))

    except:
        print("Not possible to create subfolder for photos. It probably exists already.")

    #Find images of the boulder problem
    try:
        #get rid of the part before boulder images section
        before_img = sitecontent.split("<div class=\"imagefield_slideshow\"")[1]
        #get rid of the stuff after this section
        img_all = before_img.split("</div")[0]

        #separate images
        img_sep = img_all.split("<img src=\"")

        #get rid of the stuff before first image
        img_sep = img_sep[1:]

        #counter for images = file name when saving
        count = 1

        for img in img_sep:
            #get only img url
            source = img.split("\"")[0]

            #downloading images and saving them to respective folders
            #path for the image
            location = path + "\\" + str(count)+".jpg"

            #saving the image
            with open(location, 'wb') as f:
                f.write(requests.get(source).content)

            count+=1

    except:
        print("Not able to get images for boulder ID: {}".format(id))
