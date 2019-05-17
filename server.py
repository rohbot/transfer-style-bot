from flask import Flask, render_template, jsonify, request, json
import requests
import wget
from evaluate import ffwd_to_img
#from redis import Redis
import os
import random
import sys

#redis = Redis()

app = Flask(__name__)

#bot_token = redis.get('bot:token') 
bot_token = os.environ.get('BOT_TOKEN')

if not bot_token:
	print "telegram Bot Token not set in environ variables"	
	sys.exit(1)
print "BOT_TOKEN", bot_token
thread = None

#checkpoint_dir = 'chkpt/'
checkpoint_dir = 'checkpoints/'

ckpt_files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(checkpoint_dir):
    for file in f:
        if '.ckpt' in file:
            ckpt_files.append(os.path.join(r, file))

for f in ckpt_files:
    print(f)



# def background_thread():
# 	"""Example of how to send server generated events to clients."""
# 	while True:
# 		item = redis.blpop("queue:style")

# 		data = json.loads(item[1])
# 		processMessage(data)



def get_url(method):
  return "https://api.telegram.org/bot{}/{}".format(bot_token,method)

def get_image(file_path):
	url = "https://api.telegram.org/file/bot{}/{}".format(bot_token,file_path)
	#cmd = "curl -o {} {}".format(file_path, url)
	print "getting image:", url
	wget.download(url, file_path)
	#os.system(cmd)
	in_path = file_path
	out_path = 'static/' + in_path
	checkpoint_dir = 'checkpoints/udnie.ckpt'
	print in_path, out_path
	ffwd_to_img(in_path, out_path, random.choice(ckpt_files))
	
	return out_path	

def sendMessage(chat_id, msg):
	data = {}
	data["chat_id"] = chat_id
	data["text"] = msg
	url = "https://api.telegram.org/bot{}/{}".format(bot_token,"sendMessage")
	print "Sending", chat_id, ": ",  msg
	r = requests.post(url, data=data)



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

	ffwd_to_img(in_path, out_path, random.choice(ckpt_files))


	print "done image"
	sendPhoto(data['chat_id'], "https://dl2.rohbot.cc/" + out_path)




@app.route("/{}".format(bot_token), methods=["POST"])
def process_update():
    global thread


    if request.method == "POST":
        
        update = request.get_json()
        if "message" in update:
        	print json.dumps(update)
        	msg = update['message']
        	try:

	        	if "photo" in msg:
	        		print "photos:",  len(msg['photo'])
	                if len(msg['photo']) > 2:
	                    file_id = msg['photo'][2]['file_id']
	                else:
	                    file_id = msg['photo'][0]['file_id']
	                print "File id:", file_id
	                r = requests.post(get_url("getFile"), data={'file_id':file_id})
	                data = r.json()
	                data["chat_id"] = update["message"]["from"]["id"]
	                #redis.rpush("queue:style", json.dumps(data))
	                #return "ok", 200
                	processMessage(data)
        	except:
        		print "Unexpected error:", sys.exc_info()[0]

                #redis.rpush("queue:style", json.dumps(data))
    	    	# file_path = data['result']['file_path']
        		# print "new file path", file_path
        		# new_img = get_image(file_path)
        		# print new_img
        		# data = {}
        		# data["text"] = "https://dl2.rohbot.cc/" + new_img
        		# r = requests.post(get_url("sendMessage"), data=data)

            #process_message(update)
        return "ok!", 200



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
	app.run(debug=True)
	#app.run(host='0.0.0.0',port=int(os.environ.get('PORT', 5000)))
