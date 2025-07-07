# from langchain.llms.base import LLM
# from typing import Optional, List, Mapping, Any
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # class OpenRouterLLM(LLM):
# class OpenRouterLLM(LLM):
#     @property
#     def _llm_type(self) -> str:
#         return "openrouter"
    
#     def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
#         headers = {
#             "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
#             "HTTP-Referer": os.getenv("YOUR_SITE_URL"),
#             "X-Title": os.getenv("YOUR_SITE_NAME"),
#             "Content-Type": "application/json"
#         }
        
#         data = {
#             "model": os.getenv("OPENROUTER_MODEL"),
#             "messages": [{"role": "user", "content": prompt}]
#         }
        
#         response = requests.post(
#             "https://openrouter.ai/api/v1/chat/completions",
#             headers=headers,
#             json=data
#         )
        
#         if response.status_code != 200:
#             raise ValueError(f"OpenRouter API Error: {response.text}")
        
#         return response.json()["choices"][0]["message"]["content"]
    
#     @property
#     def _identifying_params(self) -> Mapping[str, Any]:
#         return {"model": os.getenv("OPENROUTER_MODEL")}

from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class OpenRouterLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "openrouter"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        api_key = os.getenv("OPENROUTER_API_KEY")
        print(api_key)
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment")

        # Use OPENROUTER_MODEL from .env, fallback to a valid default
        model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4.1-nano")
        if not model:
            raise ValueError("OPENROUTER_MODEL not set in environment and no fallback model provided")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Optional headers
        site_url = os.getenv("YOUR_SITE_URL")
        site_name = os.getenv("YOUR_SITE_NAME")
        if site_url:
            headers["HTTP-Referer"] = site_url
        if site_name:
            headers["X-Title"] = site_name

        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code != 200:
            raise ValueError(f"OpenRouter API Error: {response.text}")

        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise ValueError(f"Unexpected API response structure: {response.text}")

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")}
