INVENTORY := inventory
NAME           ?=
IFACES         ?= 2
INVENTORY_ONLY ?=
YES            ?=
SINGLE         ?=
DRY_RUN        ?=

.PHONY: init wifi wireguard-keys vault-encrypt vault-edit add-worker add-controller kubeconfig

# ── Init ──────────────────────────────────────────────────────────────────────

init:
	@if [ ! -f $(INVENTORY)/hosts.yml ]; then \
		cp $(INVENTORY)/hosts.yml.example $(INVENTORY)/hosts.yml; \
		echo "  ✓ hosts.yml créé"; \
	else \
		echo "  - hosts.yml déjà présent, ignoré"; \
	fi
	@if [ ! -f $(INVENTORY)/group_vars/all/vault.yml ]; then \
		cp $(INVENTORY)/group_vars/all/vault.yml.example $(INVENTORY)/group_vars/all/vault.yml; \
		echo "  ✓ vault.yml créé"; \
	else \
		echo "  - vault.yml déjà présent, ignoré"; \
	fi
	@echo ""
	@echo "Prochaines étapes :"
	@echo "  make wifi              — renseigner les credentials WiFi"
	@echo "  make wireguard-keys    — générer les clés WireGuard"
	@echo "  vim $(INVENTORY)/hosts.yml  — renseigner init_host et ansible_user"

# ── WiFi ──────────────────────────────────────────────────────────────────────

wifi:
	@test -f $(INVENTORY)/group_vars/all/vault.yml \
		|| { echo "vault.yml absent — lancer make init d'abord"; exit 1; }
	@read -p "SSID WiFi : " ssid; \
	read -s -p "PSK WiFi  : " psk; echo; \
	python3 scripts/inject_wifi.py "$$ssid" "$$psk"
	@echo "  ✓ Credentials WiFi mis à jour dans vault.yml"

# ── WireGuard ─────────────────────────────────────────────────────────────────

wireguard-keys:
	@test -f $(INVENTORY)/hosts.yml \
		|| { echo "hosts.yml absent — lancer make init d'abord"; exit 1; }
	@test -f $(INVENTORY)/group_vars/all/vault.yml \
		|| { echo "vault.yml absent — lancer make init d'abord"; exit 1; }
	@CTRL_KEY=$$(wg genkey); \
	CTRL_PUB=$$(echo "$$CTRL_KEY" | wg pubkey); \
	SDK_KEY=$$(wg genkey); \
	SDK_PUB=$$(echo "$$SDK_KEY" | wg pubkey); \
	python3 scripts/inject_wg_keys.py "$$CTRL_KEY" "$$SDK_KEY" "$$CTRL_PUB" "$$SDK_PUB"
	@echo "  ✓ Clés WireGuard générées et injectées"

# ── Vault ─────────────────────────────────────────────────────────────────────

vault-encrypt:
	@ansible-vault encrypt $(INVENTORY)/group_vars/all/vault.yml

vault-edit:
	@ansible-vault edit $(INVENTORY)/group_vars/all/vault.yml

# ── Enrollment ────────────────────────────────────────────────────────────────

add-worker:
	@python3 scripts/enroll.py worker \
		$(if $(filter 1,$(IFACES)),--ifaces 1) \
		$(if $(INVENTORY_ONLY),--inventory-only) \
		$(if $(YES),--yes) \
		$(if $(SINGLE),--single) \
		$(if $(DRY_RUN),--dry-run)

add-controller:
	@python3 scripts/enroll.py controller \
		$(if $(NAME),--name $(NAME)) \
		$(if $(INVENTORY_ONLY),--inventory-only) \
		$(if $(YES),--yes)

kubeconfig:
	@python3 scripts/kubeconfig.py
