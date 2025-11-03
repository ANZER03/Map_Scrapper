## Maps Scraper

A Streamlit-based Google Maps scraper that collects business details (name, category, address, phone, website) for user-provided keywords and locations. It can also visit discovered websites to extract email addresses and export results to CSV/XLSX or to a Google Sheet.

### Key Features
- Scrape Google Maps results in parallel using Selenium
- Collect: name, category, address, phone number, website
- Extract emails from discovered websites (async or threaded)
- Download results as CSV/XLSX
- Push results to Google Sheets via a Service Account

### Typical Use Cases
- Lead generation for local businesses matching a niche and geography
- Market research on categories of businesses across cities/regions
- Enriching business listings with contact emails

## Project Structure
- `app.py`: Main Streamlit application
- `Test/`: Experimental and playground scripts (not required to run the app)
  - `map_scraper.py`, `UI.py`, etc.
- `scrapper-*.json`: Google Cloud service account credentials file (used for Google Sheets export)

## Prerequisites
- Python 3.9+ recommended
- Google Chrome installed
- Internet access
- (Optional) Google Cloud Service Account JSON for Sheets export

Selenium/WebDriver:
- Selenium 4 can auto-manage drivers on many systems. If auto-management fails, install a matching ChromeDriver or set the `PATH` accordingly.

Google Sheets (optional):
- Create a Google Service Account and download the credentials JSON.
- Share your Google Sheet (named `list_enterprises` by default) with the service account email.
- Place the credentials JSON at the repository root and ensure `app.py` references the correct filename in `insert_into_sheet()`.

## Setup
1) Clone or copy the repository.
2) Create and activate a virtual environment.

Windows (PowerShell):
```bash
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

macOS/Linux (bash):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) Install dependencies:
```bash
pip install -r requirements.txt
```

4) (Optional) Configure Google Sheets export:
- Ensure your credentials file (e.g., `scrapper-421600-b8486ed62c07.json`) is at the repo root.
- In `app.py`, function `insert_into_sheet()`, adjust the `filename=` to your credentials filename if different.
- Make sure a Google Sheet named `list_enterprises` exists and is shared with the service account.

## Running the App
From the project root:
```bash
streamlit run app.py
```

The app will open in your browser. If it doesn’t, visit the local URL Streamlit prints (e.g., `http://localhost:8501`).

## How to Use
1) In the UI, enter keywords (one per line) and optionally locations (one per line).
   - If locations are provided, the app generates every combination `keyword (location)`.
2) Choose the number of threads and the scroll time.
3) Click "Start Scraping" to collect business data from Google Maps.
4) Optional actions after scraping:
   - "Extract Emails from Webpages": visits each `website` and extracts email-like strings.
   - "Send Data To Sheets": uploads the current table to your Google Sheet.
   - "Download CSV" / "Download XLSX": export data locally.
   - "Display Data" or "Display Query Not Work": review results and any failed queries.

Notes:
- Scraping is subject to Google’s Terms of Service. Use responsibly.
- Heavy scraping can trigger rate-limiting or blocking. Adjust timeouts, scrolling, and thread counts if you encounter issues.

## Configuration Tips
- Headless mode: The code includes options to toggle headless; uncomment/add as needed for your environment.
- Driver selection: The code uses Chrome by default. You can adapt to Firefox/Edge if desired.
- Parser: BeautifulSoup uses the built-in `html.parser`. You can install and set `lxml` for performance if needed.

## Troubleshooting
- WebDriver errors: Ensure Chrome is installed and versions of Chrome/Selenium/ChromeDriver are compatible. Try updating Chrome and reinstalling Selenium.
- Permission errors on Windows: Run PowerShell as Administrator when needed or adjust execution policy for activating the virtual environment.
- Google Sheets auth errors: Verify the credentials filename, sheet name, and sharing to the service account email.


