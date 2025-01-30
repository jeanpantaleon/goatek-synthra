from threading import Thread, Event, current_thread, main_thread
from imap_tools import MailBox, MailMessage

from mail_process_util import attends_mail, analyse_mail
from log_utils import print_in_file
import bdd
import conversationnel

with open("mail_credentials.txt", "r") as credentials:
    username = credentials.readline()
    password = credentials.readline()

should_stop = False
conversation_done = Event()

def processus_analyse_mail(mail: MailMessage, mailbox: MailBox):
    try:
        analyse_mail(mail, mailbox, "./log")
    except Exception as e:
        fichier_log = open("./log", "a")
        fichier_log.write(f"Erreur lors d'une analyse : {e}.\n")
        fichier_log.close()
    

def processus_ecoute_mail():
    print("Lancement du sous-processus d'écoute.")
    global should_stop
    with MailBox('imap.gmail.com').login(username, password) as mailbox:
        while(not should_stop):
            liste_mails = attends_mail(mailbox=mailbox, fichier_log="./log")
            if liste_mails != None and liste_mails != []:
                print_in_file("Des mails ont été trouvé. Lancement des analyses.")
                for mail in liste_mails:
                    if not "vuParIa" in mail.flags:
                        # Ajout du flag "mail vu par l'ia"
                        try:
                            mailbox.flag(str(mail.uid), "vuParIa", True)
                            print_in_file(f"Drapeau 'vuParIa' ajouté pour le mail {mail.uid}.")
                        except Exception as e:
                            print_in_file(f"Erreur lors de l'ajout du drapeau pour le mail {mail.uid} : {e}")
                            return
                        Thread(target=processus_analyse_mail, name="Analyse du mail "+mail.uid, args=[mail, mailbox]).start()
                print_in_file("Tous les nouveaux mails sont en cours d'analyse. Retour à l'écoute.")

    print("Arrêt du sous-processus d'écoute.")

def processus_conversation():
    try:
        result = conversationnel.conversation()
        if result:  # Si True, signale que la conversation est terminée
            conversation_done.set()
    except EOFError:
        print("Programme arrêté par EOFError (^C sans message)")
        conversation_done.set()

if __name__ == "__main__":
    try:
        should_run = True
        print("Démarrage du programme...")
        # Ici on lance ollama comme un sous-programme de notre programme. Tout sera fonctionnel comme il faut
        """try:
            subprocess.run(["ollama", "run", "llama3.1"], shell=True, check=True)
        except subprocess.CalledProcessError:
            print("Erreur détectée. Arrêt du programme.")
            exit(1)"""
        
        # Initialisation de la bdd
        bdd.initialisation()
        
        print("Création du processus d'écoute en arrière plan...")
        t = Thread(target=processus_ecoute_mail, name="ecoute de mail")
        t.start()

        print("Démarrage du prompt local.")
        # La boucle d'intéraction utilisateur
        t2 = Thread(target=processus_conversation, name="discussion")
        t2.start()
        # question = str(input("?: "))
        # while(question != "Bye"):
        #    question = str(input("?:"))
        
        conversation_done.wait()
        print("arret du programme")
    except Exception:
        print("Erreur détectée. Arrêt du programme\n")

    # Ce except permet de passer par dessus le ^C afin de couper les sous-programmes
    except KeyboardInterrupt:
        print("Arret du programme.\n")
    
    # Que le code se soit bien passé où qu'il y ai eu erreur, on dit aux sous-programmes de s'arrêter
    should_stop = True

