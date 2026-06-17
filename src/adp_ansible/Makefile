INVENTORY      ?= $(KUBEWI_PROJECT)
TEMPLATES      := inventory
NAME           ?=
IFACES         ?= 2
INVENTORY_ONLY ?=
YES            ?=
SINGLE         ?=
DRY_RUN        ?=

.PHONY: wireguard-keys vault-encrypt vault-edit

# ── WireGuard ─────────────────────────────────────────────────────────────────

wireguard-keys:
	@test -f $(INVENTORY)/hosts.yml \
		|| { echo "hosts.yml absent — lancer make ansible-init d'abord"; exit 1; }
	@test -f $(INVENTORY)/group_vars/all/vault.yml \
		|| { echo "vault.yml absent — lancer make ansible-init d'abord"; exit 1; }
	@CTRL_KEY=$$(wg genkey); \
	CTRL_PUB=$$(echo "$$CTRL_KEY" | wg pubkey); \
	SDK_KEY=$$(wg genkey); \
	SDK_PUB=$$(echo "$$SDK_KEY" | wg pubkey); \
	python3 scripts/inject_wg_keys.py $(INVENTORY)/group_vars/all/vault.yml $(INVENTORY)/hosts.yml \
		"$$CTRL_KEY" "$$SDK_KEY" "$$CTRL_PUB" "$$SDK_PUB"
	@echo "  ✓ Clés WireGuard générées et injectées"

# ── Vault ─────────────────────────────────────────────────────────────────────

vault-encrypt:
	@ansible-vault encrypt $(INVENTORY)/group_vars/all/vault.yml

vault-edit:
	@ansible-vault edit $(INVENTORY)/group_vars/all/vault.yml
