from django.shortcuts import render

def document_view(request):
    return render(request, 'document_view.html')
