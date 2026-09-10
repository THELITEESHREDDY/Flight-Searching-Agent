# Flight Searching Agent

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


### Phase 4 — Booking

- [ ] Select a flight
- [ ] Show booking provider
- [ ] Collect passenger information
- [ ] Confirm booking details
- [ ] Redirect to booking provider


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
