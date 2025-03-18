#https://github.com/Metallerie/voye_project/blob/voye_01/collection/voye_frontend_config.json
from django.db import models
from bson import ObjectId

class FrontendConfig(models.Model):
    id = models.ObjectIdField(default=ObjectId, primary_key=True, unique=True)
    user_id = models.CharField(max_length=255)
    theme = models.CharField(max_length=50)
    layout = models.CharField(max_length=50)
    language = models.CharField(max_length=10)
    buttons_size = models.CharField(max_length=50)
    show_tutorial = models.BooleanField()
    create_date = models.DateTimeField(auto_now_add=True)
    write_date = models.DateTimeField(auto_now=True)

 class Meta:
    db_table = 'index_document'
