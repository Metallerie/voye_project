from djongo import models
from bson import ObjectId
from django.utils import timezone  # Ajoutez cette ligne

class IndexDocument(models.Model):
    id = models.ObjectIdField(default=ObjectId, primary_key=True, unique=True)
    original_filename = models.CharField(max_length=255)
    document_type = models.CharField(max_length=100)
    json_filename = models.JSONField()
    storage_path_json = models.CharField(max_length=255)
    archive_path_pdf = models.CharField(max_length=255, default='default_value')  # Set your desired default value here
    partner_name = models.CharField(max_length=255)
    document_date = models.DateField()
    file_size = models.IntegerField()
    checksum = models.CharField(max_length=255, default='default_value')  # Définir une valeur par défaut appropriée
    timestamp = models.DateTimeField()
    write_date = models.DateTimeField(auto_now=True,  blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'index_document'
  
    def get_full_json_path(self):
        return f"{self.storage_path_json.rstrip('/')}/{self.json_filename['path']}" if 'path' in self.json_filename else None
        
    def get_previous_document(self):
        return IndexDocument.objects.filter(pk__lt=self.pk).order_by('-pk').first()

    def get_next_document(self):
        return IndexDocument.objects.filter(pk__gt=self.pk).order_by('pk').first()
