# Recette de la version de développement

Les contrôles concernent la nouvelle version locale et son aperçu autonome. Ils ne prouvent pas un déploiement sur le domaine public.

- Identité bleu marine/doré et polices Georgia/Arial conservées ; logo transformé en lien d’accueil.
- Comparaison complète des données : les 17 gammes et toutes leurs variantes sont identiques à main.
- Catalogue : filtre Ciments et liants, choix CPJ 35, quantité 2, unité tonne, ajout au panier et compteur vérifiés dans le navigateur.
- Logistique : refus explicite sans matériaux ; association d’un camion-grue à la commande et récapitulatif vérifiés. Aucun envoi de formulaire ni message réel.
- Validation des formulaires : champs requis conservés ; adresses WhatsApp, téléphone et email contrôlées dans le code. L’envoi reste déclenché par le visiteur, aucun test de transmission réelle effectué.
- Références : ouverture Aïn Diab, date du 24/10/2026, informations en attente, zoom et passage photo 1 → 2 vérifiés. Vue mobile à 360 px, défilement des cartes et dialogue sans débordement horizontal contrôlés.
- Blog : accès depuis la navigation, filtre sans résultat, lecture du brouillon, retour et noindex de l’aperçu vérifiés.
- Éditorial : simulation proposition → sélection → rédaction → attente de validation dans l’atelier ; cinq JPEG 1080×1350 générés et correctement chargés dans le fichier autonome.
- Test de l’export HTML autonome : accueil, blog et atelier s’ouvrent sans serveur externe, styles, scripts et images intégrés.
- Tests automatisés : conservation intégrale du catalogue, liens/images internes, pied de page, périmètre livraison, SEO des pages articles, exclusion des brouillons/photos en attente dans le build production, décodage des 14 photos, déroulement éditorial en simulation, refus sans approbation, invalidation d’approbation après modification et accord Instagram distinct.
- JavaScript vérifié avec node --check. Aucun framework, SDK externe ou dépendance de navigateur ajouté.
- Performance : l’ancien HTML contenant les photos en base64 est remplacé dans le build par une page légère et des fichiers WebP externes chargés à la demande. Aucun score Lighthouse ou mesure réseau en conditions réelles n’est revendiqué.
- Aucun secret ajouté. Dépôt GitHub public détecté ; l’envoi de la branche avec photos a été refusé par le contrôle automatique et n’a pas été contourné. La version complète reste locale en attendant l’accord explicite de divulgation sur ce dépôt public.
- Aucune fusion, publication production, modification DNS, modification Instagram ou connexion Meta effectuée.
