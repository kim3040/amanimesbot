import re
import json
import amanobot
from amanobot.loop import MessageLoop
import time
import datetime
import requests
import sqlite3
from amanobot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from amanobot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from amanobot.namedtuple import InlineQueryResultArticle, InputTextMessageContent

def procurarassistido(id):
 conn = sqlite3.connect("animes.db")
 cursor = conn.cursor()
 cursor.execute("""
SELECT * FROM infousers WHERE id = ? ORDER BY assistidoem DESC LIMIT 5""",(id,))
 a = cursor.fetchall()
 if len(a) >= 1:
  d = "Ultimos Animes Assistidos:"
  for x in a:
   d = d + f"\n\n*Anime*:{x[1].upper()}\n*Episodio*: {x[3]}\n*Assistido em*: {x[2]}"
  else:
   return d
 else:
   return "*Nenhum anime adicionado a lista de assistidos*"

def deletardobanco(id,anime,episodio):
 conn = sqlite3.connect("animes.db")
 cursor = conn.cursor()
 cursor.execute("DELETE FROM infousers WHERE anime = ? AND episodioassistido = ? AND id = ?",(anime,episodio,id))
 conn.commit()
 
def procurarnobanco(anime,episodio,id):
 try:
  conn = sqlite3.connect("animes.db")
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM infousers WHERE episodioassistido = ? AND anime = ? and id = ?",(episodio,anime,id))
  a = cursor.fetchall()
  if len(a) == 0:
   return True
  else:
   return False
 except:
   return "Ocorreu um erro"

def addaobanco(id,anime,assistidoem,episodioassistido):
 conn = sqlite3.connect("animes.db")
 cursor = conn.cursor()
 cursor.execute(f"""
SELECT * FROM infousers WHERE episodioassistido = {episodioassistido} AND anime = '{anime}'""")
 a = cursor.fetchall()
 if len(a) == 0:
  conn.execute("""
 INSERT INTO infousers(id,anime,assistidoem,episodioassistido)
 VALUES(?,?,?,?)
 """,(id,anime,assistidoem,episodioassistido))
  conn.commit()

def novo(anime):
 try:
  animes = ""
  a = anime.split('https://www.myanimesonline.biz/animes/episodio/')[1].split("-")
  it = a.copy()
  for x in it:
   if "episodio" not in x:
    animes = animes + " {}".format(x)
    a.remove(x)
   else:
    a = json.loads(json.dumps(dict(anime=animes,episodio=a[1].replace("/",''))))
    return a
    break
 except:
  return {'animes':''}

def obternovosanimes(tipo):
 soteste = ""
 acess = requests.get("https://www.myanimesonline.biz").text
 obterlinkepisodio =  re.findall("https://www.myanimesonline.biz/animes/episodio/\w*\S*",acess) 
 a = 1
 for x in obterlinkepisodio:
  a = a + 1
  hg = x.replace('"', '').replace(")","")
  nome = novo(hg)
  fim = json.loads(json.dumps(dict(anime=nome["anime"], episodio=nome["episodio"],download=hg)))
  soteste = soteste + f"\n\n*Anime:* {fim['anime'].upper()}\n*Episodio*: {fim['episodio']}\n*Download:* [Assista Aqui]({fim['download']})"
  if a == 13:
   if tipo == 1:
    return soteste
   else:
     soteste = soteste + f"\n\n*Atualizado com sucesso as:\n*{datetime.datetime.now().strftime('%H *horas %M minutos e %S segundos*')}"
     return soteste

bot = amanobot.Bot('tokenaqui')

def customname(name,tipo):
 if tipo == "jaassistido":
  teste = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text=f"✅Marcar episodio {name} como assistido ",callback_data="marcarassistido")],
               ])
  return teste
 elif tipo == "remover":
  teste = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text=f"❌Remover episodio {name} da lista de assistidos",callback_data="deleteme")],
               ])
  return teste
  
   

