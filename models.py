from dataclasses import dataclass

@dataclass
class Projeto:
    id: int
    numero_projeto: str
    nome_projeto: str
    cliente: str

@dataclass
class Equipamento:
    id: int
    projeto_id: int
    tag: str
    package: str

@dataclass
class Checklist:
    id: int
    equipamento_id: int
    data_criacao: str

@dataclass
class ItemChecklist:
    id: int
    checklist_id: int
    pergunta: str
    resposta: str
    foto: str

@dataclass
class PlanoAcao:
    id: int
    item_checklist_id: int
    plano: str
    data_criacao: str