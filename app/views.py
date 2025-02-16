from django.shortcuts import render

def index(request):
    return render(request, "document_view.html")
