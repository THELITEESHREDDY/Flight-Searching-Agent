import serpapi,os,dotenv,json


dotenv.load_dotenv()
api_key = os.environ.get("SERP_API")

client = serpapi.Client(api_key=api_key)






def search_flights(
    departure_id: str,
    arrival_id: str,
    journey_date: str,
    return_date: str | None = None,
    currency: str = "INR",
    hl: str = "en",
) -> dict:

    """
        get all flights between src and destination
    """
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": journey_date,
        "currency": currency,
        "hl": hl,
        "stops":3
    }

    # Only include return_date when the user requested a return flight
    if return_date:
        params["return_date"] = return_date
        params["type"] = 1       # round trip
    else:
        params["type"] = 2 

    response = client.search(params)
    response_dict=response.__dict__
    data = response_dict["data"]
    routes = []

    all_routes = [
        ("best", data.get("best_flights", [])),
        ("other", data.get("other_flights", []))
    ]

    route_id = 1

    for category, flight_list in all_routes:
        for route in flight_list:

            routes.append({
                "route_id": route_id,
                "category": category,
                "flights": route.get("flights", []),
                "layovers": route.get("layovers", []),
                "total_duration": route.get("total_duration"),
                "price": route.get("price"),
                "currency": "INR",
                "type": route.get("type"),
                "airline_logo": route.get("airline_logo"),
                "carbon_emissions": route.get("carbon_emissions"),
                "departure_token": route.get("departure_token")
            })

            route_id += 1

    return {
        "routes": routes
    }


def compare_flights(data: dict) -> dict:
    routes = data.get("routes", [])

    sorted_routes = sorted(
        routes,
        key=lambda route: route.get("price", float("inf"))
    )

    return {
        "routes": sorted_routes
    }