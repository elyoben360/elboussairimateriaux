# Lot Instagram du 3 novembre 2026 — préparation uniquement

Cinq carrousels éditoriaux, quatre pages chacun, photographies réelles uniquement. Le lot est dans `content/instagram-prepared-2026-11-03.json` et les 20 JPEG dans les répertoires `assets/instagram/*-20261103-r2/`. Planche de contrôle : `assets/instagram/apercu-2026-11-03.jpg`.

| Ordre | Sujet | Angle | Traitement |
|---|---|---|---|
| 1 | Panneaux muraux | Lire les photos sans inventer de performances | Remplace dans le lot préparé le mémo commercial ciment ; aucune substitution faite dans Metricool |
| 2 | Fer à béton | Conditionnement et acheminement des barres longues | Révision éditoriale du reportage déjà programmé ; ne pas diffuser les deux versions |
| 3 | Gasoil | Hausse du carburant et coût de livraison distincts | Même sujet déjà programmé, archive de préparation avec texte agrandi |
| 4 | HCP | Indice de production et devis distincts | Même sujet déjà programmé, archive de préparation avec texte agrandi |
| 5 | Ciment | Trimestre et cumul de neuf mois distincts | Même sujet déjà programmé, archive de préparation avec texte agrandi |

## Contrôles effectués

Dernier main lu : `8c8577e2021e70ce0e8e33f240557855eb0d7d49`. Charte, six articles, file, photos du dépôt, catalogue et registre des cinq programmations antérieures lus. Aucun nouveau lot supplémentaire de cinq sujets créé à côté de celui déjà existant.

Légendes, ordre des pages, CTA unique de lecture du journal, article destination, sources datées, contexte géographique, auteur, licence, crédit par page, empreintes SHA-256 et clés de déduplication conservés. Vingt JPEG 1080 × 1350 sans EXIF, inspectés sur planche contact. Aucune génération d’image ni retouche générative.

Les sources HCP, Médias24 et La Vie éco/MAP ont été relues le 2 novembre. Les pages originales Wikimedia des briques (Saral Shots, CC0 1.0) et de Carboneras (Nicolas Vigier, CC0 1.0), la photographie de Liverpool (Raymond Okoro) et la licence Unsplash ont été relues. Les sources précises et licences figurent dans chaque entrée du lot. Les photos EBM sont fournies par le propriétaire pour sa communication. Aucun événement récent n’est illustré par un faux chantier EBM.

## Limites et prévention des doublons

Le statut `ready` porte sur les fichiers éditoriaux préparés, pas sur une autorisation technique de diffusion. Les cinq articles sont présents avec statut publié dans main ; les cinq URL ont renvoyé HTTP 403 depuis cet environnement au nouveau contrôle. Leur accessibilité en ligne n’a donc pas été reconfirmée. Ne pas déclarer les liens opérationnels sur cette seule base.

Le registre `content/instagram-scheduled-2026-11-03.json` demeure inchangé. Les cinq programmations qui y sont consignées n’ont été ni modifiées, ni renouvelées, ni vérifiées à nouveau dans cette tâche. Le mémo ciment antérieurement programmé et le reportage fer antérieur restent différents de leurs propositions corrigées ici. Aucun identifiant de publication n’a été créé ou supposé. **Ne pas programmer ce lot en supplément : rapprocher les versions et substituer, si la diffusion est un jour explicitement demandée.**

Les couvertures des trois actualités et du fer restent celles des mêmes posts, pas de nouvelles publications. Le remplacement panneaux utilise une photo de réserve ; pas de nouvelle diffusion. L’historique public complet sur sept jours n’est pas accessible par l’intégration courante : absence de doublons vérifiée dans les seuls registres disponibles, sans prétendre à un audit exhaustif du compte.

Limites de diffusion antérieurement constatées : nouvel espace Metricool 20 posts/mois et intégration ChatGPT encore liée à PremiumGarage. Aucune nouvelle vérification ni modification de forfait dans cette tâche. Aucun appel de publication ou programmation, message privé, commentaire, achat ou publicité.

## Reproduction

`python scripts/instagram_prepare_dated.py content/instagram-prepared-2026-11-03.json` avec Pillow et les polices DejaVu. La commande compose du texte sur les photographies originales ; elle n’appelle aucune API sociale.
