import os

def update_init_files(directory):
    print(f"[INFO] Début de la mise à jour des fichiers __init__.py dans {directory}\n")
    for root, dirs, files in os.walk(directory):
        print(f"[INFO] Analyse du dossier : {root}")
        python_files = [f for f in files if f.endswith('.py') and f != '__init__.py']
        init_path = os.path.join(root, '__init__.py')
        
        if python_files:
            print(f"[INFO] Modules détectés dans {root} : {', '.join(python_files)}")
            imports = []
            for file in python_files:
                module_name = os.path.splitext(file)[0]
                import_statement = f'from .{module_name} import *'
                imports.append(import_statement)
            
            if os.path.exists(init_path):
                with open(init_path, 'r+', encoding='utf-8') as init_file:
                    content = init_file.read()
                    new_content = content
                    for imp in imports:
                        if imp not in content:
                            new_content += f'\n{imp}'
                            print(f"[ADDED] {imp} -> {init_path}")
                    if new_content != content:
                        init_file.seek(0)
                        init_file.write(new_content)
                        init_file.truncate()
                        print(f"[UPDATED] {init_path}")
                    else:
                        print(f"[SKIPPED] Aucun changement nécessaire pour {init_path}")
            else:
                with open(init_path, 'w', encoding='utf-8') as init_file:
                    init_file.write('\n'.join(imports))
                print(f"[CREATED] {init_path} avec : {', '.join(imports)}")
        else:
            if os.path.exists(init_path):
                with open(init_path, 'r', encoding='utf-8') as init_file:
                    if not init_file.read().strip():
                        print(f"[EMPTY] {init_path} est vide et n'a pas été modifié")
                    else:
                        print(f"[INFO] {init_path} existe mais n'a pas besoin de mise à jour")
    print("\n[INFO] Mise à jour des fichiers __init__.py terminée !")

def main():
    directory = input("Entrez le chemin du projet : ")
    if os.path.isdir(directory):
        print(f"\n[INFO] Lancement de la mise à jour des __init__.py pour {directory}...\n")
        update_init_files(directory)
    else:
        print("[ERROR] Dossier invalide, veuillez entrer un chemin valide.")

if __name__ == "__main__":
    main()
