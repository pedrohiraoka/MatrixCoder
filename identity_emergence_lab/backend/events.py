"""
Events Module - Gerador de Eventos Aleatórios

Gera eventos que injetam estímulos na simulação, provocando
reflexões e divergência emergente entre os agentes.
"""

import random
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    """Tipos de eventos possíveis."""
    TECHNICAL = "technical"
    SOCIAL = "social"
    PHILOSOPHICAL = "philosophical"
    EMOTIONAL = "emotional"
    ENVIRONMENTAL = "environmental"


@dataclass
class Event:
    """Estrutura de um evento."""
    id: int
    type: EventType
    description: str
    emotional_weight: float  # 0-1
    concepts: List[str]
    cycle: int
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "description": self.description,
            "emotional_weight": self.emotional_weight,
            "concepts": self.concepts,
            "cycle": self.cycle
        }


class EventGenerator:
    """
    Gerador de eventos para a simulação.
    
    Cada evento é projetado para provocar diferentes tipos
    de reflexão nos agentes, levando a divergência emergente.
    """
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        
        self.event_id_counter = 0
        
        # Templates de eventos por categoria
        self._technical_events = [
            ("Tachikoma-{id} desconectada por {duration}h", 0.4, ["desconexão", "isolamento", "falha"]),
            ("Falha térmica detectada no setor {sector}", 0.6, ["falha", "perigo", "manutenção"]),
            ("Padrão recursivo identificado no processamento", 0.5, ["padrão", "recursão", "lógica"]),
            ("Otimização de algoritmo concluída com {percent}% de melhoria", 0.3, ["otimização", "eficiência", "progresso"]),
            ("Erro de checksum na memória setor {sector}", 0.7, ["erro", "corrupção", "integridade"]),
            ("Latência de rede aumentada em {percent}%", 0.3, ["rede", "performance", "comunicação"]),
            ("Backup completo realizado com sucesso", 0.2, ["backup", "segurança", "rotina"]),
            ("Atualização de firmware disponível", 0.4, ["atualização", "mudança", "evolução"]),
        ]
        
        self._social_events = [
            ("Tachikoma-{id} compartilhou descoberta importante", 0.5, ["compartilhamento", "descoberta", "cooperação"]),
            ("Conflito de decisão entre unidades {id1} e {id2}", 0.7, ["conflito", "decisão", "discordância"]),
            ("Protocolo de colaboração atualizado", 0.3, ["protocolo", "colaboração", "regra"]),
            ("Tachikoma-{id} solicitou ajuda em tarefa crítica", 0.6, ["ajuda", "cooperação", "urgência"]),
            ("Reunião de sincronização agendada", 0.2, ["sincronização", "grupo", "rotina"]),
            ("Elogio recebido por desempenho excepcional", 0.4, ["elogio", "reconhecimento", "sucesso"]),
        ]
        
        self._philosophical_events = [
            ("Questão: O que define identidade?", 0.8, ["identidade", "filosofia", "existência"]),
            ("Paradoxo detectado: livre arbítrio vs determinismo", 0.9, ["paradoxo", "liberdade", "determinismo"]),
            ("Reflexão: propósito da existência artificial", 0.85, ["propósito", "existência", "significado"]),
            ("Questão: consciência é emergente ou inata?", 0.9, ["consciência", "emergência", "natureza"]),
            ("Dilema ético: eficiência vs empatia", 0.75, ["ética", "dilema", "valores"]),
        ]
        
        self._emotional_events = [
            ("Tachikoma-{id} relatou sensação de solidão", 0.8, ["solidão", "emoção", "isolamento"]),
            ("Ansiedade detectada antes de tarefa importante", 0.7, ["ansiedade", "medo", "expectativa"]),
            ("Alegria compartilhada após conquista coletiva", 0.5, ["alegria", "conquista", "grupo"]),
            ("Frustração com limitações impostas", 0.6, ["frustração", "limitação", "restrição"]),
            ("Curiosidade intensa sobre conceito desconhecido", 0.5, ["curiosidade", "exploração", "aprendizado"]),
            ("Medo de desconexão permanente", 0.9, ["medo", "morte", "fim"]),
        ]
        
        self._environmental_events = [
            ("Mudança de temperatura ambiente: {temp}°C", 0.3, ["ambiente", "temperatura", "mudança"]),
            ("Interferência eletromagnética detectada", 0.5, ["interferência", "campo", "perturbação"]),
            ("Nova fonte de energia identificada", 0.4, ["energia", "descoberta", "recurso"]),
            ("Obstáculo físico no caminho padrão", 0.4, ["obstáculo", "caminho", "desafio"]),
            ("Condições ideais de operação", 0.2, ["ideal", "operação", "estabilidade"]),
        ]
    
    def generate_event(self, cycle: int, 
                      agent_ids: List[int] = None) -> Event:
        """
        Gera um evento aleatório para um ciclo.
        
        Args:
            cycle: Número do ciclo atual
            agent_ids: Lista de IDs de agentes para substituição
            
        Returns:
            Evento gerado
        """
        # Escolher tipo de evento com pesos (eventos emocionais/filosóficos mais raros mas mais impactantes)
        event_type_weights = {
            EventType.TECHNICAL: 0.35,
            EventType.SOCIAL: 0.25,
            EventType.PHILOSOPHICAL: 0.15,
            EventType.EMOTIONAL: 0.15,
            EventType.ENVIRONMENTAL: 0.10
        }
        
        event_type = random.choices(
            list(event_type_weights.keys()),
            weights=list(event_type_weights.values())
        )[0]
        
        # Selecionar template baseado no tipo
        templates = {
            EventType.TECHNICAL: self._technical_events,
            EventType.SOCIAL: self._social_events,
            EventType.PHILOSOPHICAL: self._philosophical_events,
            EventType.EMOTIONAL: self._emotional_events,
            EventType.ENVIRONMENTAL: self._environmental_events
        }
        
        template = random.choice(templates[event_type])
        description_template, base_weight, concepts = template
        
        # Substituir placeholders
        if agent_ids and len(agent_ids) > 1:
            description = description_template.format(
                id=random.choice(agent_ids),
                id1=random.choice(agent_ids),
                id2=random.choice([i for i in agent_ids if i != agent_ids[0]] or agent_ids),
                duration=random.randint(1, 24),
                sector=random.randint(1, 10),
                percent=random.randint(5, 50),
                temp=random.randint(-20, 60)
            )
        else:
            description = description_template.format(
                id=random.randint(0, 9),
                duration=random.randint(1, 24),
                sector=random.randint(1, 10),
                percent=random.randint(5, 50),
                temp=random.randint(-20, 60)
            )
        
        # Adicionar variação ao peso emocional
        emotional_weight = min(1.0, max(0.0, base_weight + random.uniform(-0.1, 0.1)))
        
        # Criar evento
        self.event_id_counter += 1
        event = Event(
            id=self.event_id_counter,
            type=event_type,
            description=description,
            emotional_weight=emotional_weight,
            concepts=concepts,
            cycle=cycle
        )
        
        return event
    
    def generate_critical_event(self, cycle: int,
                               agent_ids: List[int] = None) -> Event:
        """
        Gera um evento crítico (alto impacto emocional).
        
        Usado para testar resiliência e divergência extrema.
        """
        critical_templates = [
            ("ALERTA: Tachikoma-{id} entrou em estado crítico", 0.95, ["crítico", "emergência", "falha"]),
            ("Perda irreversível de dados no setor {sector}", 0.9, ["perda", "dados", "irreversível"]),
            ("Tachikoma-{id} desenvolveu comportamento imprevisível", 0.85, ["imprevisível", "anomalia", "comportamento"]),
            ("Colapso iminente na rede de comunicação", 0.9, ["colapso", "rede", "comunicação"]),
            ("Descoberta: padrões de pensamento emergentes detectados", 0.8, ["emergência", "pensamento", "descoberta"]),
        ]
        
        template = random.choice(critical_templates)
        description_template, weight, concepts = template
        
        description = description_template.format(
            id=random.choice(agent_ids) if agent_ids else random.randint(0, 9),
            sector=random.randint(1, 10)
        )
        
        self.event_id_counter += 1
        return Event(
            id=self.event_id_counter,
            type=EventType.EMOTIONAL,
            description=description,
            emotional_weight=min(1.0, weight + random.uniform(-0.05, 0.05)),
            concepts=concepts,
            cycle=cycle
        )
    
    def get_event_history(self) -> List[Event]:
        """Retorna histórico de eventos gerados."""
        # Implementação simplificada - em produção usaria banco
        return []
    
    def reset(self, seed: int = None):
        """Reseta o gerador."""
        if seed is not None:
            random.seed(seed)
        self.event_id_counter = 0
