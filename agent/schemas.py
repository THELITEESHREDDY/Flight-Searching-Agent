from pydantic import BaseModel
import enum


class ChatRole(enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"



class FlightSearchParams(BaseModel):
    departure_id: str
    arrival_id: str
    journey_date: str
    return_date: str | None=None
    travel_class: str = "1"
    adults: str = "1"
    currency: str = "INR"
    hl: str = "en"

class ModelResponse(BaseModel):
    id: str
    role: str
    content: str

tool_schema = [

    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search for flights between two airports.",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure_id": {
                        "type": "string"
                    },
                    "arrival_id": {
                        "type": "string"
                    },
                    
                    "journey_date": {
                        "type": "string"
                    }
                },
                "required": [
                    "departure_id",
                    "arrival_id",
                    "journey_date"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "compare_flights",
            "description": "Compare and rank flight results.based on cost",
            "parameters": {
                "type": "object",
                "properties": {
                    "data" :{
                        "type" : "object"
                    }
                },
                "required": [
                    "data"
                ]
            }
        }
    }

]