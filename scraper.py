import sys
import mutagen
from mutagen.easyid3 import EasyID3
import os.path
import requests
import json
import boto
from boto.s3.key import Key

#print "Welcome to Dirigible37s hype machine scraper! Please enter url below:"
#baseUrl = "http://hypem.com/" + raw_input("http://hypem.com/")
#numPages = raw_input("Please input number of pages you wish to crawl: ")

#baseUrl = "http://hypem.com/" + sys.argv[1]
#numPages = sys.argv[2]
baseUrl = "http://hypem.com/dirigible"
numPages = 1;

conn = boto.connect_s3()
bucket = conn.get_bucket('dirigible-media-player')
k = Key(bucket)

#cookies expire, need to generate cookie
#use username and pass to authenticate, then get the cookie from that
headers = {'cookie' : 'AUTH=03%3A30b60004d02a36ab7f421729ed184669%3A1399511839%3A2885858446%3ASC-US; __qca=P0-668138330-1399511840418; notice20140501=true; __utma=1717032.1900021481.1399511840.1399511840.1399511840.1; __utmb=1717032.31.9.1399514021972; __utmc=1717032; __utmz=1717032.1399511840.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'}
#Initialize
#response = requests.post(baseUrl, headers = headers)
#TODO Perhaps figure out max pages
keys = list()
ids = list()
titles = list()
artists = list()
lengths = list()

#Create necessary folders
if not os.path.exists("songs"):
    os.makedirs("songs")


for i in range (1, int(numPages)+1):	
	currentUrl = baseUrl + "/" + str(i) + "/"
	response = requests.post(currentUrl, headers = headers)
	if not response.ok:
		sys.exit("Invalid URL")

	file = "temp_src.html"
	temp_html = open(file, "w")
	temp_html.write(response.content)
	temp_html.close();

	src = open(file, "r")
	#thisdata = json.loads(src)
	#print(thisdata)

	for line in src:
		if "\"key\"" in line:
			data = line
			songs = data.split("\"type\"")

	if len(songs) is 0:
		sys.exit("No songs found on given url")

	print "Thank you! Now downloading songs from: " + currentUrl

	for x in range(0, len(songs) - 1):
		if "\"id\"" not in songs[x]:
			songs.pop(x)

	#Pull and store key, id, title, artist, length
	#TODO: Make this use json
	for i in range(0, len(songs) - 1):
		songName = songs[i][songs[i].find("\"song\"")+8:songs[i].find("\"is_sc\"")-2]
		artistName = songs[i][songs[i].find("\"artist\"")+10:songs[i].find("\"song\"")-2]
		songLength = songs[i][songs[i].find("\"time\"")+7:songs[i].find("\"ts\"")-1]
	
		if not os.path.isfile("songs/" + songName):
		  keys.append(songs[i][songs[i].find("\"key\"")+7:songs[i].find("\"artist\"")-2])
		  ids.append(songs[i][songs[i].find("\"id\"")+6:songs[i].find("\"time\"")-2])
		  titles.append(songName)
		  artists.append(artistName)
		  lengths.append(songLength)
		  #print "title of song ", i, ": " + titles[i]
		  #print "artist of song ", i, ": " + artists[i]
		  #print "length of song ", i, ": " + lengths[i]

	response.close()
	temp_html.close()
	src.close()

#Download Songs
for j in range(0, len(keys) - 1):
	currentSong = requests.post("http://hypem.com/serve/source/" + ids[j] + "/" + keys[j], headers = headers)
	songUrl = currentSong.content[currentSong.content.find("http:") : currentSong.content.find("\"}")]
	songUrl = songUrl.replace("\\","")
	with open("songs/" + titles[j] + ".mp3", 'wb') as handle:
		songConnection =  requests.get(songUrl)
		print "Downloading " + titles[j]	
		if not songConnection.ok:
			print currentSong.url
			print songConnection.status_code
			
		for block in songConnection.iter_content(1024):
			if not block:
				break
			handle.write(block)
	currentSong.close()
	
	#Add ID3 data
	filePath = "songs/" + titles[j] + ".mp3"

	try:
		meta = EasyID3(filePath)
	except mutagen.id3.ID3NoHeaderError:
		meta = mutagen.File(filePath, easy=True)
		meta.add_tags()

	meta['title'] = titles[j]
	meta['artist'] = artists[j]
	meta['length'] = lengths[j]
	meta.save()
	changed = EasyID3("songs/" + titles[j] + ".mp3")
	print changed

	k.key = titles[j]
	print "Uploading song to bucket"
	k.set_contents_from_filename("songs/" + titles[j] + ".mp3")
	
	os.remove("songs/" + titles[j] + ".mp3")
print "All done"
