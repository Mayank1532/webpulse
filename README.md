# MCP-LIVEOPS

## LiveOps Agent --- MCP-Based Real-Time API Intelligence

MCP-LIVEOPS is a mini industry-style Agentic AI project demonstrating
how Claude can use the Model Context Protocol (MCP) to retrieve
real-time cryptocurrency market data from CoinGecko and produce a
grounded final response.

## Project Objective

The project demonstrates this complete vertical slice:

``` text
User
 ↓
Claude
 ↓
Tool Selection
 ↓
MCP Client
 ↓
MCP Server
 ↓
CoinGecko Live API
 ↓
Structured Market Data
 ↓
Claude
 ↓
Final Answer
```

The main technologies demonstrated are:

-   Claude / Anthropic
-   Model Context Protocol (MCP)
-   Agentic tool calling
-   CoinGecko live API
-   Pydantic
-   Python 3.12
-   UV
-   Pytest
-   Ruff
-   Dependency injection
-   Git/GitHub
-   Docker / CI foundation

The project intentionally remains small and focused. It does not
introduce RAG, vector databases, multi-agent systems, Kubernetes, or
unnecessary cloud infrastructure.

------------------------------------------------------------------------

## 1. Problem Statement

Traditional LLM applications often embed external API calls directly
inside application logic.

MCP introduces a standardized tool boundary:

``` text
Claude
 ↓
MCP Tool
 ↓
Provider
 ↓
External API
```

This project demonstrates that architecture with a real cryptocurrency
market-data API.

------------------------------------------------------------------------

## 2. Use Case

Example user request:

``` text
What are the current Bitcoin and Ethereum prices?
```

Claude can select:

``` text
get_crypto_prices
```

with arguments such as:

``` json
{
  "coin_ids": ["bitcoin", "ethereum"],
  "currency": "usd"
}
```

The tool calls CoinGecko, returns structured market data, and the result
is supplied back to Claude for the final response.

------------------------------------------------------------------------

## 3. Architecture

``` text
                         ┌──────────────┐
                         │     User     │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │    Claude    │
                         │ Tool Select  │
                         └──────┬───────┘
                                │
                             tool_use
                                │
                                ▼
                       ┌─────────────────┐
                       │  LiveOpsAgent   │
                       │  Orchestration  │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ MCP Client      │
                       │ McpClientAdapter │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   MCP Server    │
                       │get_crypto_prices│
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ CoinGeckoClient │
                       └────────┬────────┘
                                │
                                ▼
                          CoinGecko API
                                │
                                ▼
                          Market Data
                                │
                                ▼
                             Claude
                                │
                                ▼
                           Final Answer
```

------------------------------------------------------------------------

## 4. Agentic Tool-Calling Flow

The project uses a two-turn Claude workflow.

### Turn 1

``` text
User Request
 ↓
Claude
 ↓
Claude determines live data is required
 ↓
Claude returns tool_use
```

Example:

``` json
{
  "name": "get_crypto_prices",
  "input": {
    "coin_ids": ["bitcoin", "ethereum"],
    "currency": "usd"
  }
}
```

### Tool Execution

``` text
Claude
 ↓
LiveOpsAgent
 ↓
McpClientAdapter
 ↓
MCP Server
 ↓
CoinGecko
```

### Turn 2

``` text
MCP Result
 ↓
LiveOpsAgent
 ↓
Claude
 ↓
Final Answer
```

This demonstrates genuine agentic tool use rather than manually
inserting an API response into a prompt.

------------------------------------------------------------------------

## 5. MCP Tool

Current primary MCP tool:

``` text
get_crypto_prices
```

Description:

``` text
Get live cryptocurrency prices from CoinGecko.
```

Input:

``` json
{
  "coin_ids": ["bitcoin", "ethereum"],
  "currency": "usd"
}
```

Conceptual schema:

``` json
{
  "type": "object",
  "properties": {
    "coin_ids": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "currency": {
      "type": "string",
      "default": "usd"
    }
  },
  "required": ["coin_ids"]
}
```

The MCP client discovers the tool and its schema dynamically.

------------------------------------------------------------------------

## 6. Core Components

### `LiveOpsAgent`

Location:

``` text
src/mcp_liveops/core/agent.py
```

