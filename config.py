import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")
DRAFTS_DIR = BASE_DIR / "drafts"

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "https://api.openai.com/v1")

POST_TONE = os.getenv("POST_TONE", "professional but conversational, occasional humour")
POST_LENGTH = os.getenv("POST_LENGTH", "400-600 words")
POSTS_PER_DAY = int(os.getenv("POSTS_PER_DAY", "1"))

IMAGE_GEN_ENABLED = os.getenv("IMAGE_GEN_ENABLED", "true").lower() == "true"
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "dall-e-3")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1024")
IMAGES_DIR = DRAFTS_DIR / "images"

OVERRIDE_THEME = os.getenv("OVERRIDE_THEME", "")
