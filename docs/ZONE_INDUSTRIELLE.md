# Zone Industrielle — identité et exploitation

Instruction du propriétaire du 2 novembre 2026 : identité propre au journal uniquement. Le site commercial, son logo et son catalogue restent sous El Boussairi Matériaux. Palette du journal : bleu #071d39, orange #ff6500 et crème #f7f3e9. Logo fourni par le propriétaire, pas les photomontages exploratoires.

Ligne éditoriale : matériaux, chantiers, industrie et logistique au Maroc ; informations datées, sources vérifiées, distinction entre faits et analyse. Signature « Un journal édité par El Boussairi Matériaux ». Reportages internes clairement identifiés. Aucun prompt, instruction de production ou promesse de stock/prix non confirmée dans les articles.

Le build conserve /actualites/ et les slugs existants. Il génère automatiquement trois insertions commerciales par article (intro, milieu, fin), reliées à la gamme principale ; le choix « Continuer la lecture » ferme chaque insertion. Les messages ont quatre angles : budget, livraison, conseil technique et demande directe. Aucun départ forcé vers le catalogue. Aucun paiement Meta Ads ou campagne externe lancé.

Après accord de mesure, seuls des compteurs agrégés sont envoyés : date, gamme, angle, position et affichage/clic/poursuite. Aucune personnalité n’est inférée. L’algorithme explore les quatre messages puis privilégie les meilleurs taux de clic (UCB, exploration 20 %, seuil 40 affichages). Il ne change pas un message déjà affiché. Les compteurs ne prouvent ni devis envoyé ni vente. Ne pas décrire ce système comme une IA qui connaît le caractère du lecteur.

## Infrastructure

Worker royal-rice-7dd9 conservé, configuration wrangler.jsonc. Les fichiers publics restent compatibles avec la commande historique --assets . et sa liste d’autorisation .assetsignore. Les sources serveur, bases, mots de passe et tokens ne sont jamais servis comme assets. Un Durable Object SQLite JournalStore porte les comptes, sessions, réactions uniques, commentaires, limites et compteurs. Migration zi-v1 crée le stockage au déploiement. Le binding Workers AI sert à modérer, plafonné à 100 analyses/jour. Un dépassement/une erreur laisse les commentaires en attente, jamais publics par défaut.

Inscription email/mot de passe : pseudonyme public, email privé, mot de passe 12 caractères minimum. Pas encore de validation d’email ni récupération par email ; l’interface le précise. Profil professionnel facultatif et consentement commercial distinct, désactivé par défaut. Aucune campagne email automatique n’est activée. Mots de passe PBKDF2-SHA512, sel aléatoire, 100 000 itérations (limite du runtime Workers), session HttpOnly Secure SameSite=Lax de 30 jours, protection Origin sur POST, limitation IP pseudonymisée quotidiennement et compte/email sur les routes sensibles. Les données ne transitent pas par GitHub.

Google : code OAuth serveur fourni, bouton masqué jusqu’à configuration de GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET dans les secrets Cloudflare. Déclarer exactement https://elboussairimateriaux.com/api/zi/google/callback dans le client OAuth Google. Aucune clé ni autorisation Google n’est inventée. Ne pas annoncer Google comme activé sans test réel. Un email déjà inscrit localement ne fait pas l’objet d’une liaison automatique avec Google.

Gestion privée : définir un secret aléatoire JOURNAL_ADMIN_TOKEN dans Cloudflare. GET /api/zi/admin avec Authorization: Bearer permet l’export privé des membres et la file de modération ; POST /api/zi/admin/moderate avec {id,decision:publish|remove} publie ou supprime. Jamais de token dans URL, dépôt ou navigateur public. Aucun administrateur « premier inscrit ».

Modération : filtre de langage évident puis analyse du contexte en français/arabe/darija. Critique courtoise autorisée. Insultes/haine : texte supprimé avant affichage. Doute/spam ou panne : attente. Les erreurs de classification restent possibles ; contestation par email et revue privée disponibles. Le plafond et le filtre ne garantissent pas un blocage universel.

L’alarme quotidienne purge sessions expirées, compteurs anti-abus et métriques au-delà de 90 jours. Dans son compte, un membre peut exporter ses données ou supprimer définitivement compte, réactions et commentaires. Ne jamais exposer l’email, téléphone ou entreprise dans la liste publique.

## Instagram prêt à appliquer après connexion

Compte observé : @zoneindustielle (orthographe actuelle conservée).
Nom affiché : Zone Industrielle | BTP Maroc
Bio (moins de 150 caractères) :
Matériaux · Chantiers · Industrie 🇲🇦
Le journal d’El Boussairi Matériaux
📰 Articles & demandes de matériaux ↓
Lien : https://elboussairimateriaux.com/actualites/
Photo : logo fourni, carré bleu nuit ZI crème/orange.
Stories à la une : À la une · Matériaux · Chantiers · Livraisons · Devis
Trois publications épinglées à préparer : présentation du journal ; comment commander ses matériaux ; reportage du dépôt. Ne pas inventer un reportage ou publier des chiffres non vérifiés.

Le 2 novembre, le navigateur présente un formulaire de connexion ; aucun changement de compte Instagram ne peut être annoncé avant authentification et vérification du profil modifié.

## Vérification

python3 scripts/build.py --preview
python3 scripts/stage_production.py
python3 -m unittest discover -s tests -v
node tests/journal-backend.mjs
node --check src/journal.js

Après push sur main : vérifier le check Cloudflare puis journal et /api/zi/config en production. La simulation SQLite/AI des tests n’est pas une preuve de fonctionnement de Workers AI ou Google en production.
