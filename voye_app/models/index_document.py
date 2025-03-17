class IndexDocument(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId, editable=False)
    # autres champs...

    class Meta:
        db_table = "index_document"
