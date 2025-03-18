from django import forms
from django_json_widget.widgets import JSONEditorWidget
from voye_app.models import IndexDocument, VoyeConfig, FrontendConfig

class IndexDocumentForm(forms.ModelForm):
    class Meta:
        model = IndexDocument
        fields = '__all__'
        widgets = {
            'json_filename': JSONEditorWidget,
        }

class VoyeConfigForm(forms.ModelForm):
    class Meta:
        model = VoyeConfig
        fields = '__all__'

class FrontendConfigForm(forms.ModelForm):
    class Meta:
        model = VoyeFrontendConfig
        fields = '__all__'
