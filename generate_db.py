import os
import json

LYRICS_FOLDER = 'lyrics'
OUTPUT_FILE = 'database.json'

data = []

if not os.path.exists(LYRICS_FOLDER):
    print(f"Le dossier '{LYRICS_FOLDER}' n'existe pas. Créez-le et mettez vos fichiers .lrc dedans.")
    exit()

print("Scan des fichiers en cours...")
files = sorted(os.listdir(LYRICS_FOLDER))

for filename in files:
    if filename.endswith(".lrc"):
        entry = {
            "filename": filename,
            "path": f"{LYRICS_FOLDER}/{filename}"
        }
        data.append(entry)

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Succès ! {len(data)} fichiers indexés dans {OUTPUT_FILE}.")