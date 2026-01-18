import time
import requests

URL = "http://127.0.0.1.nip.io:8000"
INTERVAL = 1.0

bytes_recv = 0
last = time.time()

proxies = {
    "http": "http://127.0.0.1:8888",
    "https": "http://127.0.0.1:8888",
}

while True:
    r = requests.get(URL, stream=True, proxies=proxies)
    for chunk in r.iter_content(chunk_size=8192):
        if not chunk:
            continue

        bytes_recv += len(chunk)

        now = time.time()
        if now - last >= INTERVAL:
            rate = bytes_recv / (now - last)
            print(f"RECV {rate:.1f} B/s", flush=True)
            bytes_recv = 0
            last = now
