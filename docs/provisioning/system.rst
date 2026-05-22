Configuration système
======================

Cette configuration s'applique à tous les nœuds du cluster,
indépendamment de leur rôle Kubernetes.

.. contents:: Sections
   :local:
   :depth: 1

Premier run
-----------

Séquence à suivre pour un premier déploiement sur nœud vierge.

**1. Installer les collections requises**

.. code-block:: bash

   cd ansible
   ansible-galaxy collection install -r requirements.yml

**2. Renseigner l'inventaire**

Éditer ``inventory/hosts.yml`` : adresses IP et users de connexion
de chaque nœud.

**3. Bootstrap — clé SSH et sudo sans mot de passe**

Le flux officiel utilise ``playbooks/bootstrap.yml``. Ce playbook prépare
l'accès SSH par clé et configure le sudo sans mot de passe. Les playbooks
suivants doivent pouvoir être exécutés sans mot de passe interactif.

Cette étape est à exécuter **une seule fois** par nœud.

.. code-block:: bash

   ansible-playbook -i inventory/hosts.yml playbooks/bootstrap.yml --ask-pass --ask-become-pass

Ansible demande deux mots de passe :

- ``SSH password`` — pour la connexion initiale
- ``BECOME password`` — pour l'escalade sudo

Après ce run, l'accès SSH par clé est actif et sudo est sans mot de passe
sur tous les nœuds.

**4. Vérifier la connectivité**

.. code-block:: bash

   ansible all -i inventory/hosts.yml -m ping

----

OS
--

.. TODO: installation OS, partitionnement, paramètres noyau de base

systemd
-------

.. TODO: configuration systemd, units critiques, watchdog

SSH
---

.. TODO: configuration sshd, clés autorisées, accès sécurisé

chrony
------

.. TODO: configuration NTP/chrony, sources, vérification synchronisation

Container runtime
-----------------

.. TODO: installation et configuration containerd

----

Exécution
---------

Une fois l'inventaire renseigné et la connectivité vérifiée, simuler
le playbook pour contrôler les changements attendus :

.. code-block:: bash

   ansible-playbook -i inventory/hosts.yml playbooks/system.yml --check --diff

Puis appliquer :

.. code-block:: bash

   ansible-playbook -i inventory/hosts.yml playbooks/system.yml
