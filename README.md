# Générateur de mèmes — Flask

## Présentation

Application web qui permet d’importer une image, d’ajouter un texte en haut et en bas, de générer un mème, de consulter une galerie et de télécharger ou supprimer les créations.

Le projet illustre les bases d’une application web Python : routage Flask, formulaires HTML, traitement d’images avec Pillow et persistance des métadonnées avec SQLite via Flask-SQLAlchemy.

## Fonctionnalités

- Import d’image avec limite de taille.
- Vérification du format d’image.
- Ajout de texte avec contour pour améliorer la lisibilité.
- Génération et affichage d’une galerie.
- Téléchargement des images créées.
- Suppression d’un élément par requête POST.
- Stockage local des métadonnées dans SQLite.

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Pillow
- HTML / CSS

## Installation locale

1. Installer Python 3.10 ou une version compatible.
2. Créer un environnement virtuel :

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Installer les dépendances :

   ```powershell
   pip install -r requirements.txt
   ```

4. Lancer l’application :

   ```powershell
   python app.py
   ```

5. Ouvrir l’adresse locale indiquée dans le terminal.

La base SQLite est créée localement au premier lancement. Les fichiers importés et générés sont conservés dans les dossiers `static/uploads` et `static/generated`.

## Sécurité et limites

- Cette application est un projet de démonstration, pas un service prêt pour une exposition publique.
- La clé Flask par défaut est destinée au développement local. Définissez `FLASK_SECRET_KEY` avec une valeur aléatoire avant tout déploiement.
- Une protection CSRF n’est pas encore intégrée aux formulaires.
- Pour un déploiement public, ajouter notamment une protection CSRF, une politique de conservation des fichiers, une limitation de débit et une configuration de production adaptée.
- N’importez que des images que vous avez le droit d’utiliser.

## Structure

- `app.py` : routes Flask, traitement des images et accès aux données.
- `templates/index.html` : interface utilisateur.
- `static/style.css` : styles.
- `requirements.txt` : dépendances.
