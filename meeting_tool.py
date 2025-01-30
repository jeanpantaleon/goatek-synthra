from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from datetime import datetime, timezone

from meeting_utils import construire_rendezvous, envoyer_rendezvous

import date_tool

class RendezvousTool(BaseModel):
    name: str = Field(description="The name of the meeting")
    endroit: str = Field(description="The place of the meeting")
    debut: str = Field(description="The start time of the meeting")
    duree: float = Field(description="The length of the meeting in hour")
    description: str = Field(description="The description of the meeting, optional")

def add_meeting(name: str, endroit: str, debut: str, duree: float = 1.0, description: str = ""):
    """Add a meeting in the calendar
    
    This function is designed to add a event to the calendar of the user using the information your read.
    """
    formatted_date = date_tool.llm_parse_date(debut)
    
    resultat = envoyer_rendezvous(construire_rendezvous(name, endroit, datetime.fromisoformat(formatted_date).astimezone(timezone.utc), duree, description))
    if not resultat:
        return "Une erreur est survenue"
    else: return f"Rendez-vous {name} le {debut} ajouté !"

outil_rendezvous = StructuredTool.from_function(
    func=add_meeting,
    name="Add meeting",
    description="Add a meeting in the calendar",
    args_schema=RendezvousTool,
    return_direct=True
)