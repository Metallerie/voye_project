from django import forms
from django_json_widget.widgets import JSONEditorWidget
from voye_app.models import IndexDocument

class IndexDocumentForm(forms.ModelForm):
    class Meta:
        model = IndexDocument
       # fields = ['original_filename', 'document_type', 'json_filename', 'storage_path_json', 'archive_path', 'partner_name', 'document_date', 'file_size', 'checksum', 'timestamp']
        fields = ['id']
       # widgets = {
       #     'json_filename': JSONEditorWidget
        #}
