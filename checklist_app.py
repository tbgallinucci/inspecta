import streamlit as st
import pandas as pd
import json
from datetime import datetime
import uuid
from pathlib import Path
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema de Checklist ODS",
    page_icon="🔧",
    layout="wide"
)

# Inicialização de dados em sessão
if 'projetos' not in st.session_state:
    st.session_state.projetos = {}
if 'equipamentos' not in st.session_state:
    st.session_state.equipamentos = {}
if 'checklists' not in st.session_state:
    st.session_state.checklists = {}

# Templates de checklist por família
TEMPLATES_CHECKLIST = {
    "1500": {
        "nome": "Big Ball Valves",
        "items": [
            "Verificar se a válvula está de acordo com a especificação técnica (material, classe de pressão, diâmetro)",
            "Confirmar se o tipo de conexão (flangeada, soldada, rosqueada) está conforme especificado",
            "Verificar se a válvula possui certificado de teste hidrostático",
            "Confirmar se o material do corpo da válvula está de acordo (Carbon Steel, Stainless Steel, etc.)",
            "Verificar se o material da esfera está conforme especificação",
            "Confirmar se os assentos da válvula são adequados para o fluido de processo",
            "Verificar se a válvula possui fire safe design quando aplicável",
            "Confirmar se o atuador (manual ou automático) está de acordo com a especificação",
            "Verificar se as conexões de drenagem e ventilação estão presentes quando especificadas",
            "Confirmar se a marcação/TAG da válvula está clara e correta",
            "Verificar se há certificados de qualidade e rastreabilidade do material",
            "Confirmar se a válvula passou por inspeção dimensional",
            "Verificar se não há danos externos, riscos ou corrosão",
            "Confirmar se todas as conexões auxiliares estão protegidas adequadamente"
        ]
    },
    "3100": {
        "nome": "Turbine",
        "items": [
            "Verificar se o medidor está de acordo com a especificação técnica (diâmetro, classe de pressão)",
            "Confirmar se o tipo de conexão está conforme especificado (flangeada, rosqueada)",
            "Verificar se o medidor possui certificado de calibração válido",
            "Confirmar se o material do corpo está de acordo com a especificação",
            "Verificar se o rotor e lâminas estão em perfeitas condições, sem danos ou deformações",
            "Confirmar se os mancais estão adequados e lubrificados conforme especificação",
            "Verificar se o sensor de rotação (pickup) está funcionando corretamente",
            "Confirmar se a eletrônica associada está presente e funcional",
            "Verificar se há retificadores de fluxo quando especificados",
            "Confirmar se as conexões de processo estão limpas e sem obstruções",
            "Verificar se há certificados de teste de desempenho e repetibilidade",
            "Confirmar se a faixa de medição está adequada para a aplicação",
            "Verificar se não há vibração excessiva ou ruídos anômalos",
            "Confirmar se a instalação permite acesso para manutenção",
            "Verificar se há proteção contra sobre-rotação quando aplicável"
        ]
    },
    "6600": {
        "nome": "Transmitters & TW",
        "items": [
            "Verificar se o transmissor está de acordo com a especificação técnica",
            "Confirmar se a faixa de medição (range) está conforme especificado",
            "Verificar se o sinal de saída (4-20mA, HART, Fieldbus) está correto",
            "Confirmar se a alimentação elétrica está de acordo (24VDC, 110VAC, etc.)",
            "Verificar se há certificado de calibração válido e rastreável",
            "Confirmar se a classificação de área (Ex) está adequada para instalação",
            "Verificar se o material do corpo é adequado para o ambiente de instalação",
            "Confirmar se as conexões de processo estão conforme especificação",
            "Verificar se há proteção contra sobrepressão quando aplicável",
            "Confirmar se o display local está funcionando corretamente (quando aplicável)",
            "Verificar se a configuração via software está correta",
            "Confirmar se há proteção IP adequada para ambiente de instalação",
            "Verificar se as conexões elétricas estão adequadamente seladas",
            "Confirmar se há documentação técnica completa (manual, certificados)",
            "Verificar se não há danos externos no invólucro ou conexões",
            "Confirmar se os acessórios (manifold, válvulas) estão presentes quando especificados"
        ]
    }
}

FAMILIAS = {
    "1500": "Big Ball Valves",
    "3100": "Turbine", 
    "6600": "Transmitters & TW"
}

