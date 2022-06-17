from rest_framework import serializers

from images.models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('pk', 'original_image', 'date_added')
