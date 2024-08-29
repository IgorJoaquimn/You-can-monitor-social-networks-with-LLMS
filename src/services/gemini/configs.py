import google.generativeai as genai
from key import GEMINI_KEY
GEMINI_MODEL = "gemini-1.5-flash"
MAX_SIZE = 1

def config():
    genai.configure(api_key=GEMINI_KEY)
    model_info = genai.get_model("models/" + GEMINI_MODEL)
    MAX_SIZE = model_info.input_token_limit
    print(f"Size {MAX_SIZE}")
    return MAX_SIZE
