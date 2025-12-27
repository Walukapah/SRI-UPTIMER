from flask import Flask, request, jsonify
import requests
import time
import os
import json

app = Flask(__name__)

DATA_FILE = "/tmp/urls.json"

def load_urls():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)

def save_urls(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@app.route("/data")
def data():
    urls = load_urls()
    now = time.time()

    for site in urls:
        if now >= site["next_check"]:
            try:
                r = requests.get(site["url"], timeout=10)
                site["status"] = "UP" if r.status_code == 200 else "DOWN"
            except:
                site["status"] = "DOWN"

            site["last_check"] = now
            site["next_check"] = now + site["interval"]

    save_urls(urls)
    return jsonify(urls)

@app.route("/add", methods=["POST"])
def add():
    data = load_urls()
    data.append({
        "id": int(time.time()*1000),
        "name": request.json["name"],
        "url": request.json["url"],
        "interval": request.json["interval"],
        "status": "UNKNOWN",
        "last_check": 0,
        "next_check": time.time()
    })
    save_urls(data)
    return {"ok": True}
