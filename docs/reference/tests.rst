Suite de tests
==============

Les tests KubeWI vérifient la conformité structurelle des paquets, la validité
de leurs descripteurs, leur intégration au CLI, la syntaxe de leurs manifests
Kubernetes, et le comportement de leurs commandes sans nécessiter de cluster réel.

.. code-block:: bash

   pip install -r requirements-test.txt
   python3 -m pytest tests/ -v

----

Organisation
------------

.. code-block:: text

    tests/
    ├── conftest.py              # fixtures partagées : PKG_DIRS, pkg_dir (parametrisé)
    ├── test_structure.py        # conformité arborescence + docs
    ├── test_kubewi_yaml.py      # validation du descripteur kubewi.yaml
    ├── test_cli.py              # intégration CLI argparse
    ├── test_manifests.py        # syntaxe YAML + champs Kubernetes
    ├── test_coverage.py         # règles de couverture fonctionnelle
    └── functional/
        ├── conftest.py          # fixture mock_subprocess
        ├── test_adp_kube.py
        ├── test_plg_embewi.py
        ├── test_plg_enroll.py
        ├── test_plg_gateway.py
        ├── test_plg_provisioning.py
        ├── test_eng_k0s.py
        └── test_wrk_ros_core.py

----

Suites transversales
--------------------

Chaque suite est **paramétrée automatiquement** sur les 17 paquets découverts
dans ``src/``. Ajouter un paquet suffit pour qu'il soit couvert.

**test_structure.py**

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Test
     - Ce qui est vérifié
   * - ``test_required_package_files``
     - ``kubewi.yaml``, ``kubewi/__init__.py``, ``kubewi/commands.py`` présents
   * - ``test_docs_required_files``
     - ``docs/index.rst``, ``docs/role.rst``, ``docs/implementation.rst`` présents
   * - ``test_docs_index_has_toctree``
     - ``index.rst`` contient ``.. toctree::``
   * - ``test_commands_py_defines_*``
     - ``NAME``, ``register()``, ``run_cmd()`` définis
   * - ``test_commands_py_valid_syntax``
     - ``commands.py`` est du Python syntaxiquement valide (``ast.parse``)
   * - ``test_d2_files_have_matching_svg``
     - Tout ``.d2`` dans ``docs/`` a son ``.svg`` commité

**test_kubewi_yaml.py**

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Test
     - Ce qui est vérifié
   * - ``test_required_fields_present``
     - ``name``, ``type``, ``description`` présents
   * - ``test_name_matches_directory``
     - ``name`` = nom du répertoire
   * - ``test_type_is_valid``
     - ``type`` ∈ ``{adapter, engine, plugin, ops, workload}``
   * - ``test_deps_reference_existing_packages``
     - Chaque dépendance pointe vers un paquet réel
   * - ``test_deps_respect_type_hierarchy``
     - Niveau du dep ≤ niveau du paquet (adapter < engine < plugin/ops < workload)
   * - ``test_image_present_for_workload``
     - Les workloads avec Dockerfile déclarent ``image:``

**test_cli.py**

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Test
     - Ce qui est vérifié
   * - ``test_discovery_finds_all_packages``
     - ``discover()`` retourne un module pour chaque paquet connu
   * - ``test_name_is_non_empty_string``
     - ``NAME`` (ou ``NAMES``) est une chaîne non vide
   * - ``test_register_does_not_crash``
     - ``register(sub)`` ne lève pas d'exception
   * - ``test_help_exits_zero``
     - ``kubewi <nom> --help`` termine avec le code 0

**test_manifests.py**

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Test
     - Ce qui est vérifié
   * - ``test_manifest_is_valid_yaml``
     - Chaque ``manifests/*.yaml`` est du YAML syntaxiquement valide
   * - ``test_manifest_k8s_required_fields``
     - Chaque document a ``apiVersion``, ``kind``, ``metadata``, ``metadata.name``
   * - ``test_manifest_api_version_non_empty``
     - ``apiVersion`` et ``kind`` sont non vides

----

Règles de couverture (test_coverage.py)
----------------------------------------

**Règle 1 — manifests → test fonctionnel**

Tout paquet dont ``manifests/`` contient au moins un fichier ``*.yaml``
doit avoir un fichier ``tests/functional/test_<nom>.py``.

Cette règle garantit que toute logique de déploiement kubectl est testée.
Si un nouveau paquet ajoute des manifests sans fichier de test, la CI échoue.

**Règle 2 — aucun test orphelin**

Tout fichier ``tests/functional/test_<nom>.py`` doit correspondre à un paquet
``src/<nom>/`` existant. Si un paquet est supprimé ou renommé, son fichier de
test devient un test orphelin détecté immédiatement.

----

Tests fonctionnels
------------------

Les tests fonctionnels **ne nécessitent pas de cluster**. Ils remplacent
``subprocess.run`` par un stub via la fixture ``mock_subprocess`` :

.. code-block:: python

   # tests/functional/conftest.py
   @pytest.fixture
   def mock_subprocess(monkeypatch):
       calls = []
       def _fake_run(cmd, **kwargs):
           calls.append([str(a) for a in cmd])
           result = MagicMock()
           result.returncode = 0
           result.stdout = b""
           return result
       monkeypatch.setattr("subprocess.run", _fake_run)
       return calls

Chaque test vérifie que la **bonne commande** est construite et envoyée,
pas que le cluster répond. Exemple :

.. code-block:: python

   def test_deploy_applies_crds(mock_subprocess):
       from plg_embewi.kubewi.commands import _deploy
       _deploy()
       assert any("crds.yaml" in " ".join(c) for c in mock_subprocess)

----

Ajouter des tests pour un nouveau paquet
-----------------------------------------

1. **Conformité automatique** : les 4 suites transversales couvrent le nouveau
   paquet dès qu'il est dans ``src/``.

2. **Test fonctionnel** : si le paquet a des ``manifests/*.yaml``,
   ``test_coverage.py`` échouera en CI jusqu'à la création de
   ``tests/functional/test_<nom>.py``.

3. **Contenu minimal** d'un test fonctionnel :

   .. code-block:: python

      def test_deploy_applies_manifest(mock_subprocess):
          from mon_paquet.kubewi.commands import run_cmd
          from argparse import Namespace
          run_cmd(Namespace(mon_cmd="deploy"))
          assert any("mon-manifest.yaml" in " ".join(c)
                     for c in mock_subprocess)