Responsibilities:

1.  Discover MCP tools.
2.  Convert MCP tools into Claude tool definitions.
3.  Send the initial Claude request.
4.  Detect tool calls.
5.  Invoke MCP tools.
6.  Normalize tool results.
7.  Build the second Claude request.
8.  Return the final response.

### `McpClientAdapter`

Provides the application-facing MCP boundary.

Responsibilities:

-   Tool discovery
-   Tool definition normalization
-   Tool invocation
-   Result normalization
-   Error normalization
-   Text extraction

### `McpCoinGeckoTools`

Exposes CoinGecko functionality through MCP.

### `CoinGeckoClient`

Owns the external CoinGecko API interaction.

### `AnthropicClaudeClient`

Owns the Anthropic API integration behind the `ClaudeClient`
abstraction.

------------------------------------------------------------------------

## 7. Project Structure

``` text
mcp-liveops/
│
├── .github/
│   └── workflows/
│
├── docs/
│
├── src/
│   └── mcp_liveops/
│       ├── acquisition/
│       │   ├── api_models.py
│       │   ├── api_normalization.py
│       │   ├── external_api.py
│       │   ├── interface.py
│       │   ├── local_text.py
│       │   ├── models.py
│       │   ├── normalization.py
│       │   ├── web.py
│       │   └── web_models.py
│       │
│       ├── config/
│       │   └── settings.py
│       │
│       ├── core/
│       │   ├── agent.py
│       │   └── health.py
│       │
│       ├── evidence/
│       │   ├── memory.py
│       │   ├── models.py
│       │   ├── repository.py
│       │   ├── validation.py
│       │   └── validator.py
│       │
│       ├── mcp/
│       │   ├── client.py
│       │   ├── coingecko_tools.py
│       │   ├── integration_server.py
│       │   ├── models.py
│       │   ├── registry.py
│       │   └── server.py
│       │
│       └── providers/
│           └── claude/
│               ├── client.py
│               └── models.py
│
├── tests/
│   └── unit/
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── README.md
├── sonar-project.properties
└── uv.lock
```

Project 9 was used as the verified baseline where appropriate. Proven
infrastructure was reused instead of rebuilt unnecessarily.

------------------------------------------------------------------------

## 8. Technology Stack

  Technology           Purpose
  -------------------- -----------------------------------
  Python 3.12          Application language
  UV                   Environment/dependency management
  Claude / Anthropic   LLM and tool-selection layer
  MCP                  Tool interoperability
  CoinGecko            Real-time market data
  Pydantic             Validation/domain models
  Pytest               Automated testing
  Ruff                 Linting
  Git                  Version control
  GitHub               Repository hosting
  Docker               Containerization foundation
  GitHub Actions       CI foundation

------------------------------------------------------------------------

## 9. Environment

Python requirement:

``` text
Python >= 3.12,<3.13
```

Verified development version:

``` text
Python 3.12.10
```

------------------------------------------------------------------------

## 10. Installation

Clone the repository:

``` powershell
git clone https://github.com/Mayank1532/mcp-liveops-.git
cd mcp-liveops-
```

Synchronize the environment:

``` powershell
uv sync
```

Verify Python:

``` powershell
uv run python --version
```

------------------------------------------------------------------------

## 11. Configuration

Create the local environment file:

``` powershell
Copy-Item .env.example .env
```

Configure:

``` text
ANTHROPIC_API_KEY=your_api_key_here
```

Never commit `.env` or real credentials.

Use `.env.example` for safe placeholder configuration.

------------------------------------------------------------------------

## 12. CoinGecko Data Model

Normalized market data contains:

``` text
coin_id
currency
price
change_24h_percent
last_updated_at
```

Example:

``` json
{
  "coin_id": "bitcoin",
  "currency": "usd",
  "price": 63534.0,
  "change_24h_percent": 0.82,
  "last_updated_at": 1786944230
}
```

Live values change continuously and therefore are not hard-coded.

------------------------------------------------------------------------

## 13. Dependency Injection

The project uses dependency injection for provider boundaries.

Example:

``` python
McpCoinGeckoTools(
    client=fake_client
)
```

and:

``` python
LiveOpsAgent(
    claude_client=fake_claude
)
```

