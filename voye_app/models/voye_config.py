from djongo.db import models
from bson import ObjectId


class VoyeConfig(models.Model):
    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=255)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    write_date = models.DateTimeField(auto_now=True)

class Meta:
    db_table = 'voye_config'
  
