import os
import json

from datetime import date
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

from tools import search_flights, compare_flights
from schemas import tool_schema


load_dotenv()

AI_KEY = os.environ.get("AI_KEY")
SEARCH_KEY = os.environ.get("SERP_API")


SYSTEM_PROMPT = SYSTEM_PROMPT = f"""
You are a flight-search agent.

Today's date is {date.today()}.

Rules:

1. Extract flight information from the user's request.
2. Convert city names to IATA airport codes when unambiguous.
3. Convert relative dates such as "tomorrow" to YYYY-MM-DD.
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
"""


TOOL_FUNCTIONS = {
    "search_flights": search_flights,
    "compare_flights": compare_flights,
}
REQUIRED_ARGS = {
    "search_flights": [
        "departure_id",
        "arrival_id"
    ]
}

class Agent:

    def __init__(
        self,
        client: InferenceClient,
        system_prompt: str = "",
        tools: list | None = None
    ):
        self.client = client
        self.system_prompt = system_prompt
        self.tools = tools or []

        self.messages = []

        if self.system_prompt:
            self.messages.append({
                "role": "system",
                "content": self.system_prompt
            })

    def __call__(self, message: str = ""):

        if message:
            self.messages.append({
                "role": "user",
                "content": message
            })

        return self.execute()

    def execute(self):

        steps = 0

        while steps < 5:

            completion = self.client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto"
            )

            response_message = completion.choices[0].message

            # --------------------------------
            # No tool call -> final response
            # --------------------------------

            if not response_message.tool_calls:
                return response_message.content

            # --------------------------------
            # IMPORTANT:
            # Store assistant tool call
            # --------------------------------

            self.messages.append(response_message)

            # --------------------------------
            # Execute requested tools
            # --------------------------------

            for tool_call in response_message.tool_calls:

                function_name = tool_call.function.name

                function_args = json.loads(
                    tool_call.function.arguments
                )


                required = REQUIRED_ARGS.get(function_name, [])

                missing = [
                    arg
                    for arg in required
                        if arg not in function_args or function_args[arg] is None
                ]

                if missing:
                    print(
                        f"Missing arguments for {function_name}: {missing}"
                    )

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps({
                            "error": "missing_required_arguments",
                            "missing": missing
                        })
                    })

                    continue

                print(
                    f"\nExecuting: {function_name}"
                )

                print(
                    f"Arguments: {function_args}"
                )

                # Find actual Python function
                function_to_call = TOOL_FUNCTIONS.get(
                    function_name
                )

                if function_to_call is None:

                    tool_result = {
                        "error": f"Unknown tool: {function_name}"
                    }

                else:

                    try:

                        executed_output = function_to_call(
                            **function_args
                        )

                        tool_result = executed_output

                    except Exception as e:

                        tool_result = {
                            "error": str(e)
                        }

                # --------------------------------
                # Send tool result back to model
                # --------------------------------

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(
                        tool_result,
                        default=str
                    )
                })

            steps += 1

        return "I couldn't complete the flight search."




client = InferenceClient(
    api_key=AI_KEY,
    model="openai/gpt-oss-20b"
)

tools = tool_schema

agent = Agent(
    client,
    SYSTEM_PROMPT,
    tools
)

print(
    agent("find flights from BLR to HYD tomorrow ")
)