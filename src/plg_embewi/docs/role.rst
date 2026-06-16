Rôle
====

``plg_embewi`` installe ``embewi-core`` sur le controller KubeWI.
``embewi-core`` est un controller Kubernetes (Go) qui gère des
microcontrôleurs ESP32 comme des ressources de cluster.

----

Architecture
------------

Les ESP32 équipés du firmware ``embewi`` rejoignent le cluster en trois étapes :

1. **Provisioning WiFi** — le firmware expose un portail captif (SSID ``embewi-XXXX``).
   L'opérateur y injecte les paramètres réseau (SSID cluster, IP, token, ctrl_url).
2. **Connexion VLAN 220** — l'ESP32 reçoit une IP ``192.168.22.x`` via dnsmasq
   sur le bridge WiFi (``br-wifi`` ↔ ``br0.220`` ↔ VLAN 220).
3. **Heartbeat** — l'ESP32 envoie un POST toutes les 5 s vers
   ``192.168.22.1:8080``. ``embewi-core`` crée et maintient le ``McuNode``
   correspondant, expose un ``Service`` + ``EndpointSlice`` pour que le
   reste du cluster puisse cibler l'ESP32 directement.

.. code-block:: text

   ESP32 ──WiFi──► br-wifi ──► VLAN 220 (192.168.22.0/24)
                                    │
                              controller-01 (192.168.22.1)
                                    │
                             embewi-core:8080  (heartbeat)
                             embewi-core:8082  (metrics Prometheus)
                             embewi-core:8083  (health probe)
                                    │
                             McuNode CR  ──► Service + EndpointSlice
                             McuDeployment ──► OTA state machine

----

CRDs
----

**McuNode** (``kubectl get mcu``)

Représente un ESP32 connecté. Créé automatiquement par ``embewi-core``
lors du premier heartbeat.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Champ
     - Description
   * - ``spec.nodeId``
     - Identifiant unique — correspond à ``EMBEWI_NODE_ID`` dans le firmware
   * - ``status.ip``
     - IP VLAN 220 rapportée par le dernier heartbeat
   * - ``status.state``
     - ``booting`` · ``pending_verify`` · ``running`` · ``degraded`` · ``rollback`` · ``failed``
   * - ``status.firmwareVersion``
     - Version courante du firmware (ex. ``v1.2.0``)
   * - ``status.ready``
     - ``true`` si l'ESP32 a validé son firmware (OTA A/B confirmé)
   * - ``status.lastHeartbeat``
     - Timestamp ISO 8601 du dernier heartbeat reçu

**McuDeployment** (``kubectl get mcudep``)

Déclenche une mise à jour OTA sur un McuNode cible. Le controller
pilote la machine d'état jusqu'à confirmation ou rollback.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Champ
     - Description
   * - ``spec.nodeName``
     - McuNode cible (recommandé, résolution déterministe)
   * - ``spec.firmware.image``
     - Référence OCI du firmware — ex. ``192.168.42.1:5000/embewi/wheel-controller:v1.1.0``
   * - ``status.phase``
     - ``Binding`` → ``Pulling`` → ``Preparing`` → ``Writing`` → ``Activating`` → ``Confirming`` → ``Deployed`` / ``Failed``

----

Tokens
------

``embewi-core`` vérifie chaque heartbeat avec un token par-device
stocké dans le Secret ``embewi/embewi-tokens``.
Clé = ``nodeId``, valeur = token hex partagé avec le firmware.

.. code-block:: yaml

   apiVersion: v1
   kind: Secret
   metadata:
     name: embewi-tokens
     namespace: embewi
   type: Opaque
   stringData:
     wheel-01: "deadbeef0123456789abcdef"
     cam-front: "cafebabe..."

----

Registry OCI
------------

Les firmwares sont stockés comme artefacts OCI dans la registry interne
(VLAN 420 — ``192.168.42.1:5000``). ``embewi-core`` tire le blob firmware
depuis cette registry pour le pousser en OTA vers l'ESP32 via HTTPS.

La variable ``OCI_INSECURE_TLS=true`` est nécessaire car la registry
interne utilise un certificat auto-signé.

----

Dépendances
-----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Paquet
     - Ce qui est requis
   * - ``adp_kube``
     - ``kubectl apply`` pour CRDs et Deployment
   * - ``plg_gateway``
     - Bridge WiFi VLAN 220 (``br-wifi``) — prérequis réseau pour les ESP32
