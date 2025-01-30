from datetime import datetime
from imap_tools import MailBox, A
from bs4 import BeautifulSoup
import json

from log_utils import print_in_file

username = ""
password = ""
 
def moveInFolder(uid, folderSource=None, folderDest=None):
    with MailBox('imap.gmail.com').login(username, password) as mailbox:
        if(folderSource != None):
            mailbox.folder.set(folderSource)
        if(folderDest != None):
            mailbox.move(uid, '[Gmail]/'+ folderDest)
        else:
            mailbox.move(uid, '[Gmail]/Spam')

def afficheFolder():
  with MailBox('imap.gmail.com').login(username, password) as mailbox:
    for f in mailbox.folder.list():
        print_in_file(f)

def intersec(l1):
    if not (l1):
        return l1
    if not (l1[1:]) :
        return l1[0]
    else:
        return list(set(l1[0]).intersection(intersec(l1[1:])))

def getMail2(arg):
    l = []
    with MailBox('imap.gmail.com').login(username, password) as mailbox:
        for msg in mailbox.fetch(arg):
            l.append(msg.uid)
    return l

def getMail(date = '', since = '', before = '', _from = '', subject = '', body = '', text = ''):
    l = []
    
    print_in_file("Utilisation de getMail avec : date = " + date + ", since =" + since + ", before = " + before + ", _from = " + _from + ", subject = " + subject + ", body = " + body + ", text = " + text)
    if(date != '' and (since == '' or before == '')):
        l.append(getMail2(A(date=datetime.fromisoformat(date).date())))
    if(since != ''):
        l.append(getMail2(A(date_gte=datetime.fromisoformat(since).date())))
    if(before != ''):
        l.append(getMail2(A(date_lt=datetime.fromisoformat(before).date())))
    if(_from != ''):
        l.append(getMail2(A(from_= _from)))
    if(subject != ''):
        l.append(getMail2(A(subject = subject)))
    if(body != ''):
        l.append(getMail2(A(body = body)))
    if(text != ''):
        l.append(getMail2(A(text=text)))
    print_in_file("UID des mails trouvés  : ")
    flog = open("./log", "a")
    json.dump(intersec(l), flog)
    flog.write("\n")
    flog.close()
    return intersec(l)

def getMailSubjectWithId(lId):
    lmsg = []
    for i in lId:
        with MailBox('imap.gmail.com').login(username, password) as mailbox:
            for msg in mailbox.fetch(A(uid=i)):
                lmsg.append(msg.subject)
    return lmsg

def getMailMessageWithId(lId):
    lmsg = []
    text = ''
    for i in lId:
        with MailBox('imap.gmail.com').login(username, password) as mailbox:
            for mail in mailbox.fetch(A(uid=i)):
                if mail.html:
                    soupe = BeautifulSoup(mail.html, 'html.parser')
                    text = soupe.get_text()
                else:
                    text = mail.text
    return text


