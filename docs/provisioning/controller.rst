Controller node
================

.. contents:: Sections
   :local:
   :depth: 1

Hardware
---------

.. TODO: spécifications matérielles minimales et recommandées du controller node

Base system
------------

OS
~~~

.. TODO: installation OS, partitionnement, paramètres de base

systemd
~~~~~~~~

.. TODO: configuration systemd, units critiques, watchdog

SSH
~~~~

.. TODO: configuration sshd, clés autorisées, accès sécurisé

chrony
~~~~~~~

.. TODO: configuration NTP/chrony, sources, vérification synchronisation

Container runtime
~~~~~~~~~~~~~~~~~~

.. TODO: installation et configuration du container runtime (containerd)

Network stack
--------------

Interfaces physiques
~~~~~~~~~~~~~~~~~~~~~

.. TODO: identification et configuration des interfaces réseau physiques

Bridge
~~~~~~~

.. TODO: configuration du bridge réseau

VLAN
~~~~~

.. TODO: configuration des VLANs

Routage
~~~~~~~~

.. TODO: configuration du routage inter-réseaux

DNS / NTP
~~~~~~~~~~

.. TODO: configuration DNS local et NTP

WireGuard
~~~~~~~~~~

.. TODO: configuration WireGuard — clés, peers, interface

Kubernetes bootstrap
---------------------

k0s
~~~~

.. TODO: installation k0s, version, méthode

Configuration controller
~~~~~~~~~~~~~~~~~~~~~~~~~

.. TODO: fichier de configuration k0s controller (k0s.yaml)

Registry locale
~~~~~~~~~~~~~~~~

.. TODO: déploiement et configuration de la registry OCI locale

Validation controller
----------------------

Le controller est considéré opérationnel lorsque :

- API Kubernetes accessible
- CoreDNS opérationnel
- registry locale accessible
- résolution DNS fonctionnelle
- services persistants après reboot

.. TODO: commandes de vérification pour chaque point