def main():
    st.title("🔧 Sistema de Checklist ODS")
    st.markdown("**Equipamentos de Óleo e Gás**")
    
    # Menu principal
    menu = st.sidebar.selectbox(
        "Menu Principal",
        ["🏠 Home", "📋 Executar Checklist", "📊 Consultar Registros", "📑 Relatórios"]
    )
    
    if menu == "🏠 Home":
        show_home()
    elif menu == "📋 Executar Checklist":
        show_checklist_execution()
    elif menu == "📊 Consultar Registros":
        show_records()
    elif menu == "📑 Relatórios":
        show_reports()

def show_home():
    st.header("Bem-vindo ao Sistema de Checklist ODS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Projetos Cadastrados", len(st.session_state.projetos))
    
    with col2:
        st.metric("Equipamentos Registrados", len(st.session_state.equipamentos))
    
    with col3:
        st.metric("Checklists Executados", len(st.session_state.checklists))
    
    st.subheader("Famílias de Equipamentos (MVP)")
    for codigo, nome in FAMILIAS.items():
        st.write(f"**{codigo}** - {nome}")
    
    st.subheader("Como usar o sistema:")
    st.write("1. 📋 **Executar Checklist**: Inicie um novo checklist para um equipamento")
    st.write("2. 📊 **Consultar Registros**: Visualize equipamentos e checklists cadastrados")
    st.write("3. 📑 **Relatórios**: Gere relatórios detalhados dos checklists")

