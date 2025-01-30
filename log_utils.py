from datetime import datetime,timezone

def print_in_file(message : str):
    fichier = open("./log", "a")
    fichier.write(f"[{datetime.now(timezone.utc)}]: {message}\n")
    fichier.close()