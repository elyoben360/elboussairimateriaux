# Circuit éditorial et Instagram

## Routine quotidienne configurée

La tâche « Sélection éditoriale BTP » est activée chaque jour à 10 h dans le fuseau Africa/Casablanca (heure du Maroc, y compris ses changements saisonniers). Elle recherche 3 à 10 sujets, contrôle les dates des faits et de publication, rapproche les chiffres avec leurs sources, puis présente titres, résumés, liens et intérêt commercial. S’il manque des informations vérifiables, la sélection doit être plus courte et le signaler. L’ancienne tâche « Journal matériaux Maroc » de 8 h n’a pas été modifiée.

La tâche transmet la sélection dans ChatGPT ; elle ne peut pas garantir à elle seule une réponse future du propriétaire. Après sélection explicite des sujets dans la conversation, Work prépare l’article complet, les sources, le carrousel 4–6 diapositives et sa légende sur une branche de développement. Les images de chantier restent des photographies réelles. Pour une illustration de marché, utiliser un visuel éditorial identifié et autorisé, jamais une fausse réalisation.

## Gestion des articles

content/articles.json est la source de contenu. Chaque article comporte : identifiant, slug, titre, résumé, catégorie, date, type, illustration, sections, sources avec leurs dates, vérification et déclinaison Instagram. Pour une actualité, enregistrer également les dates des faits et leurs périmètres dans les sections et la note de vérification. Ne pas présenter un communiqué ancien comme une nouvelle du jour.

États : proposed → selected → writing → review → approved → published. Les étapes de validation ne doivent pas être sautées. Les validations site et Instagram sont séparées et liées à l’empreinte SHA-256 du contenu. Une modification du texte, des sources, de la légende ou des diapositives invalide l’accord précédent. L’empreinte est une protection contre les erreurs de version, pas une authentification : seul le propriétaire peut donner l’accord effectif dans la conversation. Les exports du script n’effectuent aucun appel réseau.

Le build de prévisualisation affiche les brouillons avec noindex et une mention visible. Le build production exclut les articles non publiés, l’atelier et ses visuels de démonstration. Un brouillon technique est fourni uniquement pour tester tout le parcours, sans inventer de nouvelle de marché.

## Réseau social : état réel

Aucun compte Instagram n’est connecté ou identifié dans ce travail. Aucune bio ni publication n’a été changée. Le nom d’utilisateur du compte professionnel reste à confirmer. Metricool a été identifié comme intégration disponible à connecter ; ni installation, ni compte, ni abonnement payant n’ont été créés. Son accès effectif et ses capacités de publication de carrousels pour le compte devront être vérifiés après connexion. Il est possible de conserver les exports et de passer par une publication manuelle dans Meta Business Suite si aucune intégration autorisée ne convient.

La documentation officielle Meta (collection Instagram publiée par Meta sur Postman : https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api) décrit la publication pour les comptes professionnels, via des conteneurs de médias et une étape de publication distincte. Le parcours Facebook Login demande un compte Instagram professionnel lié à une Page. Le parcours Instagram Login et ses permissions doivent être validés dans la configuration réelle de l’application au moment de la connexion ; ne pas déduire d’une connexion Gmail ou GitHub un accès Meta.

Si une application Meta dédiée est choisie après autorisation : OAuth par le propriétaire, permissions minimales adaptées au type de connexion, identité du compte professionnel vérifiée et secrets conservés côté serveur. Les visuels devront être disponibles aux URL HTTPS accessibles par Meta avant publication. Le module meta_payload prépare les paramètres d’un carrousel mais ne les transmet pas. Aucun jeton ne doit être collé dans les fichiers, les logs, les commandes shell ou une page statique. Vérifier les exigences et quotas courants avec l’intégration connectée avant toute publication réelle.

## Liens de profil préparés, non appliqués

| Intitulé | URL prévue | État |
|---|---|---|
| Lire nos actualités BTP | https://elboussairimateriaux.com/actualites/ | Route fonctionnelle en développement, à vérifier publiquement APRÈS autorisation et déploiement |
| Commander mes matériaux | https://elboussairimateriaux.com/#catalogue | Ancre du catalogue existant ; le nouveau parcours est testé en développement |

Ne rien ajouter à la bio avant vérification des URL exactes sur la production et autorisation explicite du propriétaire. La dernière diapositive de chaque carrousel doit contenir exactement : « Lire l'article complet — lien en bio ».

## Ce qui est testé / ce qui reste externe

Le test automatisé déroule sélection, préparation, relecture, accord de test, export site et préparation de la charge utile Meta. Il vérifie les refus sans accord, les accords invalidés après modification et la séparation site/Instagram. Les boutons de l’atelier sont une simulation locale clairement identifiée : ils n’appellent pas un modèle ni Meta. Les articles et cinq JPEG réels de démonstration sont générés séparément par les scripts.

La publication réelle sur le site et sur Instagram n’est pas testée, car elle n’est pas autorisée dans cette mission. Une nouvelle validation est requise pour la fusion dans main, le déploiement, l’exposition des médias de publication et l’envoi Meta. Aucun changement de permissions de compte n’a été effectué.
