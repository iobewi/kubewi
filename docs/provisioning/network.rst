Configuration réseau
=====================

Le provisioning réseau applique trois rôles distincts selon le groupe
de nœuds :

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Rôle
     - Groupe ciblé
     - Périmètre
   * - ``network``
     - ``all``
     - Tronc commun : désactivation dhcpcd/NetworkManager/networking,
       bridge ``br0``, VLANs 220/420/620
   * - ``gateway``
     - ``gateways``
     - Interface externe DHCP (``enp2s0``), NAT ``kubewi-nat.service``,
       DNS ``systemd-resolved`` sur ``192.168.22.1``
   * - ``internal``
     - ``all:!gateways``
     - Route par défaut ``192.168.22.1`` sur VLAN 220,
       ``resolv.conf`` → ``192.168.22.1``

Ce découpage correspond aux trois plays du playbook ``playbooks/network.yml``.
La stack réseau repose intégralement sur ``systemd-networkd``.

.. image:: ../_static/diagrams/network-stack.svg
   :alt: Stack réseau KubeWI
   :align: center
   :target: ../_static/diagrams/network-stack.svg

.. contents:: Sections
   :local:
   :depth: 1

----

Rôle ``network`` — tronc commun
---------------------------------

| Rôle : `roles/network <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network>`_

Appliqué sur **tous les nœuds**. Première action : arrêt et désactivation
des services qui conflictent avec ``systemd-networkd`` :

- ``dhcpcd``
- ``networking`` (ifupdown)
- ``NetworkManager``

Ensuite : création du bridge ``br0``, attachement des interfaces physiques
déclarées dans ``network_bridge_members``, puis déploiement des VLANs.

----

Interface externe (gateways)
------------------------------

| Rôle : `roles/gateway/tasks/main.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/gateway/tasks/main.yml>`_
| Template : `external.network.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/gateway/templates/external.network.j2>`_

Sur les **gateways uniquement**, l'interface externe (``network_external_iface``,
ex. ``enp2s0``) est configurée en DHCP standalone et séparée du bridge.
Elle constitue le point d'entrée externe du cluster :

- **WireGuard** (``51820/UDP``) — accès opérateur depuis le SDK ;
- **HTTP/HTTPS** (``80/443``) — services Kubernetes exposés via Nginx Ingress.

Cette séparation isole le trafic externe du réseau interne porté par ``br0``.

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Variable
     - Description
   * - ``network_external_iface``
     - Interface externe (ex. ``enp2s0``). Définie dans ``hosts.yml``
       uniquement pour les gateways.

----

NAT et DNS (gateways)
----------------------

| Rôle : `roles/gateway/tasks/main.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/gateway/tasks/main.yml>`_
| Template : `kubewi-nat.service.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/gateway/templates/kubewi-nat.service.j2>`_

Le rôle ``gateway`` déploie également :

- **``kubewi-nat.service``** — service systemd qui configure iptables
  MASQUERADE sur ``network_external_iface`` pour natter le trafic sortant
  du cluster vers le LAN externe
- **DNS cluster** — ``systemd-resolved`` est configuré pour écouter en plus
  sur ``192.168.22.1`` (VLAN 220) via ``DNSStubListenerExtra``, ce qui en
  fait le résolveur DNS de l'ensemble du cluster

----

Bridge
------

| Rôle : `roles/network/tasks/bridge.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network/tasks/bridge.yml>`_
| Templates : `bridge.netdev.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network/templates/bridge.netdev.j2>`_,
  `bridge-member.network.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network/templates/bridge-member.network.j2>`_,
  `bridge.network.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network/templates/bridge.network.j2>`_

Un bridge Linux ``br0`` est créé sur chaque nœud. Les interfaces
physiques déclarées dans ``host_vars`` sont attachées comme membres
du bridge sans adresse IP propre.

Le bridge porte le trafic natif (non taggé) et les sous-interfaces
VLAN.

La composition du bridge diffère selon le rôle du nœud :

- **Gateway** : ``network_bridge_members: [enp1s0]`` — l'interface externe
  (``enp2s0``) est gérée séparément par le rôle ``gateway``
