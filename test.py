from evaluate import ffwd_to_img
import redis
import json
import wget
import requests
import os
import random

checkpoint_dir = 'chkpt/'

ckpt_files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(checkpoint_dir):
    for file in f:
        if '.ckpt' in file:
            ckpt_files.append(os.path.join(r, file))

for f in ckpt_files:
    print(f)


redis = redis.Redis()

bot_token = redis.get('bot:token')

def sendPhoto(chat_id, msg):
	data = {}
	data["chat_id"] = chat_id
	data["photo"] = msg
	url = "https://api.telegram.org/bot{}/{}".format(bot_token,"sendPhoto")
	print "Sending", chat_id, ": ",  msg
	r = requests.post(url, data=data)


def processMessage(data):
	print data
	in_path = data['result']['file_path'].encode(encoding='UTF-8')
	print "in_path:",  in_path , type(in_path)
	url = "https://api.telegram.org/file/bot{}/{}".format(bot_token,in_path)
	print "getting image:", url
	wget.download(url, in_path)

	out_path = 'static/' + in_path
	#checkpoint_dir = 'checkpoints/udnie.ckpt'
	checkpoint_dir = random.choice(ckpt_files)

	ffwd_to_img(in_path, out_path, checkpoint_dir)

	print "done image"
	sendPhoto(data['chat_id'], "https://dl2.rohbot.cc/" + out_path)


data = {'chat_id': 700442415, 'result': {'file_path': u'photos/file_18.jpg'}}

print data
#processMessage(data)

while True:
	item = redis.blpop("queue:style")

	data = json.loads(item[1])
	processMessage(data)

