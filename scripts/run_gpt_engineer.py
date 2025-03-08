import subprocess
import time
import shutil
import os
import openai

def run_command(command, cwd=None, stop_on_error=True):
    print(f"🔄 Exécution : {command} (dans {cwd if cwd else 'le répertoire actuel'})")
    process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        print(f"❌ Erreur lors de l'exécution : {command}\n{stderr.decode()}")
        if stop_on_error:
            print("🚨 Arrêt du script en raison d'une erreur.")
            exit(1)
    return stdout.decode()

def backup_prompt():
    prompt_file = "/data/voye/prompt.txt"
    backup_dir = "/data/prompt_backups/"
    os.makedirs(backup_dir, exist_ok=True)
    
    if os.path.exists(prompt_file):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"prompt_{timestamp}.txt")
        shutil.copy(prompt_file, backup_file)
        print(f"📂 Sauvegarde du prompt effectuée : {backup_file}")
    else:
        print("⚠️ Aucun prompt trouvé dans /data/voye/ à sauvegarder.")

def collect_code_from_project():
    project_dir = "/data/voye/"
    code_content = ""
    
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code_content += f"\n# Fichier : {file_path}\n"
                    code_content += f.read() + "\n"
    
    return code_content

def generate_uml_with_openai():
    print("🧠 Génération du fichier UML avec OpenAI basé sur le code source...")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    code_content = collect_code_from_project()
    
    prompt = f"""
    Analyse le projet suivant et génère un diagramme UML des classes et relations principales.
    Retourne uniquement du code PlantUML, sans explication supplémentaire.
    Voici le code source :
    {code_content}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "Tu es un assistant qui génère des diagrammes UML."},
                  {"role": "user", "content": prompt}]
    )
    
    uml_content = response.choices[0].message.content
    
    uml_file = f"/data/voye/docs/project_structure_{time.strftime('%Y%m%d_%H%M%S')}.puml"
    with open(uml_file, "w", encoding="utf-8") as f:
        f.write(uml_content)
    
    print(f"✅ UML généré et sauvegardé : {uml_file}")

def check_and_generate_uml():
    uml_dir = "/data/voye/docs/"
    if not os.path.exists(uml_dir):
        os.makedirs(uml_dir)
    
    uml_files = [f for f in os.listdir(uml_dir) if f.startswith("project_structure_") and f.endswith(".puml")]
    if not uml_files:
        print("🔍 Aucun fichier UML trouvé, génération avec OpenAI...")
        generate_uml_with_openai()
    else:
        print("✅ Un fichier UML existe déjà, poursuite du workflow normal.")

def overwrite_prompt():
    prompt_content = """📌 **Avant de coder, analyse l’architecture actuelle du projet.**  
    
1️⃣ **Lis le dernier fichier UML généré** (`docs/project_structure_YYYYMMDD_HHMMSS.puml`).  
   - Comprends la structure des classes et des relations.
   - Vérifie l'organisation du code existant.  
   - Assure-toi que ta modification s’intègre dans cette architecture.  

2️⃣ **Explique-moi brièvement ta compréhension de l'UML.**  
   - Quels sont les modules et classes principales ?  
   - Comment interagissent-ils ?  

3️⃣ **Applique ensuite les modifications demandées.**  
   - Respecte la structure actuelle du projet.  
   - Ne crée pas de nouvelles classes ou méthodes si elles existent déjà.  

4️⃣ **Une fois le code modifié, génère un nouveau fichier UML mis à jour.**  
   - Utilise OpenAI pour générer un nouvel UML.
   - Vérifie que le diagramme UML reflète bien tes changements.  

5️⃣ **Si les modifications ne conviennent pas, exécute `python scripts/restore_uml.py` pour revenir à l’ancienne version.**"""
    
    with open("/data/voye/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt_content)
    print("✅ Le prompt a été mis à jour dans /data/voye/prompt.txt")

def main():
    print("🚀 Initialisation du workflow GPT-Engineer avec gestion UML...")
    
    # Étape 1 : Sauvegarde du prompt précédent
    backup_prompt()
    
    # Étape 2 : Vérification et génération du premier UML si nécessaire
    check_and_generate_uml()
    
    # Étape 3 : Écraser l'ancien prompt et créer un nouveau
    overwrite_prompt()
    
    # Étape 4 : Pause pour permettre la modification du prompt
    input("✋ Le prompt a été mis à jour. Modifiez-le si nécessaire, puis appuyez sur Entrée pour continuer...")
    
    # Étape 5 : Lancer GPT-Engineer avec le prompt mis à jour dans le bon dossier
    print("🛠️ Lancement de GPT-Engineer avec le prompt mis à jour...")
    run_command("poetry run gpt-engineer /data/voye", cwd="/data/voye/gpt-engineer/", stop_on_error=True)
    
    # Étape 6 : Mise à jour UML après modification
    print("🔹 Mise à jour du fichier UML après modification...")
    generate_uml_with_openai()
    
    # Étape 7 : Proposer la restauration si besoin
    choice = input("⚠️ Souhaitez-vous annuler les modifications et restaurer l'ancienne version UML ? (y/n) ")
    if choice.lower() == "y":
        print("🔄 Restauration en cours...")
        run_command("python scripts/restore_uml.py", stop_on_error=True)
    else:
        print("✅ Modifications validées.")
    
    print("🎯 Workflow terminé !")

if __name__ == "__main__":
    main()
