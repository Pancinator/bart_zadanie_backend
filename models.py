import os
from django.db import models
from datetime import time


#specify upload path (/media folder)
def upload(instance, filename):
    return instance.fullpath


"""
Pictures from file directory are removed after their model instance is deleted. Django-cleanup modelu
is used.
"""


class Image(models.Model):
    image = models.ImageField(blank=True, upload_to=upload)
    path = models.CharField(max_length=255, default='defaul_path')
    fullpath = models.CharField(max_length=255, default='defaul_fullpath')
    name = models.CharField(max_length=255, null= True, blank=True, default='defaul_fullpath')
    modified = models.DateTimeField(max_length=255, blank=True, null= True,)

    def __str__(self):
        return self.path


class Galery(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255, blank=True)
    images = models.ManyToManyField(Image, null=True) #key to Image table relation

    def save(self, *args, **kwargs):
        self.path = 'media/' + self.name
        super(Galery, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
