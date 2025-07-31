import os
import google.generativeai as genai

from prompts.prompt_basic import build_batch_prompt
from core.clean_json import clean_json_response
from config.config_loader import config  

# Load Gemini model and temperature from config.yaml
model_name = config["gemini"]["model"]
temperature = config["gemini"].get("temperature", 0)

# Setup Gemini with configured values
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
_model = genai.GenerativeModel(
    model_name,
    generation_config={"temperature": temperature}
)


def call_gemini(job_description: str, all_resumes_text: str) -> dict:
    """
    Calls Gemini LLM with the given job description and resume content,
    returns parsed and cleaned response as a dictionary.
    """
    prompt = build_batch_prompt(job_description, all_resumes_text)
    try:
        response = _model.generate_content(prompt)
        content = response.text.strip()
        return content
    except Exception as e:
        raise RuntimeError("Gemini generation failed. Check the prompt or model client.") from e

