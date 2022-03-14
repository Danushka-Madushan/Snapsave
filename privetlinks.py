import webbrowser, requests, msvcrt, re, os, json

pause = lambda : msvcrt.getch()
with open('config/config.json', 'r') as config1: _headers = json.load(config1);config1.close()
with open('config/privetsnaphead.json', 'r') as config2: snaphead = json.load(config2);config2.close()
_source = requests.get(input("\n$ Privet Video Link : "), headers=_headers).content.decode('utf-8')
try:
    print("\n$ Source code obtained -> Posting to snapsave...\n$ wait for few seconds :)")
    response = requests.post('https://snapsave.app/download-private-video', headers=snaphead, data={'html_content': _source}).content.decode('utf-8')
    _regready = re.sub(r'\n', '', response)
    _directlinks = re.findall(r'td.{1}class="video-quality">(.{1,10})</td>.{4}No\D+href=\'(\S+)\'', _regready)
    links = {}
    for x in range(len(_directlinks)): links[_directlinks[x][0]] = _directlinks[x][1]
    _dlink = next(iter(links.keys()))
    print('\n$ Downloading in %s.. check your browser' % _dlink)
    webbrowser.open_new_tab(links[_dlink]);pause()
except Exception as _identifier_:
    print("\n$ Runtime Error! please try again!")
    print("$ Error : %s" % _identifier_);pause()
