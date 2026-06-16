Variables
=========

.. list-table::
   :header-rows: 1
   :widths: 38 28 34

   * - Variable
     - Défaut
     - Description
   * - ``system_packages``
     - ``avahi-daemon, curl, vim…``
     - Paquets installés sur tous les nœuds
   * - ``ssh_port``
     - ``22``
     - Port SSH
   * - ``ssh_permit_root_login``
     - ``no``
     - Connexion root désactivée
   * - ``ssh_password_authentication``
     - ``no``
     - Authentification par mot de passe désactivée
   * - ``ssh_client_alive_interval``
     - ``300``
     - Keepalive SSH (secondes)
   * - ``chrony_ntp_servers``
     - ``{{ ntp_servers }}``
     - Serveurs NTP (depuis ``group_vars/all/main.yml``)
   * - ``system_kernel_modules``
     - ``overlay, br_netfilter``
     - Modules noyau chargés au boot
   * - ``system_sysctl``
     - ip_forward=1, bridge-nf-call…
     - Paramètres sysctl pour Kubernetes
   * - ``ssh_max_auth_tries``
     - ``3``
     - Tentatives SSH max
   * - ``ssh_login_grace_time``
     - ``30``
     - Délai d'authentification (secondes)
   * - ``ssh_client_alive_count_max``
     - ``2``
     - Nombre de keepalives sans réponse avant déconnexion
   * - ``systemd_journal_max_use``
     - ``500M``
     - Taille max des journaux systemd (SD embarqué)
   * - ``systemd_journal_runtime_max_use``
     - ``100M``
     - Taille max des journaux en RAM

Paramètres sysctl déployés
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Paramètre
     - Valeur et raison
   * - ``net.ipv4.ip_forward``
     - ``1`` — requis par Cilium pour le routage inter-pods
   * - ``net.bridge.bridge-nf-call-iptables``
     - ``1`` — requis par Cilium
   * - ``net.bridge.bridge-nf-call-ip6tables``
     - ``1`` — requis par Cilium
   * - ``IPv4SendRedirects`` (networkd)
     - ``no`` — désactivé sur br0 et VLANs pour éviter les boucles
       de routage sur des nœuds qui ne sont pas des routeurs réels
