# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from languages.fields import LanguageField
from .validators import validate_image_extension

class UploadedImage(models.Model):
    # The model used in OCR recognition to proces this image
    imagelanguage = LanguageField(default = "English", blank=True )
    imagemodel = models.FileField(upload_to = 'models', null=True)
    imagefile = models.ImageField(upload_to = 'srcImages', null=False, validators=[validate_image_extension])
