from rest_framework import serializers

from .minio_serivce import MinioService
from .models import Post
from .services import FileService


class PostSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.CharField(read_only=True, source='image')

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'image_url', 'author', 'pub_date']

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        if image:
            validated_data['image'] = FileService.upload_to_minio(image, validated_data['title'])
        return Post.objects.create(**validated_data)
