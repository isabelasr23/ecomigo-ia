from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Identification(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    objeto: str = Field(min_length=1, max_length=160)
    material: Literal['papel', 'plastico', 'metal', 'vidro', 'misto', 'desconhecido']
    identificacao_inconclusiva: bool
    observacao: str = Field(min_length=1, max_length=800)

    @model_validator(mode='after')
    def uncertain_material(self):
        if self.material in ('misto', 'desconhecido'):
            self.identificacao_inconclusiva = True
        return self

class Analysis(Identification):
    orientacao: Optional[str] = None
    cuidados: Optional[str] = None
    fonte_orientacao: Optional[str] = None
    data_atualizacao: Optional[str] = None
    orientacao_provisoria: bool = True