def show_checklist_execution():
    st.header("📋 Executar Checklist")
    
    # Etapa 1: Projeto
    st.subheader("1. Informações do Projeto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        projeto_numero = st.text_input("Número do Projeto", placeholder="Ex: P-2024-001")
    
    with col2:
        projeto_existente = projeto_numero in st.session_state.projetos if projeto_numero else False
        if projeto_existente:
            st.success(f"✅ Projeto {projeto_numero} encontrado")
            projeto_nome = st.session_state.projetos[projeto_numero]["nome"]
            cliente = st.session_state.projetos[projeto_numero]["cliente"]
            st.write(f"**Nome:** {projeto_nome}")
            st.write(f"**Cliente:** {cliente}")
        else:
            if projeto_numero:
                st.warning("⚠️ Projeto não encontrado")
                if st.button("➕ Criar Novo Projeto"):
                    st.session_state.criar_projeto = True
    
    # Criar novo projeto
    if projeto_numero and not projeto_existente and st.session_state.get('criar_projeto', False):
        st.subheader("Criar Novo Projeto")
        with st.form("novo_projeto"):
            projeto_nome = st.text_input("Nome do Projeto")
            cliente = st.text_input("Cliente")
            
            if st.form_submit_button("Criar Projeto"):
                if projeto_nome and cliente:
                    st.session_state.projetos[projeto_numero] = {
                        "nome": projeto_nome,
                        "cliente": cliente,
                        "data_criacao": datetime.now()
                    }
                    st.success("Projeto criado com sucesso!")
                    st.session_state.criar_projeto = False
                    st.rerun()
                else:
                    st.error("Preencha todos os campos")
    
    # Etapa 2: Equipamento (só se projeto existir)
    if projeto_numero and projeto_numero in st.session_state.projetos:
        st.subheader("2. Informações do Equipamento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            familia = st.selectbox("Família do Equipamento", 
                                 options=list(FAMILIAS.keys()),
                                 format_func=lambda x: f"{x} - {FAMILIAS[x]}")
        
        with col2:
            tag_equipamento = st.text_input("TAG do Equipamento", placeholder="Ex: FIT-1212001A")
        
        # Verificar se TAG já existe
        if tag_equipamento and projeto_numero:
            chave_equipamento = f"{projeto_numero}_{tag_equipamento}"
            tag_existente = chave_equipamento in st.session_state.equipamentos
            
            if tag_existente:
                equipamento = st.session_state.equipamentos[chave_equipamento]
                if equipamento.get("checklist_executado", False):
                    st.error("❌ TAG já existe e checklist já foi executado")
                    return
                else:
                    st.warning("⚠️ TAG existe mas checklist não foi executado. Continuar?")
            
            # Etapa 3: Executar Checklist
            if st.button("🚀 Iniciar Checklist") or tag_existente:
                execute_checklist(projeto_numero, tag_equipamento, familia)

def execute_checklist(projeto_numero, tag_equipamento, familia):
    st.subheader(f"3. Checklist - {FAMILIAS[familia]}")
    st.write(f"**Projeto:** {projeto_numero}")
    st.write(f"**TAG:** {tag_equipamento}")
    
    template = TEMPLATES_CHECKLIST[familia]
    chave_equipamento = f"{projeto_numero}_{tag_equipamento}"
    
    # Inicializar dados do checklist
    if f"checklist_{chave_equipamento}" not in st.session_state:
        st.session_state[f"checklist_{chave_equipamento}"] = {
            "respostas": {},
            "planos_acao": {},
            "fotos": {}
        }
    
    checklist_data = st.session_state[f"checklist_{chave_equipamento}"]
    
    with st.form(f"checklist_form_{chave_equipamento}"):
        st.write("**Responda cada item do checklist:**")
        
        for i, item in enumerate(template["items"]):
            st.write(f"**{i+1}.** {item}")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                resposta = st.radio(
                    f"Resposta {i+1}",
                    ["Conforme", "Não Conforme"],
                    key=f"resposta_{i}_{chave_equipamento}",
                    horizontal=True
                )
                checklist_data["respostas"][i] = resposta
            
            with col2:
                foto = st.file_uploader(
                    f"Foto {i+1} (opcional)",
                    type=['jpg', 'jpeg', 'png'],
                    key=f"foto_{i}_{chave_equipamento}"
                )
                if foto:
                    checklist_data["fotos"][i] = foto
            
            # Plano de ação para não conformidades
            if resposta == "Não Conforme":
                plano_acao = st.text_area(
                    f"Plano de Ação para item {i+1}",
                    key=f"plano_{i}_{chave_equipamento}",
                    placeholder="Descreva as ações necessárias para corrigir a não conformidade..."
                )
                checklist_data["planos_acao"][i] = plano_acao
            
            st.divider()
        
        # Finalizar checklist
        if st.form_submit_button("✅ Finalizar Checklist"):
            finalize_checklist(projeto_numero, tag_equipamento, familia, checklist_data)

def finalize_checklist(projeto_numero, tag_equipamento, familia, checklist_data):
    chave_equipamento = f"{projeto_numero}_{tag_equipamento}"
    
    # Calcular estatísticas
    total_items = len(TEMPLATES_CHECKLIST[familia]["items"])
    conformes = sum(1 for resp in checklist_data["respostas"].values() if resp == "Conforme")
    nao_conformes = total_items - conformes
    percentual_conformidade = (conformes / total_items) * 100
    
    # Salvar equipamento
    st.session_state.equipamentos[chave_equipamento] = {
        "projeto": projeto_numero,
        "tag": tag_equipamento,
        "familia": familia,
        "nome_familia": FAMILIAS[familia],
        "data_cadastro": datetime.now(),
        "checklist_executado": True
    }
    
    # Salvar checklist
    checklist_id = str(uuid.uuid4())
    st.session_state.checklists[checklist_id] = {
        "id": checklist_id,
        "equipamento_key": chave_equipamento,
        "projeto": projeto_numero,
        "tag": tag_equipamento,
        "familia": familia,
        "data_execucao": datetime.now(),
        "total_items": total_items,
        "conformes": conformes,
        "nao_conformes": nao_conformes,
        "percentual_conformidade": percentual_conformidade,
        "respostas": checklist_data["respostas"],
        "planos_acao": checklist_data["planos_acao"],
        "fotos": checklist_data["fotos"]
    }
    
    # Limpar dados temporários
    if f"checklist_{chave_equipamento}" in st.session_state:
        del st.session_state[f"checklist_{chave_equipamento}"]
    
    st.success("✅ Checklist finalizado com sucesso!")
    
    # Mostrar resumo
    st.subheader("📊 Resumo do Checklist")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Itens", total_items)
    with col2:
        st.metric("Conformes", conformes)
    with col3:
        st.metric("Não Conformes", nao_conformes)
    
    st.metric("Percentual de Conformidade", f"{percentual_conformidade:.1f}%")
    
    if nao_conformes > 0:
        st.warning(f"⚠️ {nao_conformes} não conformidade(s) identificada(s)")

def show_records():
    st.header("📊 Consultar Registros")
    
    tab1, tab2, tab3 = st.tabs(["Projetos", "Equipamentos", "Checklists"])
    
    with tab1:
        st.subheader("Projetos Cadastrados")
        if st.session_state.projetos:
            projetos_df = pd.DataFrame([
                {
                    "Número": num,
                    "Nome": dados["nome"],
                    "Cliente": dados["cliente"],
                    "Data Criação": dados["data_criacao"].strftime("%d/%m/%Y %H:%M")
                }
                for num, dados in st.session_state.projetos.items()
            ])
            st.dataframe(projetos_df, use_container_width=True)
        else:
            st.info("Nenhum projeto cadastrado")
    
    with tab2:
        st.subheader("Equipamentos Registrados")
        if st.session_state.equipamentos:
            equipamentos_df = pd.DataFrame([
                {
                    "Projeto": dados["projeto"],
                    "TAG": dados["tag"],
                    "Família": f"{dados['familia']} - {dados['nome_familia']}",
                    "Data Cadastro": dados["data_cadastro"].strftime("%d/%m/%Y %H:%M"),
                    "Checklist": "✅" if dados["checklist_executado"] else "❌"
                }
                for dados in st.session_state.equipamentos.values()
            ])
            st.dataframe(equipamentos_df, use_container_width=True)
        else:
            st.info("Nenhum equipamento registrado")
    
    with tab3:
        st.subheader("Checklists Executados")
        if st.session_state.checklists:
            checklists_df = pd.DataFrame([
                {
                    "Projeto": dados["projeto"],
                    "TAG": dados["tag"],
                    "Família": f"{dados['familia']} - {FAMILIAS[dados['familia']]}",
                    "Data Execução": dados["data_execucao"].strftime("%d/%m/%Y %H:%M"),
                    "Conformidade": f"{dados['percentual_conformidade']:.1f}%",
                    "Não Conformes": dados["nao_conformes"]
                }
                for dados in st.session_state.checklists.values()
            ])
            st.dataframe(checklists_df, use_container_width=True)
        else:
            st.info("Nenhum checklist executado")

def show_reports():
    st.header("📑 Relatórios")
    
    if not st.session_state.checklists:
        st.info("Nenhum checklist disponível para relatório")
        return
    
    # Seletor de checklist
    checklist_options = {
        dados["id"]: f"{dados['projeto']} - {dados['tag']} ({dados['data_execucao'].strftime('%d/%m/%Y')})"
        for dados in st.session_state.checklists.values()
    }
    
    selected_checklist = st.selectbox(
        "Selecione um checklist para gerar relatório:",
        options=list(checklist_options.keys()),
        format_func=lambda x: checklist_options[x]
    )
    
    if selected_checklist:
        generate_report(selected_checklist)

def generate_report(checklist_id):
    checklist = st.session_state.checklists[checklist_id]
    projeto = st.session_state.projetos[checklist["projeto"]]
    
    st.subheader("📋 Relatório de Checklist")
    
    # Cabeçalho do relatório
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Informações do Projeto:**")
        st.write(f"• Número: {checklist['projeto']}")
        st.write(f"• Nome: {projeto['nome']}")
        st.write(f"• Cliente: {projeto['cliente']}")
    
    with col2:
        st.write("**Informações do Equipamento:**")
        st.write(f"• TAG: {checklist['tag']}")
        st.write(f"• Família: {checklist['familia']} - {FAMILIAS[checklist['familia']]}")
        st.write(f"• Data Execução: {checklist['data_execucao'].strftime('%d/%m/%Y %H:%M')}")
    
    # Estatísticas
    st.subheader("📊 Resultados do Checklist")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Itens", checklist["total_items"])
    with col2:
        st.metric("Conformes", checklist["conformes"])
    with col3:
        st.metric("Não Conformes", checklist["nao_conformes"])
    with col4:
        st.metric("Conformidade", f"{checklist['percentual_conformidade']:.1f}%")
    
    # Detalhamento dos itens
    st.subheader("📝 Detalhamento dos Itens")
    template = TEMPLATES_CHECKLIST[checklist["familia"]]
    
    for i, item in enumerate(template["items"]):
        resposta = checklist["respostas"].get(i, "Não respondido")
        
        if resposta == "Conforme":
            st.success(f"✅ **Item {i+1}:** {item}")
        elif resposta == "Não Conforme":
            st.error(f"❌ **Item {i+1}:** {item}")
            if i in checklist["planos_acao"] and checklist["planos_acao"][i]:
                st.write(f"**Plano de Ação:** {checklist['planos_acao'][i]}")
        else:
            st.warning(f"⚠️ **Item {i+1}:** {item} - {resposta}")
    
    # Planos de ação consolidados
    if checklist["nao_conformes"] > 0:
        st.subheader("🔧 Planos de Ação")
        for i, plano in checklist["planos_acao"].items():
            if plano:
                st.write(f"**Item {i+1}:** {plano}")

if __name__ == "__main__":
    main()