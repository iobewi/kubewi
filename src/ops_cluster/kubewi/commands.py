from __future__ import annotations

from pathlib import Path

from adp_ansible.kubewi import lib as ansible

NAME      = 'cluster'
_PKG_DIR  = Path(__file__).parent.parent
PLAYBOOKS = _PKG_DIR / 'playbooks'


def register(sub) -> None:
    p = sub.add_parser('cluster', help='Gestion déclarative du cluster')
    s = p.add_subparsers(dest='cluster_cmd', metavar='CMD', required=True)

    create_p = s.add_parser('create', help='Crée un nouveau projet kubewi')
    create_p.add_argument('name', metavar='NOM', help='Nom du projet/cluster')
    create_p.add_argument('--dir', '-d', default='.', metavar='DIR', help='Répertoire parent (défaut: courant)')

    s.add_parser('status', help="Affiche l'état désiré vs enrollé")

    apply_p = s.add_parser('apply', help='Enrôle les nœuds manquants')
    apply_p.add_argument('--dry-run', '-n', action='store_true', help='Affiche le plan sans exécuter')
    apply_p.add_argument('--yes',     '-y', action='store_true', help='Skip la confirmation')

    add_p = s.add_parser('add', help='Ajoute un nœud au cluster existant')
    add_s = add_p.add_subparsers(dest='add_role', metavar='ROLE', required=True)

    add_w = add_s.add_parser('worker', help='Ajoute un worker (auto-détection ou fichier host existant)')
    add_w.add_argument('name', nargs='?', metavar='NAME', help='Nom du worker (mode manuel, fichier hosts/<NAME>.yml requis)')
    add_w.add_argument('--ifaces', type=int, choices=[1, 2], default=2)
    add_w.add_argument('--dry-run', '-n', action='store_true')
    add_w.add_argument('--yes', '-y', action='store_true')

    add_c = add_s.add_parser('controller', help='Ajoute un controller secondaire (fichier hosts/<NAME>.yml requis)')
    add_c.add_argument('name', metavar='NAME')
    add_c.add_argument('--yes', '-y', action='store_true')

    s.add_parser('kubeconfig',     help='Récupère le kubeconfig depuis le controller et configure kubectl')
    s.add_parser('wifi',           help='Renseigne les credentials WiFi dans vault.yml')
    s.add_parser('vault-encrypt',  help='Chiffre vault.yml avec ansible-vault')
    s.add_parser('vault-edit',     help='Édite le vault chiffré')
    s.add_parser('system',         help='Applique la configuration système sur tous les nœuds')
    s.add_parser('network',        help='Applique la configuration réseau sur tous les nœuds')
    s.add_parser('stack',          help='Déploie la stack complète (system + network + k0s)')


def run_cmd(args) -> None:
    if args.cluster_cmd == 'create':
        from ops_cluster.kubewi._create import _create_project
        _create_project(args); return

    if args.cluster_cmd == 'status':
        from ops_cluster.kubewi._apply import _status
        _status(args); return

    if args.cluster_cmd == 'apply':
        from ops_cluster.kubewi._apply import _apply
        _apply(args); return

    if args.cluster_cmd == 'add':
        from ops_cluster.kubewi._add import _add_worker, _add_controller
        if args.add_role == 'worker':      _add_worker(args)
        elif args.add_role == 'controller': _add_controller(args)
        return

    if args.cluster_cmd == 'kubeconfig':
        from ops_cluster.kubewi._execute import _kubeconfig
        _kubeconfig(); return

    if args.cluster_cmd == 'wifi':
        from ops_cluster.kubewi._vault import _wifi
        _wifi(); return

    if args.cluster_cmd in ('vault-encrypt', 'vault-edit'):
        from ops_cluster.kubewi._vault import _vault_cmd
        _vault_cmd(args.cluster_cmd.split('-')[1]); return

    ansible.run_playbook(PLAYBOOKS / f'{args.cluster_cmd}.yml')
