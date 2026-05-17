"""
Universal Simulation Hypothesis Tester - Aplicação Principal Streamlit
ESTE APLICATIVO É UMA FERRAMENTA EDUCACIONAL E EXPLORATÓRIA.
"""

import streamlit as st
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from modules.data_loader import DataLoader
from modules.simulation_tests import SimulationTests
from modules.statistical_analysis import StatisticalAnalysis
from modules.visualization import Visualization
from modules.report_generator import ReportGenerator
from modules.educational import EducationalContent

st.set_page_config(page_title="Teste da Hipótese da Simulação Universal", page_icon="🌌", layout="wide")

DISCLAIMER = """**ESTE APLICATIVO É UMA FERRAMENTA EDUCACIONAL E EXPLORATÓRIA.**
A hipótese de simulação é filosófica e não existe método científico para prová-la ou refutá-la.
Resultados são ESPECULATIVOS e NÃO-CONCLUSIVOS."""

def main():
    st.title("🌌 Teste da Hipótese da Simulação Universal")
    st.warning(DISCLAIMER)
    
    config = {}
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
    
    data_loader = DataLoader(config.get('simulation', {}))
    simulation_tests = SimulationTests(config.get('simulation', {}))
    visualization = Visualization(config.get('visualization', {}))
    report_generator = ReportGenerator(config.get('export', {}))
    educational = EducationalContent()
    
    st.sidebar.title("🔧 Menu")
    choice = st.sidebar.radio("Navegação", ["Início", "Carregar Dados", "Executar Testes", "Resultados", "Educação", "Exportar"])
    
    if 'data_loaded' not in st.session_state: st.session_state.data_loaded = False
    if 'tests_executed' not in st.session_state: st.session_state.tests_executed = False
    if 'test_results' not in st.session_state: st.session_state.test_results = None
    if 'overall_score' not in st.session_state: st.session_state.overall_score = 0.0
    
    if choice == "Início":
        st.header("Bem-vindo!")
        st.metric("Testes Disponíveis", 6)
        for name in ["Discretização do Espaço-Tempo", "Erros de Arredondamento", "Correlações Não-Locais", "Isotropia", "Limitação de Recursos", "Consistência Temporal"]:
            st.info(f"📌 {name}")
    
    elif choice == "Carregar Dados":
        source = st.radio("Fonte:", ["Dados Simulados", "Upload CSV/JSON"])
        if source == "Dados Simulados":
            dtype = st.selectbox("Tipo:", ["cosmic_microwave", "quantum_particles", "cosmic_rays", "constants"])
            n = st.slider("Amostras:", 1000, 50000, 10000)
            if st.button("Gerar"):
                data = data_loader.generate_simulated_data(dtype, n, seed=42)
                st.session_state.data_loaded = True
                st.session_state.current_data = data
                st.success(f"Dados gerados: {len(data)} amostras")
        else:
            f = st.file_uploader("Arquivo:", type=['csv', 'json'])
            if f:
                try:
                    data = data_loader.load_csv(f) if f.name.endswith('.csv') else data_loader.load_json(f)
                    st.session_state.data_loaded = True
                    st.session_state.current_data = data
                    st.success("Arquivo carregado!")
                except Exception as e: st.error(str(e))
    
    elif choice == "Executar Testes":
        if not st.session_state.data_loaded:
            st.warning("Carregue dados primeiro!")
        else:
            if st.button("🚀 Executar Testes"):
                results = simulation_tests.run_all_tests(st.session_state.current_data)
                st.session_state.test_results = results
                st.session_state.overall_score = simulation_tests.calculate_overall_suspicion_index()
                st.session_state.tests_executed = True
                st.success("Testes concluídos!")
                score = st.session_state.overall_score
                color = "🟢" if score < 30 else "🟡" if score < 70 else "🔴"
                st.metric("Índice de Suspeita", f"{score:.1f}%", f"{color}")
    
    elif choice == "Resultados":
        if not st.session_state.tests_executed:
            st.warning("Execute os testes primeiro!")
        else:
            results = st.session_state.test_results
            for k, r in results.items():
                status = "⚠️" if r.anomaly_detected else "✓"
                st.write(f"{status} **{r.test_name}**: {r.anomaly_score:.1f}/100 (p={r.significance:.4f})")
            st.info("Lembre-se: Anomalias ≠ Evidência de simulação")
    
    elif choice == "Educação":
        t1, t2, t3 = st.tabs(["Explicações", "Físicos", "Glossário"])
        with t1:
            sel = st.selectbox("Teste:", list(educational.test_explanations.keys()), format_func=lambda x: educational.test_explanations[x]['title'])
            exp = educational.get_test_explanation(sel)
            st.write(exp.get('simple_explanation', ''))
        with t2:
            for bio in educational.physicist_biographies:
                with st.expander(f"{bio['name']}"): st.write(bio['contribution'])
        with t3:
            for term, def_ in list(educational.glossary.items())[:10]: st.write(f"**{term}**: {def_}")
    
    elif choice == "Exportar":
        if not st.session_state.tests_executed:
            st.warning("Execute os testes primeiro!")
        else:
            fmt = st.selectbox("Formato:", ["JSON", "CSV", "LaTeX", "Texto"])
            fname = st.text_input("Nome:", "resultado")
            if st.button("Exportar"):
                r = st.session_state.test_results
                if fmt == "JSON": report_generator.export_to_json(r, f"{fname}.json")
                elif fmt == "CSV": report_generator.export_to_csv(r, f"{fname}.csv")
                elif fmt == "LaTeX": st.code(report_generator.generate_latex(r, st.session_state.overall_score), language="latex")
                else: st.download_button("Baixar", report_generator.generate_summary_report(r, st.session_state.overall_score, {}), f"{fname}.txt")
                st.success("Exportado!")
    
    st.markdown("---")
    st.caption("⚠️ Ferramenta educacional. Resultados especulativos. Consulte profissionais.")

if __name__ == "__main__":
    main()
