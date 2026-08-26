import serpapi,os,dotenv,json


dotenv.load_dotenv()
api_key = os.environ.get("SERP_API")

client = serpapi.Client(api_key=api_key)






def search_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None = None,
    currency: str = "INR",
    hl: str = "en",
):

    """
        get all flights between src and destination
    """
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "currency": currency,
        "hl": hl,
        "stops":3
    }

    # Only include return_date when the user requested a return flight
    if return_date:
        params["return_date"] = return_date

    results = client.search(params)
    string_result=json.dumps(results.__dict__, indent=4, default=str)

    print("\n\n",string_result)
    return string_result

# results = search_flights(
#     departure_id="DEL",
#     arrival_id="HYD",
#     outbound_date="2026-08-27",
#     return_date="2026-09-02",
# )
# print(results)
# string_result=json.dumps(results.__dict__, indent=4, default=str)
# string_result1 = json.dumps(results.data, indent=4)
# print("\n\n\n",string_result,"\n\n\n\n",string_result1)
# with open("example.txt", "w", encoding="utf-8") as file:
#     file.write(string_result)






def compare_flights(results, limit=10):
    """
        compare flights based on the cost 
    """
    raw_flights = []

    raw_flights.extend(results.get("best_flights", []))
    raw_flights.extend(results.get("other_flights", []))

    normalized = []
    # Cheapest first
    normalized.sort(
        key=lambda x: x["price"]
    )

    return normalized[:limit]