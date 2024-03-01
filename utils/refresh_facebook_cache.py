# Dependencies: pip install splinter tqdm
import argparse
import time
from urllib.parse import quote
from pathlib import Path

from splinter import Browser
from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument("--browser", default="firefox")
parser.add_argument("--max-page-load", type=float, default=10.0)
parser.add_argument("--wait-load-time", type=float, default=0.5)
parser.add_argument("--interval-between-actions", type=float, default=15.0)
parser.add_argument("--interval-if-ok", type=float, default=3.0)
parser.add_argument("urls_filename", type=Path, help="Text file with one URL per line")
parser.add_argument("done_filename", type=Path, help="File to be created, storing URLs already refreshed")
args = parser.parse_args()
browser_name = args.browser
done_filename = args.done_filename
interval_between_actions = args.interval_between_actions
interval_if_ok = args.interval_if_ok
max_page_load = args.max_page_load
urls_filename = args.urls_filename
wait_load_time = args.wait_load_time

answers = []
done = set()
if done_filename.exists():
    with done_filename.open() as fobj:
        for line in fobj:
            done.add(line.strip())
    print(f"Loaded {len(done)} URLs to skip")
browser = Browser(browser_name)
browser.visit("https://www.facebook.com/login")
input("You must log-in into your account and then press ENTER so the script can continue")

errors = 0
progress = tqdm()
with urls_filename.open() as fobj, done_filename.open(mode="a+") as outfobj:
    for line in fobj:
        progress.update()
        url = line.strip()
        if url in done:
            continue
        try:
            encoded = quote(url, safe="")
            final_url = f"https://developers.facebook.com/tools/debug/?q={encoded}"
            browser.visit(final_url)
            if "Fetch new information" in browser.html:
                browser.find_by_text("Fetch new information").first.click()
                while browser.find_by_xpath("//span[@role = 'progressbar']")[1].visible:
                    time.sleep(wait_load_time)
                answers.append((url, None))
                while not browser.find_by_xpath("//tr[contains(.//td//text(), 'Response Code')]/td[2]"):
                    time.sleep(wait_load_time)
                response_code = int(browser.find_by_xpath("//tr[contains(.//td//text(), 'Response Code')]/td[2]")[0].text)
                answers.append((url, response_code))
                if response_code == 200:
                    outfobj.write(f"{url}\n")
                time.sleep(interval_between_actions)
            else:
                start_time = time.time()
                while not browser.find_by_xpath("//tr[contains(.//td//text(), 'Response Code')]/td[2]"):
                    time.sleep(wait_load_time)
                    if time.time() - start_time > max_page_load:
                        # Waited too much, so try reloading the page
                        browser.visit(final_url)
                response_code = int(browser.find_by_xpath("//tr[contains(.//td//text(), 'Response Code')]/td[2]")[0].text)
                answers.append((url, response_code))
                if response_code in (206, 418, 499) or response_code > 499:
                    browser.find_by_text("Scrape Again").first.click()
                    while browser.find_by_xpath("//span[@role = 'progressbar']")[1].visible:
                        time.sleep(wait_load_time)
                    while not browser.find_by_xpath("//tr[contains(.//td//text(), 'Response Code')]/td[2]"):
                        time.sleep(wait_load_time)
                    response_code = int(browser.find_by_xpath("//tr[contains(.//td//text(), 'Response Code')]/td[2]")[0].text)
                    answers.append((url, response_code))
                    if response_code == 200:
                        outfobj.write(f"{url}\n")
                    time.sleep(interval_between_actions)
                elif response_code == 200:
                    outfobj.write(f"{url}\n")
                    time.sleep(interval_if_ok)
            done.add(url)
        except KeyboardInterrupt:
            break
        except:
            errors += 1
            progress.desc = f"Errors: {errors}"
            continue

browser.quit()
