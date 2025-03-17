# voye_app/models/index_document.py

from djongo import models
from bson import ObjectId

class IndexDocument(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId, editable=False)
    # autres champs...

    class Meta:
        db_table = "index_document"
