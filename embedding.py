from langchain_ollama import OllamaEmbeddings
import numpy as np
import sqlite3
import json
import llm_utils
from langchain_core.tools import tool


conn = sqlite3.connect('emails.db', check_same_thread=False)
cursor = conn.cursor()

embeddings = OllamaEmbeddings(
    model="llama3.1",
)

def embed_query(query):
    return embeddings.embed_query(query)

def cosine_similarity_manual(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if (norm_vec1==0 or norm_vec2==0):
        return 0
    else:
        return dot_product / (norm_vec1 * norm_vec2)

def GetMailTheme(Theme):

    MsgMail = ''
    ThemeEmb = embed_query(Theme)
    cursor.execute('''SELECT theme, corps FROM Email''')
    results = cursor.fetchall()
    
    for themeMail, corps in results:
        themeMailList = json.loads(themeMail)
        if cosine_similarity_manual(ThemeEmb, themeMailList) > 0.85:
            MsgMail += corps
        CorpsEmbList = embed_query(corps)
        if cosine_similarity_manual(ThemeEmb, CorpsEmbList) > 0.15:
            MsgMail += corps

    if not MsgMail:
        return "Je n'ai rien récupéré, désolé."
    
    # Résume les mails
    mail = llm_utils.resum_mail(MsgMail, Theme)
    return mail

@tool
def RecupMail(Theme: str) -> str:
    """Get all the mail who talk about the theme specified by the user 

    Args:
        Theme (str): The theme requested by user
    """
    return GetMailTheme(Theme)
