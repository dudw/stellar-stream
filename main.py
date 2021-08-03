import traceback
import StellarPlayer
import importlib
import requests
import json

from bs4 import BeautifulSoup as bs
from .sites import match


class MyPlugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.q = ''
        self.result = [
        ]
        self.favs = [
        ]
        print(open)

    def show(self): 
        self.load_favs()
        result_layout = [
            [
                {
                    'group': [
                        {'type':'label','name':'name'},
                        {'type':'label','name':'url'},
                    ],
                    'dir':'vertical',
                },                
                {'type':'link','name':'收藏','width':50, '@click': 'on_add_fav_click'},
            ]
        ]
        favs_layout = [            
            [   
                {
                   'group': [
                        {'type':'label','name':'name'},
                        {'type':'label','name':'url'},
                    ],
                    'dir':'vertical',
                },
                {'type':'link','name':'播放','width':50, '@click': 'on_play_fav_click'},
                {'type':'link','name':'删除','width':50, '@click': 'on_del_fav_click'},
            ]
        ]     
        controls = [
            {'type':'space','height':50},
            {
                'group': [
                    {'type':'space'},
                    {'type':'edit','name':'search','height':30, 'width':0.7, 'label': ' ', '@input': 'on_search_input', ':value': 'q'},  
                    {'type':'button','name':'播放', 'height':30, 'width':0.1, '@click': 'on_play_click'},  
                    {'type':'space'},
                ],
                'height':30
            },            
            {'type':'space', 'height':10},

            {  
                'group': [
                    {'type':'space'},
                    {
                        'group': [
                            {'type':'list','name':'result', 'height': 48, 'itemheight':48, 'itemlayout': result_layout, ':value': 'result','marginSize':5},
                            {'type':'space', 'height':10},   
                            {'type':'label','name': '收藏列表', 'height':30},  
                            {'type':'list','name':'favs', 'itemheight':48, 'itemlayout': favs_layout, 'width': 0.8, ':value': 'favs','marginSize':5},                              
                        ],
                        'dir':'vertical',
                        'width': 0.8,
                    },                    
                    {'type':'space'}
                ],
            }
        ]
        
        result, controls = self.doModal('main', 800, 600, '看各种直播门户', controls)

    def play(self, url, show_result=False):
        ret, info = match(url)
        if ret:
            module_name = info['module']
            module = importlib.import_module(f'..realurl.{module_name}', package=__name__)
            try:
                stream_url = module.get_real_url(ret)
                if 'key' in info:
                    if callable(info['key']):
                        stream_url = info['key'](stream_url)
                    else:
                        stream_url = stream_url[info['key']]                     
                self.player.play(stream_url)

                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
                r = requests.get(url, headers = headers)
                print(r.status_code)
                if r.status_code == 200:
                    soup = bs(r.content, 'html.parser')
                    title = soup.find('title')
                    
                    if show_result:
                        self.result = [{
                            'name': title.string,
                            'url': url
                        }]
            except Exception as e:
                import traceback
                traceback.print_exc()

    def on_play_click(self, *args):
        self.result = []
        url = self.q
        self.play(url, True)

    def on_play_fav_click(self, page, listControl, item, itemControl):
        url = self.favs[item]['url']
        self.play(url, False)

    def on_add_fav_click(self, page, listControl, item, itemControl):
        if self.result[0] not in self.favs:
            self.favs = self.favs + self.result
            self.result = []
            self.save_favs()

    def on_del_fav_click(self, page, listControl, item, itemControl):
        self.favs.pop(item)
        self.favs = self.favs
        self.save_favs()

    def save_favs(self):        
        f = open("favs.json", "w")
        f.write(json.dumps(self.favs, indent=4))
        f.close()

    def load_favs(self):
        try:
            with open("favs.json") as f:
                self.favs = json.loads(f.read())
        except FileNotFoundError:
            pass
    
           
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = MyPlugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()