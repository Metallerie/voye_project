import os
import glob

def list_uml_versions():
    uml_dir = "/data/voye/docs/"
    uml_files = sorted(glob.glob(os.path.join(uml_dir, "project_structure_*.puml")), reverse=True)
    
    if not uml_files:
        print("⚠️ Aucun fichier UML trouvé.")
        return []
    
    print("📜 Historique des fichiers UML :")
    for idx, file in enumerate(uml_files):
        print(f"[{idx}] {file}")
    
    return uml_files

def restore_specific_version():
    uml_files = list_uml_versions()
    if len(uml_files) < 2:
        print("⚠️ Pas assez d'historique pour restaurer une version précédente.")
        return
    
    try:
        choice = int(input("🛠️ Entrez le numéro de la version à restaurer (hors dernière) : "))
        if choice <= 0 or choice >= len(uml_files):
            print("⚠️ Sélection invalide.")
            return
        
        last_uml = uml_files[0]
        selected_uml = uml_files[choice]
        
        print(f"🔄 Dernière version actuelle : {last_uml}")
        print(f"↩️ Restauration de : {selected_uml}")
        
        os.remove(last_uml)
        os.rename(selected_uml, last_uml)
        print("✅ Restauration terminée.")
    except ValueError:
        print("⚠️ Entrée invalide. Veuillez entrer un numéro valide.")

if __name__ == "__main__":
    restore_specific_version()
