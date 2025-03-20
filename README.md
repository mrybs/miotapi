# MiotAPI
Реализация интерфейса для взаимодействия с API Miot

### Пример использования
```python
from miotapi import MiotAPI


api = MiotAPI('mrxx.ru')  # Инициализация интерфейса


user = api.get_users(uuid='u/mrybs'))[0]  # Получение пользователя по уникальному идентификатору
print(user.name, user.registration_date, '\n')

print(api.search_users('05'), '\n')  # Поиск пользователей по имени

print(api.get_users(telegram_id=960063512)[0].uuid)  # Получение уникального идентификатора пользователя по Telegram ID
```
