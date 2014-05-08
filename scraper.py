import sys
import requests

print "Welcome to Dirigible37s hype machine scraper! Please enter url below:"
baseUrl = "http://hypem.com/" + raw_input("http://hypem.com/")

headers = {'cookie' : 'AUTH=03%3A30b60004d02a36ab7f421729ed184669%3A1399511839%3A2885858446%3ASC-US; __qca=P0-668138330-1399511840418; notice20140501=true; __utma=1717032.1900021481.1399511840.1399511840.1399511840.1; __utmb=1717032.31.9.1399514021972; __utmc=1717032; __utmz=1717032.1399511840.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'}
response = requests.post(baseUrl, headers = headers)
if not response.ok:
	sys.exit("Invalid URL")


file = "temp_src.html"
temp_html = open(file, "w")
temp_html.write(response.content)
temp_html.close();

src = open(file, "r")

for line in src:
	if "\"key\"" in line:
		data = line
		songs = data.split("\"type\"")
	else:
		songs = -1;

if songs is -1:
	sys.exit("No songs found on given url")

print "Thank you! Now downloading songs from: " + baseUrl

for x in range(0, len(songs) - 1):
	if "\"id\"" not in songs[x]:
		songs.pop(x)

keys = list()
ids = list()
titles = list()

for i in range(0, len(songs) - 1):	
	keys.insert(i, songs[i][songs[i].find("\"key\"")+7:songs[i].find("\"artist\"")-2])
	ids.insert(i, songs[i][songs[i].find("\"id\"")+6:songs[i].find("\"time\"")-2])
	titles.insert(i, songs[i][songs[i].find("\"song\"")+8:songs[i].find("\"is_sc\"")-2] + ".mp3")
	#print "title of song ", i, ": " + titles[i]

for j in range(0, len(songs) - 1):

	currentSong = requests.post("http://hypem.com/serve/source/" + ids[j] + "/" + keys[j], headers = headers)
	songUrl = currentSong.content[currentSong.content.find("http:") : currentSong.content.find("\"}")]
	songUrl = songUrl.replace("\\","")
	with open("songs/" + titles[j], 'wb') as handle:
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

response.close()
