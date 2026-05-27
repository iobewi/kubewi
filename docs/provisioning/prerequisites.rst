Prérequis
==========

Stratégie OS
------------

La plateforme privilégie les systèmes d'exploitation fournis ou validés
par les constructeurs matériels lorsque ceux-ci conditionnent le support
des drivers, firmwares ou accélérateurs matériels.

Kubernetes est déployé au-dessus de cette base système afin de fournir
une couche d'abstraction commune entre les capacités matérielles des
nœuds et les workloads applicatifs distribués.

Systèmes d'exploitation supportés
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 30 30 10

   * - Plateforme
     - Matériel
     - OS cible
     - Architecture
   * - x86_64 générique
     - PC / serveur x86_64
     - Debian Stable / Ubuntu Server
     - amd64
   * - Raspberry Pi
     - Raspberry Pi 4 / 5
     - Raspberry Pi OS Lite 64-bit
     - arm64
   * - NVIDIA Jetson
     - Jetson Xavier / Orin
     - JetPack / Ubuntu L4T
     - arm64

.. note::

   Le rôle Kubernetes du nœud (control plane ou worker) n'est pas un
   prérequis matériel : il est défini lors du bootstrap k0s.

Prérequis système
-----------------

Chaque nœud doit fournir :

- un accès ``root`` ou ``sudo`` ;
- une installation Linux minimale fonctionnelle ;
- ``systemd`` comme système d'init ;
- une horloge système cohérente.

Prérequis réseau
----------------

Les nœuds doivent disposer :

- d'une connectivité réseau minimale avant provisioning ;
- d'interfaces réseau fonctionnelles et identifiables ;
- d'un accès SSH initial.

Compatibilité matérielle
------------------------

Les plateformes NVIDIA Jetson nécessitent :

- NVIDIA JetPack ;
- NVIDIA Container Runtime.

Les plateformes Raspberry Pi nécessitent :

- Raspberry Pi OS Lite 64-bit ;
- le support ARM64 activé.

Compatibilité réseau Linux
--------------------------

Le provisioning réseau repose sur :

- ``systemd-networkd`` ;
- bridges Linux ;
- VLAN 802.1Q ;
- routage IPv4.