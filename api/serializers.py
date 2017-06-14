from rest_framework import serializers
from .models import UploadedImage
from languages.fields import LanguageField

class UploadedImageSerializer(serializers.ModelSerializer):
    class Meta:
	model = UploadedImage
	fields = ('id', 'imagelanguage', 'imagemodel', 'imagefile')
