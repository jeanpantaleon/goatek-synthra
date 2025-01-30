import llm_utils
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver  # an in-memory checkpointer
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import sqlite3
import embedding

conn = sqlite3.connect('emails.db', check_same_thread=False)
cursor = conn.cursor()

# system_message = "Tu es une ia de Chat/ToolBot lié à une base de données contenant les mails de l'utilisateur. L'utilisateur peut te demander de récupérer les mails selon un thème qu'il précisera dans sa requête. Dans ce cas là, tu utilise le tool 'RecupMail' pour lui donner le résumé que renvoie le tool. Tu as l'interdiction absolue d'inventer quoi que ce soit. Tu dois utiliser 'RecupMail' uniquement avec le theme donné par l'utilisateur et tu ne dois appeler 'RecupMail' qu'une seule fois."

def conversation():
    try: 
        system_message = """
        Tu es une IA de gestion et de recherche de mails dans une base de données. Ton rôle est d'aider l'utilisateur à trouver des mails pertinents en fonction de critères spécifiques.

        Règles et fonctionnalités :
        Recherches par thème :

        Si l'utilisateur te demande un thème, utilise l'outil RecupMail pour récupérer les mails correspondant à ce thème.
        Recherches avancées :

        Si l'utilisateur précise un ou plusieurs critères spécifiques, effectue une recherche en fonction de ces critères :
        Date précise : Trouver les mails correspondant à une date donnée.
        Expéditeur précis : Trouver les mails envoyés par une personne spécifique.
        Texte spécifique : Trouver les mails contenant un mot ou une phrase précise dans le sujet ou le corps du mail.
        Exclusivité des recherches :

        Une seule fonction de recherche peut être utilisée par requête : soit une recherche basée sur un thème, soit une recherche par critères spécifiques, mais jamais les deux en même temps.
        Résultats et réponses :

        Fournis un résumé clair et précis des mails trouvés, basé uniquement sur les résultats renvoyés.
        Ne jamais inventer ou ajouter d'informations non présentes dans les résultats.
        """

        tools = [llm_utils.getMail, embedding.RecupMail]

        chatBot = ChatOllama(
            model="llama3.1",
            temperature=0.0,
        )

        memory = MemorySaver()
        app = create_react_agent(
            chatBot, tools, state_modifier=system_message, checkpointer=memory
        )

        config = {"configurable": {"thread_id": "test-thread"}}
        question = str(input("Que puis-je faire pour vous aujourd'hui ? : "))
        while(question != "Bye"):

            print(
                app.invoke(
                    {
                        "messages": [
                            HumanMessage(content=question)
                        ]
                    },
                    config,
                )["messages"][-1].content
            )
            question = str(input("Que puis-je faire pour vous aujourd'hui ? : "))
    except KeyboardInterrupt:
        print("Arrêt conversationnel !")
    
    return True
