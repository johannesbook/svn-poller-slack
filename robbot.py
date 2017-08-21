#hack to check last svn checkin, and post it to slack channel #altium-svn-updates
#Johannes Book 2017

pathToLocalSvn = '"C:/robbot/svn checkout"'  #Note - don't use backslash
pathToDataFile = 'C:/robbot/robbot.data'

webhookUrl = 'https://hooks.slack.com/services/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'

import sys
import re
import time
import json
import requests
from xml.dom import minidom
from subprocess import check_output
files = []

print('Starting..')
	
while True:
	#open last revision from file
	file = open(pathToDataFile,"r")
	lastRevision = file.read()
	file.close()

	# checking if new commit, and getting commit details from svn server:
	callString = 'svn log ' + pathToLocalSvn + ' --xml -v -r ' + str(lastRevision)
	newCommit = True
	try: 
		output = check_output(callString,universal_newlines = True)
	except:
		print('checked - no new commit')
		newCommit = False
		
	if newCommit: #get commit details and post them to slack
		#match = re.search(r'revision=\"(.*)\">.*<author>(.*)</author>.*action.*>(.*)</path>.*<msg>(.*)</msg>',output,re.DOTALL) #I need to learn XML decoding, I know..
		match = re.search(r'revision=\"(.*)\">.*<author>(.*)</author>.*<paths>(.*)</paths>.*<msg>(.*)</msg>',output,re.DOTALL) #I need to learn XML decoding, I know..
		if match:
			rev = match.group(1)
			who = match.group(2)
			paths = match.group(3)
			what = match.group(4)
			
			#parse all file paths
			xmldoc = minidom.parseString(output)
			itemlist = xmldoc.getElementsByTagName('path')
			for s in itemlist:
				#print(s.firstChild.nodeValue)
				files.append(s.firstChild.nodeValue)

			for i, item in enumerate(files):
				match2 = re.search(r'/.*/([A-Z]{3,20}?).*/(.*)$',item,re.M|re.DOTALL)	#get file name
				if match2:
					project = match2.group(1)
					files[i] = match2.group(2)
				else:
					files[i] = ""
		else:
			print('Error #476 - please replace your CD-ROM')

		#sys.exit("halt!")
		
		# post to slack:
		if (what): #only if they wrote a commit message
			message = project + ": *" + what + '*' 
			for s in files:
				message = message + "\n" + s
			print(message)
			slackData = {
				"attachments": [
					{
						"title": who + ": " + rev,
						"text": message,
						"mrkdwn_in": [
							"text"
						]
					}
				]
			}


			response = requests.post(
				webhookUrl, data=json.dumps(slackData),
				headers={'Content-Type': 'application/json'}
				)
			if response.status_code != 200:
				raise ValueError(
					'Request to slack returned an error %s, the response is:\n%s'
					% (response.status_code, response.text)
				)


		#if new commit found - increment revision # in file
		file = open(pathToDataFile,"w")
		file.write(str(int(lastRevision)+1))
		file.close()
	else:
		#holdoff for a while - no need to check all the time
		time.sleep(30)
