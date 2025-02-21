import sys
import os
# Ajouter le chemin /data/voye au sys.path
sys.path.append('/data/voye')
def main():
    """Exécuter les tâches administratives."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frontend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Êtes-vous sûr qu'il est installé et "
            "disponible sur votre variable d'environnement PYTHONPATH ? Avez-vous "
            "oublié d'activer un environnement virtuel ?"
        ) from exc

    # Imprimer la liste des chemins de recherche des modules
    print("Chemins de recherche des modules :")
    for path in sys.path:
        print(path)

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
