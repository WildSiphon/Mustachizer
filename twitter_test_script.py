from modules.mustache.mustachizer import Mustachizer
from urllib.request import urlopen
from io import BytesIO
from PIL import ImageShow

url = "https://pbs.twimg.com/media/E7-7oUPXoAMOZWR.jpg"
must = Mustachizer(debug=True)

url_file = urlopen(url)
image_buffer = url_file.read()
output = must.mustachize(BytesIO(image_buffer),"JPEG")
with open('./img/tmp/0','wb') as out:
    out.write(output.read())


# from time import sleep
# from modules.twitter.bot import BotTwitter

#twitter = BotTwitter(debug=True)
# while True:
# 	twitter.reply_to_last_mentions()
# 	sleep(10)