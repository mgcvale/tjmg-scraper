import os
from datetime import datetime
from os import getcwd
from time import sleep

import mysql
import requests
import speech_recognition as sr
from fitz import fitz
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_text_from_audio(audio_file):
    """
    Retorna o texto falado em um arquivo de áudio utilizando IA.

    :param audio_file: audio file
    :return: str
    """
    r = sr.Recognizer()
    with audio_file as source:
        audio_text = r.record(source)
        text = r.recognize_google(audio_text, language='pt-BR')
    return text


def get_nums_processuais(pesquisa_livre, lista_classe, data_inicio, data_final):
    """
    Scraper para coleta de números processuasis no TJMG.
    Recebe algumas informacões para a consulta processual (pesquisa livre, ID da classe processual, data mínima e data
    máxima, e retorna uma lista do python com todos os números processuais, sem formatacão.

    :param pesquisa_livre: str
    :param lista_classe: str
    :param data_inicio: str (DD%2FMM%2FYYYY)
    :param data_final: str (DD%2FMM%2FYYYY)
    :return: list of strings
    """

    # formatar o url da pesquisa
    url = "https://www5.tjmg.jus.br/jurisprudencia/pesquisaPalavrasEspelhoAcordao.do;jsessionid=AC19FB65083C3B4D5D366A5CC1D1363C.juri_node1?numeroRegistro=1&totalLinhas=1&palavras={pesquisa_livre}&pesquisarPor=ementa&orderByData=2&codigoOrgaoJulgador=&codigoCompostoRelator=&classe=&listaClasse={lista_classe}&codigoAssunto=&dataPublicacaoInicial={data_inicial}&dataPublicacaoFinal={data_final}&dataJulgamentoInicial=&dataJulgamentoFinal=&siglaLegislativa=&referenciaLegislativa=Clique+na+lupa+para+pesquisar+as+refer%EAncias+cadastradas...&numeroRefLegislativa=&anoRefLegislativa=&legislacao=&norma=&descNorma=&complemento_1=&listaPesquisa=&descricaoTextosLegais=&observacoes=&linhasPorPagina=5000&pesquisaPalavras=Pesquisar"
    url = url.format(pesquisa_livre = pesquisa_livre, lista_classe = lista_classe, data_final = data_final, data_inicial = data_inicio)
    print(url)

    #inicializar o webdriver com o url da pesquisa
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", getcwd() + "/temp")
    driver = webdriver.Firefox(options = options)
    driver.get(url)

    # quebrar o captcha
    while True:
        driver.find_element(By.CSS_SELECTOR, 'a[href="captchaAudio.svl"]').click()
        try:
            driver.find_element(By.ID, "captcha_text").send_keys("")
            audio = sr.AudioFile(getcwd() + "/temp/audio.wav")
            text = get_text_from_audio(audio)
            driver.find_element(By.ID, "captcha_text").send_keys(text)
        except:
            sleep(2)
            continue
        sleep(2)
        os.remove(getcwd() + "/temp/audio.wav")
        try:
            driver.find_element(By.ID, "captcha_text").send_keys("")
        except:
            break

    # esperar um tempo até a página dos processos ter carregado completamente
    wait = WebDriverWait(driver, 10)

    # raspar os números da página
    numeros = []
    try:
        processos = driver.find_elements(By.CSS_SELECTOR, '.caixa_processo')
        i = 0
        for processo in processos:
            print(i)
            numeros.append(processo.find_element(By.CSS_SELECTOR, "a > br + div").text)
            i += 1
    except:
        print("deu errado :c")
        sleep(2)
    driver.quit()
    return numeros

def get_numproc_numbers(numproc: str):
    """
    Separador do número processual do TJMG em suas partes.
    Recebe um número processual do TJMG e retorna uma lista com todas as suas partes separadas.

    :param numproc: str
    :return: list of numprocs
    """

    parts = ["" for _ in range(6)]
    partsindex = 0
    lastindex = 0

    # separate the numproc onto its parts
    for i in range(len(numproc)):
        if numproc[i] == "." or numproc[i] == "/" or numproc[i] == "-":
            parts[partsindex] = numproc[lastindex:i]
            partsindex += 1
            lastindex = i + 1
    parts[partsindex] = numproc[lastindex:len(numproc)]
    return parts
