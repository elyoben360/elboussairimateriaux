# Contrôle du 1 novembre 2026

Le dépôt inspecté contient un site statique. Aucun backend, binding de base de données ou serveur de réception de commandes n’est présent. Le panier reste dans le navigateur ; les coordonnées du formulaire sont transmises uniquement par l’action WhatsApp/email du visiteur. Aucun audit d’une base externe, du compte Cloudflare ou des sauvegardes d’hébergement n’a été effectué.

Les en-têtes générés appliquent CSP (scripts locaux et empreintes exactes du JSON-LD), interdiction des connexions fetch/XHR, des objets et de l’encapsulation, blocage du détournement de base URL, restrictions des permissions et HSTS sur le domaine courant. Les styles en ligne existants restent permis. La politique est adaptée au site statique actuel : une future API devra être explicitement déclarée.

Le déploiement existant conserve la liste autorisée .assetsignore ; sources, contenu éditorial de travail et documents internes ne doivent pas être servis. Le dépôt GitHub étant public, n’y stocker aucune donnée client confidentielle, aucun prix d’achat ni secret. Un fichier exclu du site reste consultable dans le dépôt public.

Les quarante variantes WebP des vingt nouvelles photographies sont réencodées sans EXIF, GPS ou numéro de série. Les descriptions et données structurées se limitent au contenu visible et à l’attribution déclarée par le propriétaire ; aucun lieu de prise de vue, stock chiffré, certification ou caractéristique technique non vérifiée n’est ajouté.

À vérifier avec un accès d’administration à l’hébergement : MFA, droits des collaborateurs, jetons de déploiement à privilèges minimaux, restauration et sauvegardes des éventuels services externes. Le versionnement Git conserve le code et les images ; il ne sauvegarde pas une base externe.

Les visages sur les photographies du chariot et du camion-grue ont été floutés avec l’outil de retouche. Seules leurs versions floutées sont ajoutées au dépôt public.
