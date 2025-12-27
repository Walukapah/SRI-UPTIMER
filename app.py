from flask import Flask, render_template, request, jsonify
import requests
import time
import json
import os
import threading

app = Flask(__name__)

DATA_FILE = "/tmp/urls.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_urls():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_urls(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def check_sites():
    while True:
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
        time.sleep(5)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    urls = load_urls()
    now = time.time()
    for u in urls:
        u["remaining"] = max(0, int(u["next_check"] - now))
    return jsonify(urls)

@app.route("/add", methods=["POST"])
def add():
    data = load_urls()
    new = {
        "id": int(time.time() * 1000),
        "name": request.form["name"],
        "url": request.form["url"],
        "interval": int(request.form["interval"]),
        "status": "UNKNOWN",
        "last_check": 0,
        "next_check": time.time()
    }
    data.append(new)
    save_urls(data)
    return "OK"

@app.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    data = load_urls()
    for site in data:
        if site["id"] == id:
            site["name"] = request.form["name"]
            site["url"] = request.form["url"]
            site["interval"] = int(request.form["interval"])
            break
    save_urls(data)
    return "OK"

if __name__ == "__main__":
    threading.Thread(target=check_sites, daemon=True).start()
    app.run(host="0.0.0.0", port=7860)
