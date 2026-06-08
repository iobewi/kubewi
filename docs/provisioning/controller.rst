Controller node
================

Le controller héberge le plan de contrôle Kubernetes (k0s) et constitue
le point central du cluster. Il expose l'API server sur le VLAN 220
et génère le token de jonction pour les workers.

.. image:: ../_static/diagrams/controller.svg
   :alt: Bootstrap controller k0s
   :align: center
   :target: ../_static/diagrams/controller.svg

.. contents:: Sections
   :local:
   :depth: 1

----

Hardware
--------

.. TODO: spécifications matérielles minimales et recommandées du controller node

----

Installation k0s
----------------

| Rôle : `roles/k0s_install <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_install>`_

Le binaire k0s est téléchargé depuis les releases GitHub du projet via le
rôle partagé ``k0s_install``, commun au controller et aux workers.
L'architecture est détectée automatiquement (``amd64`` ou ``arm64``).

La version est contrôlée par ``k0s_version`` dans
``inventory/group_vars/kubernetes.yml``. Si non définie, la dernière
release stable est installée automatiquement.

----

Configuration
-------------

| Rôle : `roles/k0s_controller/tasks/configure.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_controller/tasks/configure.yml>`_
| Template : `roles/k0s_controller/templates/k0s.yaml.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_controller/templates/k0s.yaml.j2>`_

La configuration k0s est déployée dans ``/etc/k0s/k0s.yaml``.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Paramètre
     - Valeur
   * - ``api.address``
     - ``192.168.22.1`` (VLAN 220)
   * - ``api.port``
     - ``6443``
   * - ``network.provider``
     - ``custom`` (Cilium gère le dataplane)
   * - ``network.podCIDR``
     - ``10.244.0.0/16``
   * - ``network.serviceCIDR``
     - ``10.96.0.0/12``

Cilium est déployé automatiquement via les extensions helm de k0s au
démarrage du controller. La version est contrôlée par ``k0s_cilium_version``
dans ``inventory/group_vars/kubernetes.yml``.

----

Démarrage du service
--------------------

| Rôle : `roles/k0s_controller/tasks/service.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_controller/tasks/service.yml>`_

k0s est installé comme service systemd (``k0scontroller``), activé au
boot. Le rôle attend que l'API soit disponible sur le port 6443 avant
de continuer.

----

Registry OCI
------------

| Rôle : `roles/k0s_controller/tasks/registry.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_controller/tasks/registry.yml>`_
| Template : `registry.yaml.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_controller/templates/registry.yaml.j2>`_

La registry **Distribution** (CNCF) est déployée comme manifest statique k0s
dans ``/var/lib/k0s/manifests/registry/``. k0s applique ce manifest
automatiquement au démarrage, sans intervention kubectl.

Le pod s'exécute avec ``hostNetwork: true``, ce qui lui permet d'écouter
directement sur les interfaces réseau du nœud. La registry est ainsi
accessible à l'adresse du controller sur le VLAN 420.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Paramètre
     - Valeur
   * - Image
     - ``registry:2`` (Distribution CNCF)
   * - Adresse
     - ``192.168.42.1:5000`` (VLAN 420)
   * - Stockage
     - ``/var/lib/registry`` (hostPath, persistant)
   * - TLS
     - désactivé (réseau local fermé)

La configuration containerd est déposée dans ``/etc/k0s/containerd.d/registry.toml``
sur le controller et sur chaque worker, afin que tous les nœuds acceptent
cette registry sans TLS.

----

Service de provisioning
------------------------

| Rôle : `roles/k0s_controller/tasks/provisioning.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_controller/tasks/provisioning.yml>`_
| Template : `provisioning.yaml.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_controller/templates/provisioning.yaml.j2>`_

Un manifest statique k0s est déployé dans
``/var/lib/k0s/manifests/provisioning/dnsmasq.yaml``. Il crée le namespace
``provisioning`` et un Deployment ``dnsmasq-provisioning`` (``replicas: 0``
par défaut).

Ce Deployment fournit un serveur DHCP temporaire sur ``br0`` natif
(``192.168.0.0/24``) pour le bootstrap des workers. Il s'active uniquement
pendant l'enrollment via ``make provisioning-on`` (ou automatiquement par
``make add-worker``).

Cette tâche n'est appliquée que si ``network_provisioning_ip`` est défini
dans ``hosts.yml`` du nœud (ex. ``192.168.0.1/24`` pour le controller).

----

Token de jonction
-----------------

| Rôle : `roles/k0s_controller/tasks/token.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/k0s_controller/tasks/token.yml>`_

Un token de jonction worker est généré après démarrage du controller
et sauvegardé dans ``/etc/k0s/worker-token``. Ce token sera utilisé
lors de l'enrollment des workers.

----

Exécution
---------

Simuler avant d'appliquer :

.. code-block:: bash

   ansible-playbook -i inventory/hosts.yml playbooks/controller.yml --check --diff

Puis appliquer :

.. code-block:: bash

   ansible-playbook -i inventory/hosts.yml playbooks/controller.yml

Vérifier que le controller est opérationnel :

.. code-block:: bash

   k0s kubectl get nodes
   k0s kubectl get pods -n kube-system

Récupérer le kubeconfig depuis le SDK :

.. code-block:: bash

   make kubeconfig
   kubectl get nodes
