import asyncio
import csv
from bs4 import BeautifulSoup
from bs4.element import Tag
from playwright.async_api import async_playwright, expect

# --- Configuration ---
YEAR_FILTER = "2024"
STATUS_FILTER = "Didaftar"
TARGET_PAGES = 3
OUTPUT_FILENAME = f'dataset_pdki_{YEAR_FILTER}.csv'

# This list will hold the initial data scraped from the search result pages
initial_scraped_data = []

async def scrape_search_results(url, target_page_number):
    # Navigates the website, applies filters, iterates through pagination, and scrapes the data from each search result page.
    print("--- Starting Scraper ---")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Step 1: Go to the page and apply all filters
            await page.goto(url, wait_until='networkidle')
            await apply_filters(page)

            # Step 2: Loop through the specified number of pages
            for i in range(1, target_page_number + 1):
                print("-" * 20)
                print(f"Navigating to page {i}...")

                # Navigate to the correct page
                await page.get_by_role("button", name=str(i), exact=True).click()
                await page.wait_for_load_state('networkidle', timeout=3000000)
                await asyncio.sleep(4)

                # Step 3: Parse the content of the current page
                print(f"Parsing data from page {i}...")
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                parse_page_data(soup)

                print(f"Page {i} scraping complete.")

        except Exception as e:
            print(f"❌ An error occurred during scraping: {e}")
            await page.screenshot(path='error_screenshot.png')
            print("Saved 'error_screenshot.png' for debugging.")
        finally:
            await browser.close()
            print("--- Scraper Finished ---")

async def apply_filters(page):
    # Applies status, year, and search term filters to the search page.
    print("Applying filters...")

    # Apply Status Filter
    didaftar_checkbox = page.locator(f"label:has-text('{STATUS_FILTER}')").locator("..").locator("button[role='checkbox']")
    await didaftar_checkbox.check()
    await expect(didaftar_checkbox).to_be_checked(timeout=300000)
    await page.wait_for_load_state('networkidle', timeout=300000)
    await asyncio.sleep(3)

    # Apply Year Filter
    await page.locator("text=Tahun Permohonan").scroll_into_view_if_needed()
    await asyncio.sleep(3)
    await page.click('button:has-text("Semua Tahun")')
    await asyncio.sleep(3)
    await page.get_by_role("option", name=YEAR_FILTER, exact=True).click()
    await asyncio.sleep(3)

    # Click "Terapkan" to apply year filter
    await page.click('button:has-text("Terapkan")')
    await page.wait_for_load_state("networkidle")

    # Wait for pagination to ensure results are loaded
    await page.get_by_text("1", exact=True).wait_for(state='visible', timeout=3000000)
    print("Filters applied successfully.")

def parse_page_data(soup):
    # Parses the HTML of a single search result page to extract brand data.
    brand_containers = soup.find_all('div', class_='flex flex-col border-b pb-4 border-y-50')

    for container in brand_containers:
        brand_info = {}

        # --- Parse Text Data ---
        brand_tag = container.find('h1', class_='text-md md:text-lg cursor-pointer')
        brand_info['Brand'] = brand_tag.get_text(strip=True) if brand_tag else "N/A"

        owner_tag = container.find('div', class_='flex gap-1 text-sm')
        brand_info['Nama Pemilik'] = owner_tag.get_text(strip=True).replace("Nama Pemilik:1.", "").strip() if owner_tag else "N/A"

        nomor_tag = container.find('p', class_='text-gray-400 font-medium text-sm')
        app_number = nomor_tag.get_text(strip=True) if nomor_tag else ""
        brand_info['Nomor Permohonan'] = app_number

        brand_info['Tahun Permohonan'] = YEAR_FILTER
        brand_info['Status'] = STATUS_FILTER

        #Parse kode kelas
        kode_kelas_raw = container.find_all('p', class_="text-sm")
        for each in kode_kelas_raw:
            valid = True
            temp_kode_kelas = each.get_text(strip=True)
            temp_fix_class = temp_kode_kelas.replace("Kode kelas: ", "").split(",")
            for each_in in temp_fix_class:
                if (not each_in.isnumeric() and each_in != "") or (len(each_in) > 2) or (each_in.isnumeric() and ("Kode kelas: " not in temp_kode_kelas)):
                    valid = False
                    break
            if not valid:
                continue
            else:
                brand_info['Kode Kelas'] = temp_fix_class
                break

        desc_tag = container.find('p', class_="text-gray-400 font-medium text-sm line-clamp-1 text-ellipsis w-full")
        brand_info['Deskripsi Kelas'] = desc_tag.get_text(strip=True) if desc_tag else ""

        initial_scraped_data.append(brand_info)

