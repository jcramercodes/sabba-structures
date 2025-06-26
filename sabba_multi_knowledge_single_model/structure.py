import argparse
import os
import sys
from typing import List

import requests
from dotenv import load_dotenv
from griptape.artifacts import TextArtifact
from griptape.configs import Defaults
from griptape.configs.drivers import (
    AnthropicDriversConfig,
    DriversConfig,
    GoogleDriversConfig,
    OpenAiDriversConfig,
)
from griptape.drivers.memory.conversation.griptape_cloud import GriptapeCloudConversationMemoryDriver
from griptape.drivers.ruleset.griptape_cloud import GriptapeCloudRulesetDriver
from griptape.drivers.vector.griptape_cloud import GriptapeCloudVectorStoreDriver
from griptape.engines.rag import RagEngine
from griptape.engines.rag.modules import (
    PromptResponseRagModule,
    VectorStoreRetrievalRagModule,
)
from griptape.engines.rag.stages import ResponseRagStage, RetrievalRagStage
from griptape.rules.ruleset import Ruleset
from griptape.structures import Agent
from griptape.tools import BaseTool, RagTool
from griptape.utils import GriptapeCloudStructure

from knowledge_bases import (
    get_knowledge_base_by_id,
    parse_knowledge_base_selection,
    print_available_knowledge_bases,
)

load_dotenv()


class CloudSearchDriver(GriptapeCloudVectorStoreDriver):
    """Custom driver that uses /search endpoint instead of /query for Hybrid/Text KBs."""
    
    def query(self, query: str, *, count: int | None = None, **kw):
        """Use /search endpoint instead of /query for Hybrid knowledge bases."""
        url = f"{self.base_url}/api/knowledge-bases/{self.knowledge_base_id}/search"
        body = {"query": query, "count": count or 5}
        
        try:
            response = requests.post(url, json=body, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            # The /search endpoint returns {"response": ["text1", "text2", ...]}
            texts = result.get("response", [])
            return [TextArtifact(text) for text in texts]
            
        except Exception as e:
            print(f"⚠️  Search failed for KB {self.knowledge_base_id}: {e}")
            return []


def get_config(provider: str) -> DriversConfig | None:
    """Get the appropriate driver configuration for the specified provider."""
    if provider == "openai":
        return OpenAiDriversConfig()
    if provider == "anthropic":
        return AnthropicDriversConfig()
    if provider == "google":
        return GoogleDriversConfig()
    return None


def get_knowledge_base_tools(knowledge_base_ids: List[str]) -> List[BaseTool]:
    """Create RAG tools for each knowledge base ID provided."""
    tools = []
    
    # Get the API key from environment variables
    api_key = os.environ.get("GT_CLOUD_API_KEY")
    if not api_key:
        print("⚠️  Warning: GT_CLOUD_API_KEY not found. Knowledge base queries will fail.")
        return []
    
    for i, kb_id in enumerate(knowledge_base_ids):
        if kb_id:
            # Get knowledge base metadata if available
            kb_info = get_knowledge_base_by_id(kb_id)
            kb_name = kb_info.name if kb_info else f"Knowledge base #{i+1}"
            kb_description = f"{kb_name}: Contains specialized information and documents"
            if kb_info:
                kb_description += f" from {kb_info.org_url}"
            
            engine = RagEngine(
                retrieval_stage=RetrievalRagStage(
                    retrieval_modules=[
                        VectorStoreRetrievalRagModule(
                            vector_store_driver=GriptapeCloudVectorStoreDriver(
                                api_key=api_key,
                                knowledge_base_id=kb_id,
                            )
                        )
                    ]
                ),
                response_stage=ResponseRagStage(
                    response_modules=[PromptResponseRagModule()],
                ),
            )
            
            tools.append(
                RagTool(
                    description=kb_description,
                    rag_engine=engine,
                ),
            )
    
    return tools


def get_rulesets(ruleset_alias: str | None) -> List[Ruleset]:
    """Get rulesets if provided."""
    if ruleset_alias is None:
        return []
    return [Ruleset(name=ruleset_alias, ruleset_driver=GriptapeCloudRulesetDriver())]


def parse_knowledge_base_ids(kb_ids_str: str) -> List[str]:
    """Parse comma-separated knowledge base IDs or names."""
    return parse_knowledge_base_selection(kb_ids_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Multi-knowledge base agent with configurable model provider"
    )
    parser.add_argument(
        "-p",
        "--provider",
        choices=["openai", "anthropic", "google"],
        default="google",
        help="List the provider for the model you want to use. Must be 'openai', 'anthropic', or 'google'",
    )
    parser.add_argument(
        "-k",
        "--knowledge-base-ids",
        default="",
        help="Comma-separated list of knowledge base IDs or names. Use 'all' for all available. Examples: 'Blossom Analysis,MAPS' or 'all'",
    )
    parser.add_argument(
        "--list-kb",
        action="store_true",
        help="List all available knowledge bases and exit",
    )
    parser.add_argument(
        "-q",
        "--query",
        default="Hello! What information can you help me with?",
        help="The query you wish to ask across all knowledge bases",
    )
    parser.add_argument(
        "-r",
        "--ruleset-alias",
        default=None,
        help="Set the Griptape Cloud Ruleset alias to use",
    )
    parser.add_argument(
        "-s",
        "--stream",
        default=False,
        action="store_true",
        help="Enable streaming mode for the Agent",
    )
    parser.add_argument(
        "-t",
        "--thread-id",
        default=None,
        help="Set the Griptape Cloud Thread ID you wish to use for conversation memory",
    )

    args = parser.parse_args()
    
    # Handle list knowledge bases option
    if args.list_kb:
        print_available_knowledge_bases()
        sys.exit(0)
    
    provider = args.provider
    knowledge_base_ids = parse_knowledge_base_ids(args.knowledge_base_ids)
    query = args.query
    thread_id = args.thread_id
    ruleset_alias = args.ruleset_alias
    stream = args.stream

    # Set up the model provider configuration
    Defaults.drivers_config = get_config(provider)
    
    # Set up conversation memory if thread_id is provided
    if thread_id:
        Defaults.drivers_config.conversation_memory_driver = GriptapeCloudConversationMemoryDriver(
            thread_id=thread_id,
        )

    # Create the agent with knowledge base tools
    agent = Agent(
        rulesets=get_rulesets(ruleset_alias),
        tools=get_knowledge_base_tools(knowledge_base_ids),
        stream=stream,
    )

    # Run the agent
    with GriptapeCloudStructure():
        if knowledge_base_ids:
            print(f"Using model provider: {provider}")
            print("Knowledge bases loaded:")
            for kb_id in knowledge_base_ids:
                kb = get_knowledge_base_by_id(kb_id)
                if kb:
                    print(f"  - {kb.name} ({kb_id})")
            if thread_id:
                print(f"Using conversation memory with thread: {thread_id}")
        
        agent.run(query) 