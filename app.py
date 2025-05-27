import streamlit as st
import database
import utils
import os
import pandas as pd
from datetime import datetime
from fpdf import FPDF # Para geração de PDF

if 'checklist_started' not in st.session_state:
    st.session_state.checklist_started = False
if 'current_checklist_id' not in st.session_state:
    st.session_state.current_checklist_id = None
if 'current_equipment_tag' not in st.session_state:
    st.session_state.current_equipment_tag = None
if 'current_package' not in st.session_state:
    st.session_state.current_package = None


# Inicializa o banco de dados
database.create_tables()

# Configurações da página
st.set_page_config(layout="wide", page_title="Checklist de Equipamentos")

# Função para gerar o PDF do relatório
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Relatório de Checklist de Equipamentos', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln()

def generate_pdf_report(checklist_data):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 10)

    if not checklist_data:
        pdf.chapter_body("Nenhum dado de checklist encontrado para gerar o relatório.")
        return pdf.output(dest='S').encode('latin-1')

    # Informações do Projeto e Equipamento (pegando do primeiro item, pois são os mesmos para o checklist)
    projeto_numero = checklist_data[0]['numero_projeto']
    projeto_nome = checklist_data[0]['nome_projeto']
    equipamento_tag = checklist_data[0]['equipamento_tag']
    data_criacao = checklist_data[0]['data_criacao']

    pdf.chapter_title("Informações do Projeto e Equipamento:")
    pdf.chapter_body(f"Número do Projeto: {projeto_numero}\nNome do Projeto: {projeto_nome}\nTAG do Equipamento: {equipamento_tag}\nData do Checklist: {data_criacao}")
    pdf.ln(5)

    pdf.chapter_title("Itens do Checklist:")
    for item in checklist_data:
        pdf.chapter_body(f"Pergunta: {item['pergunta']}")
        pdf.chapter_body(f"Resposta: {item['resposta'] if item['resposta'] else 'Não respondido'}")
        if item['foto']:
            pdf.chapter_body(f"Foto: {item['foto']}") # Em um cenário real, você precisaria incorporar a imagem
        if item['plano_acao_descricao']:
            pdf.chapter_body(f"Plano de Ação: {item['plano_acao_descricao']}")
        pdf.ln(2)

    return pdf.output(dest='S').encode('latin-1') # Retorna o PDF como bytes

# Sidebar para navegação
st.sidebar.title("Menu")
menu_selection = st.sidebar.radio(
    "Navegação",
    ("Home", "Criar Checklist", "Registros", "Relatórios")
)

# --- Página Home (Dashboard) ---
if menu_selection == "Home":
    st.title("Dashboard de Checklists")

    st.header("Checklists Abertos por Projeto")
    abertos_data = database.get_checklists_abertos_por_projeto()
    df_abertos = pd.DataFrame(abertos_data, columns=["Projeto", "Quantidade"])
    st.bar_chart(df_abertos.set_index("Projeto"))

    st.header("Checklists Concluídos por Projeto")
    concluidos_data = database.get_checklists_concluidos_por_projeto()
    df_concluidos = pd.DataFrame(concluidos_data, columns=["Projeto", "Quantidade"])
    st.bar_chart(df_concluidos.set_index("Projeto"))

    st.header("Planos de Ação por Projeto")
    planos_acao_data = database.get_planos_acao_por_projeto()
    df_planos_acao = pd.DataFrame(planos_acao_data, columns=["Projeto", "Quantidade"])
    st.bar_chart(df_planos_acao.set_index("Projeto"))

