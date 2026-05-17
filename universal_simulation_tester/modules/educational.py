"""
Módulo de Conteúdo Educacional

Fornece:
- Explicações sobre cada teste
- Biografias de físicos relevantes
- Seção "Mitos e Verdades"
- Glossário de termos técnicos
- Referências científicas
"""

from typing import Dict, List


class EducationalContent:
    """Classe para conteúdo educacional sobre a hipótese de simulação."""
    
    def __init__(self):
        self.test_explanations = self._get_test_explanations()
        self.physicist_biographies = self._get_physicist_biographies()
        self.myths_and_facts = self._get_myths_and_facts()
        self.glossary = self._get_glossary()
    
    def _get_test_explanations(self) -> Dict[str, Dict]:
        return {
            'spacetime_discretization': {
                'title': 'Discretização do Espaço-Tempo',
                'simple_explanation': 'Imagine pixels em uma tela. Se o universo fosse simulado, poderia ter unidade mínima de espaço.',
                'technical_details': 'Escala de Planck (~1.6e-35 m). Loop Quantum Gravity prediz estrutura discreta.',
                'what_would_be_evidence': 'Padrões periódicos, direções privilegiadas, limites inferiores mensuráveis.'
            },
            'rounding_errors': {
                'title': 'Erros de Arredondamento Cósmico',
                'simple_explanation': 'Computadores usam precisão finita. Constantes físicas poderiam mostrar truncamentos.',
                'technical_details': 'Constantes adimensionais como alpha (~1/137) são independentes de unidades.',
                'what_would_be_evidence': 'Padrões em binário, terminações suspeitas em decimal.'
            },
            'nonlocal_correlations': {
                'title': 'Correlações Não-Locais Anômalas',
                'simple_explanation': 'Emaranhamento quântico tem limite teórico (Tsirelson). Violações sugeririam código.',
                'technical_details': 'Limite de Tsirelson: 2√2 ≈ 2.828 para parâmetro S de CHSH.',
                'what_would_be_evidence': 'Violação do limite, padrões periódicos em medições.'
            },
            'isotropy_homogeneity': {
                'title': 'Isotropia e Homogeneidade',
                'simple_explanation': 'Universo deveria ser igual em todas direções. Simulação poderia ter eixos privilegiados.',
                'technical_details': 'CMB é melhor laboratório. Planck detectou "Axis of Evil" e outras anomalias.',
                'what_would_be_evidence': 'Eixos de alinhamento, anisotropias sistemáticas.'
            },
            'resource_limitations': {
                'title': 'Limitação de Recursos',
                'simple_explanation': 'Videogames economizam processamento (LOD, frustum culling). Universo poderia fazer similar.',
                'technical_details': 'Busca por cortes em distribuições de energia, simplificação em escalas extremas.',
                'what_would_be_evidence': 'Cortes abruptos sem explicação física, entropia baixa em sistemas complexos.'
            },
            'temporal_consistency': {
                'title': 'Consistência Temporal',
                'simple_explanation': 'Tempo parece contínuo, mas em simulação avançaria em ticks discretos.',
                'technical_details': 'Tempo de Planck ~5.4e-44 s está além da precisão experimental atual.',
                'what_would_be_evidence': 'Periodicidade em timestamps, sincronização suspeita de eventos.'
            }
        }
    
    def _get_physicist_biographies(self) -> List[Dict]:
        return [
            {'name': 'Nick Bostrom', 'role': 'Filósofo', 'institution': 'Oxford',
             'contribution': 'Artigo seminal "Are You Living in a Computer Simulation?" (2003)',
             'key_publication': 'Bostrom, N. (2003). Philosophical Quarterly, 53(211)'},
            {'name': 'John Stewart Bell', 'role': 'Físico', 'institution': 'CERN',
             'contribution': 'Teorema de Bell (1964) sobre variáveis ocultas locais',
             'key_publication': 'Bell, J.S. (1964). Physics, 1(3), 195'},
            {'name': 'Max Tegmark', 'role': 'Físico', 'institution': 'MIT',
             'contribution': 'Hipótese do Universo Matemático e limites computacionais',
             'key_publication': 'Tegmark, M. (2007). Foundations of Physics, 38'},
            {'name': 'Carlo Rovelli', 'role': 'Físico', 'institution': 'Aix-Marseille',
             'contribution': 'Loop Quantum Gravity - estrutura discreta do espaço-tempo',
             'key_publication': 'Rovelli, C. (1998). Living Reviews in Relativity'},
            {'name': 'Sabine Hossenfelder', 'role': 'Física', 'institution': 'FIAS Frankfurt',
             'contribution': 'Limites experimentais para discretização do espaço-tempo',
             'key_publication': 'Hossenfelder, S. (2013). Living Reviews in Relativity'}
        ]
    
    def _get_myths_and_facts(self) -> List[Dict]:
        return [
            {'myth': '"Este app pode provar que vivemos em simulação"',
             'fact': 'FALSO. Não existe método científico estabelecido para provar/refutar definitivamente.'},
            {'myth': '"Anomalias = evidência de simulação"',
             'fact': 'NÃO NECESSARIAMENTE. Anomalias podem ter explicações convencionais (ruído, erro, física não compreendida).'},
            {'myth': '"Sem anomalias = NÃO estamos em simulação"',
             'fact': 'FALSO. Simulação poderia ser perfeita o suficiente para não deixar artefatos detectáveis.'},
            {'myth': '"Elon Musk disse, então é verdade"',
             'fact': 'Argumento de autoridade não é evidência científica. Ciência avança com dados e revisão por pares.'},
            {'myth': '"Simulação = Deus/criação divina"',
             'fact': 'SÃO DIFERENTES. Hipótese de simulação é naturalista; criação divina é tipicamente sobrenatural.'}
        ]
    
    def _get_glossary(self) -> Dict[str, str]:
        return {
            'Anomalia Estatística': 'Desvio significativo do esperado. Pode ser ruído ou erro.',
            'Constante de Estrutura Fina (α)': 'Constante adimensional ~1/137 da interação eletromagnética.',
            'Discretização': 'Divisão de algo contínuo em partes discretas (pixels).',
            'Emaranhamento Quântico': 'Correlação entre partículas que não pode ser descrita classicamente.',
            'Escala de Planck': 'Unidades fundamentais: comprimento ~1.6e-35m, tempo ~5.4e-44s.',
            'Fator de Bayes': 'Razão de verossimilhanças entre modelos. BF>1 favorece alternativa.',
            'Homogeneidade': 'Ser o mesmo em todos os lugares.',
            'Isotropia': 'Ser o mesmo em todas as direções.',
            'Limite de Tsirelson': 'Máximo (2√2) do parâmetro S em testes de Bell na MQ.',
            'Monte Carlo': 'Método usando amostragem aleatória repetida.',
            'p-value': 'Probabilidade de dados tão extremos sob hipótese nula.',
            'Princípio Cosmológico': 'Universo é isotrópico e homogêneo em grandes escalas.',
            'CMB': 'Radiação cósmica de fundo, remanescente do Big Bang (2.725K).',
            'Teorema de Bell': 'Nenhuma teoria local de variáveis ocultas reproduz MQ.',
            'Viés de Confirmação': 'Tendência de buscar informações que confirmam crenças.',
            'p-hacking': 'Analisar dados múltiplas formas até achar resultado "significativo".'
        }
    
    def get_test_explanation(self, test_name: str) -> Dict:
        return self.test_explanations.get(test_name, {})
    
    def get_all_glossary_terms(self) -> Dict[str, str]:
        return self.glossary
    
    def get_random_fact(self) -> Dict:
        import random
        return random.choice(self.myths_and_facts)
    
    def get_physicist_by_name(self, name: str) -> Dict:
        for bio in self.physicist_biographies:
            if name.lower() in bio['name'].lower():
                return bio
        return {}
