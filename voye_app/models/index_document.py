from djongo import models

class IndexDocument(models.Model):
    original_filename = models.CharField(max_length=255)
    document_type = models.CharField(max_length=100)
    json_filename = models.CharField(max_length=255)
    storage_path = models.CharField(max_length=255)
    archive_path = models.CharField(max_length=255)
    partner_name = models.CharField(max_length=255)
    document_date = models.DateField()
    file_size = models.IntegerField()
    checksum = models.CharField(max_length=64)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'index_document'
