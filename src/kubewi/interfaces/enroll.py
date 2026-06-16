from abc import ABC, abstractmethod


class EnrollInterface(ABC):
    @abstractmethod
    def worker(
        self, *,
        ifaces: int = 2,
        inventory_only: bool = False,
        yes: bool = False,
        single: bool = False,
        dry_run: bool = False,
    ) -> None: ...

    @abstractmethod
    def controller(
        self, *,
        name: str | None = None,
        inventory_only: bool = False,
        yes: bool = False,
    ) -> None: ...

    @abstractmethod
    def kubeconfig(self) -> None: ...
