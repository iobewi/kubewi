Implémentation
==============

``embewi-core`` s'exécute avec ``hostNetwork: true`` sur le controller k0s.
Ce choix expose directement le port 8080 sur ``192.168.22.1`` — l'adresse
VLAN 220 du controller — sans passer par kube-proxy ni un NodePort hors
plage standard.

.. code-block:: text

   ESP32 heartbeat POST 192.168.22.1:8080
         │
   hostNetwork=true ──► pod embewi-core (ns host)
         │                    │
         │              Kubernetes API ──► patch McuNode.Status
         │                    │
         │              EndpointSlice ──► Service embewi/<nodeId>
         │
   OTA pull  ←── 192.168.42.1:5000 (registry VLAN 420)
   OTA push  ──► ESP32 HTTPS:443 (192.168.22.x)

----

Placement
---------

Le pod est épinglé au controller via :

.. code-block:: yaml

   nodeSelector:
     node-role.kubernetes.io/control-plane: ""
   tolerations:
     - key: node-role.kubernetes.io/control-plane
       effect: NoSchedule

Le controller k0s porte déjà ce label et cette taint par défaut.

----

RBAC
----

``embewi-core`` utilise un ``ClusterRole`` car les ``McuNode`` et
``McuDeployment`` peuvent être créés dans n'importe quel namespace.
En pratique, tout est dans ``embewi``.

Permissions accordées :

.. list-table::
   :header-rows: 1
   :widths: 35 30 35

   * - Ressource
     - ApiGroup
     - Verbes
   * - ``mcunodes``, ``mcudeployments``
     - ``embewi.io``
     - get, list, watch, create, update, patch, delete
   * - ``mcunodes/status``, ``mcudeployments/status``
     - ``embewi.io``
     - get, update, patch
   * - ``services``
     - ``""``
     - get, list, watch, create, update, patch, delete
   * - ``endpointslices``
     - ``discovery.k8s.io``
     - get, list, watch, create, update, patch, delete
   * - ``secrets``
     - ``""``
     - get, list, watch
   * - ``events``
     - ``""``
     - create, patch

----

Machine d'état OTA
------------------

Lorsqu'un ``McuDeployment`` est créé, ``embewi-core`` pilote la séquence :

.. code-block:: text

   Binding ──► Pulling ──► Preparing ──► Writing ──► Activating
                                                          │
                                               ┌──────────┴──────────┐
                                          Confirming             (timeout)
                                               │                     │
                                          Deployed              rollback automatique

- **Pulling** : tire le blob firmware depuis la registry OCI interne.
- **Preparing** : envoie ``POST /ota/prepare`` à l'ESP32 (taille + SHA-256).
- **Writing** : pousse le firmware par chunks via ``POST /ota/write``.
- **Activating** : envoie ``POST /ota/activate``. L'ESP32 redémarre sur la partition B.
- **Confirming** : attend le heartbeat post-reboot avec ``otaValidated=true``.
  Si absent sous 15 s, l'ESP32 rollback automatiquement sur la partition A.

----

Intégration registry
--------------------

Les firmwares sont publiés dans la registry interne (``192.168.42.1:5000``)
comme artefacts OCI. La variable ``OCI_INSECURE_TLS=true`` permet à
``embewi-core`` de se connecter sans vérifier le certificat auto-signé.

Un Secret optionnel ``embewi-registry`` dans le namespace ``embewi``
peut porter des credentials si la registry est protégée :

.. code-block:: yaml

   apiVersion: v1
   kind: Secret
   metadata:
     name: embewi-registry
     namespace: embewi
   type: Opaque
   stringData:
     username: kubewi
     password: <mot-de-passe>
