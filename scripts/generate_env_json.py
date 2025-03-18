#!/usr/bin/env python3
import os
import json
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Create env.json structure for SAM
env_vars = {
    "QuestionGenerationFunction": {
        "BEDROCK_REGION": os.getenv("BEDROCK_REGION"),
        "BEDROCK_MODEL_ID": os.getenv("BEDROCK_MODEL_ID"),
        "QUALITY_THRESHOLD": os.getenv("QUALITY_THRESHOLD")
    }
}

# Write to env.json
with open('env.json', 'w') as f:
    json.dump(env_vars, f, indent=2) 