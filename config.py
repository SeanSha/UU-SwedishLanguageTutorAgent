import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

# Load environment variables
load_dotenv()

# Project Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Ensure required directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# File Paths
DATASET_CACHE_PATH = os.path.join(DATA_DIR, "dataset_cache.csv")
USER_MEMORY_PATH = os.path.join(MEMORY_DIR, "user_memory.json")

# Dataset Configuration
HF_DATASET_ID = "SeanSha30/swedish-pre-a1-scenario-classifier-dataset"

# Scenario Labels List
SCENARIOS = [
    "food_shop",
    "family_school",
    "health_places",
    "transport",
    "home_places",
    "social_intro"
]

# LLM Configurations
DEFAULT_LOCAL_MODEL = os.getenv("DEFAULT_LOCAL_MODEL", "qwen2.5")
DEFAULT_ONLINE_MODEL = os.getenv("DEFAULT_ONLINE_MODEL", "gpt-4o-mini")
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")

# OpenAI API config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

# Stable assignment-demo mode:
# keep dialogue flow deterministic from retrieved plans/examples unless explicitly enabled.
USE_LLM_DIALOGUE_GENERATION = os.getenv("USE_LLM_DIALOGUE_GENERATION", "0") == "1"
