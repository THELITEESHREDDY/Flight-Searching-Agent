from pydantic import BaseModel


class FlightSearchParams(BaseModel):
    departure_id: str
    arrival_id: str
    outbound_date: str
    travel_class: str = "1"
    adults: str = "1"
    stops: str = "0"
    currency: str = "INR"
    hl: str = "en"


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