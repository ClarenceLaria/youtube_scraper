# 🎬 YouTube Channel Transcript Scraper (GUI)

A desktop application built with **Python + Tkinter** that allows users to:

- Input a YouTube channel URL  
- Automatically resolve the Channel ID  
- Fetch latest videos from the channel  
- Retrieve transcripts for each video  
- Extract view counts  
- Rank videos by popularity  
- Export results to CSV  

This project combines:

- YouTube Data API v3  
- `youtube-transcript-api`  
- Pandas  
- Tkinter GUI  
- Multithreading for smooth UI experience  

---

## Features

- Accepts full channel URL (no need to manually extract channel ID)
- Fetches latest N videos
- Retrieves English transcripts
- Gets video view counts
- Ranks videos by popularity
- Saves results as CSV
- Threaded scraping (UI does not freeze)
- Live log output inside GUI

---

## 📁 Project Structure
```bash
│
├── gui.py # Tkinter GUI
├── scraper_logic.py # Core scraping logic
├── requirements.txt # Dependencies
└── README.md
```

---

## 🧰 Requirements

- Python 3.8+
- YouTube Data API Key

---

## 🔧 Installation

### Clone the Repository

```bash
git clone https://github.com/ClarenceLaria/youtube_scraper.git
cd youtube_scraper
```

---

### Create a Virtual Environment (Recommended)
```bash
python -m venv venv
```

--- 

#### Activate it:

Windows
```bash
venv\Scripts\activate
```

Mac/Linux
```bash
source venv/bin/activate
```

---

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

### Getting a YouTube API Key
Go to: https://console.cloud.google.com/

Create a new project

Enable YouTube Data API v3

Navigate to Credentials

Click Create API Key

Copy the generated key

You will paste this into the GUI when running the application.

---

### Running the Application

Run:
```bash
python gui.py
```

#### Then:

Enter YouTube API key

Enter channel URL

Enter maximum number of videos

Choose save folder

Click Start Scraping

---

## 📜 License
MIT License

Copyright (c) 2026 Clarence Laria

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Author
### Clarence Laria
Full-Stack Developer with experience in React, Next.js, Node.js, Python, and Flutter.  
Passionate about building intelligent automation tools, scalable systems, and user-friendly applications that solve real-world problems.
