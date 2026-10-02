# Google Maps Business Scraper

An automated Python tool to scrape business details (Name, Rating, Reviews count, Phone Number, Website) from Google Maps searches and export the results to an Excel (`.xlsx`) spreadsheet.

---

## Features
- **Automated Feed Scrolling**: Dynamically scrolls Google Maps results feed to gather place listings.
- **Detailed Information Extraction**:
  - Business Name
  - Rating & Total Reviews
  - Phone Number
  - Website link
- **Deduplication**: Automatically skips duplicate listings.
- **Single Business Detection**: Gracefully handles searches that lead directly to a single business page.
- **Excel Output**: Generates cleanly formatted `.xlsx` files named by your query and location.
- **Browser Compatibility**: Works out-of-the-box with Google Chrome or Brave Browser.

---

## Prerequisites
- **Python 3.10+** (Python 3.12+ / 3.14 compatible)
- Google Chrome or Brave Browser installed on your system.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/google-maps-scraper.git
   cd google-maps-scraper
   ```

2. **Create and activate a virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   Using `pip`:
   ```bash
   pip install openpyxl selenium
   ```
   Or using `uv`:
   ```bash
   uv sync
   ```

---

## Configuration (Optional)

If you are using a custom browser path (such as Brave Browser or a non-standard Chrome location), you can set the `BROWSER_BIN_PATH` environment variable:

```powershell
# Windows PowerShell example
$env:BROWSER_BIN_PATH="C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
```
Or copy `.env.example` to `.env`. If not provided, it will automatically detect Brave at standard installation paths or fall back to standard Google Chrome.

---

## Usage

Run the program via [main.py](file:///f:/python/Maps%20Scraper/main.py):

```bash
python main.py
```

You will be prompted to enter:
1. **Business Name / Category** (e.g. `gyms`, `dentists`, `coffee shops`)
2. **Location** (e.g. `Dubai`, `New York`, `London`)

The script will launch the browser, conduct the search, scroll the results, extract details, and save them into `<category>_<location>_results.xlsx`.

---

## GitHub Readiness & Privacy
- Sensitive / local files (`.env`, virtual environments `.venv`, and generated `.xlsx` spreadsheets) are ignored by git via [.gitignore](file:///f:/python/Maps%20Scraper/.gitignore).
- No hardcoded personal paths or credentials exist in the source code.
