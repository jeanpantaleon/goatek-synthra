import embedding
import json
from imap_tools import MailBox, MailMessage, AND
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List

import llm_utils

import mails_utils
from bdd import ajout_mail_bdd, retirer_mail_bdd, ajouter_theme
from log_utils import print_in_file

def analyse_mail(mail: MailMessage, mailbox: MailBox, fichier_log : str):
    print_in_file("J'analyse le mail : " + str(mail.uid))

    # Parsing du contenu du mail s'il est en html
    if mail.html:
        soupe = BeautifulSoup(mail.html, 'html.parser')
        text = soupe.get_text()
    else:
        text = mail.text
        
    # Enregistrement du mail dans la base de donnée
    ajout_mail_bdd(mail.uid, mail.date, mail.subject, text, mailbox.folder.get())

    # Vérification de si le mail est spam ou non
    msgToLlm = "[{content :" + text +"}]"
    result = llm_utils.verification_spam(msgToLlm)

    # Si le mail est un spam
    if(result):
        # Ici, on bouge le mail dans le fichier spam
        mails_utils.moveInFolder(mail.uid)
        retirer_mail_bdd(mail.uid)

    else:
        # Extraction du thème
        embedding_json = json.dumps(embedding.embed_query(llm_utils.generation_theme(msgToLlm)))
        ajouter_theme(mail.uid, embedding_json)

    # Récupération des rendez-vous
    llm_utils.enregistrer_rendezvous(text)

    print_in_file("Analyse finie pour : " + str(mail.uid))
    
    return True

def attends_mail(mailbox: MailBox, fichier_log: str) -> List[MailMessage]:
    responses = mailbox.idle.wait(timeout=30)
    if responses:
        print_in_file("Nouveau(x) mail(s) reçu(s).")
        return mailbox.fetch(AND(date=datetime.now().date()))            
    else:
        print_in_file("Pas de nouveau mail en 30 secondes.")