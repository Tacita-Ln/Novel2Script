import os
from dotenv import load_dotenv

load_dotenv()
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "glm-4.5-air")