# Dependencies: pip install requests tqdm
import csv
import multiprocessing
import time
from pathlib import Path

import requests
from tqdm import tqdm


def init_worker():
    import signal

    signal.signal(signal.SIGINT, signal.SIG_IGN)


def http_get(args):
    prerender_server, url, timeout, max_tries = args
    tried, response = 0, None
    start_time = time.time()
    while tried < max_tries:
        try:
            response = requests.get(prerender_server + url, timeout=timeout)
        except:
            tried += 1
        else:
            break
    end_time = time.time()
    return url, response.status_code if response is not None else None, end_time - start_time


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=25.0)
    parser.add_argument("--max-tries", type=int, default=3)
    parser.add_argument("prerender_server")
    parser.add_argument("urls_filename", type=Path, help="Text file with one URL per line")
    parser.add_argument("csv_filename", type=Path, help="CSV for the results")
    args = parser.parse_args()
    prerender_server = args.prerender_server
    if not prerender_server.endswith("/"):
        prerender_server += "/"
    urls_filename = args.urls_filename
    csv_filename = args.csv_filename
    timeout = args.timeout
    max_tries = args.max_tries

    processes = multiprocessing.cpu_count()
    with urls_filename.open() as fobj, csv_filename.open(mode="w") as outfobj, multiprocessing.Pool() as pool:
        writer = None
        inputs = (
            (prerender_server, line.strip(), timeout, max_tries)
            for line in fobj
            if line.strip() and not line.strip().startswith("#")
        )
        try:
            for url, status_code, delta_time in tqdm(pool.imap_unordered(http_get, inputs)):
                row = {"url": url, "status_code": status_code, "delta_time": f"{delta_time:5.3f}"}
                if writer is None:
                    writer = csv.DictWriter(outfobj, fieldnames=list(row.keys()))
                    writer.writeheader()
                writer.writerow(row)
        except KeyboardInterrupt:
            pool.terminate()
