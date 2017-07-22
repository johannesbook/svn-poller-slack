#hack to check last svn checkin, and post it to slack channel #altium-svn-updates
#Johannes Book 2017

pathToLocalSvn = '"c:/altium work/WalterSVN/"'  #Note - don't use backslash
pathToDataFile = 'c:/temp/robbot.data'

webhookUrl = 'https://hooks.slack.com/services/GET/THIS/LINK_FROM_SLACK_WEBHOOKS_API'

import re
import time
import json
import requests
from subprocess import check_output

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
		match = re.search(r'<author>(.*)</author>.*action.*>(.*)</path>.*<msg>(.*)</msg>',output,re.DOTALL) #I need to learn XML decoding, I know..
		if match:
			who = match.group(1)
			path = match.group(2)
			what = match.group(3)
			match2 = re.search(r'/.*/.*/(.*)$',path,re.M|re.DOTALL)	#get file name
			if match2:
				file = match2.group(1)
			else:
				file = ""
			match3 = re.search(r'/([A-Z]{3,20}?).*/(.*)$',path,re.M|re.DOTALL) #get project name
			if match3:
				project = match3.group(1)
			else:
				project = ""
		else:
			print('Error #476 - please replace your CD-ROM')
	
		
		# post to slack:
		if (what): #only if they wrote a commit message
			message = project + ": *" + what + '* (' + file + ')'
			slackData = {
				"attachments": [
					{
						"title": who,
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
