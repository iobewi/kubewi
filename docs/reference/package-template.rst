.. _package-template:

Trame documentaire — paquet KubeWI
====================================

Ce fichier est la trame de référence pour documenter un paquet.
Chaque paquet le recopie dans ``src/<type>_<nom>/docs.rst`` et complète
les sections. Les sections marquées ``[optionnel]`` sont omises si elles
ne s'appliquent pas au type du paquet.

----

.. ============================================================
.. DÉBUT DU TEMPLATE — copier à partir d'ici dans docs.rst
.. ============================================================

<Nom lisible du paquet>
=======================

.. list-table::
   :widths: 20 80
   :stub-columns: 1

   * - Paquet
     - ``<type>_<nom>``
   * - Type
     - ``<adapter | engine | plugin | ops | workload>``
   * - Dépendances
     - :doc:`/src/<dep1>/docs` · :doc:`/src/<dep2>/docs`

<Description courte — reprend exactement le champ ``description`` de ``kubewi.yaml``>

----

Rôle
----

<2 à 5 phrases. Ce que fait ce paquet, pourquoi il existe, sa place dans
la hiérarchie KubeWI. Ne pas répéter le nom — expliquer la valeur.>

----

Dépendances
-----------

.. [optionnel — omettre si deps: est vide dans kubewi.yaml]

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est utilisé
   * - ``<type>_<dep>``
     - <ce que ce paquet consomme de cette dépendance>

----

Couches
-------

Indiquer uniquement les couches présentes dans le paquet.

**Ansible** ``playbooks/`` + ``roles/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. [omettre pour adapter et workload]

<Lister les playbooks et rôles, leur périmètre.>

**Kubernetes** ``manifests/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. [omettre si pas de manifests/]

<Lister les manifests, leur objet (Deployment, ConfigMap, RBAC…).>

**Image** ``Dockerfile``
~~~~~~~~~~~~~~~~~~~~~~~~~

.. [workload uniquement]

<Image de base, ce qui est ajouté, tag produit.>

----

Commandes CLI
-------------

.. [omettre si le paquet n'expose pas de commandes (rare)]

.. code-block:: text

   kubewi <nom> <sous-commande>   <description courte>

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Commande
     - Usage
   * - ``kubewi <nom> <cmd>``
     - <ce que ça fait>

----

Variables
---------

.. [optionnel — adapter et workload sans Ansible peuvent omettre]

Variables Ansible clés. Les valeurs par défaut sont dans
``inventory/group_vars/`` ou dans les ``defaults/`` du rôle.

.. list-table::
   :header-rows: 1
   :widths: 38 22 40

   * - Variable
     - Défaut
     - Description
   * - ``<variable_name>``
     - ``<valeur>``
     - <à quoi elle sert>

----

Implémentation
--------------

<Ce qui se passe sous le capot. Décrire les étapes importantes des rôles
ou du code Python, les décisions non-évidentes, les contraintes connues.
Ne pas paraphraser le code — expliquer le POURQUOI.>

.. ============================================================
.. FIN DU TEMPLATE
.. ============================================================