Benefits:

-   Deterministic testing
-   Provider isolation
-   Easier maintenance
-   Easier provider replacement

------------------------------------------------------------------------

## 14. Error Handling

Important failure cases include:

  Failure                     Expected behavior
  --------------------------- ----------------------------------
  Empty cryptocurrency list   Tool validation failure
  Unknown MCP tool            Normalized MCP failure
  CoinGecko unavailable       Provider/API failure
  Invalid API response        Validation/normalization failure
  Missing Anthropic key       Configuration error
  MCP tool failure            Failure propagated to agent
  No Claude tool call         Direct Claude response
  Claude requests a tool      MCP tool executed

The application does not silently turn external failures into successful
empty responses.

------------------------------------------------------------------------

## 15. Why MCP?

A direct implementation could be:

``` text
Claude
 ↓
Application API code
 ↓
CoinGecko
```

MCP provides:

``` text
Claude
 ↓
MCP Tool
 ↓
Provider
```

Benefits:

-   Standardized tool interfaces
-   Tool discovery
-   Explicit schemas
-   Clear boundaries
-   Interoperability
-   Easier future tool additions
-   Separation between model reasoning and external capabilities

------------------------------------------------------------------------

## 16. Why a Claude Abstraction?

The application depends on:

``` text
ClaudeClient
```

rather than directly depending on the Anthropic implementation.

This allows:

-   Deterministic fake clients
-   Fast unit tests
-   Provider replacement
-   Cleaner architecture
-   Reduced coupling

------------------------------------------------------------------------

## 17. Testing Strategy

Testing is proportional to the project scope.

Coverage includes:

-   Unit tests
-   MCP tests
-   CoinGecko tests
-   Claude gateway tests
-   Agent orchestration tests
-   Failure tests
-   Live API validation
-   End-to-end validation

### Full Suite

``` powershell
uv run pytest -q
```

Verified:

``` text
105 passed
```

### Ruff

``` powershell
uv run ruff check src tests
```

Verified:

``` text
All checks passed!
```

### Agent Tests

``` powershell
uv run pytest tests\unit\test_agent.py -q
```

Verified:

``` text
3 passed
```

### MCP CoinGecko Tests

``` powershell
uv run pytest tests\unit\test_mcp_coingecko_tools.py -q
```

Verified:

``` text
4 passed
```

### Claude Gateway Tests

``` powershell
uv run pytest tests\unit\test_claude_gateway.py -q
```

Verified:

``` text
7 passed
```

------------------------------------------------------------------------

## 18. Live API Validation

The CoinGecko integration was successfully validated against the real
API.

The validated path was:

``` text
MCP
 ↓
get_crypto_prices
 ↓
CoinGecko
 ↓
Bitcoin + Ethereum
 ↓
Structured MCP Result
```

Real live values were retrieved successfully.

------------------------------------------------------------------------

## 19. End-to-End Validation

The complete vertical slice was validated using:

-   Deterministic Claude behavior
-   Real MCP server
-   Real CoinGecko API
-   Agent orchestration

Validated flow:

``` text
MCP tool discovery
        ↓
Claude tool definition
        ↓
Claude tool call
        ↓
MCP invocation
        ↓
Real CoinGecko API
        ↓
Structured result
        ↓
Tool result returned to Claude
        ↓
Final Claude response
```

Validation result:

``` text
VALIDATION RESULT: PASS
```

------------------------------------------------------------------------

## 20. Bruno

Bruno is part of the final API-validation gate.

Expected coverage:

-   Successful API request
-   Expected response structure
-   Valid cryptocurrency identifiers
-   Invalid input
-   Relevant API failure behavior

Bruno should complement, not duplicate, the Pytest suite.

Final project completion requires the Bruno validation gate to pass.

------------------------------------------------------------------------

## 21. DevOps

The project retains the verified baseline infrastructure where
appropriate:

``` text
UV
Git
GitHub
Docker
GitHub Actions
Ruff
Mypy configuration
SonarQube configuration
```

The project intentionally avoids unnecessary cloud/platform complexity.

------------------------------------------------------------------------

## 22. Docker

Build the image:

``` powershell
docker build -t mcp-liveops .
```

Docker provides a reproducible execution environment.

