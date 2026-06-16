Implémentation
==============

Si ``cgroups.yml`` modifie ``cmdline.txt``, le nœud redémarre automatiquement
(``ansible.builtin.reboot``) avant de poursuivre le playbook. C'est nécessaire
car les paramètres bootloader ne prennent effet qu'après reboot.

Le module ``zram`` (swap compressé en RAM) est activé pour limiter les
accès à la carte SD et améliorer les performances sur RPi. ``eng_debian``
désactive le swap classique — zram prend le relai sans dépendre du stockage.
