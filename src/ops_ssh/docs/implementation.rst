Implémentation
==============

``kubewi ssh init`` vérifie que le tunnel WireGuard est actif
(``ip link show wg0-sdk``) avant de tenter la distribution de la clé —
les nœuds n'étant accessibles que via le tunnel.

La distribution s'appuie sur ``ansible.posix.authorized_key`` avec ``-k``
(mot de passe SSH demandé) plutôt que ``ssh-copy-id``, ce qui permet de
cibler un groupe Ansible (``controllers``, puis ``workers``) et de gérer
le ProxyJump workers automatiquement.

``~/.ssh/config`` configure ``192.168.22.*`` avec ``ProxyJump controller``
pour que tout SSH vers un worker passe transparentement par le controller.
