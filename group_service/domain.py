from dataclasses import dataclass, field, asdict
from typing import List, Set

@dataclass
class Group:
    """Clase de Dominio pura. No depende de la DB."""
    id: str
    name: str
    owner_id: str
    members: Set[str] = field(default_factory=set)
    bmcs: List[dict] = field(default_factory=list)

    def to_dict(self):
        """Convierte el objeto a diccionario para JSON."""
        d = asdict(self)
        # Los sets no son serializables en JSON, convertimos a lista
        d['members'] = list(self.members)
        return d