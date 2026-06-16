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

from google.adk.tools import VertexAiSearchTool


def create_search_tool(
    data_store_path: str,
) -> VertexAiSearchTool | Callable[[str], str]:
    """Create a Agent Platform Search tool or mock for testing.

    Args:
        data_store_path: Full resource path of the datastore.

    Returns:
        VertexAiSearchTool instance or mock function for testing.
    """
    # For integration tests or local sandbox, return a realistic mock instead of the real tool
    if os.getenv("INTEGRATION_TEST") == "TRUE" or os.getenv("LOCAL_PLAYGROUND") == "TRUE":

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

    return VertexAiSearchTool(data_store_id=data_store_path)
