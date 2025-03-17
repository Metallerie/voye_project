from djongo import models
from bson import ObjectId

class IndexDocument(models.Model):
    id = models.ObjectIdField(default=ObjectId, primary_key=True, unique=True)
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
  
    def get_id(self):
        return str(self._id)
        
    def get_full_json_path(self):
        return f"{self.storage_path_json.rstrip('/')}/{self.json_filename['path']}" if 'path' in self.json_filename else None        
    def get_previous_document(self):
        return IndexDocument.objects.filter(pk__lt=self.pk).order_by('-pk').first()

    def get_next_document(self):
        return IndexDocument.objects.filter(pk__gt=self.pk).order_by('pk').first()
