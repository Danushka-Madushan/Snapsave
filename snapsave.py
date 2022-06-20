import os
import re
import json
import shutil
import base64
import msvcrt
import sqlite3
import requests
import webbrowser
import win32crypt
from Crypto.Cipher import AES
from datetime import datetime, timedelta

def get_chrome_datetime(chromedate):
    if chromedate != 86400000000 and chromedate:
        try:
            return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
        except Exception as e:
            print(f"Error: {e}, chromedate: {chromedate}")
            return chromedate
    else:
        return ""

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_data(data, key):
    try:
        iv = data[3:15]
        data = data[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(data)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(data, None, None, None, 0)[1])
        except:
            return ""

def cookies():
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
    filename = "Cookies"
    if os.path.isfile(filename):
        os.remove(filename)
        shutil.copyfile(db_path, filename)
    else:
        shutil.copyfile(db_path, filename)
    db = sqlite3.connect(filename)
    db.text_factory = lambda b: b.decode(errors="ignore")
    cursor = db.cursor()
    cursor.execute("""
    SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value 
    FROM cookies WHERE host_key like '%facebook.com%'""")
    key = get_encryption_key()
    _data = {}
    for host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value in cursor.fetchall():
        if not value:
            decrypted_value = decrypt_data(encrypted_value, key)
        else:
            decrypted_value = value
        _data[name] = decrypted_value
        cursor.execute("""
        UPDATE cookies SET value = ?, has_expires = 1, expires_utc = 99999999999999999, is_persistent = 1, is_secure = 0
        WHERE host_key = ?
        AND name = ?""", (decrypted_value, host_key, name))
    db.commit()
    db.close()
    return _data

class fb:
  def __init__(self, link, cookies):
    self.videolink = link
    self.headers = {
    'authority': 'www.facebook.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9,si;q=0.8',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    'sec-fetch-dest': 'document',
    'sec-fetch-site': 'none',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    'viewport-width': '1280',
    }
    self.cookies = cookies

  def viewsource(self):
    response = requests.get(self.videolink, cookies=self.cookies, headers=self.headers)
    if response.status_code == 200:
      return response.content.decode('ascii', errors='ignore')

class snapsave:
  def __init__(self, src):
    self.api = 'https://snapsave.app/download-private-video'
    self.headers = {
    'authority': 'snapsave.app',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://snapsave.app',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
    }
    self.source = src

  def extract(self):
    response = requests.post(self.api, headers=self.headers, data={'html_content': self.source})
    if response.status_code == 200:
      return response.content.decode('ascii', errors='ignore')

if __name__ == "__main__":
  link = print('\n Post Link : ')
  src = fb(link, cookies()).viewsource()
  rawdata = re.sub('\n', '', snapsave(src).extract())
  vn = re.search(r'class="video-des">([^<]+)', rawdata).group(1)
  links = re.findall(r"class=.video-quality.>(HD|SD)</td> ?<td>No</td>[^']+.([^']+)", rawdata)
  print('\n Video : %s' % vn)
  for each in links: 
    print('\n Press enter to Download in (%s)' % each[0])
    if msvcrt.getch() == b'\r':
      webbrowser.open_new_tab(each[1])
      break
