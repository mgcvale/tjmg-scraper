# tjmg-scraper
Um scraper básico para coleta de inteiros teores do Tribunal de Justica de Minas Gerais (TJMG)

# uso do scraper

O Scraper conta atualmente com duas funcões, sendo uma para coletar os números de processo, e uma para baixar os inteiros teores com os números de processo coletados pela primeira funcão.

O Scraper faz o uso do Selenium em Python, utilizando o Firefox como driver, e por isso é necessário ter este browser instalado para o seu uso.
Aqui está uma descricão básica do uso deste scraper, juntamente com um exemplo simples.

Funcão get_inteiro_teor(numproc: str, dir: str, timeout: float):
  Pega como argumento o número do processo, no formato X.XXX.XX.XXXXXX-X/XXX e retorna o PDF do inteiro teor deste processo, no diretório informado pelo parâmetro "dir".

Funcão def get_num_processuais(busca: str, page_limit: int): 
  Pega como argumento uma string da busca a ser realizada e a quantidade de páginas a serem buscadas, e retorna uma lista de strings com os números processuais de todos os processos encontrados na busca.

Exemplo:

```python
from os import getcwd
from time import sleep
import scraper as tjmg

# pegar os números processuais da busca "feminicído", até a quinta página (50 números no total)
numeros = tjmg.get_num_processuais("feminicidio", 5)

# salvar o resultado em um arquivo de texto
file = open("./inteiros-teores/numeros.txt", "w")
for numero in numeros:
    print(numero)
    file.write(numero + '\n')
file.close()

# fazer download dos inteiros teores de todos os números processuais encontrados
for numero in numeros:
    tjmg.get_inteiro_teor(numero, dir=getcwd() + "/inteiros-teores/pdfs", timeout=1)
    sleep(0.5)
```
