from django.db import models
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.conf import settings


class List(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_lists',
        blank=True
    )

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])

    @property
    def name(self):
        """Return the name of the list based on the first item"""
        first_item = self.item_set.first()
        return first_item.text if first_item else 'Empty List'


class Item(models.Model):
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None, on_delete=models.CASCADE)

    class Meta:
        ordering = ('id',)
        unique_together = ('list', 'text')

    def __str__(self):
        return self.text
