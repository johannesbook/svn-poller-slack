#hack to check last svn checkin, and post it to slack and MS teams channel #altium-svn-updates 
#Johannes Book 2017

pathToLocalSvn = '"C:/robbot/svn checkout"'  #Note - don't use backslash
pathToDataFile = 'C:/robbot/robbot.data'

slackWebhookUrl = 'ADD SLACK WEBHOOK URL HERE'
teamsWebhookUrl = 'ADD TEAMS WEBHOOK URL HERE'

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
			del files[:] #remove old stuff
			for s in itemlist:
				#print(s.firstChild.nodeValue)
				files.append(s.firstChild.nodeValue)

			for i, item in enumerate(files):
				parts = item.split('/')
				project = parts[2].split('-')[0] #project name is what comes before the '-' in the folder name
				files[i] = parts[len(parts)-1]
		else:
			print('Error #476 - please replace your CD-ROM')

		# post to teams:
		if (what): 
			
			filesString = ""
			if (len(files) > 1):
				for s in files:
					filesString = filesString + " | " + s
				filesString = filesString + " |"
			else:
				filesString = files[0]

			if not (project):
				project = "unknown"
				
			teamsData = {
				"@type": "MessageCard",
				"@context": "http://schema.org/extensions",
				"summary": project,
				"themeColor": "FF5800",
				"title": project,
				"sections": [
					{
						"facts": [
							{
								"name": "By:",
								"value": who + " (" + rev + ")"
							},
							{
								"name": "Files:",
								"value": filesString
							}
						],
						"text": what
					}	
				]
			}
				

			response = requests.post(
				teamsWebhookUrl, data=json.dumps(teamsData),
				headers={'Content-Type': 'application/json'}
				)
			if response.status_code != 200:
				raise ValueError(
					'Request to Teams returned an error %s, the response is:\n%s'
					% (response.status_code, response.text)
				)
		

		#sys.exit("Quit")
		#what = ""
		
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
				slackWebhookUrl, data=json.dumps(slackData),
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
