Rôle
====

``eng_debian`` configure le socle système de chaque nœud Debian. Il installe
les paquets essentiels, durcit SSH, configure chrony (NTP), active les
modules noyau requis par Kubernetes, applique les sysctl réseau, désactive
le swap, et installe containerd comme runtime de containers.

Il s'applique à tous les nœuds (controllers et workers) avant tout
provisioning Kubernetes. ``eng_rpios`` s'y ajoute pour les Raspberry Pi.

----

Couches
-------

- ``playbooks/provision.yml`` — applique le rôle ``debian`` sur les nœuds ciblés

**Rôle** ``debian``
   - ``tasks/os.yml`` — packages système, locales, timezone, avahi-daemon
   - ``tasks/ssh.yml`` — durcissement sshd (no root, no password, timeouts)
   - ``tasks/chrony.yml`` — configuration NTP avec les serveurs déclarés
   - ``tasks/systemd.yml`` — modules noyau (overlay, br_netfilter), sysctl réseau,
     désactivation swap, activation systemd-networkd
   - ``tasks/containerd.yml`` — installation containerd, configuration runtime

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``adp_ansible``
     - exécution du playbook
