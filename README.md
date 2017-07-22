# svn-poller-slack
python tool that polls any remote svn server and sends commit details to a slack channel

Using https://api.slack.com/incoming-webhooks API to post to slack, this tool regularly checks any SVN server for new commits, and when found, posts them to slack. 
The script can run on any computer or server, does not have to be the same machine that runs the SVN server
