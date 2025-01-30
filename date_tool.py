from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from datetime import datetime, timezone, date
from langchain_ollama import ChatOllama


class DateTool(BaseModel):
    day: int = Field(description="The day of the time, 0 by default")
    month: int = Field(description="The month of the time, 0 by default")
    year: int = Field(description="The year of the time, 0 by default")
    hour: int = Field(description="The hour of the time, 0 by default")

def parse_date(day: int = datetime.now(timezone.utc).day, month: int = datetime.now(timezone.utc).month, year: int = datetime.now(timezone.utc).year, hour: int = datetime.now(timezone.utc).hour):
    """Get a formatted date to use in other tools
    
    This function is designed to gather dates from a long text, a date that you will be using in other tools and also on questions about current and differed time.
    """

    date_courante = datetime.now(timezone.utc)

    if (year == 0):
        year = date_courante.year
    if (month == 0):
        month = date_courante.month
    if (day == 0 or day >= 32):
        day = date_courante.day
    if(hour == 0 or hour >= 24):
        hour = date_courante.hour
    
    return datetime(year=year, month=month, day=day, hour=hour).isoformat('T') + 'Z'

parse_date_tool = StructuredTool.from_function(
    func=parse_date,
    name="Parse date",
    description="Get a formatted date to use in other tools",
    args_schema=DateTool,
    return_direct=False
)

def llm_parse_date(date: str) -> str:
    formatted_date = ''
    if(date != ''):
        reponse_date = ChatOllama(model="llama3.1",temperature=0).bind_tools([parse_date_tool]).invoke(f"Peux-tu me formatter cette date ? {date}")
        if reponse_date.tool_calls != []:
            formatted_date = parse_date_tool.invoke(reponse_date.tool_calls[0]["args"])
    return formatted_date

def llm_parse_date_mail(date_input: str) -> str:
    if(date_input == ''):
        return ''
    date_parsee = llm_parse_date(date_input)
    date_tmp = datetime.fromisoformat(date_parsee)
    return date(year=date_tmp.year, month=date_tmp.month, day=date_tmp.day).isoformat()



