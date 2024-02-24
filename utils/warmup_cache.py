# Dependencies: pip install requests tqdm
import multiprocessing
import time
from pathlib import Path

import requests
from tqdm import tqdm


def init_worker():
    import signal

    signal.signal(signal.SIGINT, signal.SIG_IGN)


def http_get(args):
    prerender_server, url = args
    start_time = time.time()
    response = requests.get(prerender_server + url)
    end_time = time.time()
    return url, response.status_code, end_time - start_time


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("prerender_server")
    parser.add_argument("urls_filename", type=Path, help="Text file with one URL per line")
    args = parser.parse_args()
    prerender_server = args.prerender_server
    if not prerender_server.endswith("/"):
        prerender_server += "/"
    urls_filename = args.urls_filename

    processes = multiprocessing.cpu_count()
    responses = {}
    with urls_filename.open() as fobj, multiprocessing.Pool() as pool:
        inputs = (
            (prerender_server, line.strip())
            for line in fobj
            if line.strip() and not line.strip().startswith("#")
        )
        try:
            for url, status_code, delta_time in tqdm(pool.imap_unordered(http_get, inputs)):
                responses[url] = (status_code, delta_time)
        except KeyboardInterrupt:
            pool.terminate()
