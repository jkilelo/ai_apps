"""
Minimalist LLM Module - Single Source of Truth
"""

import os
import json
from pathlib import Path
from typing import List

from openai import OpenAI
import google.generativeai as genai

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# For backward compatibility - modules should just use call_default_llm
default_llm = lambda messages=None: call_default_llm(messages if messages else [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"}
])


def query_llm(
    model: str,
    messages: List[dict],
    llm_provider: str = "gemini",
    temperature: float = 0.0,
    stream: bool = False,
    raw_response: bool = False,
    max_tokens: int = 64000
):
    if llm_provider.lower() == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens if "gpt-4" not in model else None,
            max_completion_tokens=max_tokens if "gpt-4" in model else None,
            stream=stream
        )
        return response if (raw_response or stream) else response.choices[0].message.content
    
    elif llm_provider.lower() == "gemini":
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        gemini_messages = []
        system_message = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": min(max_tokens, 8192),
        }
        
        gemini_model = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
            system_instruction=system_message
        ) if system_message else genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config
        )
        
        if len(gemini_messages) > 1:
            chat = gemini_model.start_chat(history=gemini_messages[:-1])
            response = chat.send_message(gemini_messages[-1]["parts"][0])
        else:
            response = gemini_model.generate_content(gemini_messages[0]["parts"][0])
        
        return response if raw_response else response.text
    
    elif llm_provider.lower() == "anthropic":
        client = OpenAI(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url="https://api.anthropic.com/v1/"
        )
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        return response if (raw_response or stream) else response.choices[0].message.content
    
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")


def call_default_llm(messages: List[dict]):
    config_path = Path(__file__).parent / "llm_models.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        default_config = config.get("default", {"provider": "gemini", "model": "gemini-2.5-pro"})
        provider = default_config["provider"]
        model = default_config["model"]
    except:
        provider = "gemini"
        model = "gemini-2.5-pro"
    
    return query_llm(
        model=model,
        messages=messages,
        llm_provider=provider,
        temperature=0.0,
        stream=False,
        raw_response=False,
        max_tokens=64000
    )


if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "What's the capital city of Kenya? Reply with only one word"}
    ]
    
    response = call_default_llm(messages)
    print(f"Response: {response}")