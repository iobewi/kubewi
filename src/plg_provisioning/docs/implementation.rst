Implémentation
==============

Réseau de provisioning
-----------------------

Le DHCP de provisioning est un pod Kubernetes temporaire, pas un service
permanent. Le pod est éteint (replicas=0) entre les enrollments pour éviter
les conflits DHCP avec le réseau de production.

``kubewi provisioning on`` attend que le pod soit ``Ready`` avant de rendre
la main (``rollout_wait``). Cela garantit que le DHCP est opérationnel avant
de démarrer la détection réseau.

Le pod dnsmasq attribue des adresses ``192.168.0.x`` aux nœuds branchés sur
le switch cluster. La liaison physique est toujours active (``br0`` à
``192.168.0.1/24``, NAT toujours activé) — c'est la **CiliumNetworkPolicy**
qui contrôle la joignabilité du pod depuis le reste du réseau.

.. note::

   Le port 22 est intentionnellement ouvert dans la CiliumNetworkPolicy.
   Le pod est le « commutateur » du réseau de provisioning : pod actif = DHCP
   + SSH bootstrap accessibles depuis le réseau ; pod inactif = plus d'endpoint
   correspondant à la policy, le réseau ``192.168.0.x`` ne route plus.

----

Détection des nœuds (``lib.detect_phase``)
-------------------------------------------

``detect_phase(ifaces, single, dry_run)`` surveille en continu les baux
DHCP du pod dnsmasq via :

.. code-block:: bash

   kubectl -n provisioning exec deploy/dnsmasq-provisioning -- \
       cat /var/lib/misc/dnsmasq.leases

Format d'un bail : ``<expiry_epoch> <mac> <ip> <hostname> <clientid>``

Dès qu'un nouveau bail apparaît :

1. La MAC est transformée en identifiant court via
   ``kubewi._hostfile.mac_to_id()`` (3 derniers octets, sans séparateur) :
   ``28:94:01:88:c2:40`` → ``88c240``
2. Le nœud est nommé ``worker-88c240``.
3. Une IP VLAN 220 lui est allouée (``192.168.22.X`` via ``next_host_id()``).
4. Le fichier ``hosts/worker-88c240.yml`` est créé via
   ``create_worker_host_file()``.

En mode ``single=True`` (``cluster add worker`` auto), la détection s'arrête
au premier nœud détecté. En mode multi (anciennement ``kubewi enroll worker``),
l'utilisateur appuie sur Entrée pour terminer.

----

Nommage MAC vs nommage séquentiel
-----------------------------------

L'ancien nommage ``worker-01``, ``worker-02``… créait des « trous » lors des
suppressions de nœuds et nécessitait un état partagé pour suivre l'index
courant. Le nommage MAC (``worker-88c240``) est :

- **stable** — le même nœud reprend toujours le même nom après un remove/add
- **sans état** — dérivé directement de l'adresse matérielle, pas d'index à maintenir
- **unique** — les 3 derniers octets MAC suffisent à l'échelle d'un cluster
