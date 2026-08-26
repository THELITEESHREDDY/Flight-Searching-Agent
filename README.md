# Flight Booking Agent

A no-framework flight-search agent built around LLM tool calling, SerpApi Google Flights, and deterministic Python functions.

The goal is to understand and implement the core mechanics of an AI agent without using an agent framework.

## Architecture

```text
User
  |
  v
LLM
  |
  | tool call
  v
Agent Runtime
  |
  +--> search_flights()
  |       |
  |       v
  |     SerpApi / Google Flights
  |
  +--> compare_flights()
  |
  v
Tool result
  |
  v
LLM
  |
  v
Final response
```

The LLM decides which tool to call and with which arguments. Python executes tools, calls APIs, validates arguments, maintains conversation state, and compares flight results.

## Project Structure

```text
flight-booking-agent/
├── agent.py
├── tools.py
├── schemas.py
├── .env
├── .gitignore
└── README.md
```

### `agent.py`
Custom agent runtime: conversation state, LLM calls, tool-call handling, execution, and the agent loop.

### `tools.py`
Actual Python tools:

```python
search_flights()
compare_flights()
```

### `schemas.py`
JSON schemas exposed to the LLM.

Important:

```text
Tool schema != Python function
```

The schema goes to the LLM, while actual Python functions are kept in a registry:

```python
TOOL_FUNCTIONS = {
    "search_flights": search_flights,
    "compare_flights": compare_flights,
}
```

## Setup

```bash
python3 -m venv env
source env/bin/activate
pip install huggingface_hub python-dotenv serpapi
```

Create `.env`:

```env
AI_KEY=your_huggingface_token
SERP_API=your_serpapi_key
```

Never commit `.env`.

Example `.gitignore`:

```gitignore
.env
env/
__pycache__/
```

## LLM

The current implementation uses Hugging Face's `InferenceClient`:

```python
from huggingface_hub import InferenceClient

client = InferenceClient(
    api_key=AI_KEY,
    model="openai/gpt-oss-20b"
)
```

The selected model/provider must support tool/function calling.

## Flight Search Tool

The basic function:

```python
def search_flights(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str | None = None,
    currency: str = "INR",
    hl: str = "en",
):
    params = {
        "engine": "google_flights",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "currency": currency,
        "hl": hl,
    }

    if return_date:
        params["return_date"] = return_date

    return client.search(params)
```

Example structured arguments:

```json
{
  "departure_id": "BLR",
  "arrival_id": "HYD",
  "outbound_date": "2026-08-27",
  "return_date": null,
  "currency": "INR",
  "hl": "en"
}
```

## Required vs Optional Parameters

Required user intent:

```text
departure_id
arrival_id
outbound_date
```

If one is missing, the agent should ask the user rather than inventing a value.

Optional defaults:

```text
return_date = null
travel_class = "1"
adults = "1"
stops = "0"
currency = "INR"
hl = "en"
```

The key rule is:

> Defaults are for optional preferences, not missing core travel intent.

Example:

```text
User:
Find flights from BLR to HYD

Agent:
What date would you like to travel?
```

## System Prompt

A suitable system prompt:

```python
SYSTEM_PROMPT = f'''
You are a flight-search agent.

Today's date is {date.today()}.

Rules:

1. Extract flight information from the user's request.
2. Convert city names to IATA airport codes when unambiguous.
3. Convert relative dates such as "tomorrow" into YYYY-MM-DD.
4. Never invent missing information.
5. departure_id, arrival_id, and outbound_date are REQUIRED.
6. If any required parameter is missing, DO NOT call search_flights.
7. Ask the user for the missing required information.
8. Optional parameters should use their defaults.
9. return_date defaults to null.
10. travel_class defaults to "1".
11. adults defaults to "1".
12. stops defaults to "0".
13. currency defaults to "INR".
14. hl defaults to "en".
'''
```

## Agent Tool-Calling Loop

The core loop is:

```text
User request
    |
    v
LLM receives messages + tool schemas
    |
    v
LLM returns tool call
    |
    v
Validate arguments
    |
    v
Execute Python function
    |
    v
Append assistant tool-call message
    |
    v
Append tool result
    |
    v
Call LLM again
    |
    v
Final response OR another tool call
```

The assistant's tool-call message must be preserved before the tool result:

```python
self.messages.append(response_message)

self.messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "name": function_name,
    "content": json.dumps(result, default=str)
})
```

## Important Debugging Lessons

### 1. Use `json.loads()`

Tool arguments are JSON strings.

Correct:

```python
function_args = json.loads(
    tool_call.function.arguments
)
```

Incorrect:

```python
function_args = json.load(
    tool_call.function.arguments
)
```

`json.load()` expects a file-like object.

### 2. Tool schemas must contain dictionaries

Correct:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "...",
            "parameters": {...}
        }
    }
]
```

Do not put the actual Python function in the schema:

```python
{
    "type": "function",
    "function": search_flights
}
```

Python function objects are not JSON serializable.

### 3. Avoid accidentally nested schemas

If:

```python
tool_schema = [
    {...},
    {...}
]
```

use:

```python
tools = tool_schema
```

not:

```python
tools = [tool_schema]
```

The latter creates a list containing another list and can cause:

```text
'tools.0': value must be an object
```

### 4. Validate arguments before executing

A model can attempt a tool call with incomplete arguments.

Example:

```json
{
  "departure_id": "BLR",
  "arrival_id": "HYD",
  "return_date": null
}
```

but `outbound_date` is required.

Use:

```python
REQUIRED_ARGS = {
    "search_flights": [
        "departure_id",
        "arrival_id",
        "outbound_date"
    ]
}

