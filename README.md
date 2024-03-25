# tjmg-scraper
Um scraper básico para coleta de inteiros teores do Tribunal de Justica de Minas Gerais (TJMG)

# uso do scraper

Essa é uma versão "prática" do scraper, ou seja, uma versão facilitada para o uso pessoal da equipe do JurAI.

funcoes:
get_num_processuais_5000(pesquisa_livre, lista_classe, data_inicio, data_final): faz a raspagem dos números processuais, baseado nos dados indicados. As datas devem estar no formato usado pelo TJMG: DD%2FMM%2FYYYY. 

get_processo_table(numprocs, dir = getcwd() + "/processos", connection=None, cursor=None, returns=True): Faz a raspagem de todas as informacões de vários processos de uma vez baseado no modelo do banco de dados. A saída ocorre de duas maneiras: por um array do python, e pela entrada dos dados diretamente no banco de dados. Para receber o array, a flag "returns" tem que ser True; se ela for False a funcao não retorna nenhuma lista. Para fazer upload de tudo diretamente para o banco de dados, é necessário passar um objeto de conexao e um objeto de cursor do mysql para a funcao, que ela irá fazer a insercao de todos os dados no banco de dados.

Exemplo:

```python
import mysql.connector as connector
import src.scraper as tjmg
import json

# pegar os números processuais de uma pesquisa sobre apelacao criminal
numeros = tjmg.get_num_processuais_5000("Apelacao Cível", "9", "08%2F04%2F2023", "08%2F05%2F2023")
# salvar tudo em um arquivo de texto
with open("apelacao criminal/numprocs.txt", 'w') as file:
    file.write("\n".join(numeros))

# abrir o arquivo que acabamos de fazer com todos os números de processo
with open("apelacao criminal/numprocs.txt", "r") as file:
    entries = file.readlines()
entries = [entry.strip() for entry in entries]

# criar uma conexão no MySql
host = '111.222.333.4'
user = 'nome_usuario'
password = 'senha_usuario'
database = 'nome_db'
connection = connector.connect(host=host, user=user, password=password, port=3306, database=database)
cursor = connection.cursor()

# pegar a tabela de dados raspada pelo scraper. Vamos salvar tanto no banco de dados, passando a conexao e o cursor, 
# tanto em um array do python, setando o returns como True.
tabela = tjmg.get_processo_table(numprocs=entries, connection=connection, cursor=cursor, returns=True)

# fechar conexão com o banco de dados
if 'cursor' in locals():
    cursor.close()
if 'connection' in locals() and connection.is_connected():
    connection.close()

# transformar a tabela que pegamos em um arquivo json
with open("/apelacao criminal/processo.json", 'wb'):
    json.dump(tabela)
```

Nesse exemplo, fazemos a raspagem dos números processuais de uma busca sobre Apelacao Criminal, com cerca de 4500 processos, guardamos estes processos em um arquivo, e fazemos a raspagem e o download de todas as informacoes destes processos, guardando-as tanto em um banco de dados, quanto em um arquivo do tipo "json".

# dependencias

a lista completa de requerimentos está no arquivo requirements.txt, mas as principais bibliotecas que você deverá ter são:

mysql
fitz (PyMuPDF)
SpeechRecognition
selenium
requests