- **Worker** : ``network_bridge_members: [eth0]`` ou ``[eth0, eth1]``
  selon le nombre d'interfaces disponibles (contrôlé par ``IFACES`` lors
  de l'enrollment)

----

VLANs
-----

| Rôle : `roles/network/tasks/vlans.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network/tasks/vlans.yml>`_
| Templates : `vlan.netdev.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network/templates/vlan.netdev.j2>`_,
  `vlan.network.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network/templates/vlan.network.j2>`_

Trois VLANs sont déployés sur le bridge, communs à tous les nœuds :

.. list-table::
   :header-rows: 1
   :widths: 12 22 26 40

   * - VLAN
     - Interface
     - Sous-réseau
     - Domaine
   * - 220
     - ``br0.220``
     - ``192.168.22.0/24``
     - Infrastructure Kubernetes (k0s API, pod network, CoreDNS)
   * - 420
     - ``br0.420``
     - ``192.168.42.0/24``
     - Transferts (Vector, Loki, OCI registry, MinIO)
   * - 620
     - ``br0.620``
     - ``192.168.62.0/24``
     - Communications robotiques (ROS2, Zenoh)

Les VLANs sont déclarés dans ``inventory/group_vars/all/main.yml`` via
``network_vlans``. L'adresse IP de chaque nœud sur un VLAN est calculée
automatiquement depuis ``host_id`` (dernier octet de l'IP VLAN 220) :

.. code-block:: yaml

   network_vlan_ips:
     "220": "192.168.22.{{ host_id }}/24"
     "420": "192.168.42.{{ host_id }}/24"
     "620": "192.168.62.{{ host_id }}/24"

``host_id`` est défini explicitement dans ``hosts.yml`` pour les controllers
(dont ``ansible_host`` est une IP WireGuard) et dérivé automatiquement
du dernier octet de ``ansible_host`` pour les workers.

----

Rôle ``internal`` — nœuds non-gateway
---------------------------------------

| Rôle : `roles/internal <https://github.com/iobewi/kubewi/blob/main/ansible/roles/internal>`_
| Template : `vlan-kube.network.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/internal/templates/vlan-kube.network.j2>`_

Appliqué sur tous les nœuds **sauf les gateways**. Configure deux éléments
qui s'appuient sur l'existence de la gateway :

- **Route par défaut** sur ``br0.220`` : ``192.168.22.1`` (gateway VLAN 220)
- **DNS** : ``/etc/resolv.conf`` → ``nameserver 192.168.22.1``
  (``systemd-resolved`` du controller, configuré par le rôle ``gateway``)

Ces deux éléments nécessitent que le rôle ``gateway`` soit déjà appliqué
sur le controller avant que les workers ne soient provisionnés.

----

WiFi
----

| Rôle : `roles/network/tasks/wifi.yml <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network/tasks/wifi.yml>`_
| Templates : `wifi.network.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network/templates/wifi.network.j2>`_,
  `wpa_supplicant.conf.j2 <https://github.com/iobewi/kubewi/blob/main/ansible/roles/network/templates/wpa_supplicant.conf.j2>`_

L'interface WiFi ``wlan0`` est configurée uniquement sur le controller.
Elle constitue l'interface de communication externe normale du robot
(accès opérateur, réseau terrain).

La tâche WiFi ne s'exécute que si ``network_wifi`` est défini dans
le ``host_vars`` du nœud. Les workers ne sont pas affectés.

Les credentials WiFi (SSID, PSK) sont renseignés via :

.. code-block:: bash

   make wifi

Ils sont stockés dans ``inventory/group_vars/all/vault.yml`` (gitignore)
et référencés via ``vault_wifi_ssid`` et ``vault_wifi_psk``.

----

Ré-application
--------------

Pour le premier run, utiliser ``playbooks/init.yml`` (voir :doc:`system`).

Pour ré-appliquer la configuration réseau après une modification
(tunnel WireGuard actif) :

.. code-block:: bash

   make vpn-up
   ansible-playbook -i inventory/hosts.yml playbooks/network.yml --check --diff
   ansible-playbook -i inventory/hosts.yml playbooks/network.yml --ask-vault-pass