required = REQUIRED_ARGS.get(function_name, [])

missing = [
    arg
    for arg in required
    if arg not in function_args
    or function_args[arg] is None
]
```

Do not execute the function until required arguments are available.

## Flight Comparison

SerpApi results can contain:

```text
best_flights
other_flights
```

Combine them:

```python
def get_all_flights(results):
    flights = []

    flights.extend(results.get("best_flights", []))
    flights.extend(results.get("other_flights", []))

    return flights
```

Then normalize the raw response into a stable structure:

```python
{
    "price": 4500,
    "stops": 0,
    "duration_minutes": 135,
    "airline": "IndiGo",
    "flight_numbers": ["6E123"],
    "departure": {
        "airport": "BLR",
        "time": "09:10"
    },
    "arrival": {
        "airport": "HYD",
        "time": "11:25"
    }
}
```

The comparison function can then sort by:

```text
price
duration
stops
```

Example:

```python
def compare_flights(
    results,
    sort_by="price",
    max_stops=None,
    limit=10
):
    raw_flights = []

    raw_flights.extend(results.get("best_flights", []))
    raw_flights.extend(results.get("other_flights", []))

    flights = []

    for raw in raw_flights:
        flight = normalize_flight(raw)

        if flight is None:
            continue

        if (
            max_stops is not None
            and flight["stops"] > max_stops
        ):
            continue

        flights.append(flight)

    if sort_by == "price":
        flights.sort(key=lambda x: x["price"])
    elif sort_by == "duration":
        flights.sort(key=lambda x: x["duration_minutes"])
    elif sort_by == "stops":
        flights.sort(key=lambda x: x["stops"])

    return flights[:limit]
```

The LLM can translate user preferences:

```text
"cheapest"       -> price
"fastest"        -> duration
"fewest stops"   -> stops
```

The actual ranking should remain deterministic Python code.

## Example Interaction

User:

```text
Find me a flight from BLR to HYD tomorrow.
```

LLM tool call:

```json
{
  "name": "search_flights",
  "arguments": {
    "departure_id": "BLR",
    "arrival_id": "HYD",
    "outbound_date": "2026-08-27",
    "return_date": null,
    "currency": "INR",
    "hl": "en"
  }
}
```

Python executes:

```text
search_flights()
      |
      v
SerpApi
      |
      v
Google Flights
```

Then the result goes back to the LLM.

If the user asks:

```text
Show me the cheapest ones.
```

the model can request:

```json
{
  "name": "compare_flights",
  "arguments": {
    "sort_by": "price",
    "max_stops": null,
    "limit": 5
  }
}
```

## Current Debugging Case

A previous execution showed:

```text
Executing: search_flights
Arguments:
{
    'arrival_id': 'HYD',
    'departure_id': 'BLR',
    'return_date': None
}
```

followed by:

```text
Executing: search_flights
Arguments:
{
    'arrival_id': 'HYD',
    'departure_id': 'BLR',
    'outbound_date': '2026-08-27',
    'return_date': None
}
```

The first call is invalid because `outbound_date` is missing.

The second call is valid.

The agent should validate arguments before execution so the invalid call never reaches `search_flights()`.

If the valid call still produces no useful result, inspect the raw SerpApi response:

```python
results = client.search(params)
print(results)
return results
```

This separates an external search problem from an agent/result-processing problem.

## Design Principles

### LLM responsibilities

Use the LLM for:

- Natural-language understanding
- Parameter extraction
- Tool selection
- User preference interpretation
- Final response generation

### Python responsibilities

Use Python for:

- Tool execution
- External API calls
- Argument validation
- State management
- Data normalization
- Sorting and comparison
- Error handling

### External API responsibilities

Use SerpApi for live Google Flights search data.

The LLM should not be treated as the source of live flight information.

## Roadmap

### Phase 1 — Flight Search

- [x] LLM tool calling
- [x] SerpApi integration
- [x] Structured flight parameters
- [x] Custom no-framework agent loop
- [ ] Robust required-argument validation
- [ ] Missing-information handling

### Phase 2 — Flight Comparison

- [x] Collect `best_flights`
- [x] Collect `other_flights`
- [ ] Normalize results
- [ ] Remove duplicates
- [ ] Cheapest ranking
- [ ] Fastest ranking
- [ ] Fewest-stops ranking
- [ ] User-preference ranking

### Phase 3 — Agent Reliability

- [ ] Tool error handling
- [ ] API timeout handling
- [ ] Retry logic
- [ ] Invalid tool-call recovery
- [ ] Conversation state
- [ ] Better structured outputs

### Phase 4 — Booking

- [ ] Select a flight
- [ ] Show booking provider
- [ ] Collect passenger information
- [ ] Confirm booking details
- [ ] Redirect to booking provider

### Phase 5 — Production

- [ ] Persistent state
- [ ] Caching
- [ ] Observability
- [ ] Rate limiting
- [ ] Authentication
- [ ] Database
- [ ] Background tasks
- [ ] Cost monitoring

## Core Learning Goal

This project is intentionally built without an agent framework.

The goal is to understand the primitives underneath agent frameworks:

```text
Natural Language
       |
       v
Structured Intent
       |
       v
Tool Selection
       |
       v
Function Execution
       |
       v
External Data
       |
       v
Tool Result
       |
       v
LLM
       |
       +----> Next Tool
       |
       +----> Final Answer
```

Once this loop is understood, frameworks become abstractions over concepts you already understand.
