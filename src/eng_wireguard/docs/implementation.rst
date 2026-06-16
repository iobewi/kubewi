Implémentation
==============

Le tunnel est asymétrique : le controller est serveur (``ListenPort``),
le SDK est client (``Endpoint`` pointant vers le controller via mDNS ou IP fixe).

``controller_endpoint`` utilise mDNS (``<hostname>.local``) par défaut pour
rester stable même avec une IP DHCP changeante — ``avahi-daemon`` doit être
actif sur le controller (garanti par ``eng_debian``).

``work/wg0-sdk.conf`` est généré par ``delegate_to: localhost`` dans
``sdk_config.yml`` : Ansible s'exécute côté controller pour lire les variables
vault, mais écrit le fichier sur la machine de contrôle. Ce fichier ne transite
jamais par le réseau chiffré, il est produit en local.

Le playbook est idempotent : relancer ``kubewi wireguard deploy`` sur un
controller déjà configuré ne produit aucun effet si les clés et la config
sont identiques. Il régénère systématiquement ``work/wg0-sdk.conf``.
