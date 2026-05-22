Controller node
================

.. contents:: Sections
   :local:
   :depth: 1

Hardware
--------

.. TODO: spécifications matérielles minimales et recommandées du controller node

Kubernetes bootstrap
--------------------

k0s
~~~

.. TODO: installation k0s, version, méthode

Configuration controller
~~~~~~~~~~~~~~~~~~~~~~~~

.. TODO: fichier de configuration k0s controller (k0s.yaml)

Validation controller
---------------------

Le controller est considéré opérationnel lorsque :

- l'API Kubernetes est accessible ;
- CoreDNS est opérationnel ;
- la résolution DNS fonctionne ;
- les services sont persistants après reboot.

.. TODO: commandes de vérification pour chaque point
