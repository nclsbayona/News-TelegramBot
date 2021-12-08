import os, requests, threading, multiprocessing
from time import sleep
from random import randint
from replit import db
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from signal import SIGSTOP

def fetch_suscritos():
  suscritos=dict()
  for key in db:
    suscritos[key]=db[key]
  return suscritos

def getXataka_GenbetaNews(api_key: str, latest=False):
    the_news = requests.get(
        "https://newsapi.org/v2/everything?domains=xataka.com,genbeta.com&apiKey={}"
        .format(api_key)).json()
    try:
      the_news = list(the_news.get("articles"))
    except:
      the_news=None
    if (latest and the_news is not None):
        the_news = the_news[0]
    return the_news

def incrementar_cont():
  global cont, keys
  cont+=1
  cont%=len(keys)

def transformar_noticia(article):
  ret="\n"
  try:
    ret+="From: "+str(article.get("source").get("name"))+"\n"
    ret+="Author: "+str(article.get("author"))+"\n"
    ret+="Title: "+ str(article.get("title"))+"\n"
    ret+="Description: "+ str(article.get("description"))+"\n"
    ret+="Url: "+ str(article.get("url"))+"\n"
    ret+="Publish date: "+ str(article.get("publishedAt"))+"\n"
  except:
    ret+="No hay noticias en el momento..."
    pass
  return ret

def existe_nueva(noticias_v, noticias_n, suscritos):
  lista=[]
  try:
    for noticia_n in noticias_n:
      if (noticia_n not in noticias_v):
        lista.append(noticia_n)
  except:
    pass
  if (len(lista)>0):
      for noti in lista:
        nueva_noticia=transformar_noticia(noti)
        print (f"Hay que enviar {nueva_noticia}")
        p = multiprocessing.Process(target=notificar_nueva_noticia, args=(suscritos, nueva_noticia))
        p.start()

# Esto debe de ejecutarse en un proceso aparte
def nueva_noticia(noticias, suscritos, func):
  while True:
    sleep(300) #Cada 5 min
    print("Buscar noticias...")
    news=func(keys[cont])
    incrementar_cont()
    p = multiprocessing.Process(target=
    existe_nueva, args=(noticias, news, suscritos))
    p.start()
    noticias=news
      
# Esto se debe ejecutar en proceso/hilo aparte
def enviar_noticia(suscriptor, noticia):
  global updater
  print (f"Enviando {noticia} a {suscriptor}")
  updater.bot.send_message(chat_id=suscriptor, text=noticia)

# Esto debe ejecutarse en un proceso aparte
def notificar_nueva_noticia(suscriptores, noticia):
  for suscriptor in suscriptores:
    hilo=threading.Thread(target=enviar_noticia, args=(suscriptores[suscriptor], noticia))
    hilo.start()

def iniciar_busqueda():
  global actualSeeker, noticias, suscritos, getXataka_GenbetaNews
  try:
    if (actualSeeker!=-1):
      os.kill(actualSeeker, SIGSTOP)
  except:
    pass
  finally:
    p = multiprocessing.Process(target=nueva_noticia, args=(noticias, suscritos, getXataka_GenbetaNews))
    p.start()
    print ("Running new process")
    while (not p.is_alive()):
      print ("Process not alive")
    actualSeeker=p.pid
    print ("New process started")

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Bienvenidos al bot de noticias de tecnología de las fuentes Genbeta y Xataka. Este bot está pensado para hispanohablantes"+"🇪🇸")
    suscribirse(update, context)

def help(update: Update, context: CallbackContext):
    update.message.reply_text("Este bot entiende por el momento tres comandos:")
    update.message.reply_text(
        "1. suscribirse --> Este comando suscribe al usuario a la lista de usuarios que reciben una actualización de noticias cada cierto tiempo"
    )
    update.message.reply_text(
        "2. nueva --> Este comando envia al usuario la noticia más reciente que encuentre en las fuentes previamente mencionadas"
    )
    update.message.reply_text(
        "3. ver --> Este comando envia al usuario las noticias que hasta el momento se encuentren en las fuentes previamente mencionadas"
    )

def ver(update:Update, context: CallbackContext):
  chat_id=update.message.chat_id
  for noticia in noticias:
      enviar_noticia(chat_id, transformar_noticia(noticia))

def in_suscritos(username):
  global suscritos
  for suscriptor in (suscritos):
    if (suscriptor==username):
      return True
  return False

def suscribirse(update: Update, context: CallbackContext):
  global suscritos, SIGSTOP
  username=update.message.from_user.username
  if (not in_suscritos(username)):
    chat_id=update.message.chat_id
    global db, noticias
    suscritos[username]=chat_id
    db[username]=chat_id  
    update.message.reply_text("Suscrito con éxito ✌️✌️✌️")
    update.message.reply_text("Noticias hasta ahora️")
    for noticia in noticias:
      enviar_noticia(chat_id, transformar_noticia(noticia))
    iniciar_busqueda()
  else:
    update.message.reply_text("Ya se encuentra suscrito 🦾🦾🦾")
  try:
    if (actualSeeker==-1):
      iniciar_busqueda()
  except:
    pass

def nueva(update: Update, context: CallbackContext):
  global cont
  enviar_noticia(update.message.chat_id, transformar_noticia(noticias[cont%len(noticias)]))

NEWS_API_KEY = os.environ['NEWS_API_KEY']
NEWS_API_KEY2 = os.environ['NEWS_API_KEY2']
NEWS_API_KEY3 = os.environ['NEWS_API_KEY3']
NEWS_API_KEY4 = os.environ['NEWS_API_KEY4']
NEWS_API_KEY5 = os.environ['NEWS_API_KEY5']
NEWS_API_KEY6 = os.environ['NEWS_API_KEY6']
NEWS_API_KEY7 = os.environ['NEWS_API_KEY7']
NEWS_API_KEY8 = os.environ['NEWS_API_KEY8']
NEWS_API_KEY9 = os.environ['NEWS_API_KEY9']
NEWS_API_KEY10 = os.environ['NEWS_API_KEY10']
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
keys=[NEWS_API_KEY, NEWS_API_KEY2, NEWS_API_KEY3, NEWS_API_KEY4, NEWS_API_KEY5,NEWS_API_KEY6, NEWS_API_KEY7, NEWS_API_KEY8, NEWS_API_KEY9, NEWS_API_KEY10]
cont=randint(0, len(keys)-1)
updater = Updater(token=TELEGRAM_BOT_TOKEN)
noticias=getXataka_GenbetaNews(keys[cont])
incrementar_cont()
suscritos = fetch_suscritos()
actualSeeker=-1
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('suscribirse', suscribirse))
updater.dispatcher.add_handler(CommandHandler('nueva', nueva))
updater.dispatcher.add_handler(CommandHandler('ver', ver))
updater.start_polling()
print ("Bot alive")
iniciar_busqueda()
from keep_alive import keep_alive
keep_alive()