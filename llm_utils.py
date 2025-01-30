from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.output_parsers import BooleanOutputParser
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import mails_utils
import date_tool
import meeting_tool
from langchain_core.tools import tool
import embedding

from log_utils import print_in_file


llm = ChatOllama(
        model="llama3.1",
        temperature=0.0,
    )

def verification_spam(msgMail) -> bool | str:
    prompt = (
        "You are a Spam analyser. I will provide you with an email, and you must analyze it to determine "
        "if it is spam or not. Answer strictly with 'YES' or 'NO'. DO NOT ADD ANY OTHER TEXT! "
        "Now, analyze the following email:\n" + msgMail
    )
    
    try:
        chain = llm | BooleanOutputParser()
        result = chain.invoke(prompt)
        
        if result == True or result == False:
            return result
        else:
            raise ValueError(f"Unexpected output: {result}")
    
    except Exception as e:
        print_in_file(f"[SPAM] Erreur : {e}")
        return "ERROR"  
    
def enregistrer_rendezvous(msgMail) -> bool | str:

    prompt = (
        "You are a Meeting analyser. I will provide you with an email, and you must analyze it to determine "
        "if there is a meeting that is announced in the email or not. Answer strictly with 'YES' or 'NO'. DO NOT ADD ANY OTHER TEXT! "
        "Now, analyze the following email:\n" + msgMail
    )
    
    try:
        chain = llm | BooleanOutputParser()
        result = chain.invoke(prompt)
        
        if result == True or result == False:
            if result == True:
                prompt = ("Please register the meeting that is in this email content "+msgMail)

                chain = llm.bind_tools([meeting_tool.outil_rendezvous])
                result = chain.invoke(prompt)
                
                # Le modèle a appelé l'outil avec ToolCall et on execute l'outil pour avoir la sortie voulue
                if result.tool_calls != []:
                    output = meeting_tool.outil_rendezvous.invoke(result.tool_calls[0]["args"])
                    print(output)
                
                return output
            else:
                return "Aucun rendez-vous n'a été ajouté"
        else:
            raise ValueError(f"Unexpected output: {result}")
    
    except Exception as e:
        print_in_file(f"[RDV] Erreur : {e}")
        return "ERROR"  

def resum_mail(msgMail, theme):
    prompt = (
        "Vous êtes un professionnel du résumé de texte selon un theme recherché. L'utilisateur va vous fournir un texte et un theme. "
        "Votre seule tâche est d'extraire les informations les plus importantes du texte selon le theme, en vous concentrant spécifiquement sur "
        "les faits, les statistiques ou les points détaillés. Évitez toute forme d'interprétation, de commentaire ou de généralisation. "
        "Fournissez uniquement le contenu pertinent sous forme de points ou de phrases courtes. Si le thme n'est pas mentionné"
        "explicitement, vous devez chercher ce qui s'en rapproche le plus."
        "Voici le texte :\n" + msgMail +
        "\nEt voici le theme recherché : " + theme
    )
    try:
        result = llm.invoke(prompt)
        return result.content
    except Exception as e:
        print_in_file(f"[RESUM_MAIL] Erreur : {e}")
        return "Erreur lors du résumé."


class GetMailTool(BaseModel):
    date: str = Field(description="The exact date (YYYY-MM-DD) from which to retrieve emails. Retrieves only the emails received on this specific date.")
    since: str = Field(description="A date (YYYY-MM-DD) from which to retrieve all emails up to today. Includes emails from the specified date onwards.")
    before: str = Field(description="A date (YYYY-MM-DD) to retrieve all emails received before this date. Excludes emails from the specified date.")
    fromm: str = Field(description="contain specified str in envelope struct’s FROM field")
    subject: str = Field(description="contain specified str in envelope struct’s SUBJECT field")
    body: str = Field(description="contain specified str in body of the message")
    text: str = Field(description="contain specified str in header or body of the message")


def getMail(date : str = '', since: str = '', before: str = '', fromm: str = '', subject: str = '', body: str = '', text: str = ''):
    """Find mail corresponding to the argument
    
    """
    formatted_date = date_tool.llm_parse_date_mail(date)
    formatted_since = date_tool.llm_parse_date_mail(since)
    formatted_before = date_tool.llm_parse_date_mail(before)

    return mails_utils.getMailSubjectWithId(mails_utils.getMail(formatted_date, formatted_since, formatted_before, fromm, subject, body, text))

tool_get_Mail = StructuredTool.from_function(
    func=getMail,
    name="GetMail",
    description="Find mail corresponding to the argument",
    args_schema= GetMailTool,
    return_direct=False
)

def generation_theme(msgMail):
    question = "You are a theme detector, you receive a mail and give ONLY his theme in one or few word, this is the mail : " + msgMail
    chain = llm
    result = chain.invoke(question)

    return result.content
