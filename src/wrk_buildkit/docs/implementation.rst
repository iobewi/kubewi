Implémentation
==============

``hadolint.yaml`` est colocalisé dans ``wrk_buildkit/`` (et non à la racine)
car c'est ce paquet qui appelle hadolint. ``lib.lint()`` passe
``--config <pkg_dir>/hadolint.yaml`` explicitement.

``build_arm64()`` combine ``docker buildx build --platform linux/arm64`` et
``push`` en une seule opération pour éviter un push séparé sur un registry
interne (accessible uniquement via VPN — le tunnel doit être actif).

La variable d'environnement ``REGISTRY_HOST`` permet de surcharger le
registry cible (par défaut ``registry.kubewi.internal:5000``).
