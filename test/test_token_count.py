import os
from openai import OpenAI
from dotenv import load_dotenv
import sys
sys.path.append(".")  # Search in the current directory and one level up
sys.path.append("..")
from common.token_count import get_token_count_with_tiktoken, get_token_count_with_dummy_completion, get_token_count

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Set up the chat messages
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Write a Tcl script that prints numbers 1 to 5."}
]

def main():
    # Make a non-streaming chat completion call
    resp1 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=False
    )
    response_content = resp1.choices[0].message.content
    non_streaming_total = resp1.usage.total_tokens
    print(f"[Non-streaming] Total tokens: {non_streaming_total}")

    # Add the assistant message to the history
    full_history = messages + [{"role": "assistant", "content": response_content}]

    # tiktoken estimate for prompt (full_history)
    tiktoken_prompt = get_token_count_with_tiktoken(full_history, model="gpt-3.5-turbo")
    print(f"[tiktoken] Estimated prompt tokens for full_history: {tiktoken_prompt}")

    # dummy call for prompt tokens
    dummy_prompt = get_token_count_with_dummy_completion(
        client.chat.completions.create,
        full_history,
        model="gpt-3.5-turbo"
    )
    print(f"[Dummy call] Prompt tokens: {dummy_prompt}")

def test_models(models):
    from tabulate import tabulate
    results = []
    for model in models:
        # Non-streaming call
        resp1 = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False
        )
        response_content = resp1.choices[0].message.content
        non_streaming_total = resp1.usage.total_tokens

        # Dummy call with full history
        full_history = messages + [{"role": "assistant", "content": response_content}]
        resp2 = client.chat.completions.create(
            model=model,
            messages=full_history,
            max_tokens=1,
            stream=False
        )
        dummy_prompt = resp2.usage.prompt_tokens - 4

        # tiktoken estimate
        tiktoken_prompt = get_token_count_with_tiktoken(full_history, model=model)

        results.append([
            model,
            non_streaming_total,
            dummy_prompt,
            tiktoken_prompt,
        ])
    print(tabulate(
        results,
        headers=["Model", "Non-streaming total", "Dummy call prompt-4", "tiktoken estimate"],
        tablefmt="github"
    ))

if __name__ == "__main__":
    main()
    models = [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0125",
        "gpt-4",
        "gpt-4o"
    ]
    test_models(models)
