# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class UploadedImage(models.Model):
    imagefile = models.FileField(upload_to = 'srcImages')
