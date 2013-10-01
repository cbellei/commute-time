import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from xvfbwrapper import Xvfb
from PIL import Image
#import ImageEnhance
import pylab
import mahotas
import os
import time
#import pandas
import csv
import numpy as np
#from pyvirtualdisplay import Display

#you may need to install mahotas
#as simple as sudo pip install mahotas

plt.close('all')
global ext
ext = ".jpg"
fname = "commute_output.csv"

if not os.path.isfile(fname): #if file does not exist, write header
	with open('commute_output.csv', 'wb') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['Day'] + ['Time'] + ['From_Street'] + ['From_City'] + ['To_Street'] + \
    					['To_City'] + ['Hours'] + ['Minutes'])    

#open url database
f = open("url_database.dat")
url_files = f.readlines()
f.close()

cont = 0

while True:
	for s in range(pylab.size(url_files)):
		 cont = cont + 1
		 url = url_files[s]
		 url = url[0:len(url)-1] #get rid of new line automatic character
		 #find "from" and "to" instances
		 p  = url.find(',',33) #starts @ index 33 and finds first comma
		 fr_str = url[33:p]
		 p1  = url.find(',',p+1)
		 fr_ct = url[p+1:p1]	
		 if (fr_str[0:4] == "7000"):
			 fr_str = "LLNL"    			 
		 p1 = url.find('/',p)
		 p2 = url.find(',',p1)
		 p3 = url.find(',',p2+1)
		 to_str = url[p1+1:p2]
		 if (to_str[0:4] == "7000"):
			 to_str = "LLNL"  		 	 
		 to_ct =  url[p2+1:p3] 
		 #### open url #######
		 browser = webdriver.Firefox()
		 browser.set_window_position(0,0)
		 browser.set_window_size(250,600)
		 browser.set_page_load_timeout(60) #set timeout if page does not load properly
		 try:
		 	browser.get(url)
		 except:
		 	browser.quit()
		 	continue  #do not break the code, go instead to next element in the loop
		 #content = browser.page_source
		 #-----------------------------------------
		 #html = browser.find_element_by_tag_name("html");
		 #html.send_keys(Keys.COMMAND,Keys.SUBTRACT)

		 ##### save screenshot of webpage ########
		 destination="screenshot.jpg"
		 if browser.save_screenshot(destination):
		 	 print "File saved in the destination filename"
		 browser.quit()
		 #-----------------------------------------

		 ##### now crop image ######
		 im = Image.open("screenshot.jpg")

		 def imgCrop(im):    
			 box = (105, 310, 190, 350)
			 region = im.crop(box)
			 region.save( "cropped" + ext )

		 imgCrop(im)
		 #-----------------------------------------

		 ##### very basic image processing ######
		 #-----------------------------------------
		 data = mahotas.imread('cropped.jpg')
		 pylab.gray()

		 #RGB values of image
		 r = data[:,:,0]
		 g = data[:,:,1]
		 b = data[:,:,2]

		 g[g>170] = 255
		 g[g<=170] = 0
		 ind = np.argmax(np.argmin(g,1)) #this is the row where there should be the green dot (top left corner)
		 try:
		 	ind2 = np.argmin(g[ind+4,:]) #ind+3 because try to be at middle of dot
		 except:
		 	continue
		 g[:,1:ind2+12] = 255 #try to eliminate green dot		
          	 
		 #tranform into 24-bit jpeg
		 #data2 = 65536 * r + 256 * g + b;
		 #very rough binary image constructor
		 #data2[data2>=2**23.4] = 2**24
		 #data2[data2<2**23.4] = 0.
		 data2 = g  #it turns out that it is pretty good just to use the greens
		 #-----------------------------------------

		 plt.axis('off')
		 final = plt.imshow(data2)

		 plt.savefig('final.jpg')

		 #get the data with tesseract OCR (Optical Character Recognition) from Google
		 os.system("tesseract final.jpg commute_time")

		 #read text file to get string
		 f = open("commute_time.txt")
		 s = f.read()
		 
		 s.replace(" ","") #eliminates white spaces
		 print s
		 
		 try:
		 	int(s[0])
		 except:
		 	continue  #something wrong with the webpage loading/OCR
		  
		 if ( s[1] == ":" ): #like 1:25 h
		 	 hours = s[0:1]
		 	 hours = hours.replace('[','1') #this is a common mistake of the OCR
		 	 hours = hours.replace('L','1') #this is a common mistake of the OCR
			 hours   = int(hours)
			 minutes = s[2:4]
			 minutes = minutes.replace('?','7') #this is a common mistake of the OCR	
			 minutes = minutes.replace('O','0') #this is a common mistake of the OCR	
			 minutes = int(minutes)	
		 elif ( s[2] == ":" ): #like 10:25 h
			 hours   = s[0:2]
		 	 hours = hours.replace('[','1') #this is a common mistake of the OCR
			 hours   = int(hours)
			 minutes = s[3:5]
			 minutes = minutes.replace('?','7') #this is a common mistake of the OCR	
			 minutes = minutes.replace('O','0') #this is a common mistake of the OCR	
			 minutes = int(minutes)	
		 elif ( s[1] != ' '): ##like 25 min <--- 2 digit number <-- not a white space on 2nd digit
			 hours   = 0
			 minutes = s[0:2]
			 minutes = minutes.replace('?','7') #this is a common mistake of the OCR	
			 minutes = minutes.replace('O','0') #this is a common mistake of the OCR
			 try:	
			 	minutes = int(minutes)	
			 except:
			 	continue #something wrong with OCR
		 else:  #like 2 min
			 hours   = 0
			 minutes = s[0:1]
			 minutes = minutes.replace('?','7') #this is a common mistake of the OCR	
			 minutes = minutes.replace('O','0') #this is a common mistake of the OCR
			 try:	
			 	minutes = int(minutes)	
			 except:
			 	continue #something wrong with the webpage loading/OCR
		
		 #now start database
		 T = time.localtime()
	
		 with open(fname, 'a') as csvfile:
			 filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			 current_day = str(T.tm_year) + '-' + str(T.tm_mon) + '-' + \
					 str(T.tm_mday) 
			 current_time = str(T.tm_hour) + ':' + \
					 str(T.tm_min) + ':' + str(T.tm_sec)
			 filewriter.writerow([current_day] + [current_time] + [fr_str] + [fr_ct] + \
			 						[to_str] + [to_ct] + [hours] + [minutes] )
			 						
		 print "Hours: " + str(hours) + ". Minutes: ", str(minutes)
	
	sleep_time = 300
	print "-"*25
	print "waiting for " + str(int(sleep_time/60)) + ' minutes'
	print "-"*25
	time.sleep(sleep_time)