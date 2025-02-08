import sys

def process_facture(filename):
    print(f"📄 Traitement de la facture : {filename}")
    # TODO: Ajouter ici le traitement complet de la facture

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Erreur : Aucun fichier spécifié.")
        sys.exit(1)

    process_facture(sys.argv[1])
