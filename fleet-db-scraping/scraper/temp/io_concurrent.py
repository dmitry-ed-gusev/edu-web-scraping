import concurrent.futures
import requests
import threading
import time

# todo: https://stackoverflow.com/questions/52082665/store-results-threadpoolexecutor

thread_local = threading.local()  # thread local storage
futures = []  # list to store future results of threads


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def download_site(url):
    session = get_session()
    with session.get(url) as response:
        content = response.content
        print(f"Read {len(content)} from {url}")
        return len(content)


def download_all_sites_1(sites):
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        executor.map(download_site, sites)  # directly execute provided functions with multiple threads


def download_all_sites_2(sites):
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        for site in sites:
            future = executor.submit(download_site, site)
            futures.append(future)

        # directly loop over futures to wait for them in the order they were submitted
        counter = 0
        for future in futures:
            result = future.result()
            counter = counter + result

        return counter


def download_all_sites_3(sites):
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        for site in sites:
            future = executor.submit(download_site, site)
            futures.append(future)

        # if we need to wait for them all to be finished before doing any work:
        my_futures, _ = concurrent.futures.wait(futures)
        counter = 0
        for future in futures:
            result = future.result()
            counter = counter + result

        return counter


def download_all_sites_4(sites):
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        for site in sites:
            future = executor.submit(download_site, site)
            futures.append(future)

        # if we want to handle each one as soon as it’s ready, even if they come out of order, use as_completed:
        counter = 0
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            counter = counter + result

        return counter


if __name__ == "__main__":
    sites = [
        "https://www.jython.org",
        "http://olympus.realpython.org/dice",
    ] * 80

    # start_time = time.time()
    # download_all_sites_1(sites)
    # duration = time.time() - start_time
    # print(f"Option I: downloaded {len(sites)} in {duration} seconds\n")

    # start_time = time.time()
    # volume = download_all_sites_2(sites)
    # duration = time.time() - start_time
    # print(f"Option II: downloaded {len(sites)} in {duration} seconds")
    # print(f"Downloaded volume: {volume}")

    # start_time = time.time()
    # volume = download_all_sites_3(sites)
    # duration = time.time() - start_time
    # print(f"Option III: downloaded {len(sites)} in {duration} seconds")
    # print(f"Downloaded volume: {volume}")

    start_time = time.time()
    volume = download_all_sites_4(sites)
    duration = time.time() - start_time
    print(f"Option IV: downloaded {len(sites)} in {duration} seconds")
    print(f"Downloaded volume: {volume}")
