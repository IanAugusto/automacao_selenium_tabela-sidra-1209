# 🤖 Automação RPA - Tabela SIDRA 1209

## 📋 Descrição

Script Python automatizado para extração de dados da **Tabela 1209** do IBGE/SIDRA (Sistema IBGE de Recuperação Automática). O script realiza a busca, configuração de filtros e download automático de dados sobre população por grupos de idade.

### O que o script faz:

1. **Acessa o site SIDRA** (https://sidra.ibge.gov.br/)
2. **Busca a Tabela 1209** através do campo de pesquisa
3. **Configura os filtros automaticamente:**
   - **Grupo de Idade:** 60 anos ou mais
   - **Recorte Territorial:** Unidades da Federação (UF)
   - **Ano:** Ano mais recente disponível
4. **Realiza o download** do arquivo CSV com os dados filtrados
5. **Salva o arquivo** na pasta configurada

---

## 📦 Requisitos

### Software Necessário

- **Python 3.8 ou superior**
- **Brave Browser** ou **Google Chrome** instalado
- **ChromeDriver** (geralmente gerenciado automaticamente pelo Selenium)

### Dependências Python

- `selenium==4.16.0`

---

## 🚀 Instalação

### 1. Clone ou baixe o repositório

```bash
git clone <url-do-repositorio>
cd entrevista
```

### 2. Crie um ambiente virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Verifique a instalação do ChromeDriver

O Selenium geralmente gerencia o ChromeDriver automaticamente. Se encontrar problemas, você pode:

- **Opção 1:** Deixar o Selenium baixar automaticamente (recomendado)
- **Opção 2:** Baixar manualmente do [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads) e definir a variável de ambiente `CHROMEDRIVER_PATH`

---

## ⚙️ Configuração

### Variáveis de Ambiente (Opcional)

Você pode personalizar o comportamento do script através de variáveis de ambiente:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `BRAVE_BINARY` | Caminho para o executável do Brave | `C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe` |
| `CHROMEDRIVER_PATH` | Caminho para o ChromeDriver | Gerenciado automaticamente |
| `SIDRA_DOWNLOAD_DIR` | Pasta onde os arquivos serão salvos | `./dados` |

**Exemplo (Windows PowerShell):**
```powershell
$env:SIDRA_DOWNLOAD_DIR = "C:\MeusDownloads\IBGE"
python desafio_ibge_1209.py
```

**Exemplo (Linux/Mac):**
```bash
export SIDRA_DOWNLOAD_DIR="/home/usuario/downloads/ibge"
python desafio_ibge_1209.py
```

---

## ▶️ Como Executar

### Execução Básica

```bash
python desafio_ibge_1209.py
```

### O que acontece durante a execução:

1. O navegador (Brave/Chrome) será aberto automaticamente
2. O script navegará para o site SIDRA
3. Realizará a busca pela Tabela 1209
4. Configurará os filtros necessários
5. Baixará o arquivo CSV
6. Aguardará você pressionar Enter para fechar o navegador

### ⚠️ Importante

- **Não feche o navegador manualmente** durante a execução
- O script aguardará você pressionar Enter antes de fechar o navegador (para verificação visual)
- O processo leva aproximadamente **1-2 minutos** dependendo da velocidade da internet

---

## 📊 Resultado

### Localização do Arquivo

O arquivo CSV será salvo em:
```
dados/populacao_60mais_1209.csv
```

Ou na pasta definida pela variável de ambiente `SIDRA_DOWNLOAD_DIR`.

### Estrutura dos Dados

O arquivo CSV contém dados sobre:
- **População com 60 anos ou mais**
- **Por Unidade da Federação (UF)**
- **Ano mais recente disponível**

---

## 🏗️ Estrutura do Projeto

```
entrevista/
│
├── desafio_ibge_1209.py    # Script principal de automação
├── requirements.txt         # Dependências Python
├── README.md               # Este arquivo
└── dados/                  # Pasta de downloads (criada automaticamente)
    └── populacao_60mais_1209.csv
```

---

## 🔧 Funcionalidades Técnicas

### Principais Funções

- `iniciar_driver()` - Inicializa o driver Selenium com configurações otimizadas
- `buscar_tabela_1209()` - Realiza a busca e navegação até a tabela
- `aplicar_filtros_tabela()` - Configura todos os filtros necessários
- `baixar_csv()` - Realiza o download do arquivo CSV
- `acessar_tabela_1209()` - Função principal que orquestra todo o processo

### Recursos Implementados

- ✅ **Esperas explícitas** (WebDriverWait) para garantir estabilidade
- ✅ **Tratamento de erros** robusto
- ✅ **Configurações anti-detecção** para evitar bloqueios
- ✅ **Download automático** sem prompts
- ✅ **Logs informativos** durante a execução
- ✅ **Suporte a Brave e Chrome**

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+** - Linguagem de programação
- **Selenium WebDriver 4.16.0** - Automação de navegador
- **Brave Browser / Google Chrome** - Navegador para automação
- **ChromeDriver** - Driver para controle do navegador

---

## 🐛 Troubleshooting

### Problema: "ChromeDriver não encontrado"

**Solução:**
- O Selenium 4+ gerencia o ChromeDriver automaticamente
- Se persistir, baixe manualmente e defina `CHROMEDRIVER_PATH`

### Problema: "Brave não encontrado no caminho padrão"

**Solução:**
- Defina a variável de ambiente `BRAVE_BINARY` com o caminho correto
- Ou altere o código para usar Chrome padrão

### Problema: "Timeout ao encontrar elemento"

**Solução:**
- Verifique sua conexão com a internet
- O site SIDRA pode estar lento ou temporariamente indisponível
- Tente executar novamente

### Problema: "Arquivo CSV não foi baixado"

**Solução:**
- Verifique se a pasta de download existe e tem permissões de escrita
- Verifique se o download foi concluído antes de fechar o navegador
- Verifique a pasta definida em `SIDRA_DOWNLOAD_DIR`

### Problema: "Elemento não clicável"

**Solução:**
- O script usa scroll automático, mas se persistir, pode ser necessário ajustar os seletores
- Verifique se a estrutura HTML do site SIDRA mudou

---

## 📝 Notas Adicionais

- O script foi desenvolvido para funcionar com a estrutura atual do site SIDRA
- Se o site sofrer atualizações significativas, pode ser necessário ajustar os seletores XPath/CSS
- O script mantém o navegador aberto até você pressionar Enter para facilitar a verificação visual
- Todos os tempos de espera são configuráveis no código

---

## 📄 Licença

Este projeto foi desenvolvido para fins de automação e extração de dados públicos do IBGE.

---

## 👤 Autor

Desenvolvido para automação de extração de dados do IBGE/SIDRA.

---

## 🔗 Links Úteis

- [Site SIDRA - IBGE](https://sidra.ibge.gov.br/)
- [Documentação Selenium](https://www.selenium.dev/documentation/)
- [Tabela 1209 - População por grupos de idade](https://sidra.ibge.gov.br/tabela/1209)