def callbacks(msg):
 info = novo(msg['message']['reply_to_message']['text'].replace('/animes ',''))
 anime, episodio = info.get("anime"),info.get("episodio")
 query_id, from_id, query_data = amanobot.glance(msg, flavor='callback_query')
 id = msg.get('message').get('chat').get('id')
 id2 = msg["from"]["id"]
 if query_data == 'marcarassistido':
  if msg["from"]["id"] == msg["message"]["reply_to_message"]["from"]["id"]:
   enviar = addaobanco(id2,anime,datetime.datetime.now().strftime("%d/%m/%y  %H:%M:%S"),episodio)
   bot.editMessageReplyMarkup((id,msg['message']['message_id']),reply_markup=customname(episodio,"remover"))
   bot.answerCallbackQuery(query_id, text='Adicionado a lista de assistidos')
  else:
   bot.answerCallbackQuery(query_id, text='Você  não pode alterar a lista dos outros')
 if query_data == 'deleteme':
  if msg["from"]["id"] == msg["message"]["reply_to_message"]["from"]["id"]:
   info = novo(msg['message']['reply_to_message']['text'].replace('/animes ',''))
   anime, episodio = info['anime'],info['episodio']
   deletardobanco(id2,anime,episodio)
   bot.editMessageReplyMarkup((id,msg['message']['message_id']),reply_markup=customname(episodio,"jaassistido"))
   bot.answerCallbackQuery(query_id, text='Adicionado ao banco')
  else:
   bot.answerCallbackQuery(query_id, text='Você  não pode alterar a lista dos outros')
 if query_data == 'atualizar':
  if msg["from"]["id"] == msg["message"]["reply_to_message"]["from"]["id"]:
   mensagem = obternovosanimes(2)
   bot.editMessageText((id,msg['message']['message_id']),mensagem,parse_mode="markdown",reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text=f"Atualizar",callback_data="atualizar")],
               ]))
   bot.answerCallbackQuery(query_id, text='Atualizado com sucesso')
   
  else:
   bot.answerCallbackQuery(query_id, text='Digite /novos e tente novamente')
   
 
  
def getanimes(url):
 try:
  animehtml = requests.get(url)
  regex = re.findall("https://api.animesgratisbr.com/video/\d[0-9]*",animehtml.text)
  if len(regex) == 1:
   a = requests.head(regex[0],stream=True).headers
   if a['Content-Type'] == "video/mp4":
    return f"[Assista/Baixe Aqui]({a['Location']})"
   else:
    return "NAO ENCONTRADO"
  else:
   novoregex = re.findall("https://videos.animesgratisbr.com/pubfolder/animes/\S*" , animehtml.text)
   if len(novoregex) == 1:
    return f"""[Assista/Baixe Aqui]({novoregex[0].replace('"','')})"""
   else:
    novoregex = re.findall('https://video.wixstatic.com/video/\w*\S*',animehtml.text)
    if len(novoregex) == 1:
     return f"""[Assista/Baixe Aqui]({novoregex[0].replace('"','')}"""
    else:
     return "NAO ENCONTRADO"
 except:
  pass
 

def pesquisa(anime):
 a = requests.get("https://www.myanimesonline.biz/?s="+anime).text
 teste = re.findall("https://www.myanimesonline.biz/animes/episodio/\S*.",a)
 soteste = ""
 for x in teste:
  nome = novo(x)
  fim = json.loads(json.dumps(dict(anime=nome["anime"], episodio=nome["episodio"].replace('"',''),download=x)))
  soteste = soteste + f"""\n\n*Anime:* {fim['anime'].upper()}\n*Episodio*: {fim['episodio']}\n*Download*: [Assista Aqui]({fim['download'].replace('"','')})"""
 else:
   if len(soteste) >= 1:
    return soteste
   else:
    return "*Anime Não Encontrado*"

def on_inline_query(msg):
    query_id, from_id, query_string = amanobot.glance(msg, flavor='inline_query')
    resultados = pesquisa(msg["query"])
    articles = [InlineQueryResultArticle(
                    id='abcd',
                    title=resultados.replace("*",""),
                    input_message_content=InputTextMessageContent(
                        message_text=resultados,parse_mode="markdown"
                    )
               )]

    bot.answerInlineQuery(query_id, articles)