async def process_multiple_classes(scraped_data):
    # Processes items with multiple class codes by visiting their detail pages to get individual class descriptions.
    print("\n--- Processing Multi-Class Items ---")
    final_data_processed = []

    # Setup a single browser instance for efficiency
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Step 1: Open search page
        await page.goto("https://pdki-indonesia.dgip.go.id/search", wait_until="networkidle")
        await asyncio.sleep(2)

        for idx, item in enumerate(scraped_data):
            # Check if the item has more than one class code
            if len(item['Kode Kelas']) > 1:
                print(f"Fetching details for '{item['Brand']}' ({item['Nomor Permohonan']})...")
                try:
                    # Step 2: Enter keyword and search
                    await page.fill("input >> nth=0", item['Nomor Permohonan'])
                    await asyncio.sleep(1)
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(2)

                    await page.wait_for_selector('a[href^="/link/"]', timeout=3000000)
                    await asyncio.sleep(1)
                    await page.click('a[href^="/link/"]')
                    await asyncio.sleep(3)

                    await page.wait_for_selector('text=Nomor Registrasi', timeout=3000000)
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')

                    # Scrape all class descriptions from the detail page table
                    descriptions = []
                    for tbody in soup.find_all('tbody'):
                        if isinstance(tbody, Tag):
                            for row in tbody.find_all('tr'):
                                if isinstance(row, Tag):
                                    tds = row.find_all('td')
                                    if len(tds) >= 2:
                                        descriptions.append(tds[1].get_text(strip=True))

                    # Create a new row for each class
                    for i, class_code in enumerate(item['Kode Kelas']):
                        new_row = item.copy() # Copy base info
                        new_row['Kode Kelas'] = class_code.strip()
                        new_row['Deskripsi Kelas'] = descriptions[i] if i < len(descriptions) else "N/A"
                        final_data_processed.append(new_row)

                except Exception as e:
                    print(f"❌ Error processing multi-class item {item['Nomor Permohonan']}: {e}")
                    # If it fails, add the original item back with joined classes
                    item['Kode Kelas'] = ", ".join(item['Kode Kelas'])
                    final_data_processed.append(item)
            else:
                # For single-class items, just format and add
                item['Kode Kelas'] = item['Kode Kelas'][0] if item['Kode Kelas'] else ""
                final_data_processed.append(item)

        await browser.close()

    print("--- Multi-Class Processing Finished ---")
    return final_data_processed

def save_data_to_csv(data_to_save):
    # Saves the final processed data to a CSV file.
    print(f"\n--- Saving data to {OUTPUT_FILENAME} ---")
    if not data_to_save:
        print("No data to save.")
        return

    with open(OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
        # Define headers from the keys of the first dictionary item
        fieldnames = ['No'] + list(data_to_save[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for idx, row_data in enumerate(data_to_save, start=1):
            row_data_with_index = {'No': idx, **row_data}
            writer.writerow(row_data_with_index)

    print(f"✅ Successfully saved {len(data_to_save)} rows to {OUTPUT_FILENAME}")

async def main():
    # Main function to orchestrate the scraping process.
    url_to_scrape = "https://pdki-indonesia.dgip.go.id/search"

    # 1. Scrape the initial data from search result pages
    await scrape_search_results(url_to_scrape, TARGET_PAGES)

    # 2. Process items with multiple classes to get detailed descriptions
    final_data = await process_multiple_classes(initial_scraped_data)

    # 3. Save the final, clean data to a CSV file
    save_data_to_csv(final_data)

if __name__ == '__main__':
    asyncio.run(main())
