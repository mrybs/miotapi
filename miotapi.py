import requests
import urllib.parse
import os.path
import inspect
import sys
from datetime import datetime


class AttributedDict(dict): 
    def __getattr__(self, item):
        return self[item]


class User:
    def __init__(self, api, data):
        self.api = api
        data = AttributedDict(data)
        self.uuid = data.uuid
        self.telegram_id = int(data.telegram_id)
        self.telegram_username = data.get('telegram_username', None)
        self.name = data.name
        self.flags = data.flags
        self.registration_date = datetime.strptime(data.registration_date, '%Y-%m-%d %H:%M:%S.%f')

    def profile_page(self):
        return f'{self.api.protocol}://{self.api.host}/{self.uuid}'
    
    def __repr__(self):
        return f'\nUser {self.uuid}\n'\
               f'Name: {self.name}\n'\
               f'Telegram ID: {self.telegram_id}\n'\
               f'Telegram username: @{self.telegram_username}\n'\
               f'Registration date: {self.registration_date}\n'\
               f'Flags: {", ".join(self.flags)}\n'


class AssetsManager:
    @staticmethod
    def get_root_path():
        return os.path.dirname(inspect.getfile(sys.modules[__name__]))
    
    @staticmethod
    def get_assets_path():
        return AssetsManager.get_root_path() + '/assets'
    
    @staticmethod
    def get_items_path():
        return AssetsManager.get_assets_path() + '/items'
    
    @staticmethod
    def get_item_path(item_id):
        items_path = AssetsManager.get_items_path()
        item_path = items_path + '/' + item_id
        if os.path.isfile(item_path + '.webp'):
            return item_path + '.webp'
        if os.path.isfile(item_path + '.png'):
            return item_path + '.png'


class MiotAPI:
    VERSION = '0.1.1'

    @staticmethod
    def dict_to_args(d):
        args = []
        for key in d.keys():
            if d[key] is not None:
                args.append(f'{key}={urllib.parse.quote_plus(str(d[key]))}')
        return '?' + '&'.join(args) if len(args) > 0 else ''


    def __init__(self, host: str, protocol: str = 'https', prefix: str = '/api', timeout=1):
        self.host = host
        self.protocol = protocol
        self.prefix = prefix
        self.timeout = timeout
    
    def _status(self):
        try:
            res = self.get('/')
            return res['status']
        except Exception:
            return 'offline'
    
    def get(self, meth, tries=3):
        try:
            return requests.get(f'{self.protocol}://{self.host}{self.prefix}{meth}', timeout=self.timeout).json()
        except Exception as e: 
            if tries > 1:
                return self.get(meth, tries-1)
            raise e

    def get_users(self, uuid: str=None, telegram_id: int=None, telegram_username: str=None, name: str=None, flags: list[str]=None,
                  registration_date: int=None, roles: list[str]=None) -> list[AttributedDict]:
        args = self.dict_to_args({
             'uuid': uuid,
             'telegram_id': telegram_id,
             'telegram_username': telegram_username,
             'name': name,
             'flags': ','.join(flags) if flags is not None else None,
             'registration_date': registration_date,
             'roles': ','.join(roles)
if roles is not None else None
        })
        return [
             User(self, user) 
             for user in self.get(f'/users{args}')
        ]
    
    def search_users(self, query: str) -> list[AttributedDict]:
        return [
             User(self, user) 
             for user in self.get(f'/search/users?query={urllib.parse.quote_plus(query)}')
        ]
         
    def get_search_suggestions(self, query: str) -> list[str]:
        return self.get(f'/search.suggestions?query={urllib.parse.quote_plus(query)}')['suggestions']
         

if __name__ == '__main__':
    print(AssetsManager.items_path())
    print(AssetsManager.item_path('miotbot'))
    api = MiotAPI('mrxx.ru')
    print(api._status())
    print(api.get_users(uuid='u/mrybs'))
    print()
    print(api.get_search_suggestions('чин'))
    print()
    print(api.search_users('чинчопа <3'))
    print()
    print(api.get_users(telegram_id=960063512)[0].uuid)