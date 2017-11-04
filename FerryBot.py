import sys
import os
import telepot
import datetime
import time
 
"""
Ctrl-C per uscire.
"""
 
id_a = [45170836,4444444,5555555]
 
def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    sender = msg['from']['id']
 
 
    print 'Got command: %s' % command
    
    if sender in id_a:
        if   command == '/ciao':
            bot.sendMessage(chat_id, 'Ciao Raf!')
        elif command == '/foto':
            #os.system("sudo python /home/pi/FerryBot/takephoto.py")
            bot.sendMessage(chat_id, "Ancora non sono pronto, ma presto lo saro'")
        elif command == '/video':
            #bot.sendMessage(chat_id, 'Riavvio in corso...')
            bot.sendMessage(chat_id, "Ancora non sono pronto, ma presto lo saro'")
        elif command == '/testo':
            bot.sendMessage(chat_id, "Ancora non sono pronto, ma presto lo saro'")
    else:
        bot.sendMessage(chat_id, 'Io non prendo ordini da nessuno!')
        bot.sendMessage(chat_id, sender) # invia l'ID del chiamante per poterlo inserire fra gli utenti registrati
 
bot = telepot.Bot('407932832:AAHQhAfKV7oIVIcGQ_L4Q0H_iLT4NV0WLx8')
bot.message_loop(handle)
print 'Ok, Sono in ascolto...'
 
while True:
    time.sleep(1)
