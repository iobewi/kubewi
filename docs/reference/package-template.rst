.. _package-template:

Trame documentaire — paquet KubeWI
====================================

Chaque paquet possède un répertoire ``docs/`` avec les fichiers décrits
ci-dessous. Copier les trames, supprimer les sections ``[optionnel]``
qui ne s'appliquent pas, compléter le contenu.

----

``docs/index.rst``
------------------

.. code-block:: rst

    Plugin / Engine / Adapter <Nom lisible>
    ========================================

    .. list-table::
       :widths: 20 80
       :stub-columns: 1

       * - Paquet
         - ``<type>_<nom>``
       * - Type
         - ``<adapter | engine | plugin | ops | workload>``
       * - Dépendances
         - :doc:`../adp_kube/index`,
           :doc:`../adp_ansible/index`

    <Description courte — reprend le champ ``description`` de ``kubewi.yaml``>

    .. toctree::
       :maxdepth: 1

       role
       commands
       variables
       implementation

Supprimer les entrées ``toctree`` correspondant aux fichiers optionnels
non créés (``commands``, ``variables``).

----

``docs/role.rst``
-----------------

.. code-block:: rst

    Rôle
    ====

    <2 à 5 phrases : ce que fait ce paquet, pourquoi il existe,
    sa place dans la hiérarchie KubeWI. Expliquer la valeur, pas le nom.>

    .. image:: <nom>.svg         [optionnel — diagramme D2 colocalisé]
       :alt: <légende>
       :align: center

    ----

    Architecture
    ------------

    <Description de l'architecture interne ou des interactions clés.
    Diagrammes textuels (code-block:: text), tableaux, listes.>

    ----

    Dépendances
    -----------

    .. list-table::
       :header-rows: 1
       :widths: 30 70

       * - Paquet
         - Ce qui est utilisé
       * - ``<type>_<dep>``
         - <ce que ce paquet consomme>

----

``docs/commands.rst``  *[si le paquet expose une CLI]*
------------------------------------------------------

.. code-block:: rst

    Commandes
    =========

    .. code-block:: text

       kubewi <nom> <sous-commande>   # description courte

    ----

    ``kubewi <nom> <sous-commande>``
    --------------------------------

    <Ce que fait la commande, séquence d'actions, exemples de sortie.>

----

``docs/variables.rst``  *[si le paquet utilise Ansible]*
---------------------------------------------------------

.. code-block:: rst

    Variables
    =========

    Variables de l'inventaire (``group_vars/``) et des ``defaults/`` des rôles.

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

``docs/implementation.rst``
---------------------------

.. code-block:: rst

    Implémentation
    ==============

    <Ce qui se passe sous le capot.
    Décrire les décisions non-évidentes, les contraintes, les séquences clés.
    Extraits de templates Jinja2 ou de manifests si le POURQUOI n'est pas
    lisible dans le code seul. Ne pas paraphraser le code.>

----

Diagrammes D2 colocalisés
--------------------------

Placer les fichiers ``.d2`` dans ``docs/`` du paquet. Sphinx les compile
automatiquement. Référencer le ``.svg`` généré par son nom seul :

.. code-block:: rst

    .. image:: mon-diagramme.svg
       :alt: Diagramme
       :align: center
       :target: mon-diagramme.svg
