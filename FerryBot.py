import sys
import os
import telepot
import datetime
import time
import picamera
from subprocess import check_call, CalledProcessError
import scrollphathd
from scrollphathd.fonts import font5x5, font5x7


"""
Ctrl-C per uscire.
"""
 
id_a = [45170836,11111111,22222222] # lista ID autorizzati
 
class FerryBot(telepot.Bot):
    def __init__(self, access_token): # il codice telegram e' passato come argomento
        telepot.Bot.__init__(self, access_token) # inizializza il bot
        self.camera = picamera.PiCamera()        # inizializza la camera
        self.listening_since = time.time()       # ora di inizio attivita' del bot
        self.request_count = 0                   # conteggio richeste
        self.invalid_users_count = 0             # conteggio utenti non autorizzati 
        self.clockDisplay = False               # mostra l'orologio sul display
        self.textMessageDisplay = False         # mostra il messaggio di testo sul display
        self.pulisciDisplay = False             # spegne il display (cancella)
        # Set some camera options if needed
        # self.camera.vflip = True
        # self.camera.hflip = True
        return
        
    """ gestisce i messaggi in arrivo """
    def handle(self, msg):
        chat_id = msg['from']['id']
        user_name = "%s %s" % (msg['from']['first_name'], msg['from']['last_name'])
        command = msg['text']
        self.request_count += 1
        sender = msg['from']['id']
     
        print 'Ricevuto un comando: %s' % command
        
        if sender in id_a:
            if   command == '/ciao':
                self.sendMessage(chat_id, 'Ciao!')

            elif command == '/foto':
                self.sendMessage(chat_id, "Adesso ti faccio una foto.")
                self.sendMessage(chat_id, "Sei pronto? Guarda il display.")
                self.DisplayOff()
                # cancella immagine precedente
                try:
                    os.remove('image.jpg')
                except OSError:
                    pass
                    
                self.camera.resolution = (1920, 1080)
                time.sleep(0.5)
                self.countdown()
                self.clic()
                time.sleep(0.2)
                self.camera.capture('image.jpg')
                time.sleep(0.8)
                self.DisplayOff()
                
                self.sendMessage(chat_id, "Fatto!")
                self.sendMessage(chat_id, "Attendi un attimo per il caricamento...")
                f = open('image.jpg', 'rb')
                self.sendPhoto(chat_id, f)                

            elif command == '/video':
                self.sendMessage(chat_id, "Ora ti faccio un filmato di 5 secondi.")
                self.sendMessage(chat_id, "Sei pronto? Guarda il display.")
                self.DisplayOff()
                # cancella video precedente
                try:
                    os.remove('video.h264')
                except OSError:
                    pass
                try:
                    os.remove('video.mp4')
                except OSError:
                    pass
                    
                self.camera.resolution = (1280, 720)
                time.sleep(0.5)
                self.countdown()
                self.camera.start_recording('video.h264')
                self.recblink()
                #self.camera.wait_recording(5)
                self.camera.stop_recording()
                self.endrec()
                time.sleep(1)
                self.DisplayOff()
                self.sendMessage(chat_id, "Fatto!")
                self.sendMessage(chat_id, "Attendi qualche secondo per il caricamento...")

                cmd = ['MP4Box', '-add', 'video.h264', 'video.mp4']
                try:
                    check_call(cmd)
                    f = open('video.mp4', 'rb')                
                    self.sendVideo(chat_id, f)
                except CalledProcessError:
                    self.sendMessage(chat_id, 'A problem occured!')                
                
            elif command == '/orologio':
                self.sendMessage(chat_id, "Guarda l'orologio sul display")
                self.clockDisplay = True

            elif command == '/nodisplay':
                self.sendMessage(chat_id, "Spengo il display")
                self.clockDisplay = False
                self.pulisciDisplay = True
                
            elif command == '/status':
                durata = int(time.time() - self.listening_since)
                self.sendMessage(chat_id, 'FerryBot in ascolto da %d secondi' % durata)
                self.sendMessage(chat_id, 'Numero delle richieste gestite: %s' % self.request_count)
                self.sendMessage(chat_id, 'Numero dei tentativi di utenti non autorizzati: %s' % self.invalid_users_count)
                
            else:
                self.sendMessage(chat_id, "Scrivo il tuo messaggio sul display")
                self.DisplayOff()
                
                scrollphathd.rotate(0)
                scrollphathd.clear()
                scrollphathd.set_brightness(0.7)
                textMessage = command + "____"
                scrollphathd.write_string(textMessage, x=0, y=0, font=font5x7)
                scrollphathd.show()
                time.sleep(0.4)
                self.clockDisplay = False
                self.textMessageDisplay = True

        else: # utente non nella lista degli autorizzati
            self.invalid_users_count += 1
            self.sendMessage(chat_id, 'Io non ti conosco!')
            self.sendMessage(chat_id, sender) # invia l'ID del chiamante per poterlo inserire fra gli utenti registrati
        return
        
    def clock(self):
        scrollphathd.set_brightness(0.3)
        scrollphathd.rotate(270)
        scrollphathd.clear()
        # Ore
        scrollphathd.write_string(time.strftime("%H"),x=0,y=0,font=font5x5)
        # Minuti
        scrollphathd.write_string(time.strftime("%M"),x=0,y=6,font=font5x5)
        # Secondi
        scrollphathd.write_string(time.strftime("%S"),x=0,y=12,font=font5x5)
        scrollphathd.show()
        return

    def DisplayScroll(self):
        scrollphathd.show()
        scrollphathd.scroll()
        return

    def DisplayOff(self):
        self.clockDisplay = False
        self.textMessageDisplay = False
        scrollphathd.clear()
        scrollphathd.show()
        return

    def countdown(self):    
        scrollphathd.set_brightness(0.3)
        scrollphathd.rotate(0)
        # 3 - 2 - 1
        scrollphathd.clear()
        scrollphathd.write_string('3', x=6, y=0, font=font5x7)
        scrollphathd.show()
        time.sleep(1)
        scrollphathd.clear()
        scrollphathd.write_string('2', x=6, y=0, font=font5x7)
        scrollphathd.show()
        time.sleep(1)
        scrollphathd.clear()
        scrollphathd.write_string('1', x=7, y=0, font=font5x7)
        scrollphathd.show()
        time.sleep(1)
        return

    def clic(self):    
        scrollphathd.set_brightness(0.4)
        scrollphathd.rotate(0)
        scrollphathd.clear()
        scrollphathd.write_string('c', x=0, y=0)
        scrollphathd.write_string('l', x=5, y=0)
        scrollphathd.write_string('i', x=9, y=0)
        scrollphathd.write_string('c', x=12, y=0)
        scrollphathd.show()
        return

    def recblink(self):    
        scrollphathd.set_brightness(0.15)
        scrollphathd.rotate(0)
        for i in range(5):
            scrollphathd.clear()
            scrollphathd.write_string('REC', x=0, y=0)
            scrollphathd.show()
            time.sleep(0.7)
            scrollphathd.clear()
            scrollphathd.show()
            time.sleep(0.3)
        return

    def endrec(self):
        scrollphathd.set_brightness(0.3)
        scrollphathd.rotate(0)
        scrollphathd.clear()
        scrollphathd.write_string('ok', x=3, y=0)
        scrollphathd.show()
        return

        
#start the app/webserver
if __name__ == "__main__":
    bot = FerryBot('407932832:AAHQhAfKV7oIVIcGQ_L4Q0H_iLT4NV0WLx8')
    bot.message_loop(bot.handle)
    print 'Ok, Sono in ascolto...'
    # ciclo infinito
    while True:
        time.sleep(0.05)
        if bot.clockDisplay:
            bot.clock()
        elif bot.textMessageDisplay:
            bot.DisplayScroll()
        
        if bot.pulisciDisplay:
            bot.DisplayOff()
            bot.pulisciDisplay = False
