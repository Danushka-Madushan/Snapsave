import subprocess, requests, json, re, os

_isprivet = lambda _response, _link : False if re.findall(r'parent.{1}sendEvent.{2}error_video_private.{1},.{1}"%s".{1};' % _link, _response) else True
_isvalid = lambda _response, _link : False if re.findall(r'parent.{1}sendEvent.{2}error_url_support.{1},.{1}"%s".{1};' % _link, _response) else True

try:
  _fblink = input("\n$ FB Post Link : ")
  with open('config/snaphead.json', 'r') as _config: headers = json.load(_config);_config.close()
  response = requests.post('https://snapsave.app/action.php', headers=headers, data={'url': _fblink}).content.decode('utf-8')
  if _isvalid(response, _fblink):
    if _isprivet(response, _fblink):
      _scriptcatcher = re.search(r'<script>(.+)</script>', response).group(1)
      _decodecode = re.search(r'return.{1}(decodeURIComponent.{1}escape.{4})', response).group(1)
      _finaljs = re.sub(r'return.{1}decodeURIComponent.{1}escape.{4}', "console.log(%s)" % _decodecode , _scriptcatcher)
      with open('main.js', 'w') as _js: _js.write(_finaljs);_js.close()
      _resultjs = subprocess.Popen('node main.js', stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
      _regreadyjs = re.sub(r'\\', '', _resultjs[0].decode('utf-8'))
      _directlinks = re.findall(r'td.{1}class="video-quality">(.{1,10})</td>.{1}<td>No.{10}<a.{1}href="(\S+)"', _regreadyjs)
      _renderlinks = re.findall(r'td.{1}class="video-quality">(.{1,10})</td>.{1}<td>Yes.{18}onclick="get_progressApi.{1}\'(\S+)\'.{1};', _regreadyjs)
      _directfile, _renderfile = {}, {}
      for x in range(len(_directlinks)): _directfile[_directlinks[x][0]] = _directlinks[x][1]
      with open('_directlinks.json', 'w') as _directlinksfile: _directlinksfile.write(json.dumps(_directfile, indent=4));_directlinksfile.close()
      for x in range(len(_renderlinks)): _renderfile[_renderlinks[x][0]] = _renderlinks[x][1]
      with open('_renderlinks.json', 'w') as _renderlinksfile: _renderlinksfile.write(json.dumps(_renderfile, indent=4));_renderlinksfile.close()
      os.system('del main.js')
      print("\n$ All links saved locally!")
    else: raise RuntimeError("Privet Video!")
  else: raise RuntimeError("the link you provided is not related to facebook.com domain!")
except KeyboardInterrupt: print("\n\n$ KeyboardInterrupt recieved!")
except requests.exceptions.ConnectionError: print("\n$ No internet conneciton!")
except Exception as _identifier_: print("\n$ Oops! this happened : %s" % _identifier_)
