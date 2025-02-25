import requests
import urllib.parse


class AttributedDict(dict):
	def __getattr__(self, item):
		return self[item]


class MiotAPI:
    @staticmethod
    def dict_to_args(d):
        args = []
        for key in d.keys():
            args.append(f'{key}={urllib.parse.quote_plus(d[key])}')
        return '?' + '&'.join(args) if len(args) > 0 else ''


    def __init__(self, host: str, protocol: str = 'https', prefix: str = '/api'):
        self.host = host
        self.protocol = protocol
        self.prefix = prefix

    def get_users(self, uuid: str, telegram_id: int, telegram_username: str, name: str, flags: list[str],
                  registration_date: int, roles: list[str]) -> list[AttributedDict]:
        args = self.dict_to_args({
             'uuid': uuid,
             'telegram_id': telegram_id,
             'telegram_username': telegram_username,
             'name': name,
             'flags': ','.join(flags),
             'registration_date': registration_date,
             'roles': ','.join(roles)
        })
        return [
             AttributedDict(user) 
             for user in requests.get(f'{self.protocol}://{self.host}{self.prefix}/users{args}', timeout=1).json()
        ]
    
    def search_users(self, query: str) -> list[AttributedDict]:
        return [
             AttributedDict(user) 
             for user in requests.get(f'{self.protocol}://{self.host}{self.prefix}/search/users?query={urllib.parse.quote_plus(query)}', timeout=1).json()
        ]
         
