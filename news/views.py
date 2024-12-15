from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from NewsService import settings
from .redis_manager import RedisManager
from .minio_serivce import MinioService
from .models import Post
from .serializers import PostSerializer


# Create your views here.
class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    redis_manager = RedisManager()

    def list(self, request, *args, **kwargs):
        # Попробуйте получить кэшированный список постов из Redis
        cached_posts = self.redis_manager.get('post_list')
        if cached_posts:
            return Response(cached_posts)  # Если данные найдены в кэше, возвращаем их

        # Если кэша нет, получаем данные из базы данных
        response = super().list(request, *args, **kwargs)

        # Сохраняем данные в Redis (с TTL на 5 минут)
        self.redis_manager.set('post_list', response.data, ttl=60 * 5)  # кэшируем на 5 минут

        return response

    def perform_create(self, serializer):
        # Сохраняем новый пост в базе данных
        instance = serializer.save()

        # Обновляем кэш после добавления нового поста
        self.redis_manager.delete('post_list')  # Удаляем старый кэш
        self.redis_manager.set('post_list', PostSerializer(Post.objects.all(), many=True).data, ttl=60 * 5)  # Обновляем кэш

        return instance


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'id'
    redis_manager = RedisManager()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        image_url = instance.image  # Получаем URL файла из модели

        # Удаляем файл из MinIO
        if image_url:
            unique_name = image_url.split(f"{settings.MINIO_STORAGE_BUCKET_NAME}/")[-1]  # Извлекаем путь файла
            MinioService().delete_file(unique_name)  # Удаляем файл

        # Удаляем объект из базы данных
        self.perform_destroy(instance)

        # Удаляем пост из кэша
        self.redis_manager.delete(f'post_{instance.id}')  # Удаляем конкретный пост из кэша

        # Обновляем общий список постов в кэше
        self.redis_manager.delete('post_list')  # Удаляем кэшированное представление всех постов

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        # Сохраняем изменения поста в базе данных
        instance = serializer.save()

        # Обновляем кэш после обновления поста
        self.redis_manager.delete(f'post_list')  # Удаляем старый кэш
        self.redis_manager.set('post_list', PostSerializer(Post.objects.all(), many=True).data, ttl=60 * 5)  # Обновляем кэш

        return instance