Docker is supporting infrastructure rather than the main learning
objective.

------------------------------------------------------------------------

## 23. Security

Security principles:

-   Keep API keys in environment variables.
-   Never commit `.env`.
-   Use `.env.example` for placeholders.
-   Validate external input.
-   Normalize external API responses.
-   Propagate failures explicitly.
-   Keep provider credentials outside source code.

------------------------------------------------------------------------

## 24. Cost

Most automated development testing is inexpensive because Claude is
mocked during unit tests.

No database, GPU, vector database, or cloud infrastructure is required
for the core workflow.

Real Claude API requests may incur usage costs.

The intended pattern is:

``` text
Unit Tests
 ↓
Fake Claude
```

and:

``` text
Final Validation
 ↓
Real Claude Credentials
```

------------------------------------------------------------------------

## 25. Performance

The main latency contributors are:

``` text
Claude request
+
MCP execution
+
CoinGecko network request
+
Claude second request
```

The two-turn agentic flow naturally introduces more latency than a
single LLM request.

Possible production improvements:

-   Caching
-   Connection pooling
-   Timeouts
-   Bounded retries
-   Rate-limit handling
-   Streaming
-   Metrics
-   Tracing
-   Observability

These are outside the current mini-project scope.

------------------------------------------------------------------------

## 26. Limitations

Current limitations:

-   One primary external API
-   One primary MCP tool
-   Limited agent loop
-   No persistent memory
-   No multi-agent architecture
-   No RAG
-   No vector database
-   External API dependency
-   Claude dependency
-   No production cloud deployment

These limitations are intentional to prevent scope creep.

------------------------------------------------------------------------

## 27. Design Decisions

### One External API

CoinGecko is sufficient to demonstrate live API + MCP integration.

### One Primary MCP Tool

`get_crypto_prices` is sufficient to demonstrate discovery, schema,
invocation, and result handling.

### Provider Boundary

CoinGecko HTTP logic remains separate from MCP orchestration.

### Claude Abstraction

The application depends on `ClaudeClient`, enabling deterministic tests.

### Two-Turn Agentic Loop

The workflow is:

``` text
Claude → Tool
Tool → Claude
```

This demonstrates actual agentic tool use.

### Deterministic Tests

Mocks and fakes are preferred during development. Real credentials and
external services are reserved for final validation.

------------------------------------------------------------------------

## 28. Interview Questions and Answers

### Q1. What is MCP?

MCP stands for Model Context Protocol. It provides a standardized way
for AI applications to interact with external tools and capabilities.

### Q2. Why use MCP instead of directly calling CoinGecko?

MCP provides a standardized tool boundary. Claude does not need to know
the implementation details of the external API.

### Q3. How does Claude decide to use the tool?

Claude receives the available tool definitions and their schemas. Based
on the user's request, it can produce a `tool_use` request.

### Q4. What is tool discovery?

Tool discovery means asking the MCP server which tools it exposes and
obtaining their names, descriptions, and input schemas.

### Q5. Why use dependency injection?

It allows real providers to be replaced with deterministic test doubles,
improving testability and reducing external dependencies during testing.

### Q6. Why are most Claude tests mocked?

Real model calls can be slower, expensive, nondeterministic, and
credential-dependent. Unit tests should be fast and repeatable.

### Q7. Why are there two Claude calls?

The first call decides whether a tool is needed. The second call
receives the tool result and produces the final answer.

### Q8. What happens if CoinGecko fails?

The provider failure is propagated through the MCP layer and normalized
by the client so the agent can handle the failure.

### Q9. What happens if Claude requests an unknown tool?

The MCP client returns a normalized unsuccessful result rather than
silently executing an unavailable capability.

### Q10. How would you scale this system?

Potential production improvements include caching, retries, rate-limit
handling, observability, authentication, authorization, multiple MCP
servers, tool governance, and persistent state.

------------------------------------------------------------------------

## 29. Lessons Learned

### MCP is a tool interoperability layer

It separates AI reasoning from external capabilities.

### Tool schemas matter

Claude needs a clear description of what the tool does and which
arguments it accepts.

### Agentic workflows are loops

``` text
LLM
 ↓
Tool Request
 ↓
Tool Execution
 ↓
Tool Result
 ↓
LLM
```

