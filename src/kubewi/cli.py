"""
role:
    Point d'entrée CLI — construction du parser et dispatch vers les paquets.

responsibilities:
    - découvrir les paquets via _discovery
    - construire le parser en appelant register(sub) sur chaque paquet
    - router vers paquet.run_cmd(args)

does_not:
    - implémenter la logique métier
    - définir les arguments (délégué à chaque paquet via register)
"""
from __future__ import annotations

import argparse
import sys

from ._discovery import discover
from ._pkgmgr   import cmd_list, cmd_search, cmd_info_name, print_help


class _FrParser(argparse.ArgumentParser):
    """ArgumentParser avec messages d'erreur en français."""

    def error(self, message: str) -> None:
        message = (message
            .replace('the following arguments are required:', 'argument(s) requis :')
            .replace('expected one argument',                 'un argument est attendu')
            .replace('expected at most one argument',         'un argument maximum attendu')
            .replace('unrecognized arguments:',               'arguments non reconnus :')
            .replace('invalid choice:',                       'choix invalide :')
            .replace('(choose from',                          '(valeurs possibles :')
            .replace('argument',                              'argument')
        )
        self.print_usage(sys.stderr)
        self.exit(2, f'{self.prog}: erreur: {message}\n')

_MODULES: dict = {}

_TYPE_LABELS = {
    'tool':    'Outils',
    'os':      'Système d\'exploitation',
    'ops':     'Opérations',
    'service': 'Services',
}


def build_parser() -> argparse.ArgumentParser:
    global _MODULES
    parser = _FrParser(prog='kubewi', add_help=False)

    # ── flags gestionnaire de packages ───────────────────────────
    parser.add_argument('-h', '--help',   action='store_true')
    parser.add_argument('--list',         action='store_true',  help='Lister les packages')
    parser.add_argument('--type',         metavar='TYPE',       choices=list(_TYPE_LABELS),
                        help='Filtrer --list par type')
    parser.add_argument('--search',       metavar='QUERY',      help='Rechercher un package')
    parser.add_argument('--info',         metavar='PACKAGE',    help='Détails d\'un package')

    # ── dispatch vers un package ─────────────────────────────────
    sub = parser.add_subparsers(dest='package', parser_class=_FrParser)
    _MODULES = discover()
    for mod in dict.fromkeys(_MODULES.values()):
        mod.register(sub)

    return parser


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    if args.help or (not args.package and not args.list
                     and not args.search and not args.info):
        print_help()
        return

    if args.list:   cmd_list(args);          return
    if args.search: cmd_search(args);        return
    if args.info:   cmd_info_name(args.info); return

    mod = _MODULES.get(args.package)
    if not mod:
        print(f"  ✗ Package inconnu : {args.package}")
        print("  → kubewi --list   pour voir les packages disponibles")
        sys.exit(1)

    try:
        mod.run_cmd(args)
    except KeyboardInterrupt:
        print('\n  Interruption.')
        sys.exit(1)
