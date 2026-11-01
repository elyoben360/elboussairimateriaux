# Contrôle du 1 novembre 2026

Le dépôt inspecté contient un site statique. Aucun backend, binding de base de données ou serveur de réception de commandes n’est présent. Le panier reste dans le navigateur ; les coordonnées du formulaire sont transmises uniquement par l’action WhatsApp/email du visiteur. Aucun audit d’une base externe, du compte Cloudflare ou des sauvegardes d’hébergement n’a été effectué.

Les en-têtes générés appliquent CSP (scripts locaux et empreintes exactes du JSON-LD), interdiction des connexions fetch/XHR, des objets et de l’encapsulation, blocage du détournement de base URL, restrictions des permissions et HSTS sur le domaine courant. Les styles en ligne existants restent permis. La politique est adaptée au site statique actuel : une future API devra être explicitement déclarée.

Le déploiement existant conserve la liste autorisée .assetsignore ; sources, contenu éditorial de travail et documents internes ne doivent pas être servis. Le dépôt GitHub étant public, n’y stocker aucune donnée client confidentielle, aucun prix d’achat ni secret. Un fichier exclu du site reste consultable dans le dépôt public.

Les quarante variantes WebP des vingt nouvelles photographies sont réencodées sans EXIF, GPS ou numéro de série. Les descriptions et données structurées se limitent au contenu visible et à l’attribution déclarée par le propriétaire ; aucun lieu de prise de vue, stock chiffré, certification ou caractéristique technique non vérifiée n’est ajouté.

À vérifier avec un accès d’administration à l’hébergement : MFA, droits des collaborateurs, jetons de déploiement à privilèges minimaux, restauration et sauvegardes des éventuels services externes. Le versionnement Git conserve le code et les images ; il ne sauvegarde pas une base externe.

Les visages sur les photographies du chariot et du camion-grue ont été floutés avec l’outil de retouche. Seules leurs versions floutées sont ajoutées au dépôt public.

## Images et navigation — ajout du 1 novembre 2026

Le propriétaire confirme que les photographies proviennent de son téléphone et de son propre travail. Les nouvelles copies publiques sont limitées à 1280 px et 560 px, réencodées sans EXIF/GPS. Les originaux JPEG ne sont pas ajoutés au dépôt ni à l’hébergement. Huit vues utiles sont retenues dans le troisième lot ; une capture avec interface et une vue redondante sont écartées.

Attribution visible sur les galeries, aperçus et agrandissements ; copyright, créateur, conditions de réutilisation et demande d’autorisation dans les données structurées. Les nouvelles images WebP contiennent aussi les métadonnées XMP de droits. L’attribution visuelle est un calque d’interface : elle ne constitue pas un filigrane incorporé aux pixels et peut être retirée hors du site. CORP same-origin limite l’incorporation intersite dans les navigateurs compatibles. Aucune garantie anti-copie, aucun blocage du clic droit ni promesse de trafic SEO.

Les métadonnées publiques sont descriptives ; aucun numéro de série du téléphone, géolocalisation ou date de prise de vue déduite n’est publié. Le catalogue ne publie aucun prix d’achat. Aucune performance chiffrée, classement feu, isolation, agrément structurel ou exclusivité commerciale n’est inventé pour les panneaux.
