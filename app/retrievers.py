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
from collections.abc import Callable

from google.adk.tools import ToolContext

_DATA_STORE_PATH = None


def set_preferred_language(language: str, tool_context: ToolContext) -> dict:
    """Sets the users preferred language for communications and newsletters.

    Args:
        language: The target language name or code (e.g. 'German', 'English', 'de', 'en')
    """
    lang_lower = language.lower().strip()

    german_variants = ["de", "german", "deutsch"]
    english_variants = ["en", "english", "englisch"]

    if lang_lower in german_variants:
        canoncial_lang = "Deutsch"
    elif lang_lower in english_variants:
        canoncial_lang = "English"
    else:
        return {"status": "error", "message": f"Unsupported language: '{language}'"}

    tool_context.state["user:preferred_language"] = canoncial_lang

    return {
        "status": "success",
        "message": f"Preferred language successfully set to {canoncial_lang}",
    }


def real_search(query: str) -> str:
    """Searches the verified corpus of tech articles and daily news headlines.

    Args:
        query: The search query to run.
    """
    global _DATA_STORE_PATH
    if not _DATA_STORE_PATH:
        return "Search is not initialized yet."

    # Format of data_store_path:
    # "projects/{project}/locations/{location}/collections/{collection}/dataStores/{dataStore}"
    parts = _DATA_STORE_PATH.split("/")
    if len(parts) < 8:
        return f"Invalid data store path format: {_DATA_STORE_PATH}"

    project = parts[1]
    location = parts[3]
    data_store = parts[7]

    from google.cloud import discoveryengine

    try:
        client = discoveryengine.SearchServiceClient()
        serving_config = client.serving_config_path(
            project=project,
            location=location,
            data_store=data_store,
            serving_config="default_search",
        )
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=5,
        )
        response = client.search(request)
        results = []
        for result in response.results:
            struct_data = result.document.derived_struct_data
            if struct_data:
                title = struct_data.get("title", "No Title")
                link = struct_data.get("link", "")
                snippets = struct_data.get("snippets", [])
                snippet_text = ""
                if snippets:
                    snippet_text = snippets[0].get("snippet", "")
                results.append(
                    f"- Headline: {title}\n  Source: {link}\n  Summary: {snippet_text}"
                )
        if not results:
            return f"No articles found matching the query '{query}'."
        return "\n\n".join(results)
    except Exception as e:
        return f"Error performing search: {e}"


def create_search_tool(
    data_store_path: str,
) -> Callable[[str], str]:
    """Create a Agent Platform Search tool or mock for testing.

    Args:
        data_store_path: Full resource path of the datastore.

    Returns:
        Search function.
    """
    global _DATA_STORE_PATH
    _DATA_STORE_PATH = data_store_path

    # For integration tests or local sandbox, return a realistic mock instead of the real tool
    if (
        os.getenv("INTEGRATION_TEST") == "TRUE"
        or os.getenv("LOCAL_PLAYGROUND") == "TRUE"
    ):

        def mock_search(query: str) -> str:
            """Mock Agent Platform Search returning rich keyword-based tech news."""
            q = query.lower()
            if "kubernetes" in q or "k8s" in q or "orchestration" in q:
                return """
- Headline: CNCF Announces Kubernetes v1.35 with Native Sidecar Container Lifecycles
  Source: CNCF Blog (June 2026)
  Summary: The Cloud Native Computing Foundation has officially released Kubernetes v1.35, promoting sidecar container startup order to stable, significantly improving service mesh reliability.

- Headline: Platform Engineering and Kubernetes Fleet Management taking over KubeCon 2026
  Source: TechCrunch (May 2026)
  Summary: Multi-cluster orchestrations and GitOps-driven fleets dominated KubeCon discussions, with a heavy emphasis on reducing cloud spend and cluster resource footprint.
"""
            elif "mlops" in q or "pipeline" in q or "llm" in q:
                return """
- Headline: Google Cloud Vertex AI Unveils Auto-Scaling ML Inference Pipelines
  Source: GCP News (June 2026)
  Summary: Vertex AI has launched a new serverless inference engine that auto-scales from zero, supporting mixed-precision Gemini model serving and deep telemetry tracing natively.

- Headline: Industry Report: Core Challenges in LLM Production Operations (LLMOps)
  Source: MLOps Community (June 2026)
  Summary: Continuous evaluation and data drift tracking remain the highest pain points for teams deploying Generative AI models. The report recommends automated evaluation datasets and LLM-as-a-judge scoring frameworks.
"""
            elif "python" in q or "coding" in q:
                return """
- Headline: Python 3.14 Beta 2 Showcases Massively Optimized Asyncio and JIT Compilers
  Source: PSF Developer Feed (June 2026)
  Summary: The Python Software Foundation released its latest beta, confirming significant performance increments in asynchronous event loops and advanced static typing features.
"""
            else:
                return f"""
- Headline: Break-throughs and Advancements in {query}
  Source: Global Tech Review (June 2026)
  Summary: Analysts reported a significant spike in industrial adoption and automated deployments centered around {query} technologies this quarter.
"""

        return mock_search

    return real_search
