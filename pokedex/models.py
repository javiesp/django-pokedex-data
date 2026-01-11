from django.db import models

class Pokemon(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    types = models.JSONField()
    height = models.IntegerField()
    weight = models.IntegerField()
    image_url = models.URLField()
    name_reversed = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name