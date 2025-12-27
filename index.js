// index.js
const express = require("express");
const fs = require("fs");
const path = require("path");
const axios = require("axios");

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const DATA_FILE = path.join("/tmp", "urls.json");

// Ensure file exists
if (!fs.existsSync(DATA_FILE)) {
  fs.writeFileSync(DATA_FILE, JSON.stringify([]));
}

function loadUrls() {
  return JSON.parse(fs.readFileSync(DATA_FILE, "utf-8"));
}

function saveUrls(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

// Site checker
async function checkSites() {
  const urls = loadUrls();
  const now = Date.now() / 1000;

  for (let site of urls) {
    if (!site.next_check) site.next_check = now;
    if (now >= site.next_check) {
      try {
        const res = await axios.get(site.url, { timeout: 10000 });
        site.status = res.status === 200 ? "UP" : "DOWN";
      } catch {
        site.status = "DOWN";
      }
      site.last_check = now;
      site.next_check = now + site.interval;
    }
  }

  saveUrls(urls);
}

// Periodic check every 5 seconds
setInterval(checkSites, 5000);

// Routes
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

app.get("/data", (req, res) => {
  const urls = loadUrls();
  const now = Date.now() / 1000;
  urls.forEach(u => {
    u.remaining = Math.max(0, Math.floor(u.next_check - now));
  });
  res.json(urls);
});

app.post("/add", (req, res) => {
  const data = loadUrls();
  const now = Date.now() / 1000;
  const newSite = {
    id: Date.now(),
    name: req.body.name,
    url: req.body.url,
    interval: parseInt(req.body.interval),
    status: "UNKNOWN",
    last_check: 0,
    next_check: now
  };
  data.push(newSite);
  saveUrls(data);
  res.send("OK");
});

app.post("/edit/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const data = loadUrls();
  for (let site of data) {
    if (site.id === id) {
      site.name = req.body.name;
      site.url = req.body.url;
      site.interval = parseInt(req.body.interval);
      break;
    }
  }
  saveUrls(data);
  res.send("OK");
});

// Start server
const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server running on port ${port}`));
