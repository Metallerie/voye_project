from djongo import models

class IndexDocument(models.Model):
    original_filename = models.CharField(max_length=255)
    document_type = models.CharField(max_length=100)
    json_filename = models.JSONField()
    storage_path_json = models.CharField(max_length=255)
    archive_path = models.CharField(max_length=255)
    partner_name = models.CharField(max_length=255)
    document_date = models.DateField()
    file_size = models.IntegerField()
    checksum = models.CharField(max_length=64)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'index_document'

    def get_previous_document(self):
        return IndexDocument.objects.filter(pk__lt=self.pk).order_by('-pk').first()

    def get_next_document(self):
        return IndexDocument.objects.filter(pk__gt=self.pk).order_by('pk').first()
