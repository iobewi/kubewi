Commandes CLI
=============

.. code-block:: text

   kubewi cluster init                génère cluster.yaml (description déclarative)
   kubewi cluster status              affiche l'état désiré vs enrollé
   kubewi cluster apply               enrôle les nœuds manquants
   kubewi cluster apply --dry-run     simule l'enrollment
   kubewi cluster inventory-init      crée hosts.yml + vault.yml depuis les exemples
   kubewi cluster wifi                renseigne les credentials WiFi dans vault.yml
   kubewi cluster vault-encrypt       chiffre vault.yml avec ansible-vault
   kubewi cluster vault-edit          édite le vault chiffré
   kubewi cluster system              applique la config système sur tous les nœuds
   kubewi cluster network             applique la config réseau sur tous les nœuds
   kubewi cluster stack               déploie la stack complète (system + network + k0s)

Workflow de déploiement initial :

.. code-block:: bash

   kubewi cluster inventory-init    # 1 — crée hosts.yml + vault.yml
   kubewi cluster wifi              # 2 — (si WiFi AP) renseigne les credentials
   kubewi cluster vault-encrypt     # 3 — chiffre le vault
   kubewi cluster init              # 4 — génère cluster.yaml
   # — éditer cluster.yaml pour décrire les nœuds —
   kubewi cluster apply             # 5 — enrollment guidé
   kubewi cluster stack             # 6 — déploie la stack complète
