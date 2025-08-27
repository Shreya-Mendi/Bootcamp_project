# 🌐 Skyline

## 🌍 Overview

This project is an aviation-themed Streamlit application that provides visualizations for live aircraft data, RDU statistics, and airline profiles. 

## 🧩 Breakdown of Core Features

### 1. Global Flight Snapshot (via OpenSky Network)
- Fetches a real-time snapshot of active flights (~1,800 aircraft globally) by leveraging live aircraft data from the OpenSky Network API
- Displays
    
    (a) Number of active flights
    
    (b) Top 30 countries by active flights (bar chart)
    
    (c) Scatter map of global flight positions

### 2. Raleigh-Durham (RDU) Airport Stats
- Displays the Top 10 Airlines departed from RDU in the last 6 hours through the use of the OpenSky Network API

### 3. Airline Profile Comparison
- Provides different profile comparisons of various airlines (including fleet size, fleet average age, and founding year) based on the user's preferences as well as data fetched from the aviationstack API

## 🚩 Getting Started

### 📦 Prerequisites

Before running the app, make sure you have:
- Python 3.11+ installed (The version of Python this project uses is 3.13.5)
- Access to the internet (to fetch live OpenSky API data) pip package manager
- Access to an aviationstack API key

### ⚙️ Installation

#### 1. Clone this repository or copy the source files:

- git clone https://github.com/Shreya-Mendi/Bootcamp_project.git
cd Bootcamp_project/

#### 2. (Optional but recommended) Create and activate a virtual environment:

#### MacOS/Linux

- python3 -m venv .venv
- source venv/bin/activate

#### Windows

- python -m venv .venv
- .venv\Scripts\Activate.ps1

#### 3. Install the required dependencies:
- pip install -r requirements.txt


### 📂 Project Structure
├── src/
│   ├── cli_demo.py # Fetches flight snapshot from OpenSky API and airline data from  aviationstack API
│   └── streamlit_app.py  # Streamlit application

├── .gitattributes # How Git should treat files

├── .gitignore # Files to ignore

├── airplane.jpg # Airplane picture in README

├── Dockerfile # Set up environment and dependencies for deployment

├── README.md  # Project documentation

└── requirements.txt  # Python dependencies



## 🚀 Usage

### Run locally

Start the Streamlit app:
streamlit run src/streamlit_app.py
This will open a browser window at http://localhost:8501.

### Example Workflow

#### Click "Fetch Live Flights"

- <u>View:</u> Total number of flights in the snapshot
Top 30 countries by active flights (bar chart)
- <u>View:</u> Global Flight Positions (Scatter Map): A scatter plot of aircraft positions by latitude/longitude.

#### Click "Fetch RDU Data" 
- <u>View:</u> Bar Graph of Top 10 Airlines from RDU

#### Scroll Down To "Airline Profile Comparison":
- Choose the type of profile comparison you would like to see (fleet size, fleet average age, and founding year)

- Pick a country of origin to filter by (select "All Countries" if you do not want to filter by a specific country)

- <u>View ("All Countries" Option):</u> Bar graph representing profile comparison only with the top 10 largest airlines (if the fleet size option is selected), top 10 youngest airlines (if the fleet average age size is selected), top 10 oldest airlines by founding year (if the founding year option is selected)

- <u>View (Not "All Countries" Option):</u> Bar graph representing profile comparison with all the airlines that align with the country of origin filter

### Run cli_demo.py

python src/cli_demo.py (Windows PowerShell)

python3 src/cli_demo.py (MacOS/Linux)


## ⚠️ Notes & Limitations

- The OpenSky free API is rate-limited (about 1 request every 10 seconds, max ~1,800 aircraft per snapshot).
If no flights are shown, try again after a few seconds.
Only live data is shown—no historical flight data is stored.
- The aviationstack API is limited to 100 requests per month with the free tier. Moreover, multiple requests are made to the aviationstack API as the user chooses different comparison types and country of origin filters for the Airline Profile Comparison feature.

## 🧠 Data Source

Data comes from the public OpenSky API
Snapshot (limited to ~1800 flights by the free tier) and the aviationstack API (limited to 100 requests per month with the free tier)

## 🌐 Live Demo

👉 View on Hugging Face Spaces:
🔗 https://huggingface.co/spaces/ShreyaMendi/Skyline 

![Skyline Image](airplane.jpg)
Photo by <a href="https://unsplash.com/@artturijalli?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Artturi Jalli</a> on <a href="https://unsplash.com/photos/white-airplane-under-blue-sky-during-daytime-Su1gc1A63xE?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>