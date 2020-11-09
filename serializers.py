from rest_framework import serializers, status
from .models import Galery, Image

class ImagesSerializer(serializers.ModelSerializer):
    fullpath = serializers.CharField(source='image.url')
    class Meta:
        model = Image
        fields = ['path', 'fullpath', 'name', 'modified']

class GalerySerializerGet(serializers.ModelSerializer):

    class Meta:
        model = Galery
        fields = ['name', 'path']


class GalerySerializerPostRead(serializers.ModelSerializer):
    #Check if instatnce already exists
    def create(self, validated_data):
        if Galery.objects.filter(**validated_data).exists():
            return status.HTTP_409_CONFLICT
        else:
            return Galery.objects.create(**validated_data)

    class Meta:
        model = Galery
        fields = '__all__'


class GalleryDetailSerializerPost(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['image', 'path', 'fullpath', 'name', 'modified']


class GaleryDetailSerializerGet(serializers.ModelSerializer):
    images = ImagesSerializer(many=True)

    class Meta:
        model = Galery
        fields = ['name', 'path', 'images']
        depth = 2
