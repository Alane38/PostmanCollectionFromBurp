# PostmanCollectionFromBurp

![Project Logo](https://i.imgur.com/example-logo.png)

Un outil pour convertir les exports de Burp Suite en collections Postman, facilitant le test et le débogage des requêtes HTTP.

## 📌 Table des matières
- [PostmanCollectionFromBurp](#postmancollectionfromburp)
  - [📌 Table des matières](#-table-des-matières)
  - [📝 Description](#-description)
  - [✨ Fonctionnalités](#-fonctionnalités)
  - [🛠 Prérequis](#-prérequis)
  - [🔧 Installation](#-installation)
  - [📤 Exportation depuis Burp Suite](#-exportation-depuis-burp-suite)
  - [🚀 Utilisation](#-utilisation)
  - [📂 Exemples](#-exemples)
  - [🤝 Contribution](#-contribution)
  - [📄 Licence](#-licence)

## 📝 Description

PostmanCollectionFromBurp est un outil qui permet de convertir les données exportées depuis Burp Suite en collections Postman. Cela facilite le partage, le test et l'automatisation des requêtes HTTP capturées lors de tests de sécurité ou de développement.

## ✨ Fonctionnalités

- Conversion des requêtes Burp Suite en collections Postman
- Prise en charge des formats XML et texte
- Gestion des en-têtes et des corps de requête
- Organisation des requêtes en dossiers
- Exportation des variables d'environnement

## 🛠 Prérequis

- Python 3.6 ou supérieur
- Burp Suite (pour l'exportation des données)
- Postman (pour importer les collections)

## 🔧 Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/Alane38/PostmanCollectionFromBurp.git
```

2. Accédez au répertoire du projet :
```bash
cd PostmanCollectionFromBurp
```

## 📤 Exportation depuis Burp Suite

Pour utiliser ce script, vous devez d'abord exporter vos données depuis Burp Suite :

1. **Désactiver l'encodage Base64** :
   - Dans Burp Suite, lors de l'exportation, assurez-vous de décocher l'option "Base64-encode items"
   - ![Désactiver Base64](https://i.imgur.com/disable-base64.png)

2. **Exporter le fichier** :
   - Allez dans l'onglet "Target" ou "Proxy"
   - Sélectionnez les éléments à exporter
   - Choisissez "Save items" ou "Export"
   - Sélectionnez le format (XML ou TXT)
   - Enregistrez le fichier

3. **Renommer le fichier** :
   - Renommez le fichier exporté avec l'extension `.txt` ou `.xml` selon le format choisi

## 🚀 Utilisation

Pour convertir un fichier exporté depuis Burp Suite en collection Postman :
```bash
python main.py chemin/vers/votre_fichier.txt
```

ou pour un fichier XML :
```bash
python main.py chemin/vers/votre_fichier.xml
```

Le script générera un fichier de collection Postman que vous pourrez importer directement dans Postman.

## 📂 Exemples

Voici quelques exemples d'utilisation :

1. Conversion du fichier XML par défaut :
```bash
python main.py exports/burp_export
```

2. Conversion d'un fichier texte :
```bash
python main.py exports/burp_export.txt output/postman_collection.json
```

1. Conversion d'un fichier XML avec un nom de collection spécifique :
```bash
python main.py exports/burp_export.xml output/ma_collection.json
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

1. Fork le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.