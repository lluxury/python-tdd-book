from django.db import models


class List(models.Model):
    def get_absolute_url(self):
        return f'/lists/{self.id}/'


class Item(models.Model):
    text = models.TextField()
    list = models.ForeignKey(List, on_delete=models.CASCADE, default=None, null=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
