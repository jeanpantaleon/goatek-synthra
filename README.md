# GOATEK-SYNTHRA

Projet réalisé dans le cadre de l'UE LIFPROJET en L3 informatique à l'Université Claude Bernard Lyon 1

Le projet repose sur un modèle de langage en utilisant le logiciel [Ollama](https://ollama.com/) et la librairie [LangChain](https://www.langchain.com/)

### Objectifs

Goatek Synthra agit comme votre **secrétaire numérique**

### Fonctionnalités
- Tri des mails en spam
- Ajouts des rendez-vous dans le calendrier
- Discuter avec le modèle pour avoir des informations sur les mails : dates, thèmes...

### Comment installer ?

**Attention, le programme nécéssite un ordinateur suffisamment puissant pour faire tourner un modèle**

***

1) Cloner le dépôt et s'y mettre 

```shell
git clone https://forge.univ-lyon1.fr/p2210217/goatek-synthra.git
cd goatek-synthra
```

2) Installer [Ollama](https://ollama.com/download/)
3) Télécharger le modèle `llama3.1` via `ollama pull llama3.1`
8) Installer le modèle et créer l'environnement virtuel python avec `.\install.bat`
9) Et lancer le programme !