# --- Página Criar Checklist ---
elif menu_selection == "Criar Checklist":
    st.title("Criar Novo Checklist")

    st.header("Informações do Projeto")
    numero_projeto = st.text_input("Número do Projeto:")
    projeto_selecionado = None

    if numero_projeto:
        projeto_selecionado = database.get_projeto_por_numero(numero_projeto)
        if projeto_selecionado:
            st.success(f"Projeto encontrado: {projeto_selecionado.nome_projeto} - Cliente: {projeto_selecionado.cliente}")
            st.session_state.current_project_id = projeto_selecionado.id
        else:
            st.warning("Projeto não encontrado. Deseja criar um novo projeto?")
            with st.expander("Criar Novo Projeto"):
                novo_nome_projeto = st.text_input("Nome do Novo Projeto:")
                novo_cliente_projeto = st.text_input("Cliente do Novo Projeto:")
                if st.button("Criar Projeto"):
                    if database.criar_projeto(numero_projeto, novo_nome_projeto, novo_cliente_projeto):
                        st.success(f"Projeto '{novo_nome_projeto}' criado com sucesso!")
                        projeto_selecionado = database.get_projeto_por_numero(numero_projeto)
                        st.session_state.current_project_id = projeto_selecionado.id
                    else:
                        st.error("Erro ao criar projeto. O número do projeto pode já existir.")

    if projeto_selecionado:
        st.header("Informações do Equipamento")
        package_options = list(utils.get_checklist_template("").keys()) # Pega todas as chaves de templates
        selected_package = st.selectbox("Família (Package) do Equipamento:", package_options)
        tag_equipamento = st.text_input("TAG do Equipamento (Ex: FIT-1212001A):")

        if tag_equipamento:
            equipamento_existente = database.get_equipamento_por_tag_projeto(projeto_selecionado.id, tag_equipamento)
            if equipamento_existente:
                st.warning(f"O TAG '{tag_equipamento}' já existe para este projeto. Não é possível iniciar um novo checklist para este TAG.")
                # Opcional: Permitir continuar se o checklist não foi rodado
                # if not database.get_checklist_completo(equipamento_existente.id):
                #     st.info("No entanto, nenhum checklist foi iniciado para este equipamento. Você pode continuar.")
                #     if st.button("Continuar Checklist Existente"):
                #         # Lógica para carregar checklist existente
                #         pass
            else:
                if st.button("Iniciar Checklist"):
                    # Cria o equipamento e o checklist
                    if database.criar_equipamento(projeto_selecionado.id, tag_equipamento, selected_package):
                        equipamento_novo = database.get_equipamento_por_tag_projeto(projeto_selecionado.id, tag_equipamento)
                        checklist_id = database.criar_checklist(equipamento_novo.id)
                        st.session_state.current_checklist_id = checklist_id
                        st.session_state.current_equipment_tag = tag_equipamento
                        st.session_state.current_package = selected_package
                        st.session_state.checklist_started = True
                        st.success(f"Checklist iniciado para o TAG: {tag_equipamento} ({selected_package})")
                        st.experimental_rerun() # Reinicia para mostrar a seção do checklist
                    else:
                        st.error("Erro ao criar equipamento. Verifique se o TAG já existe para este projeto.")

    if st.session_state.get('checklist_started', False) and st.session_state.get('current_checklist_id'):
        st.header(f"Realizar Checklist para {st.session_state.current_equipment_tag} ({st.session_state.current_package})")
        checklist_template = utils.get_checklist_template(st.session_state.current_package)

        st.write("Responda 'S' (Conforme), 'NA' (Não Aplicável) ou 'N' (Não Conforme).")

        # Usar um formulário para submeter todas as respostas de uma vez
        with st.form("checklist_form"):
            for i, pergunta in enumerate(checklist_template):
                st.subheader(f"Item {i+1}: {pergunta}")
                col1, col2 = st.columns([1, 3])
                with col1:
                    resposta = st.radio(
                        "Resposta:",
                        ('S', 'NA', 'N'),
                        key=f"resposta_{i}"
                    )
                with col2:
                    foto = st.file_uploader(
                        "Anexar Foto (Opcional):",
                        type=["png", "jpg", "jpeg"],
                        key=f"foto_{i}"
                    )
                if resposta == 'N':
                    plano_acao = st.text_area(
                        "Plano de Ação para Não Conformidade:",
                        key=f"plano_acao_{i}"
                    )
                    st.session_state[f'plano_acao_required_{i}'] = True
                else:
                    st.session_state[f'plano_acao_required_{i}'] = False

                st.session_state[f'pergunta_{i}'] = pergunta
                st.session_state[f'resposta_temp_{i}'] = resposta
                st.session_state[f'foto_temp_{i}'] = foto.name if foto else None # Apenas o nome do arquivo

            submitted = st.form_submit_button("Finalizar Checklist")

            if submitted:
                all_items_saved = True
                for i, pergunta in enumerate(checklist_template):
                    resposta = st.session_state[f'resposta_temp_{i}']
                    foto_name = st.session_state[f'foto_temp_{i}']
                    plano_acao_required = st.session_state[f'plano_acao_required_{i}']
                    plano_acao = st.session_state.get(f'plano_acao_{i}', '')

                    # Salva o item do checklist
                    database.adicionar_item_checklist(
                        st.session_state.current_checklist_id,
                        pergunta
                    )
                    # Recupera o ID do item recém-adicionado para atualizar
                    # Isso é um pouco complicado com SQLite e Streamlit sem um ORM.
                    # Uma abordagem mais robusta seria adicionar o item com a resposta já,
                    # ou ter uma função que retorna o ID do último item inserido para o checklist
                    # Por simplicidade, vamos assumir que a ordem de inserção é a mesma da iteração.
                    # Em um sistema real, você buscaria o item pelo checklist_id e pergunta.
                    # Para este exemplo, vamos simplificar:
                    # A função adicionar_item_checklist não retorna o ID, então vamos ter que buscar.
                    # Para fins de demonstração, vamos simular a atualização.
                    # Em um ambiente real, você faria um INSERT com todos os dados de uma vez
                    # ou uma busca mais precisa para o item_id.

                    # Para o propósito desta demonstração, vamos simular a atualização
                    # ao invés de buscar o item_id recém-criado, que seria mais complexo
                    # sem um ORM ou um retorno direto da função de inserção.
                    # A melhor abordagem seria modificar `adicionar_item_checklist`
                    # para retornar o `cursor.lastrowid` e então usar esse ID para o plano de ação.
                    # Por enquanto, vamos usar uma simulação:
                    # Supondo que o item_id é o último adicionado.
                    # Isso é um ponto fraco que precisaria ser melhorado em produção.

                    # Para fins de demonstração, vamos buscar o último item adicionado para este checklist
                    # (isso não é ideal para concorrência, mas funciona para um app simples)
                    conn = database.sqlite3.connect(database.DATABASE_NAME)
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM itens_checklist WHERE checklist_id=? AND pergunta=? ORDER BY id DESC LIMIT 1",
                                   (st.session_state.current_checklist_id, pergunta))
                    item_id_for_update = cursor.fetchone()[0]
                    conn.close()

                    database.atualizar_item_checklist(
                        item_id_for_update,
                        resposta,
                        foto_name
                    )

                    if resposta == 'N' and plano_acao_required and plano_acao:
                        database.criar_plano_acao(item_id_for_update, plano_acao)
                    elif resposta == 'N' and plano_acao_required and not plano_acao:
                        st.error(f"O item '{pergunta}' foi marcado como 'Não Conforme', mas o plano de ação está vazio.")
                        all_items_saved = False
                        break # Para o loop se um plano de ação obrigatório estiver faltando

                if all_items_saved:
                    st.success("Checklist finalizado e salvo com sucesso!")
                    # Limpa o estado da sessão para um novo checklist
                    del st.session_state.checklist_started
                    del st.session_state.current_checklist_id
                    del st.session_state.current_equipment_tag
                    del st.session_state.current_package
                    st.experimental_rerun() # Reinicia para limpar o formulário
                else:
                    st.warning("Por favor, preencha todos os planos de ação para itens 'Não Conforme'.")


