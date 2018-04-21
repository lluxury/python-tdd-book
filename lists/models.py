from django.db import models

# Create your models here.
class Item(models.Model):
    text = models.TextField(default='')
    list = models.TextField(default='')

# class List(object):
class List(models.Model):
    pass
