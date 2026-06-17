Commandes CLI
=============

.. code-block:: text

   kubewi cluster inventory-init <nom>   crée un projet kubewi (hosts.yml + vault.yml)
   kubewi cluster init                   génère cluster.yaml dans le projet actif
   kubewi cluster status                 affiche l'état désiré vs enrollé
   kubewi cluster apply                  enrôle les nœuds manquants
   kubewi cluster apply --dry-run        simule l'enrollment
   kubewi cluster wifi                   renseigne les credentials WiFi dans vault.yml
   kubewi cluster vault-encrypt          chiffre vault.yml avec ansible-vault
   kubewi cluster vault-edit             édite le vault chiffré
   kubewi cluster system                 applique la config système sur tous les nœuds
   kubewi cluster network                applique la config réseau sur tous les nœuds
   kubewi cluster stack                  déploie la stack complète (system + network + k0s)

Workflow de déploiement initial :

.. code-block:: bash

   kubewi cluster inventory-init mon-cluster   # 1 — crée le projet
   cd mon-cluster                              # 2 — activer le projet (répertoire courant)
   # — éditer hosts.yml —
   kubewi cluster wifi                         # 3 — (si WiFi AP) credentials
   kubewi cluster vault-encrypt               # 4 — chiffre le vault
   kubewi cluster init                         # 5 — génère cluster.yaml
   # — éditer cluster.yaml pour décrire les nœuds —
   kubewi cluster apply                        # 6 — enrollment guidé
   kubewi cluster stack                        # 7 — déploie la stack complète

Sélection du projet actif :

.. code-block:: bash

   # Via répertoire courant (recommandé)
   cd mon-cluster && kubewi cluster status

   # Via variable d'environnement (depuis n'importe où)
   KUBEWI_PROJECT=~/clusters/prod kubewi cluster status
