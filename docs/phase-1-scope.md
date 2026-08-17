# Project 11 — WEBPULSE
## Phase 1 — Scope Lock

### Project

WebPulse — Agentic Live Web Intelligence

### Objective

Build a focused Agentic AI system where Claude can determine when current web information is required, invoke a controlled MCP web-retrieval tool, retrieve live web content, extract useful information, and produce a grounded response with source information.

### Problem

LLM knowledge can be outdated or incomplete. WEBPULSE provides Claude with a controlled live-web capability so current information can be retrieved when required.

### Primary Use Case

Current technology and product intelligence.

Example:

"What is the latest Python release and what changed compared with the previous release?"

### Core Workflow

User
→ Claude
→ Agentic decision
→ MCP web tool
→ Live HTTP retrieval
→ HTML/content extraction
→ Structured WebResult
→ Claude
→ Grounded answer + sources

### Architecture

Claude is the agentic decision layer.

The MCP web tool provides the controlled tool boundary.

The web retrieval layer performs HTTP retrieval.

The extraction layer removes irrelevant HTML and produces useful content.

The normalization layer converts the retrieved information into validated structured data.

Claude receives the structured result and produces the final grounded response.

### Web Retrieval Strategy

Initial implementation:

1. Validate URL.
2. Perform HTTP retrieval.
3. Apply timeout and response-size controls.
4. Parse HTML.
5. Extract useful page content.
6. Normalize the result.
7. Return structured information through MCP.

Browser automation is intentionally deferred.

Playwright will only be introduced if the selected real-world pages cannot be retrieved and interpreted adequately using normal HTTP.

### Reused Project 10 Infrastructure

- Claude provider abstraction
- MCP client patterns
- MCP tool schema patterns
- MCP registry/discovery patterns
- MCP server foundation
- agent/tool-loop patterns
- configuration patterns
- dependency injection patterns
- Pydantic validation patterns
- testing structure
- Ruff/Mypy/Pytest configuration
- applicable CI foundation

### Reused Project 9 Concepts

- source/evidence concepts where genuinely useful
- grounding concepts
- source metadata concepts
- relevant validation/error-handling patterns

The complete Project 9 evidence architecture will not be copied unless required.

### Project 10 Components To Remove

- CoinGecko client
- CoinGecko MCP tool
- CoinGecko models
- CoinGecko tests
- Project 10 Bruno collection
- Project 10-specific documentation
- Project 10-specific business logic

### Components To Modify

- Python package name
- project metadata
- Claude agent
- MCP server registration
- acquisition/web retrieval layer
- web models
- configuration
- tests
- README
- environment configuration
- Docker/CI configuration where required

### Required Technologies

- Python 3.12
- UV
- Claude
- MCP
- HTTP client
- HTML/content parser
- Pydantic
- Pytest
- Ruff
- Mypy where applicable

### Technologies Intentionally Deferred

- Playwright
- Bruno
- Docker changes beyond actual requirements
- advanced observability

### Explicitly Out of Scope

- RAG
- vector database
- multi-agent architecture
- general-purpose crawler
- frontend/UI
- AWS
- Kubernetes
- database
- message queue
- unnecessary authentication
- unnecessary API layer
- advanced observability platform
- unnecessary browser automation

### Security Scope

Implement only security controls directly relevant to arbitrary web retrieval:

- HTTP/HTTPS protocol validation
- URL validation
- request timeout
- response-size limit
- basic private/internal network protection
- malformed response handling
- empty content handling
- untrusted treatment of retrieved page instructions

### Agentic Requirement

The web tool must not be unconditionally invoked by application code.

Claude must receive the tool definition and be able to decide whether the live-web capability is required.

### Final Demonstration

The final validation must use real current web information.

The demonstration must prove:

1. Claude receives the user request.
2. Claude determines that live information is required.
3. Claude selects the MCP web tool.
4. The MCP tool retrieves a real web page.
5. Useful content is extracted.
6. Structured information is returned.
7. Claude produces a grounded response.
8. Source information is retained/displayed.

### Scope Decision

LOCKED.

The project prioritizes:

Hard technology
+
Small scope
+
Real implementation
+
Agentic MCP tool selection
+
Live web retrieval
+
Content extraction
+
Grounded response
+
Testing
+
Fast completion

No additional technology or architecture should be added unless a genuine requirement emerges.
