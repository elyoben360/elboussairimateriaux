# Parcours de commande

Le formulaire comporte trois étapes : matériaux et quantités, coordonnées et adresse, date souhaitée et vérification. Le panier reste stocké dans le navigateur ; les coordonnées ne sont pas enregistrées dans le stockage navigateur.

Le bouton final transmet les données à POST /api/orders. L’interface affiche une réception et sa référence uniquement après une réponse valide du serveur. La réception ne vaut pas confirmation des disponibilités ou de la date. Une erreur réseau, un délai dépassé ou un service indisponible laisse la réception non confirmée. Seule une reprise exacte est permise ; sinon, le visiteur est invité à contacter l’équipe pour vérifier. Ouvrir WhatsApp ne constitue jamais une preuve de réception.

Les tentatives identiques réutilisent une clé d’idempotence. Avant tout appel serveur, le navigateur doit enregistrer un verrou de transmission dans sa session : uniquement empreinte SHA-256 et clé aléatoire, sans coordonnées. Si cet enregistrement est impossible, aucune transmission n’est effectuée.

Après une réponse perdue, un délai dépassé ou une erreur, le verrou reste actif. Un contenu modifié ne peut pas produire de nouvelle clé ni être transmis tant que le résultat précédent n’a pas été retrouvé. Le visiteur doit restaurer exactement le récapitulatif et réessayer avec la même clé. Après rechargement, il doit ressaisir les mêmes coordonnées, date et commentaires, car ces données ne sont pas conservées. La réponse de reprise retrouve la référence si la commande avait déjà été enregistrée. Un refus structuré 400/413/415/429 ne libère le verrou que sur la toute première transmission, avec le marqueur serveur strict rejectedBeforeInsert. Sur reprise ou rechargement, même ce refus garde le verrou : une tentative antérieure peut déjà avoir été enregistrée. Les réponses illisibles, réseau, 409 et 503 restent incertaines. Une date devenue passée après minuit ne bloque pas la reprise strictement identique ; une nouvelle commande avec date passée reste refusée. Une réception confirmée libère le verrou ; une empreinte déjà reçue restitue sa référence sans nouvel appel.

Aucun message WhatsApp de nouvelle commande n’est proposé pendant une incertitude : le site invite à contacter l’équipe pour vérifier. Sans ressaisie exacte, il n’existe pas de recherche publique par clé ; une vérification avec l’équipe est nécessaire. Le verrou couvre la session de cet onglet, pas un nouvel appareil, un autre onglet indépendant, une suppression du stockage ni les tentatives antérieures à cette protection. Il ne remplace pas une vérification métier des doublons.

## Vérifications locales

- `node --check src/catalogue.js`
- `node tests/order-recovery.cjs` : réponse perdue après enregistrement simulé, modification bloquée, reprise exacte après rechargement, absence de coordonnées stockées et refus si stockage indisponible.
- `node tests/order-payload.cjs` : contrat de chaque variante du catalogue, coordonnées, livraison et références anciennes.
- `node tests/orders-backend.mjs` : réception et protections serveur.
- `python3 -m unittest discover -s tests -v`
- `python3 scripts/build.py --preview` puis `python3 scripts/stage_production.py` : artefacts locaux, sans déploiement.
- Navigateur : servir dist sur le port 8765 puis `node tests/order-flow.cjs` dans un environnement avec Playwright et Chromium (`CHROMIUM_PATH` configurable). Le test simule l’API et ne transmet aucune commande réelle.

Le test navigateur couvre les largeurs 320, 390 et 1280 px, sélection vide, champs requis, retours et corrections, erreur API, nouvelle tentative avec la même clé, réception simulée, rechargement et retrait. Ce script doit effectivement terminer avant de revendiquer la validation visuelle ou interactive. La validation locale du serveur ne prouve pas la disponibilité de l’API sur le domaine public.
