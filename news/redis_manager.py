import json
import redis
from django.conf import settings


class RedisManager:
    def __init__(self):
        # Подключение к Redis
        self.client = redis.StrictRedis(
            host=settings.REDIS_HOST,  # Задайте хост Redis
            port=settings.REDIS_PORT,  # Порт Redis
            db=settings.REDIS_DB,  # Номер базы данных Redis (по умолчанию 0)
            decode_responses=True  # Декодировать ответы как строки
        )

    def get(self, key):
        """Получение данных из Redis по ключу."""
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set(self, key, value, ttl=0):
        """Сохранение данных в Redis с возможностью задать TTL (в секундах)."""
        self.client.set(key, json.dumps(value), ex=ttl)

    def delete(self, key):
        """Удаление данных из Redis по ключу."""
        self.client.delete(key)
