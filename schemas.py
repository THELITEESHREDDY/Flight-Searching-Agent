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
                    
                    "return_date": {
                        "type": ["string", "null"]
                    }
                },
                "required": [
                    "departure_id",
                    "arrival_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "compare_flights",
            "description": "Compare and rank flight results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sort_by": {
                        "type": "string",
                        "enum": [
                            "price",
                            "duration",
                            "stops"
                        ]
                    },
                    "max_stops": {
                        "type": ["integer", "null"]
                    },
                    "limit": {
                        "type": "integer"
                    }
                },
                "required": [
                    "sort_by"
                ]
            }
        }
    }

]