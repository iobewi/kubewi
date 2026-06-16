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
