import os
import json

# Configuration
LYRICS_FOLDER = 'lyrics'
OUTPUT_FILE = 'database.json'

data = []

# Vérifier si le dossier existe
if not os.path.exists(LYRICS_FOLDER):
    print(f"Le dossier '{LYRICS_FOLDER}' n'existe pas. Créez-le et mettez vos fichiers .lrc dedans.")
    exit()

# Boucle sur les fichiers
print("Scan des fichiers en cours...")
for filename in os.listdir(LYRICS_FOLDER):
    if filename.endswith(".lrc"):
        # On crée un objet simple pour chaque fichier
        entry = {
            "filename": filename,
            "path": f"{LYRICS_FOLDER}/{filename}"
        }
        data.append(entry)

# Écriture du fichier JSON
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Succès ! {len(data)} fichiers indexés dans {OUTPUT_FILE}.")