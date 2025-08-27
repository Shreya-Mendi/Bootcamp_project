🌍 Global Flight Snapshot (via OpenSky Network)

This project is a Streamlit dashboard that visualizes live aircraft data from the OpenSky Network API. It fetches a real-time snapshot of active flights (~1,800 aircraft globally) and displays:

Number of active flights

Top 30 countries by active flights (bar chart)

Scatter map of global flight positions

Top 10 Airlines departed from RDU in the last 6 hours

Airline Profile Comparison (provides profile comparisons of various airlines based on data fetched from the AviationStack API)


📦 Prerequisites

Before running the app, make sure you have:
Python 3.11+ installed (The version of Python this project uses is 3.11.0)
Access to the internet (to fetch live OpenSky API data)
pip package manager

⚙️ Installation

Clone this repository or copy the source files:

git clone https://github.com/Shreya-Mendi/Bootcamp_project.git
cd Bootcamp_project/


(Optional but recommended) Create a virtual environment:

python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

Install the required dependencies:

pip install -r requirements.txt


📂 Project Structure

.

├── fetchapi.py           # Fetches flight snapshot from OpenSky API

├── streamlit_app.py      # Streamlit dashboard

├── requirements.txt      # Python dependencies

└── README.md             # Project documentation


🚀 Usage

Run locally

Start the Streamlit app:
streamlit run streamlit_app.py
This will open a browser window at http://localhost:8501.

Example Workflow

Click "Fetch Live Flights"
View:
Total number of flights in the snapshot
Top 30 countries by active flights (bar chart)
Global scatter map of flight positions

Click "Fetch RDU Data" View:
Bar Graph of Top 10 Airlines from RDU

Scroll Down To "Airline Profile Comparison"
Choose the type of profile comparison you would like to see (fleet size, fleet average age, and founding year) and pick a country of origin to filter by (select "All Countries" if you do not want to filter by a specific country). View: Bar graph representing profile comparison only with the airlines that align with the country of origin filter

Run cli_demo.py

python cli_demo.py (Windows PowerShell)

python3 clit_demo.py (MacOS/Linux)


⚠️ Notes & Limitations

The OpenSky free API is rate-limited (about 1 request every 10 seconds, max ~1,800 aircraft per snapshot).
If no flights are shown, try again after a few seconds.
Only live data is shown—no historical flight data is stored.

🧠 Data Source

All data comes from the public OpenSky API
Snapshot is limited to ~1800 flights by the free tier

🌐 Live Demo

👉 View it on Hugging Face Spaces:
🔗 https://huggingface.co/spaces/ShreyaMendi/Skyline 

Global Flight Positions (Scatter Map)
A scatter plot of aircraft positions by latitude/longitude.


![Skyline Image](airplane.jpg)

Photo by <a href="https://unsplash.com/@artturijalli?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Artturi Jalli</a> on <a href="https://unsplash.com/photos/white-airplane-under-blue-sky-during-daytime-Su1gc1A63xE?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>