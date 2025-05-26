# 🔧 Sistema de Checklist ODS

Sistema de execução e registro de checklists para equipamentos de óleo e gás.

## 📋 Sobre o Projeto

Este sistema foi desenvolvido para a ODS, permitindo o controle de qualidade de equipamentos utilizados em sistemas de medição de vazão de óleo e gás através de checklists padronizados.

### Funcionalidades Principais

- ✅ **Gestão de Projetos**: Cadastro e controle de projetos por cliente
- 🏷️ **Registro de Equipamentos**: TAGs únicos por projeto com classificação por família
- 📝 **Checklists Especializados**: Templates específicos para cada tipo de equipamento
- 📊 **Relatórios Detalhados**: Análise de conformidade e planos de ação
- 📸 **Upload de Fotos**: Documentação visual opcional para cada item
- 🔍 **Consultas Avançadas**: Histórico completo de equipamentos e checklists

### Famílias de Equipamentos (MVP)

- **1500 - Big Ball Valves**: Válvulas esfera de grande porte
- **3100 - Turbine**: Medidores tipo turbina
- **6600 - Transmitters & TW**: Transmissores e instrumentação

## 🚀 Como Executar

### Opção 1: Local (Recomendado para desenvolvimento)

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/checklist-ods.git
cd checklist-ods
```

2. **Crie um ambiente virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação:**
```bash
streamlit run app.py
```

5. **Acesse no navegador:**
```
http://localhost:8501
```

### Opção 2: GitHub Codespaces

1. **Acesse o repositório no GitHub**
2. **Clique em "Code" > "Create codespace on main"**
3. **Aguarde o ambiente carregar**
4. **No terminal do Codespace, execute:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Opção 3: Streamlit Community Cloud

1. **Faça fork do repositório**
2. **Acesse [share.streamlit.io](https://share.streamlit.io)**
3. **Conecte sua conta GitHub**
4. **Deploy o app selecionando o repositório**

## 📁 Estrutura do Projeto

```
checklist-ods/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências Python
├── README.md          # Este arquivo
└── .streamlit/
    └── config.toml    # Configurações do Streamlit
```

## 🔧 Configuração

### Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações opcionais
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### Configuração do Streamlit

O arquivo `.streamlit/config.toml` contém configurações específicas da aplicação.

## 📊 Como Usar o Sistema

### 1. Executar Checklist
- Informe o número e nome do projeto
- Selecione a família do equipamento
- Insira o TAG do equipamento
- Execute o checklist respondendo cada item
- Adicione fotos quando necessário
- Crie planos de ação para não conformidades

### 2. Consultar Registros
- Visualize projetos cadastrados
- Consulte equipamentos registrados
- Analise histórico de checklists

### 3. Gerar Relatórios
- Selecione um checklist executado
- Visualize relatório detalhado
- Analise estatísticas de conformidade

## 🔒 Armazenamento de Dados

**Importante**: Esta versão MVP armazena dados na sessão do usuário. Para uso em produção, considere implementar:

- Banco de dados PostgreSQL/MySQL
- Sistema de autenticação
- Backup automático
- Logs de auditoria

## 🛠️ Desenvolvimento

### Adicionando Novas Famílias

1. **Edite o dicionário `FAMILIAS`:**
```python
FAMILIAS = {
    "1500": "Big Ball Valves",
    "3100": "Turbine", 
    "6600": "Transmitters & TW",
    "1100": "Flow Conditioner",  # Nova família
}
```

2. **Adicione o template em `TEMPLATES_CHECKLIST`:**
```python
"1100": {
    "nome": "Flow Conditioner",
    "items": [
        "Item de verificação 1",
        "Item de verificação 2",
        # ...
    ]
}
```

### Personalizando Templates

Os templates são baseados em experiência prática com equipamentos de óleo e gás. Para customizar:

1. Edite o array `items` na família desejada
2. Adicione itens específicos da sua operação
3. Considere normas aplicáveis (API, ASME, etc.)

## 📝 Roadmap

- [ ] **Fase 2**: Expansão para todas as famílias (1100-7900)
- [ ] **Fase 3**: Banco de dados persistente
- [ ] **Fase 4**: Sistema de usuários e permissões
- [ ] **Fase 5**: Exportação PDF/Excel
- [ ] **Fase 6**: Dashboard executivo
- [ ] **Fase 7**: Integração com ERP

## 🤝 Contribuindo

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou sugestões:
- Abra uma issue no GitHub
- Entre em contato com a equipe de desenvolvimento

## 📄 Licença

Este projeto é propriedade da ODS - todos os direitos reservados.

---

**Desenvolvido com ❤️ para ODS**