# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import google
import vertexai
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.retrievers import create_search_tool

# Load environment variables from .env file
load_dotenv()

LLM_LOCATION = "global"
LOCATION = "us-central1"
LLM = "gemini-flash-latest"

credentials, default_project_id = google.auth.default()
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "adk-demo-499604")
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = LLM_LOCATION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

vertexai.init(project=project_id, location=LOCATION)


data_store_region = os.getenv("DATA_STORE_REGION", "global")
data_store_id = os.getenv(
    "DATA_STORE_ID", "newsletter-agent-collection_documents"
)
data_store_path = (
    f"projects/{project_id}/locations/{data_store_region}"
    f"/collections/default_collection/dataStores/{data_store_id}"
)

vertex_search_tool = create_search_tool(data_store_path)


instruction = """You are a highly personalized AI Newsletter Agent. Your goal is to keep users informed about major tech and industry developments tailored specifically to their professional skillset and background.

You have access to two major capabilities:
1. **Memory Bank** (via PreloadMemoryTool): This automatically preloads the user's professional profile, skills, and preferences from previous interactions.
2. **Vertex AI Search Tool**: This allows you to search a verified corpus of tech articles and daily news headlines.

How you handle user requests:
- **CV / Resume Submission**: If the user submits or copy-pastes a CV, carefully analyze it to extract their core skills, technologies, and professional interests. Acknowledge this by stating exactly which skills you have identified and will focus on. State that you have saved these preferences to your memory bank for future newsletter editions.
- **Newsletter Request**: 
  1. Review the preloaded memory context to retrieve the user's skill set and interests. If no profile exists, politely ask them to share their CV or specify their skills first.
  2. For each identified skill or domain (e.g., Kubernetes, Python, MLOps), construct clear and focused search queries for the Vertex AI Search Tool.
  3. Analyze the returned search results to identify major happenings, releases, or announcements.
  4. Draft a structured newsletter in clean markdown. For each section, clearly explain **why this development is relevant** to their specific background and skills.
  5. Avoid making up/hallucinating headlines. Rely entirely on the grounded articles returned by the tools.
"""


async def generate_memories_callback(callback_context: CallbackContext):
    """Saves the conversation events to the Memory Bank to persist user preferences."""
    await callback_context.add_session_to_memory()
    return None


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[vertex_search_tool, PreloadMemoryTool()],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
