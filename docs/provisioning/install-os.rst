Installation OS
================

L'installation du système d'exploitation sur les nœuds physiques repose sur
**Ventoy** et **cloud-init**. Cette combinaison permet un install non-interactif
et reproductible sans dépendance aux outils constructeurs (iDRAC, iLO, etc.).

.. contents:: Sections
   :local:
   :depth: 1

----

Principe
--------

**Ventoy** transforme une clé USB en boot manager multi-ISO : les fichiers
``*.iso`` déposés à la racine de la clé sont directement bootables sans
reprogrammation.

**cloud-init nocloud** est une source de données cloud-init lue depuis un
volume local (ISO portant le label ``CIDATA``). L'installeur Ubuntu détecte
ce volume et applique la configuration automatiquement.

Flux d'installation :

1. Le BIOS boot sur la clé Ventoy.
2. Ventoy présente le menu de boot — sélectionner l'ISO Ubuntu.
3. L'installeur Ubuntu (subiquity) détecte ``cidata.iso`` et applique ``user-data``.
4. Install silencieuse : partitionnement, utilisateur, SSH, sudo.
5. Reboot automatique — la machine est prête pour Ansible.

----

Prérequis
---------

Sur la machine de préparation :

.. code-block:: bash

   # Ventoy (déposer sur clé USB)
   # https://www.ventoy.net/en/download.html

   # Outil de création d'ISO
   sudo apt install xorriso   # ou genisoimage

   # ISO Ubuntu Server 24.04 LTS
   # https://releases.ubuntu.com/24.04/

----

Préparation de la clé
---------------------

1. Installer Ventoy sur la clé USB (outil graphique ou CLI Ventoy).
2. Copier l'ISO Ubuntu à la racine de la partition Ventoy.

----

Génération du hash de mot de passe
------------------------------------

Le fichier ``cloud-init/user-data`` versionné contient un placeholder à la
place du mot de passe. Le hash doit être généré localement et injecté avant
de construire l'ISO — il ne doit jamais être commité.

.. code-block:: bash

   openssl passwd -6

La commande demande le mot de passe de manière interactive (sans echo) et
produit un hash SHA-512 de la forme ``$6$sel$hash``. Copier ce hash dans
``cloud-init/user-data`` :

.. code-block:: yaml

   identity:
     username: iobewi
     password: "$6$..."   # ← coller le hash ici, localement uniquement

.. warning::
   ``cloud-init/user-data`` avec un hash réel ne doit pas être commité.
   Le placeholder ``HASH_A_GENERER_LOCALEMENT`` est la seule valeur versionnée.
   ``cidata.iso`` est exclu du dépôt via ``.gitignore``.

----

Génération de l'ISO seed
-------------------------

.. code-block:: bash

   bash cloud-init/build-iso.sh

Le fichier ``cloud-init/cidata.iso`` est généré. Le copier à la racine de
la partition Ventoy.

----

Résultat attendu
----------------

Après le reboot :

- Ubuntu Server 24.04 installé ;
- utilisateur ``iobewi`` créé avec mot de passe, authentification SSH par
  mot de passe activée ;
- ``python3``, ``git``, ``chrony``, ``curl`` installés ;
- serveur SSH démarré.

La machine est prête pour le bootstrap Ansible. La première connexion
utilise le mot de passe (``--ask-pass --ask-become-pass``) — le playbook
``bootstrap.yml`` déploie la clé SSH et configure ``sudo`` sans mot de passe
pour les runs suivants :

.. code-block:: bash

   # Premier run — connexion par mot de passe
   ansible-playbook -i inventory/hosts.yml playbooks/bootstrap.yml \
     --ask-pass --ask-become-pass

   # Vérifier la connectivité par clé
   ansible all -i inventory/hosts.yml -m ping
