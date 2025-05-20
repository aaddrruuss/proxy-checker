import asyncio
import aiohttp
import time

q = asyncio.Queue()
valid_proxies = 0
total_proxies = 0


async def load_proxies() -> None:
    global total_proxies
    with open("proxy_list.txt", "r") as f:
        proxies: list[str] = [p for p in f.read().split("\n") if p.strip()]
        for p in proxies:
            await q.put(p)
            total_proxies += 1


async def check_proxies() -> None:
    global valid_proxies
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                proxy = await asyncio.wait_for(q.get(), timeout=5) #You can lower the timeout to make the script a bit faster, but you might skip some valid proxies
                try:
                    async with session.get(
                        "http://ipinfo.io/json", proxy=f"http://{proxy}"
                    ) as resp:
                        if resp.status == 200:
                            print(f"Valid: {proxy}")
                            valid_proxies += 1
                            with open("validated_proxy_list.txt", "a") as f:
                                f.write(proxy + "\n")
                except:
                    pass
                finally:
                    q.task_done()
            except asyncio.TimeoutError:
                break


async def main() -> None:
    open("validated_proxy_list.txt", "w").close()
    await load_proxies()

    workers: list[asyncio.Task[None]] = [asyncio.create_task(check_proxies()) for _ in range(10)]
    await q.join()

    for w in workers:
        w.cancel()

    print(f"{total_proxies} proxies checked - {valid_proxies} valid")


if __name__ == "__main__":
    start: float = time.perf_counter()
    asyncio.run(main())
    print(f"Done in {time.perf_counter() - start:.2f}s")