# --- Página Registros ---
elif menu_selection == "Registros":
    st.title("Registros de Projetos e Equipamentos")

    st.header("Projetos Registrados")
    conn = database.sqlite3.connect(database.DATABASE_NAME)
    conn.row_factory = database.sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projetos")
    projetos_raw = cursor.fetchall()
    conn.close()

    if projetos_raw:
        df_projetos = pd.DataFrame([dict(row) for row in projetos_raw])
        st.dataframe(df_projetos)
    else:
        st.info("Nenhum projeto registrado ainda.")

    st.header("Equipamentos Registrados")
    conn = database.sqlite3.connect(database.DATABASE_NAME)
    conn.row_factory = database.sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id, p.numero_projeto, p.nome_projeto, e.tag, e.package
        FROM equipamentos e
        JOIN projetos p ON e.projeto_id = p.id
    ''')
    equipamentos_raw = cursor.fetchall()
    conn.close()

    if equipamentos_raw:
        df_equipamentos = pd.DataFrame([dict(row) for row in equipamentos_raw])
        st.dataframe(df_equipamentos)
    else:
        st.info("Nenhum equipamento registrado ainda.")

# --- Página Relatórios ---
elif menu_selection == "Relatórios":
    st.title("Geração de Relatórios de Checklist")

    conn = database.sqlite3.connect(database.DATABASE_NAME)
    conn.row_factory = database.sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.id, p.numero_projeto, p.nome_projeto, e.tag, c.data_criacao
        FROM checklists c
        JOIN equipamentos e ON c.equipamento_id = e.id
        JOIN projetos p ON e.projeto_id = p.id
        ORDER BY c.data_criacao DESC
    ''')
    all_checklists = cursor.fetchall()
    conn.close()

    if all_checklists:
        checklist_options = {f"Projeto: {row['numero_projeto']} - TAG: {row['tag']} - Data: {row['data_criacao']}": row['id'] for row in all_checklists}
        selected_checklist_display = st.selectbox("Selecione um Checklist para Gerar Relatório:", list(checklist_options.keys()))

        if selected_checklist_display:
            selected_checklist_id = checklist_options[selected_checklist_display]
            checklist_data = database.get_checklist_completo(selected_checklist_id)

            if checklist_data:
                st.subheader(f"Detalhes do Checklist para {checklist_data[0]['equipamento_tag']} (Projeto {checklist_data[0]['numero_projeto']})")
                for item in checklist_data:
                    st.write(f"**Pergunta:** {item['pergunta']}")
                    st.write(f"**Resposta:** {item['resposta'] if item['resposta'] else 'Não respondido'}")
                    if item['foto']:
                        st.write(f"**Foto Anexada:** {item['foto']}") # Em um cenário real, você precisaria exibir a imagem
                    if item['plano_acao_descricao']:
                        st.write(f"**Plano de Ação:** {item['plano_acao_descricao']}")
                    st.markdown("---")

                # Botão para gerar PDF
                pdf_output = generate_pdf_report(checklist_data)
                st.download_button(
                    label="Baixar Relatório em PDF",
                    data=pdf_output,
                    file_name=f"relatorio_checklist_{checklist_data[0]['numero_projeto']}_{checklist_data[0]['equipamento_tag']}.pdf",
                    mime="application/pdf"
                )
            else:
                st.info("Nenhum detalhe encontrado para o checklist selecionado.")
    else:
        st.info("Nenhum checklist realizado ainda para gerar relatórios.")
