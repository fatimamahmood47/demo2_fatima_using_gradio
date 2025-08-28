# app/dependencies/openai_client.py

from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment *once* at module level
load_dotenv()

# Fetch your secret *once*
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Optional: raise an error if it's missing
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment")

# Create and reuse a single client instance
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def get_openai_client() -> OpenAI:
    return openai_client
