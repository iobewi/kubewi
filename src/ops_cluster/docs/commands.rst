Commandes CLI
=============

.. code-block:: text

   kubewi cluster inventory-init <nom>      crée un projet kubewi vide
   kubewi cluster create                    bootstrap le gateway + rename MAC
   kubewi cluster add worker [NAME]         ajoute un worker (auto ou manuel)
   kubewi cluster add controller NAME       ajoute un controller secondaire
   kubewi cluster apply [--dry-run]         applique la conf sur tous les nœuds
   kubewi cluster status                    affiche l'état désiré vs en ligne
   kubewi cluster init                      régénère hosts.yml depuis hosts/*.yml
   kubewi cluster kubeconfig                récupère le kubeconfig depuis le controller
   kubewi cluster wifi                      renseigne les credentials WiFi dans vault.yml
   kubewi cluster vault-encrypt             chiffre vault.yml avec ansible-vault
   kubewi cluster vault-edit                édite le vault chiffré
   kubewi cluster system                    applique la config système sur tous les nœuds
   kubewi cluster network                   applique la config réseau sur tous les nœuds
   kubewi cluster stack                     déploie la stack complète (system + network + k0s)

----

Workflow de déploiement initial
--------------------------------

.. code-block:: bash

   # 1 — Créer le projet
   kubewi cluster inventory-init mon-cluster
   cd mon-cluster

   # 2 — Renseigner les clés VPN dans hosts/controller-01.yml
   kubewi vpn generate-keys
   # éditer hosts/controller-01.yml (init_host, ansible_user, réseau…)

   # 3 — (optionnel) Credentials WiFi
   kubewi cluster wifi
   kubewi cluster vault-encrypt

   # 4 — Bootstrap du gateway + renommage MAC
   kubewi cluster create
   # → le controller est renommé controller-<6octets-MAC>
   # → cluster.yml est mis à jour avec le nouveau nom

   # 5 — Ajouter des workers
   kubewi cluster add worker          # auto : détection DHCP, nommage MAC
   kubewi cluster add worker worker-88c240   # manuel : fichier host existant

   # 6 — Récupérer le kubeconfig
   kubewi cluster kubeconfig

   # 7 — Déployer la stack complète
   kubewi cluster stack

----

Ajout d'un worker
-----------------

**Mode auto** (aucun nom fourni) — le réseau de provisioning est activé,
le worker est branché sur le switch cluster, et dnsmasq lui attribue une IP
sur ``192.168.0.x``. Dès qu'un bail DHCP est détecté, le nœud est nommé
``worker-<3 derniers octets MAC>`` et son fichier ``hosts/<nom>.yml`` est
créé automatiquement.

.. code-block:: bash

   kubewi cluster add worker          # brancher le nœud quand demandé
   kubewi cluster add worker --ifaces 1   # nœud avec une seule interface réseau

**Mode manuel** — le fichier ``hosts/<NAME>.yml`` doit exister au préalable.

.. code-block:: bash

   kubewi cluster add worker worker-88c240

----

Ajout d'un controller secondaire
---------------------------------

Le fichier ``hosts/<NAME>.yml`` doit exister et déclarer ``eng_k0s.role: controller``.

.. code-block:: bash

   kubewi cluster add controller controller-a3f1b2

----

``cluster apply``
-----------------

Régénère ``hosts.yml`` depuis ``hosts/*.yml``, compare le hash au cache
``.kubewi/hosts.yml.hash``, puis itère les nœuds déclarés dans l'ordre
(controllers d'abord). Pour chaque nœud :

- **en ligne** → synchronisation (``gateway.yml`` ou ``workers-init.yml``)
- **hors ligne** → bootstrap complet depuis l'adresse provisioning

.. code-block:: bash

   kubewi cluster apply             # interactif — confirme nœud par nœud
   kubewi cluster apply --yes       # non-interactif
   kubewi cluster apply --dry-run   # affiche le plan sans modifier

----

Sélection du projet actif
--------------------------

.. code-block:: bash

   # Via répertoire courant (recommandé)
   cd mon-cluster && kubewi cluster status

   # Via variable d'environnement
   KUBEWI_PROJECT=~/clusters/prod kubewi cluster status
