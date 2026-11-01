# Publication du journal toutes les deux heures

Le propriétaire a demandé le 1 novembre 2026 une publication automatique d’actualités sourcées sur les matériaux, le BTP et le transport de marchandises au Maroc. Cette instruction remplace la sélection manuelle préalable pour le SITE. Instagram conserve une validation distincte et n’est pas connecté.

## Chaîne réelle

Une tâche ChatGPT programmée toutes les deux heures, fuseau Africa/Casablanca, recherche et lit les publications récentes. Elle prépare un à deux nouveaux articles distincts par exécution, dans la limite de 24 par jour, seulement si les sources sont vérifiables. Elle récupère le dernier main du dépôt elyoben360/elboussairimateriaux, traite les contenus et publie les fichiers du site via le connecteur GitHub. La liaison existante Cloudflare Workers Builds déploie main. Ni accès Cloudflare interactif ni nouveau secret n’est nécessaire pour cette voie.

La tâche est le planificateur et le chercheur/rédacteur. Le dépôt seul n’effectue pas de recherches et ne contient aucun faux cron. La première exécution planifiée devra être contrôlée dans les résultats de la tâche ; une configuration active n’est pas une garantie de réussite future. En cas d’échec de recherche, d’accès GitHub ou de Cloudflare : conserver le site existant, fournir l’erreur exacte et ne pas annoncer de publication réussie.

## Vérification et préparation

1. Lire les pages exactes : titre, date de publication, date/période des faits, chiffres, unités, périmètre, source primaire et éventuelle mise à jour.
2. Préférer HCP, APC, autorités et opérateurs officiels. À défaut, recouper au moins deux éditeurs indépendants de la liste content/editorial-policy.json. Aucune source non datée ou non lue. Aucun article vieux de plus de sept jours dans le fil récent. Une statistique mensuelle récente conserve la période ancienne explicite.
3. Éviter les doublons par sujet, slug et URL de source ; ne pas multiplier les articles à partir du même communiqué. Pas de reprise intégrale d’articles, d’images de presse sans droits ni de prix commerciaux inventés. Rédiger une synthèse originale et distinguer clairement la lecture éditoriale des faits.
4. Préparer un tableau JSON d’articles selon content/articles.json : id/slug uniques, status review, title/summary/category/date, event_period, illustration locale /assets/, cover_alt, sections [{title,paragraphs}], source_note, sources [{title,url,date}], verification {checked_on,facts_checked,date_checked,evidence}, instagram {caption,slides}. Les cinq diapositives textuelles peuvent être préparées, jamais publiées automatiquement sur Instagram. Dernière diapositive : Lire l'article complet — lien en bio.
5. Enregistrer ce lot dans un fichier temporaire hors du dépôt et exécuter `python3 scripts/news_batch.py --batch /chemin/lot-verifie.json`. Ce script vérifie structure, éditeurs, dates, doublons, quota, période et autorisation ; il ne remplace pas la lecture documentaire par le chercheur. Il ajoute une trace de publication automatique selon la politique, pas une fausse validation humaine.
6. Exécuter `python3 scripts/build.py --preview`, `python3 scripts/stage_production.py`, `python3 -m unittest discover -s tests -v`, puis contrôler liens, sitemap, RSS et l’absence de brouillons dans les fichiers publics. La comparaison catalogue utilise le commit historique 372f241.
7. Diff autorisé pour la tâche de veille : content/articles.json ; pages dans actualites/ ; index.html pour les derniers articles ; sitemap.xml, _headers pour les empreintes CSP et fichiers générés dans assets/ si requis par le build. Ne pas modifier catalogue, contacts, références, scripts, politique, accès ou configuration d’hébergement pendant une exécution de veille.
8. Publier un commit atomique avec le connecteur GitHub. Les objets GitHub create_blob/create_tree/create_commit puis update_ref(main, expected_sha=SHA lu au départ) suffisent. Pour les blobs inchangés, conserver leurs SHA. Ne pas forcer une branche. En cas de concurrence, recharger main et réappliquer le lot en préservant les articles et autres changements. Ne jamais écraser un article antérieur ni stocker de secret. Le fichier .assetsignore maintient les sources hors du site.
9. Attendre l’état terminal Cloudflare Workers Builds pour le nouveau commit (API publique GitHub check-runs si le connecteur ne l’expose pas), puis vérifier au moins la page du journal et une nouvelle URL. Signaler le résultat exact et les liens publiés à l’utilisateur. Sans nouvel article vérifiable, ne pas créer de commit vide ; expliquer brièvement l’absence de nouveauté.

