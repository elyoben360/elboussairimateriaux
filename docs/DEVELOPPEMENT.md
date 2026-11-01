# Version de développement — 1 novembre 2026

## Audit et déploiement existant

Le dépôt d’origine contient README.md et index.html : site statique, sans framework ni backend. HTML, CSS et JavaScript natifs. Le catalogue comprend 17 gammes et toutes leurs variantes. Six photos de Bouznika étaient intégrées dans le HTML en base64. Les commandes ouvrent WhatsApp ou le logiciel de messagerie ; aucun serveur de commande ne les réceptionne.

Hébergement existant : Worker Cloudflare `royal-rice-7dd9`. La conversation confirme la liaison GitHub/main et la commande `npx wrangler deploy --name royal-rice-7dd9 --assets . --compatibility-date 2026-10-23`. Les paramètres actuels du tableau de bord Cloudflare n’ont pas été inspectés : les contrôler avant une future mise en production. Aucun changement effectué sur main, les DNS ni les paramètres Cloudflare.

Branche de travail : `dev/site-editorial-2026-11-01`. Pas de fusion automatique, pas de workflow de déploiement, pas de commandes de publication ajoutées. Le fichier index.html à la racine reste celui de production ; la nouvelle version est construite uniquement dans dist. Les prévisualisations du Worker étaient désactivées selon la configuration décrite par le propriétaire ; aucun déclenchement distant de production n’est nécessaire pour tester.

## Source et composants

- src/home.html : page d’accueil et parcours matériaux/livraison.
- src/legacy.css + src/site.css : marque existante et composants responsive.
- src/catalogue.js et content/catalogue.json : 17 gammes d’origine, variantes, unités, panier et demandes conservés. Après modification des données, synchroniser DATA en tête de catalogue.js ou utiliser scripts/sync_catalogue.py.
- content/references.json : modèle unique de référence. photos : validées ; pending_photos : visibles en aperçu seulement.
- src/references.js : fiches, galeries réutilisables, flèches, défilement tactile, zoom et navigation clavier.
- content/articles.json : gestion des articles ; scripts/build.py produit les pages statiques, titres, descriptions, URLs, sitemap et données structurées.
- scripts/editorial.py : validation de structure et accord lié à l’empreinte du contenu, distinct pour site/Instagram ; exports uniquement, jamais d’appel réseau.
- scripts/carousel.py : carrousels JPEG exacts en bleu/doré (Pillow, polices DejaVu).
- src/atelier.html : démonstration uniquement en aperçu ; absente des builds production.

## Exécuter et tester

Python 3 standard suffit au build. Pillow est requis seulement pour les carrousels : installer depuis PyPI si absent dans l’environnement de travail. Aucun service payant nécessaire.

```
python3 scripts/sync_catalogue.py
python3 -m unittest discover -s tests -v
python3 scripts/carousel.py --article demo-logistique --out preview-media/demo-logistique
python3 scripts/build.py --preview
python3 scripts/build.py --out dist-production
```

Les deux dernières commandes créent des fichiers, elles ne déploient rien. Ne pas utiliser la production pour montrer les brouillons. Le build production exclut l’atelier, les brouillons et les photos en attente.

## Publication future — validation requise

Après accord explicite seulement : vérifier les éléments à confirmer, auditer le diff, puis choisir avec le propriétaire la fusion et la modification des paramètres Cloudflare (Build command `python3 scripts/build.py`, Deploy command pointant sur `--assets ./dist` et conservant le nom du Worker et sa date de compatibilité). Ne jamais déployer `--assets .` pour cette nouvelle architecture : cela exposerait les sources et brouillons. Conserver la configuration existante tant que la publication n’est pas autorisée. Vérifier les deux domaines et les liens définitifs après déploiement.

## Points commerciaux à confirmer

La fiche Aïn Diab utilise les dernières données : 24/10/2026, B7/B10, environ 3 500 unités à confirmer, camion-grue, rénovation de villa. Aucun classement patrimonial. Les huit photographies originales reçues sont optimisées mais leur rattachement à cette fiche est en attente de validation. Aucun prix, stock, autorisation administrative obtenue ou absence d’incident n’est inventé.

## Sécurité

Aucun mot de passe, jeton, clé ou secret n’est nécessaire au site statique. Aucun formulaire de login trompeur ni faux CMS protégé par JavaScript. L’atelier est un outil de prévisualisation, pas un espace privé authentifié. Le dépôt est actuellement PUBLIC : ne jamais y ajouter de notes confidentielles. Les coordonnées des formulaires restent en mémoire ; seul le panier de matériaux est stocké localement. Un export validé ne vaut pas autorisation de transmission. Les secrets Meta éventuels doivent rester dans un gestionnaire de secrets du serveur, jamais dans le navigateur, le dépôt ni un build statique. Aucun SDK tiers, tracker ou formulaire d’identifiants ajouté. Les en-têtes de sécurité doivent être vérifiés sur l’hébergement après le futur déploiement.

## Mise en production autorisée

Le propriétaire a explicitement autorisé le transfert du code et des photos au dépôt public et le déploiement. scripts/stage_production.py génère le build de production puis copie les seuls fichiers publics à la racine pour rester compatible avec la commande Cloudflare existante --assets . (à vérifier par le déploiement distant). .assetsignore utilise une liste de fichiers autorisés : les sources, notes, brouillons, atelier et photos Aïn Diab en attente sont exclus du site. Aucun secret nécessaire. La conservation intégrale du catalogue est comparée au commit historique 372f241. Pour chaque future mise à jour, exécuter le script de préparation et committer les fichiers générés.
