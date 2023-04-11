from django.db import models


class Quotes(models.Model):
    quote = models.TextField()
    author = models.TextField(blank=True, null=True)

class Categories(models.Model):
    category = models.TextField(blank=True)
    quote = models.ManyToManyField(Quotes, related_name='categories')
