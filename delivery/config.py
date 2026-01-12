from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ProviderStrategy:
    provider: str
    settlement_policy: str
    priority: int


@dataclass
class CompanyDeliveryConfig:
    company_id: str
    strategies: List[ProviderStrategy]

    def sorted_strategies(self) -> List[ProviderStrategy]:
        return sorted(self.strategies, key=lambda strategy: strategy.priority)


class CompanyConfigStore:
    def __init__(self) -> None:
        self._configs: Dict[str, CompanyDeliveryConfig] = {}

    def upsert(self, config: CompanyDeliveryConfig) -> None:
        self._configs[config.company_id] = config

    def get(self, company_id: str) -> CompanyDeliveryConfig | None:
        return self._configs.get(company_id)
