import os
import tiktoken

def get_token_count_with_tiktoken(messages, model="gpt-3.5-turbo"):
    """
    Estimate token count using tiktoken. Returns int or raises Exception if model is unknown.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception as e:
        raise RuntimeError(f"tiktoken does not support model {model}: {e}")
    tokens_per_message = 4
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(str(value)))
    num_tokens -= 4  # Adjust for the last message's end token
    return num_tokens

def get_token_count_with_dummy_completion(completions_command, messages, model="gpt-3.5-turbo"):
    """
    Get token count by making a dummy OpenAI completion call with max_tokens=1.
    completions_command should be a function that returns an OpenAI response object.
    Returns the prompt_tokens - 4 (to match tiktoken logic).
    """
    resp = completions_command(
        model=model,
        messages=messages,
        max_tokens=1,
        stream=False
    )
    return resp.usage.prompt_tokens - 4 # Adjust for the last message's end token

def get_token_count(completions_command, messages, model="gpt-3.5-turbo"):
    """
    Try tiktoken first, fallback to dummy completion if tiktoken fails.
    completions_command should be a function that returns an OpenAI response object.
    """
    try:
        return get_token_count_with_tiktoken(messages, model)
    except Exception:
        return get_token_count_with_dummy_completion(completions_command, messages, model)
