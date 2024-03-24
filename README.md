# tjmg-scraper
Um scraper básico para coleta de inteiros teores do Tribunal de Justica de Minas Gerais (TJMG)

# uso do scraper

Essa é uma versão "prática" do scraper, ou seja, uma versão facilitada para o uso pessoal da equipe do JurAI.

funcoes:
get_num_processuais(url): faz a raspagem dos números processuais no URL indicado por você (Você que faz a busca, não o bot. O bot apenas faz a raspagem). Antes de mandar o URL, modifique a parte nele que diz "&linhasPorPagina=10" pra 5000, para mostrar todos os processos em uma só pagina.  Essa funcão retorna uma lista de strings.

get_processo_table(numprocs, dir = getcwd() + "/processos", connection=None, cursor=None, returns=True): Faz a raspagem de todas as informacões de vários processos de uma vez baseado no modelo do banco de dados. A saída ocorre de duas maneiras: por um array do python, e pela entrada dos dados diretamente no banco de dados. Para receber o array, a flag "returns" tem que ser True; se ela for False a funcao não retorna nenhuma lista. Para fazer upload de tudo diretamente para o banco de dados, é necessário passar um objeto de conexao e um objeto de cursor do mysql para a funcao, que ela irá fazer a insercao de todos os dados no banco de dados.

Exemplo:

```python
import mysql.connector as connector
import src.scraper as tjmg
import json

# pegar os números processuais de uma pesquisa sobre apelacao criminal
numeros = tjmg.get_num_processuais_5000("https://www5.tjmg.jus.br/jurisprudencia/pesquisaPalavrasEspelhoAcordao.do?numeroRegistro=1&totalLinhas=1&palavras=Apela%E7%E3o+Criminal&pesquisarPor=ementa&orderByData=2&codigoOrgaoJulgador=&codigoCompostoRelator=&classe=&listaClasse=9&codigoAssunto=&dataPublicacaoInicial=22%2F02%2F2024&dataPublicacaoFinal=&dataJulgamentoInicial=&dataJulgamentoFinal=&siglaLegislativa=&referenciaLegislativa=Clique+na+lupa+para+pesquisar+as+refer%EAncias+cadastradas...&numeroRefLegislativa=&anoRefLegislativa=&legislacao=&norma=&descNorma=&complemento_1=&listaPesquisa=&descricaoTextosLegais=&observacoes=&linhasPorPagina=5000&pesquisaPalavras=Pesquisar")
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

Nesse exemplo, fazemos a raspagem dos números processuais de uma busca sobre Apelacao Criminal, com cerca de 4500 processos, guardamos estes processos em um arquivo, e fazemos a raspagem e o download de todas as informacoes destes processos, guardando-as tanto em um banco de dados, tanto em um arquivo do tipo "json".

# dependencias

a lista completa de requerimentos está no arquivo requirements.txt, mas as principais bibliotecas que você deverá ter são:

mysql
fitz
SpeechRecognition
selenium
requests
