import threading
import queue
import requests

from typing import List

q = queue.Queue()

file_lock = threading.Lock()

with open("proxy_list.txt", "r") as f:
    proxies = f.read().split("\n")
    for p in proxies:
        q.put(p)


def check_proxies() -> None:
    while not q.empty():
        proxy = q.get()
        try:
            resp = requests.get(
                "http://ipinfo.io/json", proxies={"http": proxy, "https": proxy}
            )
        except:
            continue
        if resp.status_code == 200:
            print(proxy)
            with file_lock:
                with open("validated_proxy_list.txt", "a") as f:
                    f.write(proxy + "\n")


threads: List[threading.Thread] = []
for _ in range(10):
    thread = threading.Thread(target=check_proxies)
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print("All proxies has been checked")