def get_inteiro_teor(numproc: str, dir = getcwd() + "/inteiros-teores", timeout=3, filename = None):

    # formatar o número processual
    parts = get_numproc_numbers(numproc)

    #  pegar o url do inteiro teor
    url = ("https://www5.tjmg.jus.br/jurisprudencia/relatorioEspelhoAcordao.do?inteiroTeor=true&ano="
           + parts[2] + "&ttriCodigo=" + parts[0] + "&codigoOrigem=" + parts[1] + "&numero=" + parts[3] +
           "&sequencial=" + parts[5] + "&sequencialAcordao=0")

    # setup do nome do arquivo e diretório
    if(filename is None):
        dir = dir + "/"
        for string in parts:
            dir = dir + string
        dir = dir + ".pdf"
    else:
        dir = dir + "/" +  filename + ".pdf"

    # debug
    print(dir)
    print(url)

    # fazer requisicão e pegar o seu resultado
    try:
        r = requests.get(url, allow_redirects=True, timeout=timeout)
    except:
        print("nao foi possivel fazer a requisicao.")
        return
    open(dir, "wb").write(r.content)


def get_processo_table(numprocs, dir = getcwd() + "/processos", connection=None, cursor=None, returns = True):
    """
    Faz a raspagem dos dados de uma lista de processos, retornando uma tabela (em forma de array OU em um banco de
    dados) com o número processual, câmara, classe, assunto, data de cadastro, limiar, juiz, comarca,
    documento de origem, assistência judiciária, aruacao do juiz, acordao formatado, ementa formatada e sumula
    formatada.

    :param numprocs: str []:  lista dos números processuais a serem consultados
    :param dir: str: diretório para salvar dados temporários utilizados pelo scraper
    :param connection: connection: conexão do banco de dados no qual as informacoes serão armazenadas.
    :param cursor: cursor: cursor com o banco de dados no qual as informacões serão armazenadas.
    :param returns: bool: flag indicando se a funcao deverá retornar um array com as informacoes.
    :return: string array
    """

    if returns:
        table = []
    #init webdriver
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", getcwd() + "/temp")
    driver = webdriver.Firefox(options=options)

    # checar se o banco de dados será utilizado, e, em caso positivo, fazer o seu setup.
    if(connection is not None):
        insert_query = """
            INSERT INTO processo (numero_tjmg, camara, classe, assunto, data_cadastro, liminar, juiz, comarca, documento_origem, assistencia_judiciaria, atuacao_juiz, acordao, ementa, sumula)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        using_database = True

    for numproc in numprocs:
        numproc_clean = numproc.replace("-", "").replace(".", "").replace("/", "")
        driver.get("https://www4.tjmg.jus.br/juridico/sf/proc_complemento2.jsp?listaProcessos=" + numproc_clean)
        try:
            # raspar a maioria dos dados
            data = [
                numproc_clean,
                driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr[1]/td[1]").text[9:],
                driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr[2]/td[1]").text[9:],
                driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr[3]/td").text[10:],
                driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr[4]/td[1]").text[20:],
                driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr[6]/td[1]").text[9:] == 'S',
                driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr[1]/td[1]").text[9:],
                driver.find_element(By.XPATH, "/html/body/table[5]/tbody/tr[2]/td[1]").text[16:],
                driver.find_element(By.XPATH, "/html/body/table[5]/tbody/tr[3]/td[1]").text[18:],
                driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr[4]/td[2]").text[24:] == 'S',
                driver.find_element(By.XPATH, "/html/body/table[3]/tbody/tr[1]/td[2]").text[17:]
            ]
            # formatar a data
            data[4] = datetime.strptime(data[4], '%d/%m/%Y').strftime('%Y-%m-%d')

            # fazer download do pdf do acórdão e o transformar em texto
            get_inteiro_teor(numproc, dir + "/temp", filename="acordao")
            acordao_txt = ''
            acordao_doc = fitz.open(dir + "/temp/acordao.pdf")
            for pagen in range(acordao_doc.page_count):
                page = acordao_doc.load_page(pagen)
                acordao_txt += page.get_text()

            # pegar a ementa e súmula do acórdão
            ementa = acordao_txt[acordao_txt.find("EMENTA: ") + len("EMENTA: "):]
            ementa = ementa[:ementa.find("\n")]
            sumula = acordao_txt[acordao_txt.find("SÚMULA: ") + len("SÚMULA: "):]
            sumula = sumula[:sumula.rfind("\"")]

            # concatenar o resto das informacões
            data.append(acordao_txt)
            data.append(ementa)
            data.append(sumula)

            # fazer a insercao dos dados no banco de dados, se possível
            if using_database:
                try:
                    cursor.execute(insert_query, data)
                    connection.commit()
                except mysql.connector.Error as e:
                    print("error inserting into table: " + e)

            # colocar as informacoes na tabela, se possível
            if returns:
                table.append(data)
        except:
            continue
    # fehar o driver e retornar, se possível
    driver.close()
    if returns:
        return table
