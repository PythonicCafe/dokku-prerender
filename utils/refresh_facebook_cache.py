# Dependencies: pip install splinter tqdm
import argparse
import time
from urllib.parse import quote
from pathlib import Path

from splinter import Browser
from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument("--browser", default="firefox")
parser.add_argument("--wait-load-time", type=float, default=0.5)
parser.add_argument("--interval-between-actions", type=float, default=5.0)
parser.add_argument("urls_filename", type=Path, help="Text file with one URL per line")
parser.add_argument("done_filename", type=Path, help="File to be created, storing URLs already refreshed")
args = parser.parse_args()
wait_load_time = args.wait_load_time
interval_between_actions = args.interval_between_actions
urls_filename = args.urls_filename
done_filename = args.done_filename
browser_name = args.browser

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

with urls_filename.open() as fobj, done_filename.open(mode="a+") as outfobj:
    for line in tqdm(fobj):
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
                while not browser.find_by_xpath("//tr[contains(.//td//text(), 'Response Code')]/td[2]"):
                    time.sleep(wait_load_time)
                response_code = int(browser.find_by_xpath("//tr[contains(.//td//text(), 'Response Code')]/td[2]")[0].text)
                answers.append((url, response_code))
                if response_code > 499:
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
            done.add(url)
        except KeyboardInterrupt:
            break
        except:
            continue

browser.quit()
