# services/llm_service.py

import os
import re
from typing import List, Optional
import openai
import requests
import streamlit as st

class LLMService:
    def __init__(self, openai_api_key: Optional[str] = None, local_model: Optional[str] = None, default_openai_model: str = "gpt-3.5-turbo"):
        """
        :param openai_api_key: your OpenAI key (if using OpenAI).
        :param local_model: local HF model path (if using a local model).
        :param default_openai_model: which GPT model to use (e.g., gpt-3.5-turbo).
        """
        self.provider = "openai"
        self.openai_model = default_openai_model
        self._pipeline = None

        if local_model:
            # Use local HF model
            self.provider = "local"
            try:
                from transformers import pipeline
            except ImportError:
                raise ImportError("Please install 'transformers' to use local models.")
            try:
                self._pipeline = pipeline("text-generation", model=local_model, tokenizer=local_model, device_map="auto")
            except Exception as e:
                raise RuntimeError(f"Failed to load local model '{local_model}': {e}")
        else:
            # Use OpenAI
            try:
                import openai
            except ImportError:
                raise ImportError("Please install 'openai' to use OpenAI API.")
            if openai_api_key:
                openai.api_key = openai_api_key
            else:
                env_key = st.secrets["OPENAI_API_KEY"]
                if env_key:
                    openai.api_key = env_key
                else:
                    raise ValueError("No OpenAI API key provided or found in environment.")
            self.provider = "openai"

def complete(self, prompt: str, system_message: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 100) -> str:
        """
        Generate text using either OpenAI ChatCompletion or a local HF pipeline.
        """
        if self.provider == "openai":
            import openai
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            try:
                response = openai.ChatCompletion.create(
                    model=self.openai_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=1
                )
                return response["choices"][0]["message"]["content"].strip()
            except Exception as e:
                raise RuntimeError(f"OpenAI API request failed: {e}")
        else:
            # Local HF pipeline
            if not self._pipeline:
                raise RuntimeError("Local pipeline not initialized.")
            full_prompt = (system_message + "\n" + prompt) if system_message else prompt
            try:
                outputs = self._pipeline(full_prompt, max_new_tokens=max_tokens, do_sample=True, temperature=temperature, num_return_sequences=1)
                generated_text = outputs[0]["generated_text"]
                # Remove prompt from output if present
                if generated_text.startswith(full_prompt):
                    generated_text = generated_text[len(full_prompt):]
                return generated_text.strip()
            except Exception as e:
                raise RuntimeError(f"Local model generation failed: {e}")

def generate_suggestions(self, job_title: str, category: str, count: int = 15) -> List[str]:
        """
        Provide a short list of suggestions for tasks, skills, or benefits, tailored to a job title.
        """
        cat = category.lower()
        if cat not in ["tasks", "skills", "benefits"]:
            raise ValueError(f"Invalid category '{category}'. Must be 'tasks','skills','benefits'.")
        user_prompt = ""
        if cat == "tasks":
            user_prompt = f"List {count} key tasks or responsibilities for a '{job_title}' role. No numbering, each on a new line."
        elif cat == "skills":
            user_prompt = f"List {count} important skills needed for a '{job_title}' role. No numbering, each on a new line."
        else:  # benefits
            user_prompt = f"List {count} compelling benefits that could be offered for a '{job_title}' position. No numbering, each on a new line."

        system_text = "You are an AI assistant helping create job descriptions. Provide concise suggestions."

        raw = self.complete(prompt=user_prompt, system_message=system_text, temperature=0.7, max_tokens=100)
        suggestions = self._parse_suggestions_from_text(raw, count)
        return suggestions

def _parse_suggestions_from_text(self, raw_text: str, limit: int = 15) -> List[str]:
        """
        Splits the raw LLM output into lines, cleans them up, returns up to `limit`.
        """
        lines = []
        for line in raw_text.split("\n"):
            line = line.strip("-• \t0123456789.")
            line = line.strip()
            if line:
                lines.append(line)
        return lines[:limit]

def create_llm_service(llm_choice: Optional[str] = None) -> LLMService:
    """
    Create and return an LLMService instance based on the given or configured model choice.
    If llm_choice is None, uses the environment variable LLM_CHOICE or defaults to "openai_3.5".
    If the choice indicates a local model, use the local model path from environment (if set).
    """
    import os
    if llm_choice is None:
        llm_choice = st.secrets.get("LLM_CHOICE", "openai_3.5")
    # Retrieve OpenAI API key from environment (if available)
    openai_api_key = st.secrets.get("OPENAI_API_KEY") or None
    if llm_choice == "local_llama":
        local_model_path = os.getenv("LOCAL_MODEL_PATH", "decapoda-research/llama-7b-hf")
        return LLMService(openai_api_key=None, local_model=local_model_path)
    else:
        # Default to OpenAI model (gpt-3.5-turbo)
        return LLMService(openai_api_key=openai_api_key, local_model=None)