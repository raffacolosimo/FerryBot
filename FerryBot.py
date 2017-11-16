import os           # per cancellare i file
import telepot      # per gestire telegram
import time         # per gestire il tempo
import picamera     # per la telecamera
from subprocess import check_call, CalledProcessError # per la conversione MP4
import scrollphathd # per il display scroll pHat HD
from scrollphathd.fonts import font5x5, font5x7 # per i font del display
import ConfigParser         # per gestione file di configurazione


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
        self.LEDscrollLeft = 0                   # numero di pixel rimasti da far scorrere
        self.FBotConfig = ConfigParser.ConfigParser()
        self.FBotConfig.read('FerryBot.ini')
        nl = self.FBotConfig.get('TELEGRAM', 'id_a').split('\n') #stringa incolonnata con id Telegram autorizzati
        self.id_a = [int(nl) for x in nl]                   # lista di id (come numeri) estratta dalla stringa precedente
        # Opzioni per la telecamera
        if   self.FBotConfig.get('CAMERA', 'vflip').split() == 'True':
            self.camera.vflip = True
        elif self.FBotConfig.get('CAMERA', 'vflip').split() == 'False':
            self.camera.vflip = False
        else:
            print 'errore nel file di configurazione per il parametro vflip'
        if   self.FBotConfig.get('CAMERA', 'hflip').split() == 'True':
            self.camera.hflip = True
        elif self.FBotConfig.get('CAMERA', 'hflip').split() == 'False':
            self.camera.hflip = False
        else:
            print 'errore nel file di configurazione per il parametro hflip'
        return

    def handle(self, msg):         #gestisce i messaggi in arrivo
        chat_id = msg['from']['id']
        user_name = "%s %s" % (msg['from']['first_name'], msg['from']['last_name'])
        completeCommand = msg['text']
        commandParam = completeCommand.split('', 1) # separa comando ed eventuale argomento
        command = commandParam[0] # comando
        param   = commandParam[1] # argomento
        self.request_count += 1
        sender = msg['from']['id']

        print 'Ricevuto un comando: %s' % command

        if sender in self.id_a:
            if   command == '/ciao':
                self.sendMessage(chat_id, 'Ciao!')
                self.LEDmessage('ciao') # messaggio LED, non in loop

            elif command == '/foto':
                self.sendMessage(chat_id, "Adesso ti faccio una foto.")
                self.sendMessage(chat_id, "Sei pronto? Guarda il display.")
                self.takePhoto()
                self.sendMessage(chat_id, "Fatto!")
                self.sendMessage(chat_id, "Attendi un attimo per il caricamento...")
                f = open('image.jpg', 'rb')
                self.sendPhoto(chat_id, f)

            elif command == '/video':
                self.sendMessage(chat_id, "Ora ti faccio un filmato di 5 secondi.")
                self.sendMessage(chat_id, "Sei pronto? Guarda il display.")
                self.makeVideo()
                self.sendMessage(chat_id, "Fatto!")
                self.sendMessage(chat_id, "Attendi qualche secondo per il caricamento...")
                # conversione MP4 e caricamento
                cmd = ['MP4Box', '-add', 'video.h264', 'video.mp4']
                try:
                    check_call(cmd)
                    f = open('video.mp4', 'rb')
                    self.sendVideo(chat_id, f)
                except CalledProcessError:
                    self.sendMessage(chat_id, "C'e' stato un problema!")

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

            elif command == '/LED':
                self.sendMessage(chat_id, "Scrivo il tuo messaggio sul display")
                textMessage = param + "____"
                self.LEDmessage(textMessage)

            else:
                self.sendMessage(chat_id, "Scrivo il tuo messaggio sul display")
                textMessage = completeCommand + "____"
                self.LEDmessage(textMessage)

        else: # utente non nella lista degli autorizzati
            self.invalid_users_count += 1
            self.sendMessage(chat_id, 'Io non ti conosco!')
            self.sendMessage(chat_id, sender) # invia l'ID del chiamante per poterlo inserire fra gli utenti registrati
        return

    def LEDmessage(self, txtMessage, loop=False):
        self.DisplayOff()
        scrollphathd.rotate(0)
        scrollphathd.clear()
        scrollphathd.set_brightness(0.5)
        scrollphathd.write_string(txtMessage, x=18, y=0, font=font5x7)
        if loop == True:
            self.textMessageDisplay = True
            self.LEDscrollLeft = 0
        else:
            self.textMessageDisplay = False
            self.LEDscrollLeft = scrollphathd.get_buffer_shape()[0]
            #print self.LEDscrollLeft
            #print self.scrollphathd.get_buffer_shape()
        scrollphathd.show()
        self.clockDisplay = False


    def clockVert(self):
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

    def clockHor(self):
        scrollphathd.set_brightness(0.5)
        scrollphathd.rotate(0)
        scrollphathd.clear()
        BRIGHTNESS = 0.3
        # prende il resto della divisione per 60 (= secondi) e lo convert nel campo 0.0-15.0
        seconds_progress = 15 * ((time.time() % 60) / 59.0) # ogni pixel sono 4 secondi
        # barra dei secondi a luminosita' variabile
        for y in range(15): # 15 = numero di pixel
            # For each pixel, we figure out its brightness by
            # seeing how much of "seconds_progress" is left to draw
            # If it's greater than 1 (full brightness) then we just display 1.
            current_pixel = min(seconds_progress, 1)
            # Multiply the pixel brightness (0.0 to 1.0) by our global brightness value
            scrollphathd.set_pixel(y + 1, 6, current_pixel * BRIGHTNESS)
            # Subtract 1 now we've drawn that pixel
            seconds_progress -= 1
            # If we reach or pass 0, there are no more pixels left to draw
            if seconds_progress <= 0:
                break
        # Display the time (HH:MM) in a 5x5 pixel font
        scrollphathd.write_string(
            time.strftime("%H:%M"),
            x=0, # Align to the left of the buffer
            y=0, # Align to the top of the buffer
            font=font5x5, # Use the font5x5 font we imported above
            brightness=BRIGHTNESS # Use our global brightness value
        )
        # int(time.time()) % 2 will tick between 0 and 1 every second.
        # We can use this fact to clear the ":" and cause it to blink on/off
        # every other second, like a digital clock.
        # To do this we clear a rectangle 8 pixels along, 0 down,
        # that's 1 pixel wide and 5 pixels tall.
        if int(time.time()) % 2 == 0:
            scrollphathd.clear_rect(8, 0, 1, 5)
        # Display our time and sleep a bit. Using 1 second in time.sleep
        # is not recommended, since you might get quite far out of phase
        # with the passing of real wall-time seconds and it'll look weird!
        #
        # 1/10th of a second is accurate enough for a simple clock though :D
        scrollphathd.show()
        return

    def countdown(self):
        scrollphathd.set_brightness(0.3)
        scrollphathd.rotate(0)
        # 3 - 2 - 1
        scrollphathd.clear()
        scrollphathd.write_string('3', x=6, y=0, font=font5x7)
        scrollphathd.show()
        time.sleep(0.75)
        scrollphathd.clear()
        scrollphathd.show()
        time.sleep(0.25)
        scrollphathd.clear()
        scrollphathd.write_string('2', x=6, y=0, font=font5x7)
        scrollphathd.show()
        time.sleep(0.75)
        scrollphathd.clear()
        scrollphathd.show()
        time.sleep(0.25)
        scrollphathd.clear()
        scrollphathd.write_string('1', x=7, y=0, font=font5x7)
        scrollphathd.show()
        time.sleep(0.75)
        scrollphathd.clear()
        scrollphathd.show()
        time.sleep(0.25)
        return

    def takePhoto(self):
        self.DisplayOff()
        scrollphathd.rotate(0)
        scrollphathd.set_brightness(0.25)
        #scorre scritta foto
        scrollphathd.clear()
        scrollphathd.write_string('foto', x=18, y=0, font=font5x7)
        scrollphathd.show()
        buffL=scrollphathd.get_buffer_shape()[0]
        time.sleep(0.5)
        for i in range(buffL+1):
            scrollphathd.show()
            scrollphathd.scroll()
            time.sleep(0.015)
        # cancella immagine precedente
        try:
            os.remove('image.jpg')
        except OSError:
            pass
        self.camera.resolution = (1920, 1080)
        time.sleep(0.25)
        self.countdown()
        # clic (piccolo flash)
        scrollphathd.clear()
        scrollphathd.set_brightness(0.7)
        scrollphathd.fill(1, x=0, y=0, width=17, height=7)
        #scrollphathd.write_string('c', x= 0, y=0)
        #scrollphathd.write_string('l', x= 5, y=0)
        #scrollphathd.write_string('i', x= 9, y=0)
        #scrollphathd.write_string('c', x=12, y=0)
        scrollphathd.show()
        #scatta la foto
        time.sleep(0.05)
        scrollphathd.clear()
        scrollphathd.show()
        # scatta la foto
        self.camera.capture('image.jpg')
        return

    def makeVideo(self):
        self.DisplayOff()
        scrollphathd.rotate(0)
        scrollphathd.set_brightness(0.25)
        #scorre scritta video
        scrollphathd.clear()
        scrollphathd.write_string('video', x=18, y=0, font=font5x7)
        scrollphathd.show()
        buffL=scrollphathd.get_buffer_shape()[0]
        time.sleep(0.5)
        for i in range(buffL+1):
            scrollphathd.show()
            scrollphathd.scroll()
            time.sleep(0.015)
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
        time.sleep(0.25)
        self.countdown()
        # registra
        self.camera.start_recording('video.h264')
        # lampeggia REC per 5 secondi
        self.recblink()
        # fine registrazine
        self.camera.stop_recording()
        # scrive ok
        self.endrec()
        time.sleep(1)
        self.DisplayOff()

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

    def DisplayScrollLoop(self):
        scrollphathd.show()
        scrollphathd.scroll()
        return
    def DisplayScrollOnce(self):
        if self.LEDscrollLeft > 0:
            self.LEDscrollLeft -= 1 # decrementa il contatore dei pixel rimasti da far scorrere
            scrollphathd.show()
            scrollphathd.scroll()
        if self.LEDscrollLeft ==0:
            scrollphathd.show()
            scrollphathd.clear()
        return

    def DisplayOff(self):
        self.clockDisplay = False
        self.textMessageDisplay = False
        self.LEDscrollLeft = 0
        scrollphathd.clear()
        scrollphathd.show()
        return

    def run(self):
        # gestisce le visualizzazioni
        while True:
            time.sleep(0.05)
            if bot.pulisciDisplay: # se e' richiesto lo spegnimento del display lo effettua
                bot.DisplayOff()
                bot.pulisciDisplay = False

            if self.clockDisplay: # se l'orologio e' attivo lo aggiorna
                self.clockHor()
            elif self.textMessageDisplay: # se e' attivo lo scroll a nastro continuo del display, lo effettua
                self.DisplayScrollLoop()
            elif self.LEDscrollLeft > 0: # se e' attivo lo scroll a singolo messaggio, lo effettua
                self.DisplayScrollOnce()

#start the app/webserver
if __name__ == "__main__":
    bot = FerryBot('407932832:AAHQhAfKV7oIVIcGQ_L4Q0H_iLT4NV0WLx8')
    bot.message_loop(bot.handle)
    print 'Ok, FerryBot in ascolto...'
    bot.run() # gestisce le visualizzazioni LED
