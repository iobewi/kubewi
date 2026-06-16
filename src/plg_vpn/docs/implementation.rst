Implémentation
==============

``kubewi vpn up`` vérifie la présence de ``work/wg0-sdk.conf`` avant de
monter le tunnel et sort en erreur explicite si le fichier est absent
(rappelant de lancer ``generate-keys`` d'abord).

``eng_wireguard`` est importé en import tardif dans ``run_cmd`` pour éviter
une dépendance circulaire au chargement du module.

``work/wg0-sdk.conf`` est gitignored — il contient la clé privée WireGuard
du SDK. Ce fichier ne doit jamais être commité.
