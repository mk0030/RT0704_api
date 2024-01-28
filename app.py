from flask import Flask, render_template, request, jsonify
import requests
import json
from flask_cors import CORS
import os
import uuid
from fnmatch import fnmatch
app = Flask(__name__, static_url_path='/static')
CORS(app)
API_KEY = 'aac19cc46b730b8b2f70f53b819fad71'

API_MOVIES_URL = "https://api.themoviedb.org/3/movie/popular?api_key=aac19cc46b730b8b2f70f53b819fad71"

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATA_FILE = 'films.json'

@app.route('/')
def home():
    return "hello"

    
@app.route('/films', methods=["GET"] )
def get_films():
    with open('films.json', 'r') as f:
        films = json.load(f)
    return jsonify(films)

@app.route('/films', methods= ["POST"])
def post_films():
    try:
        titre = request.form['titre']# Récupérer les données du formulaire
        realisateur = request.form['realisateur']
        annee = request.form['annee']
        genre = request.form['genre']
        description = request.form['description']
        film_id = str(uuid.uuid4()) # Générer un identifiant unique pour le film avec uuid
        if 'image' in request.files:# Gérer le fichier d'image
            image = request.files['image']
            if image.filename != '':
                nom_unique = f"{film_id}.jpg"  # Générer un nom de fichier unique avec uuid
                chemin_image = os.path.join(app.config['UPLOAD_FOLDER'], nom_unique) # Enregistrer l'image dans le répertoire /static/images/
                image.save(chemin_image)
            else:
                chemin_image = None
        else:
            chemin_image = None
        donnees_formulaire = {# Créer un dictionnaire avec les données
            'id': film_id,
            'titre': titre,
            'realisateur': realisateur,
            'annee': annee,
            'genre': genre,
            'description': description,
            'url_image': chemin_image
        }
        enregistrer_donnees(donnees_formulaire)# Enregistrer les données dans le fichier JSON
        return jsonify({"message": "Données enregistrées avec succès!"}), 200
    except Exception as e:
        return jsonify({"message": "Erreur lors de l'enregistrement des données", "error": str(e)}), 500
def enregistrer_donnees(donnees):
    try:    
        if os.path.exists(DATA_FILE): # Charger les données existantes du fichier JSON
            with open(DATA_FILE, 'r') as f:
                films = json.load(f)
        else:
            films = []
        films.append(donnees)# Ajouter les nouvelles données
        with open(DATA_FILE, 'w') as f:# Enregistrer les données mises à jour dans le fichier JSON
            json.dump(films, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de l'enregistrement des données : {str(e)}")


@app.route('/films/<film_id>', methods= ["DELETE"])
def delete_film(film_id):
    try:
        # Charger les données existantes du fichier JSON
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                films = json.load(f)
        else:
            return jsonify({"error": "Fichier de données introuvable"}), 404

        # Trouver et supprimer le film avec l'ID correspondant
        films = [film for film in films if film.get('id') != film_id]

        # Enregistrer les données mises à jour dans le fichier JSON
        with open(DATA_FILE, 'w') as f:
            json.dump(films, f, indent=4)

        return jsonify({"message": "Film supprimé avec succès"}), 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la suppression du film : {str(e)}"}), 500

@app.route('/films/<film_id>', methods= ["PUT"])
def put_films(film_id):
    try:
    # Récupérer les données du formulaire
        titre = request.form['titre']
        annee = request.form['annee']
        realisateur = request.form['realisateur']
        genre = request.form['genre']
        description = request.form['description']

        # Récupérer le fichier image du formulaire
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                nom_unique = str(uuid.uuid4()) + '.jpeg'
                chemin_image = os.path.join(app.config['UPLOAD_FOLDER'], nom_unique)
                image.save(chemin_image)
            else:
                chemin_image = None
        else:
            chemin_image = None

        # Charger les données existantes du fichier JSON
        with open(DATA_FILE, 'r') as f:
            films = json.load(f)

        # Mettre à jour les informations du film avec l'ID correspondant
        for film in films:
            if film.get('id') == film_id:
                film['titre'] = titre
                film['annee'] = annee
                film['realisateur'] = realisateur
                film['genre'] = genre
                film['description'] = description
                film['url_image'] = chemin_image

        # Enregistrer les données mises à jour dans le fichier JSON
        with open(DATA_FILE, 'w') as f:
            json.dump(films, f, indent=4)

        return jsonify({"message": "Film mis à jour avec succès"}), 200
    except Exception as e:
        return jsonify({"message": "Erreur lors de la mise à jour du film", "error": str(e)}), 500

@app.route('/films/recherche', methods=["GET"])
def recherche_films():
    terme_recherche = request.args.get('terme')

    if terme_recherche:
        try:
            with open(DATA_FILE, 'r') as f:
                films = json.load(f)

            resultats_recherche = [film for film in films if terme_recherche.lower() in film['titre'].lower()]
            return jsonify(resultats_recherche), 200
        except Exception as e:
            return jsonify({"message": "Erreur lors de la recherche", "error": str(e)}), 500

    return jsonify({"message": "Terme de recherche vide"}), 400

if __name__ == '__main__':
    app.run(debug=True)






