from django.shortcuts import render

def document_view(request):
    # Logique de la vue ici
    return render(request, 'document_view.html')
