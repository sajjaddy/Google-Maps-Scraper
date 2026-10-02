from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl import Workbook
import time
import os
import sys

def init_driver(custom_binary_path: str = None) -> webdriver.Chrome:
    """Initialize Chrome/Brave WebDriver with resilient binary detection."""
    options = Options()

    # Prioritize user-provided path or environment variable
    binary_path = custom_binary_path or os.getenv("BROWSER_BIN_PATH")

    # If not explicitly specified, check common Brave paths, otherwise Selenium defaults to standard Chrome
    if not binary_path:
        brave_paths = [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]
        for path in brave_paths:
            if os.path.exists(path):
                binary_path = path
                break

    if binary_path and os.path.exists(binary_path):
        print(f"Using browser at: {binary_path}")
        options.binary_location = binary_path
    else:
        print("Using standard Chrome installation.")

    # Useful defaults to reduce unnecessary browser noise
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    return driver


def extract_current_details(driver: webdriver.Chrome, wait: WebDriverWait) -> dict | None:
    try:
        name_elem = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf"))
        )
        name = name_elem.text.strip()
    except Exception:
        name = "Unknown"
        for selector in ["h1.fontTitleLarge", "h1"]:
            try:
                name = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if name:
                    break
            except Exception:
                pass

    if not name or name == "Unknown":
        return None

    # Rating
    rating = "No rating"
    for selector in ["div.F7nice span[aria-hidden='true']", "span.fontBodyMedium span[aria-hidden='true']"]:
        try:
            rating_elem = driver.find_element(By.CSS_SELECTOR, selector)
            if rating_elem.text:
                rating = rating_elem.text.strip()
                break
        except Exception:
            pass

    # Reviews
    reviews = "No reviews"
    for selector in [
        "div.F7nice span[aria-label*='reviews']",
        "span.fontBodyMedium span[aria-label*='reviews']",
        "span[aria-label*='reviews']"
    ]:
        try:
            reviews_elem = driver.find_element(By.CSS_SELECTOR, selector)
            aria_label = reviews_elem.get_attribute('aria-label')
            if aria_label:
                reviews = aria_label.strip()
                break
        except Exception:
            pass

    # Phone
    phone = "No phone"
    for selector in [
        "button[data-item-id*='phone:tel:']",
        "//button[contains(@data-item-id, 'phone')]"
    ]:
        try:
            if selector.startswith("//"):
                phone_elem = driver.find_element(By.XPATH, selector)
            else:
                phone_elem = driver.find_element(By.CSS_SELECTOR, selector)
            if phone_elem.text:
                phone = phone_elem.text.strip()
                break
        except Exception:
            pass

    # Website
    website = "No website"
    for selector in [
        "a[data-item-id='authority']",
        "//a[@data-item-id='authority']"
    ]:
        try:
            if selector.startswith("//"):
                web_elem = driver.find_element(By.XPATH, selector)
            else:
                web_elem = driver.find_element(By.CSS_SELECTOR, selector)
            href = web_elem.get_attribute('href')
            if href:
                website = href.strip()
                break
        except Exception:
            pass

    return {
        "name": name,
        "rating": rating,
        "reviews": reviews,
        "phone": phone,
        "website": website
    }


def scroll(driver: webdriver.Chrome, wait: WebDriverWait):
    print("Scrolling feed to load all results...")
    try:
        scroll_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
    except Exception:
        print("Could not find the results feed container. Skipping scroll.")
        return

    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_div)
    no_change_count = 0
    max_no_change = 4

    while True:
        # Scroll down
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_div)
        time.sleep(2.5)

        # Check if the height of the container has changed
        new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_div)
        if new_height == last_height:
            no_change_count += 1
            if no_change_count >= max_no_change:
                print("Scrolling complete (reached the bottom).")
                break
        else:
            no_change_count = 0
            last_height = new_height

        # Check for 'reached the end' indicator
        try:
            feed_text = scroll_div.text
            if "reached the end of the list" in feed_text.lower() or "end of the list" in feed_text.lower():
                print("End of list indicator found.")
                break
        except Exception:
            pass

        # Safety limit to avoid infinite scrolling on extremely long lists
        try:
            current_results = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
            if len(current_results) >= 200:
                print("Reached safety limit of 200 results. Stopping scroll.")
                break
        except Exception:
            pass


