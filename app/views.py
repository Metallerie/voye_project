from django.shortcuts import render
from django.http import JsonResponse
import subprocess
import os

def document_view(request):
    return render(request, 'document_view.html')

def index(request):
    return render(request, 'index.html')

def run_gpt_engineer(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')

        if not prompt:
            return JsonResponse({'status': 'Erreur', 'error': 'Aucun prompt fourni.'})

        project_path = '/data/voye/gpt-engineer/projects/web_interface'
        os.makedirs(project_path, exist_ok=True)
        prompt_file = os.path.join(project_path, 'prompt')
        with open(prompt_file, 'w') as f:
            f.write(prompt)

        try:
            process = subprocess.Popen(
                ['gpte', project_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate(input=prompt.encode('utf-8'))

            if process.returncode == 0:
                return JsonResponse({'status': 'Succès', 'output': stdout.decode('utf-8')})
            else:
                return JsonResponse({'status': 'Erreur', 'error': stderr.decode('utf-8')})
        except Exception as e:
            return JsonResponse({'status': 'Erreur', 'error': f'Exception: {str(e)}'})

    return JsonResponse({'status': 'Erreur', 'error': 'Méthode non autorisée'})
