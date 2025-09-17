# Instructions pour l'exportation depuis Burp Suite

Pour utiliser ce script avec les données exportées depuis Burp Suite, suivez ces instructions :

## Prérequis

1. **Désactiver l'encodage Base64** lors de l'exportation
2. **Renommer le fichier exporté** avec l'extension appropriée (.txt ou .xml)

## Étapes d'exportation

### 1. Désactiver l'encodage Base64

Lors de l'exportation depuis Burp Suite, assurez-vous de désactiver l'option d'encodage Base64 :

![Désactiver Base64 dans Burp Suite](https://i.imgur.com/example.png)

*Dans l'image ci-dessus, vous pouvez voir où décocher l'option "Base64-encode items" avant d'exporter.*

### 2. Exporter le fichier

1. Dans Burp Suite, allez dans l'onglet "Target" ou "Proxy" selon ce que vous voulez exporter
2. Faites un clic droit sur les éléments que vous souhaitez exporter (de préférence, un dossier)
3. Sélectionnez "Save selected items" ou "Export" selon votre version de Burp Suite
4. Choisissez un format (XML ou TXT)
5. **Décochez l'option "Base64-encode items"**
6. Enregistrez le fichier

### 3. Renommer le fichier

Après avoir exporté le fichier, vous pouvez le renommer avec l'extension appropriée :

- Si vous avez exporté en format texte : renommez le fichier avec l'extension `.txt`
- Si vous avez exporté en format XML : renommez le fichier avec l'extension `.xml`

## Dépannage

Si vous rencontrez des erreurs :

1. Vérifiez que le fichier n'est pas encodé en Base64
2. Assurez-vous que l'extension du fichier est correcte (.txt ou .xml)
3. Vérifiez que le contenu du fichier est bien formaté

Pour toute question supplémentaire, n'hésitez pas à ouvrir une issue sur ce dépôt.