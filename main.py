
import os, requests, threading, multiprocessing
from time import sleep
from replit import db
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from signal import SIGSTOP
from copy import deepcopy, copy

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

NEWS_API_KEY = os.environ['NEWS_API_KEY']
NEWS_API_KEY2 = os.environ['NEWS_API_KEY2']
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
keys=[NEWS_API_KEY2]
cont=0
updater = Updater(token=TELEGRAM_BOT_TOKEN)
noticias=getXataka_GenbetaNews(NEWS_API_KEY)
suscritos = fetch_suscritos()
actualSeeker=-1

def incrementar_cont():
  global cont, keys
  cont+=1
  cont%=len(keys)

def transformar_noticia(article):
  ret="\n"
  try:
    ret+="From:"+ str(article.get("source").get("name"))+"\n"
    ret+="Author:"+ str(article.get("author"))+"\n"
    ret+="Title:"+ str(article.get("title"))+"\n"
    ret+="Description:"+ str(article.get("description"))+"\n"
    ret+="Url:"+ str(article.get("url"))+"\n"
    ret+="Publish date:"+ str(article.get("publishedAt"))+"\n"
  except:
    ret+="No hay noticias en el momento..."
    pass
  return ret

def existe_nueva(noticias_v, noticias_n):
  if ((noticias_n is not None and noticias_v is None) or (noticias_n[0] not in noticias_v)):
    return True
  return False

# Esto debe de ejecutarse en un proceso aparte
def nueva_noticia(noticias, suscritos, func):
  while True:
    sleep(1080) #Cada 18 min
    news=func(keys[cont])
    incrementar_cont()
    if (news is not None and (noticias is None or existe_nueva(noticias, news))):
      nueva_noticia=transformar_noticia(news[0])
      p = multiprocessing.Process(target=notificar_nueva_noticia, args=(suscritos, nueva_noticia))
      p.start()
      noticias=news
      try:
        os.kill(p.pid, SIGSTOP)
      except:
        pass

# Esto se debe ejecutar en proceso/hilo aparte
def enviar_noticia(suscriptor, noticia):
  global suscritos
  suscritos[suscriptor][0].message.reply_text(noticia)

# Esto debe ejecutarse en un proceso aparte
def notificar_nueva_noticia(suscriptores, noticia):
  for suscriptor in suscriptores:
    hilo=threading.Thread(target=enviar_noticia, args=(suscriptor, noticia))
    hilo.start()

def iniciar_busqueda():
  global actualSeeker, noticias, suscritos, getXataka_GenbetaNews
  try:
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
    update.message.reply_text("Este bot entiende por el momento dos comandos:")
    update.message.reply_text(
        "1. suscribirse --> Este comando suscribe al usuario a la lista de usuarios que reciben una actualización de noticias cada cierto tiempo"
    )
    update.message.reply_text(
        "2. nueva --> Este comando envia al usuario la noticia más reciente que encuentre en las fuentes previamente mencionadas"
    )

def in_suscritos(username):
  global suscritos
  for suscriptor in (suscritos):
    if (suscriptor==username):
      return True
  return False

def suscribirse(update: Update, context: CallbackContext):
  global suscritos, db
  username=deepcopy(update.message.from_user.username)
  if (not in_suscritos(username)):
    suscritos[username]=copy(update)
    db=suscritos
    update.message.reply_text("Suscrito con éxito ✌️✌️✌️")
    iniciar_busqueda()
  else:
    update.message.reply_text("Ya se encuentra suscrito 🦾🦾🦾")

def nueva(update: Update, context: CallbackContext):
    update.message.reply_text(transformar_noticia(getXataka_GenbetaNews(NEWS_API_KEY, latest=True)))

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('suscribirse', suscribirse))
updater.dispatcher.add_handler(CommandHandler('nueva', nueva))
updater.start_polling()
print ("Bot alive")
from keep_alive import keep_alive
keep_alive()