from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from voye_app.models.index_document import IndexDocument
from voye_app.forms import IndexDocumentForm

def document_view(request, pk):
    instance = get_object_or_404(IndexDocument, pk=pk)
    if request.method == 'POST':
        form = IndexDocumentForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
    else:
        form = IndexDocumentForm(instance=instance)
    return render(request, 'index_document_view_form.xml', {'form': form, 'instance': instance})

def previous_document(request, pk):
    instance = get_object_or_404(IndexDocument, pk=pk)
    previous_doc = instance.get_previous_document()
    if previous_doc:
        return redirect('document_view', pk=previous_doc.pk)
    return redirect('document_view', pk=pk)

def next_document(request, pk):
    instance = get_object_or_404(IndexDocument, pk=pk)
    next_doc = instance.get_next_document()
    if next_doc:
        return redirect('document_view', pk=next_doc.pk)
    return redirect('document_view', pk=pk)

def document_list(request):
    documents = IndexDocument.objects.all()
    return render(request, 'index_document_list.xhtml', {'documents': documents})

def hello_world(request):
    return HttpResponse("Hello World")