### Provider boundaries improve testing

Claude and CoinGecko can be replaced with deterministic fakes.

### Live validation matters

Mocks verify application behavior; live validation verifies the actual
external integration.

------------------------------------------------------------------------

## 30. Project 9 Reuse

Project 9 was used as the verified baseline where appropriate.

Reused patterns include:

-   UV
-   Configuration
-   Environment management
-   Pydantic
-   Acquisition boundaries
-   MCP integration
-   Claude provider abstraction
-   Testing patterns
-   Docker
-   CI foundation
-   Linting
-   Documentation patterns

Project 10 adds the new focus:

``` text
MCP
+
Claude
+
Live API
+
Agentic Tool Use
```

------------------------------------------------------------------------

## 31. Why the Project Is Small

The objective is not to build a full AI platform.

The objective is to prove one technically meaningful vertical slice:

``` text
Claude
+
MCP
+
Live API
+
Agentic Tool Calling
+
Testing
+
Industry Engineering
```

Once the required capability works and is validated, unrelated
functionality becomes scope creep.

------------------------------------------------------------------------

## 32. Future Improvements

Potential future work, outside current Project 10 scope:

-   Additional MCP tools
-   Multiple market-data providers
-   Currency conversion
-   Market-news tool
-   Caching
-   Retry policies
-   Rate-limit management
-   Persistent conversation state
-   Streaming
-   Rich observability
-   Authentication
-   Authorization
-   Cloud deployment
-   MCP server hosting
-   Production monitoring

------------------------------------------------------------------------

## 33. Final Architecture Summary

``` text
                    USER
                      │
                      ▼
                 ┌─────────┐
                 │ Claude  │
                 └────┬────┘
                      │
                   tool_use
                      │
                      ▼
              ┌───────────────┐
              │ LiveOpsAgent  │
              └───────┬───────┘
                      │
                      ▼
             ┌─────────────────┐
             │ McpClientAdapter│
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │   MCP Server    │
             │                 │
             │get_crypto_prices│
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ CoinGeckoClient │
             └────────┬────────┘
                      │
                      ▼
                CoinGecko API
                      │
                      ▼
                  Market Data
                      │
                      ▼
                   Claude #2
                      │
                      ▼
                 FINAL ANSWER
```

------------------------------------------------------------------------

## 34. Release Checklist

``` text
[✓] Project objective implemented
[✓] Real CoinGecko API validated
[✓] MCP server validated
[✓] MCP tool validated
[✓] MCP tool discovery validated
[✓] MCP schema exposed
[✓] Claude tool definition generated
[✓] Claude tool call handled
[✓] MCP tool invocation works
[✓] Tool result returned to Claude
[✓] Two-turn agentic loop works
[✓] MCP failure handling validated
[✓] Invalid input handling validated
[✓] Pytest passes
[✓] Ruff passes
[✓] End-to-end deterministic validation passes
[✓] Real CoinGecko validation passes
[ ] Bruno validation completed
[ ] Final DevOps validation completed
[ ] Final repository cleanliness verified
```

Unchecked items must not be marked complete until actually validated.

------------------------------------------------------------------------

## 35. Current Project Status

**Core agentic vertical slice: COMPLETE**

Verified:

``` text
105 automated tests passing
Ruff checks passing
Real CoinGecko API working
MCP tool discovery working
MCP tool invocation working
Claude tool-call orchestration working
Two-turn Claude/MCP loop working
End-to-end deterministic validation passing
```

Final release remains gated by the remaining Bruno, DevOps, and
repository-cleanliness checks.

------------------------------------------------------------------------

## 36. Final Takeaway

MCP-LIVEOPS demonstrates a complete agentic tool-use architecture using
a real external API:

``` text
User Request
     ↓
Claude Reasoning
     ↓
MCP Tool Selection
     ↓
MCP Invocation
     ↓
Real CoinGecko API
     ↓
Structured Result
     ↓
Claude
     ↓
Grounded Final Answer
```

The project combines:

``` text
Claude
+
MCP
+
Live API
+
Agentic AI
+
Structured Tool Schemas
+
Error Handling
+
Testing
+
DevOps
```

while keeping the implementation small enough to understand, test,
demonstrate, and explain.
