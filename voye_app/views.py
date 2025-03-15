from django.shortcuts import render, get_object_or_404
from voye_db.models import IndexDocument
from voye_app.forms import IndexDocumentForm

def document_view(request, pk):
    instance = get_object_or_404(IndexDocument, pk=pk)
    if request.method == 'POST':
        form = IndexDocumentForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
    else:
        form = IndexDocumentForm(instance=instance)
    return render(request, 'voye_app/document_view.html', {'form': form})
