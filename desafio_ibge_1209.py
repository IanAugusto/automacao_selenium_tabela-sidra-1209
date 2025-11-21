import os
import time
import sys
import platform
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime 



# Lista de possíveis caminhos (ordem de prioridade)
# ====== CONFIGURAÇÕES DE NAVEGADOR (MULTI-PLATAFORMA) ======

def detectar_navegador():
    """
    Detecta automaticamente o navegador instalado no sistema.
    Suporta: Windows, macOS, Linux
    """
    sistema = platform.system()
    
    caminhos_navegadores = {
        "Windows": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ],
        "Darwin": [  # macOS
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            os.path.expanduser("~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ],
        "Linux": [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/brave-browser",
            "/usr/bin/brave",
            "/snap/bin/chromium",
            "/usr/local/bin/chrome",
        ]
    }
    
    # Primeiro tenta variáveis de ambiente
    if os.environ.get("CHROME_BINARY"):
        caminho = os.environ.get("CHROME_BINARY")
        if os.path.exists(caminho):
            print(f"✅ Navegador configurado via CHROME_BINARY: {caminho}")
            return caminho
    
    if os.environ.get("BRAVE_BINARY"):
        caminho = os.environ.get("BRAVE_BINARY")
        if os.path.exists(caminho):
            print(f"✅ Navegador configurado via BRAVE_BINARY: {caminho}")
            return caminho
    
    # Detecta o sistema operacional
    if sistema not in caminhos_navegadores:
        raise OSError(f"❌ Sistema operacional não suportado: {sistema}")
    
    print(f"🔍 Detectando navegador no {sistema}...")
    
    # Procura pelos caminhos padrão
    for caminho in caminhos_navegadores[sistema]:
        if os.path.exists(caminho):
            print(f"✅ Navegador encontrado: {caminho}")
            return caminho
    
    # Linux: usa 'which' como fallback
    if sistema == "Linux":
        for comando in ["google-chrome", "chromium", "chromium-browser", "brave-browser"]:
            try:
                resultado = subprocess.run(["which", comando], capture_output=True, text=True, timeout=5)
                if resultado.returncode == 0:
                    caminho = resultado.stdout.strip()
                    if caminho and os.path.exists(caminho):
                        print(f"✅ Navegador encontrado via 'which': {caminho}")
                        return caminho
            except:
                pass
    
    # Erro se não encontrou
    raise FileNotFoundError(
        f"❌ Nenhum navegador compatível encontrado no {sistema}!\n\n"
        "Instale um dos seguintes:\n"
        "  • Google Chrome: https://www.google.com/chrome/\n"
        "  • Brave Browser: https://brave.com/\n"
        "  • Chromium: https://www.chromium.org/\n\n"
        "Ou configure manualmente:\n"
        "  Windows: set CHROME_BINARY=C:\\caminho\\chrome.exe\n"
        "  macOS/Linux: export CHROME_BINARY=/caminho/chrome\n"
    )


# Detecta o navegador
BROWSER_BINARY = detectar_navegador()

# Outras configurações
CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH")
DOWNLOAD_DIR = Path(os.environ.get("SIDRA_DOWNLOAD_DIR", Path.cwd() / "dados"))


def iniciar_driver():
    """Inicializa o driver com configurações anti-detecção."""
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.binary_location = BROWSER_BINARY  # ← Usa o navegador detectado
    
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-notifications")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    prefs = {
        "download.default_directory": str(DOWNLOAD_DIR.resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    if CHROMEDRIVER_PATH:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
        """
    })
    
    print(f"🌐 Navegador iniciado: {BROWSER_BINARY}")
    return driver


def buscar_tabela_1209(driver, wait):
    """
    Acessa a Tabela 1209 APENAS pela interface do SIDRA.
    NÃO permite acesso direto pela URL.
    """
    print("   -> Acessando página inicial do SIDRA...")
    driver.get("https://sidra.ibge.gov.br/")
    time.sleep(3)
    
    # Fecha popups
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
    except:
        pass
    
    # ====== PASSO 1: CLICAR NA LUPA (OBRIGATÓRIO) ======
    print("   -> Procurando ícone da lupa...")
    try:
        lupa = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.lupa-li a")))
        driver.execute_script("arguments[0].click();", lupa)
        print("   -> ✅ Lupa clicada!")
        time.sleep(2)
    except TimeoutException:
        # ❌ Se não encontrar a lupa, PARA O SCRIPT
        raise RuntimeError(
            "❌ ERRO CRÍTICO: Lupa de pesquisa não encontrada!\n"
            "A navegação pela interface do SIDRA é obrigatória.\n"
            "Não é permitido acessar diretamente a URL da tabela."
        )
    
    # ====== PASSO 2: DIGITAR "1209" NO CAMPO DE BUSCA (OBRIGATÓRIO) ======
    print("   -> Localizando campo de busca...")
    try:
        container = wait.until(EC.visibility_of_element_located((By.ID, "sidra-pesquisa-lg")))
        campo = container.find_element(By.CSS_SELECTOR, "input[type='text']")
        
        print("   -> Digitando '1209' no campo de busca...")
        campo.clear()
        for char in "1209":
            campo.send_keys(char)
            time.sleep(0.15)
        print("   -> ✅ Texto digitado com sucesso!")
        time.sleep(2)
        
    except TimeoutException:
        raise RuntimeError(
            "❌ ERRO CRÍTICO: Campo de busca não encontrado!\n"
            "Não foi possível interagir com a interface do SIDRA."
        )
    
    # ====== PASSO 3: EXECUTAR A BUSCA (OBRIGATÓRIO) ======
    print("   -> Executando busca...")
    try:
        botao = container.find_element(By.CSS_SELECTOR, "button")
        driver.execute_script("arguments[0].click();", botao)
        print("   -> ✅ Botão de busca clicado!")
    except NoSuchElementException:
        print("   -> Botão não encontrado. Pressionando ENTER...")
        campo.send_keys(Keys.ENTER)
    
    time.sleep(3)
    
    # ====== PASSO 4: VERIFICAR SE JÁ ESTÁ NA PÁGINA DA TABELA ======
    print("   -> Verificando redirecionamento automático...")
    current_url = driver.current_url
    
    if "tabela/1209" in current_url.lower() or "1209" in driver.title:
        print("   -> ✅ Redirecionado automaticamente para Tabela 1209!")
        esperar_carregamento_tabela(wait)
        fechar_tour_tabela(driver, wait)
        return
    
    # ====== PASSO 5: PROCURAR E CLICAR NO LINK DA TABELA (OBRIGATÓRIO) ======
    print("   -> Procurando link da Tabela 1209 nos resultados...")
    try:
        link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, 'tabela/1209') or contains(@href, 'Tabela=1209') or contains(., '1209')]")
            )
        )
        
        # Scroll até o link
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
        time.sleep(1)
        
        # Clica no link
        print("   -> Clicando no link da Tabela 1209...")
        driver.execute_script("arguments[0].click();", link)
        print("   -> ✅ Link clicado com sucesso!")
        time.sleep(2)
        
    except TimeoutException:
        # ❌ Se não encontrar o link, PARA O SCRIPT
        raise RuntimeError(
            "❌ ERRO CRÍTICO: Link da Tabela 1209 não encontrado nos resultados da busca!\n"
            "Possíveis causas:\n"
            "  1. A busca não retornou resultados\n"
            "  2. A interface do SIDRA mudou\n"
            "  3. Problema de conexão\n"
            "\n"
            "Não é permitido acessar diretamente a URL da tabela."
        )
    
    # ====== PASSO 6: AGUARDAR TABELA CARREGAR ======
    esperar_carregamento_tabela(wait)
    fechar_tour_tabela(driver, wait)
    
    print("   -> ✅ Navegação pela interface concluída com sucesso!")

def esperar_carregamento_tabela(wait):
    """Aguarda a tabela carregar completamente."""
    print("   -> Aguardando tabela carregar...")
    try:
        wait.until(EC.presence_of_element_located((By.ID, "panel-C58")))
        print("   -> ✅ Tabela carregada!")
        time.sleep(2)
    except TimeoutException:
        print("   -> ⚠️ Timeout, mas continuando...")


def fechar_tour_tabela(driver, wait):
    """Fecha popups de ajuda."""
    print("   -> Fechando popups...")
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.5)
    except:
        pass


def clicar_botao_sidra_toggle(driver, wait, texto_opcao, marcar=True):
    """
    Função UNIVERSAL para clicar em botões sidra-toggle.
    """
    print(f"   -> {'Marcando' if marcar else 'Desmarcando'} '{texto_opcao}'...")
    
    # Procura pelo span com o nome
    xpath = f"//span[@class='nome' or contains(@class, 'nome linhaAfastado')][contains(text(), '{texto_opcao}')]"
    
    max_tentativas = 10
    for tentativa in range(max_tentativas):
        try:
            span = driver.find_element(By.XPATH, xpath)
            
            # Scroll até o elemento
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span)
            time.sleep(0.5)
            
            # Pega o botão sidra-toggle
            item_pai = span.find_element(By.XPATH, "./ancestor::div[contains(@class, 'item-lista') or contains(@class, 'item-arvore')]")
            botao = item_pai.find_element(By.CSS_SELECTOR, "button.sidra-toggle")
            
            # Verifica estado atual
            esta_marcado = botao.get_attribute("aria-selected") == "true"
            
            if marcar:
                if not esta_marcado:
                    driver.execute_script("arguments[0].click();", botao)
                    print(f"   -> ✅ '{texto_opcao}' marcado!")
                    time.sleep(0.7)
                else:
                    print(f"   -> '{texto_opcao}' já estava marcado.")
            else:
                if esta_marcado:
                    driver.execute_script("arguments[0].click();", botao)
                    print(f"   -> ✅ '{texto_opcao}' desmarcado!")
                    time.sleep(0.7)
                else:
                    print(f"   -> '{texto_opcao}' já estava desmarcado.")
            
            return True
            
        except NoSuchElementException:
            # Tenta rolar o painel
            try:
                container = driver.find_element(By.CSS_SELECTOR, "div.lv-container")
                driver.execute_script(f"arguments[0].scrollTop += 100;", container)
                time.sleep(0.5)
            except:
                pass
            
            if tentativa == max_tentativas - 1:
                print(f"   -> ❌ '{texto_opcao}' não encontrado após {max_tentativas} tentativas!")
                return False

def selecionar_unidade_federacao(driver, wait):
    """
    Seleciona Unidade da Federação expandindo a árvore corretamente.
    """
    print("\n--- CONFIGURANDO UNIDADE TERRITORIAL ---")
    
    try:
        # 1. Localiza o item "Unidade da Federação" na árvore
        xpath_uf = "//li[@id='arvore-435e-1']"
        item_uf = wait.until(EC.presence_of_element_located((By.XPATH, xpath_uf)))
        
        # Scroll até o elemento
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item_uf)
        time.sleep(1)
        
        # 2. Verifica se precisa expandir (procura o ícone de expansão)
        try:
            icone_expandir = item_uf.find_element(By.CSS_SELECTOR, "i.expande")
            
            # Se está colapsado (classe 'collapsed'), clica para expandir
            if "collapsed" in icone_expandir.get_attribute("class"):
                print("   -> Expandindo árvore 'Unidade da Federação'...")
                driver.execute_script("arguments[0].click();", icone_expandir)
                time.sleep(1.5)
                print("   -> ✅ Árvore expandida!")
        except NoSuchElementException:
            print("   -> Árvore já estava expandida.")
        
        # 3. Agora localiza o subitem "Em Grande Região [27/27]"
        xpath_em_grande_regiao = "//li[@id='arvore-715e-1']//span[@class='nome' and contains(text(), 'Em Grande Região')]"
        
        try:
            span_em_grande_regiao = wait.until(EC.presence_of_element_located((By.XPATH, xpath_em_grande_regiao)))
            
            # Scroll até o elemento
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", span_em_grande_regiao)
            time.sleep(0.5)
            
            # Pega o botão sidra-toggle
            item_pai = span_em_grande_regiao.find_element(By.XPATH, "./ancestor::div[contains(@class, 'item-arvore')]")
            botao = item_pai.find_element(By.CSS_SELECTOR, "button.sidra-toggle")
            
            # Verifica se já está marcado
            esta_marcado = botao.get_attribute("aria-selected") == "true"
            
            if not esta_marcado:
                driver.execute_script("arguments[0].click();", botao)
                print("   -> ✅ 'Em Grande Região [27/27]' selecionado!")
                time.sleep(1)
            else:
                print("   -> ✅ 'Em Grande Região [27/27]' já estava selecionado!")
                
        except TimeoutException:
            print("   -> ⚠️ Não foi possível encontrar 'Em Grande Região'. Tentando pela Unidade da Federação diretamente...")
            
            # Fallback: Marca o próprio "Unidade da Federação"
            xpath_botao_uf = "//li[@id='arvore-435e-1']//button[@class='sidra-toggle']"
            botao_uf = driver.find_element(By.XPATH, xpath_botao_uf)
            
            esta_marcado = botao_uf.get_attribute("aria-selected") == "true"
            
            if not esta_marcado:
                driver.execute_script("arguments[0].click();", botao_uf)
                print("   -> ✅ 'Unidade da Federação [27/27]' selecionado!")
            else:
                print("   -> ✅ 'Unidade da Federação [27/27]' já estava selecionado!")
    
    except Exception as e:
        print(f"   -> ❌ Erro ao selecionar Unidade da Federação: {e}")
        raise


def aplicar_filtros_tabela(wait):
    """Aplica todos os filtros necessários."""
    print("\n" + "="*60)
    print("APLICANDO FILTROS")
    print("="*60)
    
    driver = wait._driver
    
    # 1. Grupo de Idade
    print("\n--- FILTRO: GRUPO DE IDADE ---")
    clicar_botao_sidra_toggle(driver, wait, "Total", marcar=False)
    time.sleep(2)
    clicar_botao_sidra_toggle(driver, wait, "60 a 69 anos", marcar=True)
    time.sleep(2)
    clicar_botao_sidra_toggle(driver, wait, "70 anos ou mais", marcar=True)
    time.sleep(2)

    # 2. Ano
    print("\n--- FILTRO: ANO ---")
    print("   -> Ano 2022 já está selecionado por padrão.")

    # 3. Unidade Territorial - CORRIGIDO
    selecionar_unidade_federacao(driver, wait)
    
    print("\n" + "="*60)
    print("✅ FILTROS APLICADOS!")
    print("="*60 + "\n")


def baixar_csv(wait, timeout=60):
    """Realiza o download do CSV com timestamp."""
    print("\n" + "="*60)
    print("INICIANDO DOWNLOAD")
    print("="*60)
    
    driver = wait._driver
    
    # 1-4: Código anterior permanece igual...
    print("   -> Clicando no botão 'Download' para abrir modal...")
    botao_download = wait.until(EC.element_to_be_clickable((By.ID, "botao-downloads")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_download)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", botao_download)
    
    wait.until(EC.visibility_of_element_located((By.ID, "modal-downloads")))
    time.sleep(1)
    
    select_formato = driver.find_element(By.CSS_SELECTOR, "#modal-downloads select.select-formato-arquivo")
    driver.execute_script("arguments[0].value = 'br.csv'; arguments[0].dispatchEvent(new Event('change'));", select_formato)
    time.sleep(0.5)
    
    botao_download_verde = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#modal-downloads a.btn-green-sucess")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_download_verde)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", botao_download_verde)
    
    # 5. Aguardar download
    print("   -> Aguardando arquivo CSV ser baixado...")
    arquivo_final = None
    fim = time.time() + timeout
    
    while time.time() < fim:
        time.sleep(1)
        candidatos = sorted(DOWNLOAD_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
        if candidatos and candidatos[0].stat().st_size > 0:
            arquivo_final = candidatos[0]
            break
    
    # 6. Renomear COM TIMESTAMP
    if arquivo_final:
        print(f"   -> ✅ CSV baixado: {arquivo_final.name}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        nome_exigido = f"populacao_60mais_1209_{timestamp}.csv"
        caminho_final = DOWNLOAD_DIR / nome_exigido
        
        if caminho_final.exists():
            caminho_final.unlink()
        
        arquivo_final.rename(caminho_final)
        print(f"   -> ✅ Renomeado para: {nome_exigido}")
        print(f"   -> 📂 Localização: {caminho_final}")
    else:
        raise TimeoutError(f"CSV não foi localizado após {timeout} segundos.")


def acessar_tabela_1209():
    """Fluxo completo."""
    driver = iniciar_driver()
    wait = WebDriverWait(driver, 30)

    try:
        buscar_tabela_1209(driver, wait)
        aplicar_filtros_tabela(wait)
        baixar_csv(wait)
        
        print("\n" + "="*60)
        print("🎉 PROCESSO CONCLUÍDO COM SUCESSO! 🎉")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        input("\nPressione Enter para fechar o navegador...")
        driver.quit()


if __name__ == "__main__":
    acessar_tabela_1209()