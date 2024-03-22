import os
from os import getcwd

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from time import sleep
import speech_recognition as sr

import src.captcha as cap


def get_inteiro_teor(numproc: str, dir = getcwd() + "/inteiros-teores", timeout=3):
    """

    This function is used to get the inteiro teor from a process number.

    :return: void
    :param numproc: number of the process to get the inteiro teor from (should be formated in the following way: X.XXX.XX.XXXXXX-X/XXX.
    :param dir: the directory where the inteiro teor should be sored. This directory must not end in a forward slash.
    :param timeout: the amount of timeout of the request. If the request takes longer than the timeout, the file isn't downloaded, and the function returns.
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

    # get url
    url = ("https://www5.tjmg.jus.br/jurisprudencia/relatorioEspelhoAcordao.do?inteiroTeor=true&ano="
           + parts[2] + "&ttriCodigo=" + parts[0] + "&codigoOrigem=" + parts[1] + "&numero=" + parts[3] +
           "&sequencial=" + parts[5] + "&sequencialAcordao=0")

    # setup filename
    dir = dir + "/"
    for string in parts:
        dir = dir + string
    dir = dir + ".pdf"

    # make and retrieve request result
    try:
        r = requests.get(url, allow_redirects=True, timeout=timeout)
    except:
        print("nao foi possivel fazer a requisicao.")
        return
    open(dir, "wb").write(r.content)


def get_num_processuais(busca: str, page_limit: int):

    """

    This function is used to search for process numbers in the court page.

    :param busca: the keyword to be searched on the TJMG jurisprudence search
    :param page_limit: the maximum amount of pages to be searched. Bear in mind that each page contains 10 numbers.
    :return: string[] - the numbers of the processes
    """

    # create driver
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", getcwd() + "/temp")
    driver = webdriver.Firefox(options=options)

    # make the querry
    driver.get("https://www5.tjmg.jus.br/jurisprudencia/formEspelhoAcordao.do")
    driver.find_element(By.ID, "palavras").send_keys(busca)
    driver.find_element(By.ID, "pesquisaLivre").click()

    # get the captcha audio
    sleep(2)
    while True:
        driver.find_element(By.CSS_SELECTOR, 'a[href="captchaAudio.svl"]').click()
        try:
            driver.find_element(By.ID, "captcha_text").send_keys("")
            audio = sr.AudioFile(getcwd() + "/temp/audio.wav")
            text = cap.get_text_from_audio(audio)
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

    # get process numbers
    sleep(3)
    numeros = []
    pages = 0
    while pages < page_limit:
        if pages != 0:
            # go to the next page
            driver.find_element(By.CSS_SELECTOR,
                "td.footerlink:nth-last-child(2) > a:nth-child(1)").click()
        # get the process numbers in the current page
        sleep(1)
        processos = driver.find_elements(By.CSS_SELECTOR, '.caixa_processo')
        i = pages * 10
        for processo in processos:
            numeros.append(processo.find_element(By.CSS_SELECTOR, "a > br + div").text)
            i += 1
        pages += 1

    driver.quit()
    return numeros
