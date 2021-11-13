from flask import Flask
from flask import make_response, send_file

import requests
import json
import subprocess

app = Flask(__name__)
 
@app.route('/')
def home():
    return json.dumps({"status": "ok"})

@app.route('/api/v1/tor')
def tor():
    r = requests.get("https://onionoo.torproject.org/details?search=family:6D04FFDA1E5E352B9F7477D3E15BB1B59B459691")
    api = r.json()

    bandwidth = 0

    relay = []

    for i in range(3):
        #print(api["relays"][i]["nickname"])
        bandwidth = bandwidth + int(api["relays"][i]["observed_bandwidth"])
        relay.append(api["relays"][i]["nickname"])

    #print(api["relays"][1]["nickname"])

    new = round(bandwidth, 3) * 8
    new2 = round(bandwidth, 3)

    mbps = round(new * 0.000001, 1)
    mbs = round(new2 * 0.000001, 1)

    final = {"nodes": relay, "bandwidth": {"mbps": mbps, "mbs": mbs}}


    
    return json.dumps(final)


@app.route('/api/v1/metrics')
def b():
    def vnStatGetJSON():
        result = subprocess.run(['vnstat', '--json'], stdout=subprocess.PIPE)
        json_blob = result.stdout.decode('utf-8')
        return json_blob
    api = json.loads(vnStatGetJSON())
    rx = api["interfaces"][0]["traffic"]["total"]["rx"]
    tx = api["interfaces"][0]["traffic"]["total"]["tx"]
    total = rx + tx
    divide = 1024*3
    all_bandwidth = round(total/1073741824, 2)
    all_bandwidth_tb = all_bandwidth/1024
    return json.dumps({"total_bandwidth": {"GB": all_bandwidth, "TB": all_bandwidth_tb}})

@app.route('/api/v1/apache')
def apache():

    web_server = "apache2" # CHANGE THIS TO THE WEB SERVER!!!

    result = subprocess.run(['wc', '-l', '/var/log/' + web_server + '/access.log'], stdout=subprocess.PIPE)
    l = result.stdout.decode('utf-8')
    fi = l[:-26]
    apache_today = fi.strip()

    result = subprocess.run(['wc', '-l', '/var/log/' + web_server + '/access.log.1'], stdout=subprocess.PIPE)
    l = result.stdout.decode('utf-8')
    fi = l[:-26]
    apache_yesterday = fi.strip("/v")
    return json.dumps({"traffic": {"today": apache_today, "yesterday": apache_yesterday.strip()}})

@app.route('/api/v1/youtube')
def youtube():
    youtube_home = requests.get("https://www.youtube.com")
    youtube_thumb = requests.get("https://i.ytimg.com/vi/N9PcNrhiMUc/mqdefault.jpg")
    youtube_video = requests.get("https://www.youtube.com/watch?v=ci1PJexnfNE")
    youtube_feeds = requests.get("https://www.youtube.com/feeds/videos.xml?channel_id=UCeeFfhMcJa1kjtfZAGskOCA")

    return json.dumps({"homepage": youtube_home.status_code, "thumbnails": youtube_thumb.status_code, "videos": youtube_video.status_code, "feeds": youtube_feeds.status_code})
 
@app.errorhandler(404)
def page_not_found(e):
    return json.dumps({"status": "404"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