def handle(msg):
 if msg['text'].lower() == '/start': 
  mensagem = "*Bot feito com a intenção para facilitar a busca de animes digite /Ajuda Para Saber Mais*"
  if "group" not in msg["chat"]["type"]:
   bot.sendMessage(msg['chat']['id'], mensagem, reply_to_message_id=msg['message_id'],parse_mode="markdown",reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="/ajuda")]
                                ],resize_keyboard=True))
  else:
   bot.sendMessage(msg['chat']['id'],mensagem , reply_to_message_id=msg['message_id'],parse_mode="markdown")
 if msg['text'].lower() == '/exemplos':
  bot.sendMessage(msg['chat']['id'], "*Exemplos de comandos\n\n/pesquisar - esse e um dos comandos mais simples do bot voce digita /pesquisar naruto(e apenas um exemplo inves de naruto voce digita o anime que voce deseja) e ele ira te retornar os episodios encontrados no site myanimesonline*\n\n/*baixar - esse comando funciona especificamente para episodios de animes do site myanimesonline esses episodios voce pode consequir acessando o site ou usando o comando /pesquisar depois para utilizar esse comando voce digita /baixar https://www.myanimesonline.biz/animes/episodio/dororo-episodio-05/(essa url voce troca por a url contendo o anime/episodio desejado)*\n\n/*novos - esse e o comandos mais simples nao tem segredo voce digita /novos e automaticamente ele ira pegar todos os links dos mais recentes episodios do site myanimesonline para voce baixar ou assistir*\n\n/*mylist - Mostra os ultimos animes que você marcou como assistido*", reply_to_message_id=msg['message_id'],parse_mode="markdown")
 if msg['text'].lower() == '/ajuda': 
  mensagem = """*Seja bem vindo ao menu de ajuda logo abaixo voce vera um tutorial de como usar os comandos do bot*

/novos - *Obtem a mais recentemente lista de animes lancados no site myanimesonline*

/pesquisar - *Pesquisa animes no no site myanimesonline* 
(B)
/baixar - *Obtem o link direto para download ou stream do anime citado*
/mylist - *Mostra os ultimos animes adicionados a lista de assistidos*

*Para mais exemplos digite /exemplos*

"""
  if "group" not in msg["chat"]["type"]:
   bot.sendMessage(msg['chat']['id'],mensagem , reply_to_message_id=msg['message_id'],parse_mode="markdown",reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="/exemplos")]
                                ],resize_keyboard=True))
  else:
   bot.sendMessage(msg['chat']['id'],mensagem , reply_to_message_id=msg['message_id'],parse_mode="markdown")                               
 
 if msg['text'].split()[0] == '/baixar':
  print(f"{msg['from']['id']} Baixou um Anime")
  anime = msg['text'][7:]
  dados = novo(anime)
  po = getanimes(anime)
  if "Assista/Baixe Aqui" in po:
   bank = procurarnobanco(dados['anime'],dados['episodio'],msg['from']['id'])
   if bank:
    bot.sendMessage(msg['chat']['id'], po, reply_to_message_id=msg['message_id'], parse_mode="markdown",reply_markup=customname(dados["episodio"],"jaassistido"))
   else:
    bot.sendMessage(msg['chat']['id'], po, reply_to_message_id=msg['message_id'], parse_mode="markdown",reply_markup=customname(dados["episodio"],"remover"))
  else:
   bot.sendMessage(msg['chat']['id'], "*Anime não encontrado*", reply_to_message_id=msg['message_id'], parse_mode="markdown")
    
 

 if msg['text'].split()[0] == '/pesquisar':
  print(f"{msg['from']['id']} Pesquisou um Anime") 
  busca = msg['text'][10:]
  bot.sendMessage(msg['chat']['id'], pesquisa(busca), reply_to_message_id=msg['message_id'], parse_mode="markdown")
 if msg['text'] == '/novos':
  bot.sendMessage(msg['chat']['id'], obternovosanimes(1), reply_to_message_id=msg['message_id'],parse_mode="markdown",reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text=f"Atualizar",callback_data="atualizar")],
               ]))
 if msg['text'] == "/mylist":
  bot.sendMessage(msg['chat']['id'], procurarassistido(msg["from"]["id"]), reply_to_message_id=msg['message_id'], parse_mode="markdown")
MessageLoop(bot, {'chat':handle,'callback_query':callbacks,'inline_query': on_inline_query}).run_as_thread()
print("Rodando")
while 1:
 time.sleep(10)
	
