Rôle
====

``ops_ssh`` gère les accès SSH du SDK vers les nœuds du cluster.
Il couvre trois opérations :

- **setup** — installation initiale de la clé SDK sur le bastion (une fois,
  avec mot de passe) ; utilisé pour accéder au controller vierge avant
  tout déploiement.
- **init** — génération de la clé ``kubewi_ansible``, configuration de
  ``~/.ssh/config`` (ProxyJump workers → controller), distribution de
  la clé par mot de passe sur tous les nœuds.
- **config** — régénération de ``~/.ssh/config`` uniquement (idempotent).

----

Couches
-------

- ``kubewi/commands.py`` — CLI (Python pur, appels ``ssh-keygen``,
  ``ssh-copy-id`` via ``ansible.posix.authorized_key``)

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``adp_ansible``
     - inventaire ``hosts.yml`` pour lire les IPs et groupes
