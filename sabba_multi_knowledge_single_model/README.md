# Sabba Multi-Knowledge Single Model

This sample demonstrates how to create a Griptape agent that can work with multiple knowledge bases simultaneously while using a configurable model provider. This structure combines the model switching capabilities from the `griptape_model_switcher` sample with the knowledge base integration from the `griptape_chat_memory_agent` sample.

[![Deploy_to_Griptape](https://github.com/griptape-ai/griptape-cloud/assets/2302515/4fd57873-5c93-44a8-8fa3-ac1bf7d73bcc)](https://cloud.griptape.ai/structures/create/sabba_multi_knowledge_single_model)

## Features

- **Multi-Knowledge Base Support**: Query multiple knowledge bases simultaneously
- **Model Provider Switching**: Choose between OpenAI, Anthropic, and Google models
- **Conversation Memory**: Optional persistent conversation threads
- **Streaming Support**: Real-time response streaming
- **Ruleset Integration**: Apply custom rulesets to your agent

## Requirements

- [Open AI Key](https://platform.openai.com/api-keys)
- [Anthropic API Key](https://console.anthropic.com/settings/keys)
- [Google API Key](https://ai.google.dev/gemini-api/docs)
- [Griptape Cloud Key](https://cloud.griptape.ai/configuration/api-keys)
- [Griptape Cloud Knowledge Base IDs](https://cloud.griptape.ai/knowledge-bases)

## Configuration

```
OPENAI_API_KEY=<encrypted_value> # Fill in with your own key
ANTHROPIC_API_KEY=<encrypted_value> # Fill in with your own key
GOOGLE_API_KEY=<encrypted_value> # Fill in with your own key
GT_CLOUD_API_KEY=<encrypted_value> # Fill in with your own key
```

## Running this Sample

### Locally

You can run this with no parameters to use defaults:

```bash
python structure.py
```

**Default behavior:**
- Provider: Google
- Query: "Hello! What information can you help me with?"
- No knowledge bases loaded

### With Knowledge Bases

To use with multiple knowledge bases:

```bash
python structure.py -k "kb-id-1,kb-id-2,kb-id-3" -q "What can you tell me about our company policies?"
```

### With Different Model Provider

To use OpenAI with knowledge bases:

```bash
python structure.py -p openai -k "kb-id-1,kb-id-2" -q "Summarize the key points from our documentation"
```

### With Conversation Memory

To enable persistent conversation memory:

```bash
python structure.py -k "kb-id-1" -t "thread-id-123" -q "Continue our previous conversation"
```

### All Parameters

```bash
python structure.py \
  -p anthropic \
  -k "kb-id-1,kb-id-2,kb-id-3" \
  -q "What information is available across all knowledge bases?" \
  -r "my-ruleset-alias" \
  -s \
  -t "my-thread-id"
```

### Griptape Cloud

When creating runs in the UI, specify parameters on separate lines:

```
-p
openai
-k
kb-id-1,kb-id-2,kb-id-3
-q
What can you tell me about our products and services?
```

## Parameters

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| `--provider` | `-p` | Model provider: `openai`, `anthropic`, or `google` | `google` |
| `--knowledge-base-ids` | `-k` | Comma-separated knowledge base IDs | `""` (none) |
| `--query` | `-q` | The query to ask across knowledge bases | `"Hello! What information can you help me with?"` |
| `--ruleset-alias` | `-r` | Griptape Cloud ruleset alias | `None` |
| `--stream` | `-s` | Enable streaming mode | `False` |
| `--thread-id` | `-t` | Conversation memory thread ID | `None` |

## Use Cases

- **Multi-source Research**: Query across different knowledge bases (documentation, policies, FAQs)
- **Customer Support**: Access multiple information sources simultaneously
- **Knowledge Aggregation**: Combine insights from various specialized knowledge bases
- **Model Comparison**: Test different AI providers with the same knowledge sources
- **Persistent Conversations**: Maintain context across multiple interactions

## Architecture

This structure creates:
1. **RAG Tools**: One tool per knowledge base for specialized retrieval
2. **Model Configuration**: Dynamic provider switching
3. **Memory Management**: Optional conversation persistence
4. **Streaming Support**: Real-time response delivery

The agent can intelligently route queries to the appropriate knowledge bases and synthesize responses from multiple sources. 