## Désactivation et limites

La tâche se désactive dans ChatGPT ; content/editorial-policy.json permet aussi de refuser les nouveaux lots. Les articles existants restent consultables. Un contrôle de format ne prouve pas l’exactitude d’une actualité : celle-ci dépend des vérifications du chercheur. La publication directe sur Instagram attend toujours une intégration autorisée. Aucun abonnement payant ajouté.

## Première livraison

Deux synthèses sourcées sont préparées le 1 novembre 2026 : note HCP publiée le 30 octobre sur septembre 2026 ; dépêche MAP du 31 octobre sur le lancement des opérations du terminal Est de Nador West Med, ajoutée à la demande du propriétaire, avec le communiqué officiel du 28 octobre en contexte. Aucun ancien brouillon de démonstration n’est publié. Les huit photos Aïn Diab sont désormais affectées à la référence à la demande explicite du propriétaire. L’accueil utilise la même photographie réelle avec un filtre bleu CSS.

## Illustrations, regroupement et animation

La tâche active 6ae68bbad17c8191bca9b7aa0fc0a010 est passée à un intervalle de deux heures le 1 novembre 2026 à la demande du propriétaire. Elle n’impose aucun quota : sans nouveauté vérifiable, aucun article n’est créé. La recherche couvre aussi les publications officielles AMMC et Holcim. Ne jamais présenter un ancien rapport comme une nouvelle information à chaque passage.

Chaque article comporte une image locale autorisée, un texte alternatif, une légende précisant son lien réel avec le sujet, un crédit et les dimensions. Les images du propriétaire sont descriptives de son activité ; elles n’illustrent jamais faussement un autre port ou chantier. Utiliser les mêmes chemins d’assets, sans recopier les fichiers. Les galeries regroupent automatiquement les médias par produit ou sujet grâce à product_pages.album_key. Les articles de type « Notre activité » sont des reportages internes fondés sur les informations/photos du propriétaire ; la veille externe ne doit pas en inventer de nouveaux.

Le build insère les nouveaux titres dans le bandeau défilant et les carrousels. L’animation s’arrête hors écran, dans un onglet masqué, au survol ou à la demande. Les réglages de réduction des mouvements sont respectés. Une animation n’est pas une publication et le navigateur ne prétend pas rechercher de nouvelles sources en arrière-plan.

## Photographies réelles uniquement — dernière instruction du propriétaire

Aucune image IA n’est autorisée, y compris arrière-plans, couvertures, vignettes et images de secours. Utiliser uniquement une photographie réelle liée au sujet et dont les droits de réutilisation ont été vérifiés sur la page originale. Google permet de découvrir la source, pas de prouver la licence. Préférer domaine public/CC0 ou licence libre compatible avec crédit et lien. Garder auteur, page source, fichier original, licence, lien de licence et date de vérification dans cover_provenance et content/media-licenses.json. Les crédits et liens de licence doivent rester visibles sur l’article, et les légendes doivent préciser si un autre lieu est représenté. Si aucune photo appropriée n’est trouvée, conserver le nouvel article en attente : jamais de génération IA.

Les photos du propriétaire restent dans son catalogue, ses références et les articles « Notre activité ». Les floutages des visages sont obtenus par traitement local classique des pixels originaux. Les anciennes versions régénérées par IA sont retirées des fichiers publics et remplacées par de nouvelles URLs. Les originaux privés ne sont jamais publiés.

Madriers : mètre linéaire uniquement. Polystyrène : m³ uniquement. Fer à béton : kg, tonne ou barre. Le héros défile dès l’ouverture sans clic ni arrêt au simple survol. Le journal ouvre par défaut « Marché & projets » ; les reportages internes restent consultables par « Notre activité ».