def scrape_and_save(driver: webdriver.Chrome, wait: WebDriverWait, n: str, l: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "Google maps scraping"
    ws.append(["Name", "Rating", "Reviews", "Phone", "Website"])

    # Gather all unique items with their href and expected name
    elements = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
    targets = []
    seen_hrefs = set()

    for elem in elements:
        href = elem.get_attribute("href")
        name = elem.get_attribute("aria-label")
        if href and href not in seen_hrefs:
            seen_hrefs.add(href)
            targets.append({"href": href, "name": name})

    total_count = len(targets)
    print(f"\nFound {total_count} unique results to scrape.")

    scraped_names = set()

    for i, target in enumerate(targets):
        href = target["href"]
        expected_name = target["name"] or "Unknown"
        print(f"\n[{i+1}/{total_count}] Scraping: {expected_name}...")

        clicked = False
        try:
            elem = driver.find_element(By.CSS_SELECTOR, f'a[href="{href}"]')
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
            time.sleep(1)
            elem.click()

            # Wait up to 4 seconds for detail panel to match expected name
            success = False
            for _ in range(8):
                try:
                    current_name = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text.strip()
                    if current_name and (expected_name.lower() in current_name.lower() or current_name.lower() in expected_name.lower()):
                        success = True
                        break
                except Exception:
                    pass
                time.sleep(0.5)

            if success:
                clicked = True
            else:
                print("Detail panel did not update, navigating directly to link...")
        except Exception as e:
            print(f"Could not click directly: {e}. Navigating directly...")

        # Fallback to direct navigation if clicking didn't update the pane
        if not clicked:
            try:
                driver.get(href)
                time.sleep(3.5)
            except Exception as e:
                print(f"Failed to navigate to {href}: {e}")
                continue

        # Extract details using the helper
        details = extract_current_details(driver, wait)
        if details:
            name = details["name"]

            # Prevent duplicates in Excel
            if name in scraped_names:
                print(f"Skipping duplicate record for '{name}'")
                continue

            scraped_names.add(name)
            ws.append([details["name"], details["rating"], details["reviews"], details["phone"], details["website"]])
            print(f"✓ Scraped: {details['name']} | Rating: {details['rating']} | Phone: {details['phone']}")
        else:
            print("Failed to extract details.")

    # Clean filename of disallowed characters
    safe_name = "".join(c for c in n if c.isalnum() or c in (" ", "_", "-")).strip()
    safe_loc = "".join(c for c in l if c.isalnum() or c in (" ", "_", "-")).strip()
    filename = f"{safe_name}_{safe_loc}_results.xlsx"
    wb.save(filename)
    print(f"\n✓ Data successfully saved to {filename}")


def run_scraper(name: str = None, location: str = None, browser_bin: str = None):
    # Change working directory to the folder containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if not name:
        name = input("Enter Business Name / Category: ").strip()
    if not location:
        location = input("Enter Location: ").strip()

    if not name or not location:
        print("Business Name and Location cannot be empty.")
        return

    driver = None
    try:
        driver = init_driver(custom_binary_path=browser_bin)
        wait = WebDriverWait(driver, 10)

        search_query = f"{name} in {location}"
        print(f"\nNavigating to Google Maps for: '{search_query}'...")
        driver.get(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}")

        # Wait for the page to initialize
        time.sleep(4)

        # Check if we landed directly on a single place detail page instead of a list
        is_single_place = False
        try:
            driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf")
            try:
                driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            except NoSuchElementException:
                is_single_place = True
        except NoSuchElementException:
            pass

        if is_single_place:
            print("Redirected directly to a single business page. Scraping directly...")
            wb = Workbook()
            ws = wb.active
            ws.title = "Google maps scraping"
            ws.append(["Name", "Rating", "Reviews", "Phone", "Website"])

            details = extract_current_details(driver, wait)
            if details:
                ws.append([details["name"], details["rating"], details["reviews"], details["phone"], details["website"]])
                print(f"✓ Scraped: {details['name']} | Rating: {details['rating']} | Phone: {details['phone']}")

            safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip()
            safe_loc = "".join(c for c in location if c.isalnum() or c in (" ", "_", "-")).strip()
            filename = f"{safe_name}_{safe_loc}_results.xlsx"
            wb.save(filename)
            print(f"\n✓ Data successfully saved to {filename}")
        else:
            scroll(driver, wait)
            scrape_and_save(driver, wait, name, location)

    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred during scraping: {e}")
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    run_scraper()