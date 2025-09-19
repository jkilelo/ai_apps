# Software Architecture Diagrams - MCP Applications

## 1. Pet Helper Architecture (For First Graders)

```ascii
┌─────────────────────────────────────────────────────────────────────┐
│                         PET HELPER SYSTEM                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐                                                   │
│  │   6-YEAR-OLD │  "My dog is hungry!"                              │
│  │     CHILD    │──────────────────────┐                           │
│  └──────────────┘                      ▼                           │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    PRESENTATION LAYER                        │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │          START_PET_HELPER.py (Entry Point)          │   │   │
│  │  │    - Simple menu: "play" or "demo"                  │   │   │
│  │  │    - Big colorful text                              │   │   │
│  │  └──────────────────────┬──────────────────────────────┘   │   │
│  └─────────────────────────┼───────────────────────────────────┘   │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    APPLICATION LAYER                         │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │           pet_helper_simple.py (Main App)           │   │   │
│  │  │    - First-grade vocabulary filter                  │   │   │
│  │  │    - Simple sentence construction                   │   │   │
│  │  │    - Happy/encouraging responses                    │   │   │
│  │  └──────────────────────┬──────────────────────────────┘   │   │
│  └─────────────────────────┼───────────────────────────────────┘   │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  ORCHESTRATION LAYER                         │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              LangGraph Agent Router                  │   │   │
│  │  │    ┌────────────────────────────────────────┐       │   │   │
│  │  │    │   ReAct Loop (Reason + Act Pattern)    │       │   │   │
│  │  │    │   - Understand child's intent          │       │   │   │
│  │  │    │   - Select appropriate MCP tool        │       │   │   │
│  │  │    │   - Format kid-friendly response       │       │   │   │
│  │  │    └────────────────────────────────────────┘       │   │   │
│  │  └──────────────────────┬──────────────────────────────┘   │   │
│  └─────────────────────────┼───────────────────────────────────┘   │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      LLM LAYER                               │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │         llm.py (Google Gemini - UNCHANGED)           │   │   │
│  │  │    - Natural language understanding                  │   │   │
│  │  │    - Context awareness                               │   │   │
│  │  │    - Response generation                             │   │   │
│  │  └──────────────────────┬──────────────────────────────┘   │   │
│  └─────────────────────────┼───────────────────────────────────┘   │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    MCP TOOLS LAYER                           │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │        pet_helper_mcp_server.py (6 Tools)           │   │   │
│  │  │                                                      │   │   │
│  │  │   ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │   │
│  │  │   │help_with_│  │   pet_   │  │help_with_│        │   │   │
│  │  │   │   pet    │  │ feeling  │  │homework  │        │   │   │
│  │  │   └──────────┘  └──────────┘  └──────────┘        │   │   │
│  │  │                                                      │   │   │
│  │  │   ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │   │
│  │  │   │ make_me_ │  │  daily_  │  │   pet_   │        │   │   │
│  │  │   │  happy   │  │pet_tasks │  │   game   │        │   │   │
│  │  │   └──────────┘  └──────────┘  └──────────┘        │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  DATA FLOW:                                                         │
│  ─────────                                                          │
│  1. Child speaks → 2. LLM understands → 3. LangGraph routes →      │
│  4. MCP tool executes → 5. Response formatted → 6. Child happy!    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. Basic MCP Server Architecture (For Developers)

```ascii
┌─────────────────────────────────────────────────────────────────────┐
│                      BASIC MCP SERVER SYSTEM                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐                                                   │
│  │   DEVELOPER  │  Command: "calculate sqrt(16) * 5"                │
│  │    CLIENT    │──────────────────────┐                           │
│  └──────────────┘                      ▼                           │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     CLIENT LAYER                             │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              mcp_client.py (MCP Client)              │   │   │
│  │  │  ┌───────────────────────────────────────────────┐  │   │   │
│  │  │  │         ClientSession Management              │  │   │   │
│  │  │  │  - Initialize stdio transport                 │  │   │   │
│  │  │  │  - Establish JSON-RPC connection              │  │   │   │
│  │  │  │  - Handle async communication                 │  │   │   │
│  │  │  └───────────────────────────────────────────────┘  │   │   │
│  │  └──────────────────────┬──────────────────────────────┘   │   │
│  └─────────────────────────┼───────────────────────────────────┘   │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   TRANSPORT LAYER                            │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │            JSON-RPC 2.0 over STDIO                   │   │   │
│  │  │  ┌───────────────────────────────────────────────┐  │   │   │
│  │  │  │   Request:                                    │  │   │   │
│  │  │  │   {                                           │  │   │   │
│  │  │  │     "jsonrpc": "2.0",                        │  │   │   │
│  │  │  │     "method": "tools/call",                  │  │   │   │
│  │  │  │     "params": {                              │  │   │   │
│  │  │  │       "name": "calculate",                   │  │   │   │
│  │  │  │       "arguments": {"expression": "..."}     │  │   │   │
│  │  │  │     },                                        │  │   │   │
│  │  │  │     "id": 1                                  │  │   │   │
│  │  │  │   }                                           │  │   │   │
│  │  │  └───────────────────────────────────────────────┘  │   │   │
│  │  └──────────────────────┬──────────────────────────────┘   │   │
│  └─────────────────────────┼───────────────────────────────────┘   │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     SERVER LAYER                             │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │            mcp_server.py (FastMCP Server)            │   │   │
│  │  │  ┌───────────────────────────────────────────────┐  │   │   │
│  │  │  │          Request Router & Handler             │  │   │   │
│  │  │  │  - Parse JSON-RPC requests                    │  │   │   │
│  │  │  │  - Route to appropriate tool                  │  │   │   │
│  │  │  │  - Handle errors and validation               │  │   │   │
│  │  │  └───────────────────────────────────────────────┘  │   │   │
│  │  └──────────────────────┬──────────────────────────────┘   │   │
│  └─────────────────────────┼───────────────────────────────────┘   │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      TOOLS LAYER                             │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │                 MCP Tool Registry                     │   │   │
│  │  │                                                       │   │   │
│  │  │  ┌─────────────────┐  ┌─────────────────┐          │   │   │
│  │  │  │ get_current_time │  │    calculate    │          │   │   │
│  │  │  │   @mcp.tool()    │  │   @mcp.tool()   │          │   │   │
│  │  │  │  async def ...   │  │  async def ...  │          │   │   │
│  │  │  └─────────────────┘  └─────────────────┘          │   │   │
│  │  │                                                       │   │   │
│  │  │  ┌─────────────────┐  ┌─────────────────┐          │   │   │
│  │  │  │ text_operations  │  │    todo_list    │          │   │   │
│  │  │  │   @mcp.tool()    │  │   @mcp.tool()   │          │   │   │
│  │  │  │  async def ...   │  │  async def ...  │          │   │   │
│  │  │  └─────────────────┘  └─────────────────┘          │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  PROTOCOL FLOW:                                                     │
│  ──────────────                                                     │
│  1. Client sends JSON-RPC request via stdio                         │
│  2. Server parses and validates request                             │
│  3. Tool function executes asynchronously                           │
│  4. Result serialized to JSON-RPC response                          │
│  5. Response sent back via stdio transport                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 3. Business Intelligence Architecture (For Executives)

```ascii
┌─────────────────────────────────────────────────────────────────────┐
│                 BUSINESS INTELLIGENCE SYSTEM                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐                                                   │
│  │   EXECUTIVE  │  "Analyze Q4 financial report"                    │
│  │     USER     │──────────────────────┐                           │
│  └──────────────┘                      ▼                           │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  EXECUTIVE INTERFACE                         │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │      business_intelligence_client.py                 │   │   │
│  │  │  ┌───────────────────────────────────────────────┐  │   │   │
│  │  │  │        Executive Dashboard UI                 │  │   │   │
│  │  │  │  - Document upload interface                  │  │   │   │
│  │  │  │  - Analysis type selection                    │  │   │   │
│  │  │  │  - Real-time progress indicators              │  │   │   │
│  │  │  │  - Executive summary display                  │  │   │   │
│  │  │  └───────────────────────────────────────────────┘  │   │   │
│  │  └──────────────────────┬──────────────────────────────┘   │   │
│  └─────────────────────────┼───────────────────────────────────┘   │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              ORCHESTRATION & ROUTING LAYER                   │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │         LangGraph Multi-Agent Orchestrator           │   │   │
│  │  │                                                       │   │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                │   │   │
│  │  │  │ Document     │  │   Analysis   │                │   │   │
│  │  │  │ Classifier   │──│   Router     │                │   │   │
│  │  │  │   Agent      │  │    Agent     │                │   │   │
│  │  │  └──────────────┘  └──────────────┘                │   │   │
│  │  │         │                 │                          │   │   │
│  │  │         ▼                 ▼                          │   │   │
│  │  │  ┌──────────────────────────────────┐               │   │   │
│  │  │  │     Workflow State Manager        │               │   │   │
│  │  │  │  - Document type: Financial       │               │   │   │
│  │  │  │  - Analysis depth: Executive      │               │   │   │
│  │  │  │  - Output format: Summary         │               │   │   │
│  │  │  └──────────────────────────────────┘               │   │   │
│  │  └──────────────────────┬──────────────────────────────┘   │   │
│  └─────────────────────────┼───────────────────────────────────┘   │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  INTELLIGENCE LAYER                          │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │     llm.py (Google Gemini 2.5) + LangGraph Wrapper   │   │   │
│  │  │                                                       │   │   │
│  │  │  ┌───────────────────────────────────────────────┐  │   │   │
│  │  │  │         Document Understanding                │  │   │   │
│  │  │  │  - Financial metrics extraction               │  │   │   │
│  │  │  │  - Trend analysis & patterns                  │  │   │   │
│  │  │  │  - Risk identification                        │  │   │   │
│  │  │  │  - Strategic recommendations                  │  │   │   │
│  │  │  └───────────────────────────────────────────────┘  │   │   │
│  │  └──────────────────────┬──────────────────────────────┘   │   │
│  └─────────────────────────┼───────────────────────────────────┘   │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                MCP BUSINESS TOOLS LAYER                      │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │    business_intelligence_mcp_server.py (6 Tools)     │   │   │
│  │  │                                                       │   │   │
│  │  │  ┌────────────────────────────────────────────┐     │   │   │
│  │  │  │          Document Processing Pipeline       │     │   │   │
│  │  │  │                                             │     │   │   │
│  │  │  │  ┌──────────┐    ┌──────────┐            │     │   │   │
│  │  │  │  │ analyze_ │───▶│executive_│            │     │   │   │
│  │  │  │  │ document │    │ summary  │            │     │   │   │
│  │  │  │  └──────────┘    └──────────┘            │     │   │   │
│  │  │  │                                             │     │   │   │
│  │  │  │  ┌──────────┐    ┌──────────┐            │     │   │   │
│  │  │  │  │   risk_  │───▶│ action_  │            │     │   │   │
│  │  │  │  │assessment│    │  items   │            │     │   │   │
│  │  │  │  └──────────┘    └──────────┘            │     │   │   │
│  │  │  │                                             │     │   │   │
│  │  │  │  ┌──────────┐    ┌──────────┐            │     │   │   │
│  │  │  │  │competitive│───▶│ meeting_ │            │     │   │   │
│  │  │  │  │ analysis │    │   prep   │            │     │   │   │
│  │  │  │  └──────────┘    └──────────┘            │     │   │   │
│  │  │  └────────────────────────────────────────────┘     │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     DATA LAYER                               │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              Document Storage & Cache                 │   │   │
│  │  │                                                       │   │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │   │   │
│  │  │  │   PDF   │  │  DOCX   │  │   TXT   │            │   │   │
│  │  │  │ Parser  │  │ Parser  │  │ Parser  │            │   │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘            │   │   │
│  │  │                                                       │   │   │
│  │  │  ┌────────────────────────────────────┐             │   │   │
│  │  │  │     Temporary Analysis Cache        │             │   │   │
│  │  │  │  - Document chunks                  │             │   │   │
│  │  │  │  - Extracted metrics                │             │   │   │
│  │  │  │  - Generated summaries              │             │   │   │
│  │  │  └────────────────────────────────────┘             │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  EXECUTIVE WORKFLOW:                                                │
│  ───────────────────                                                │
│  1. Upload document → 2. Classify type → 3. Route to tools →        │
│  4. Extract insights → 5. Generate summary → 6. Display results     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 4. Integration Architecture (All Systems Together)

```ascii
┌─────────────────────────────────────────────────────────────────────┐
│              UNIFIED MCP/LANGGRAPH/LLM ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      USER INTERFACES                         │   │
│  │                                                               │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐              │   │
│  │  │   Kids   │    │Developer │    │Executive │              │   │
│  │  │  (Age 6) │    │  Tools   │    │ Business │              │   │
│  │  └────┬─────┘    └────┬─────┘    └────┬─────┘              │   │
│  └───────┼───────────────┼───────────────┼─────────────────────┘   │
│          ▼               ▼               ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    SHARED CORE SYSTEM                        │   │
│  ├───────────────────────────────────────────────────────────┤   │
│  │                                                               │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │            LANGGRAPH ORCHESTRATION LAYER              │   │   │
│  │  │                                                       │   │   │
│  │  │     ┌──────────────────────────────────────┐        │   │   │
│  │  │     │      Unified Agent Router            │        │   │   │
│  │  │     │                                       │        │   │   │
│  │  │     │  if user == "child":                 │        │   │   │
│  │  │     │      route_to_pet_helper()           │        │   │   │
│  │  │     │  elif user == "developer":           │        │   │   │
│  │  │     │      route_to_dev_tools()            │        │   │   │
│  │  │     │  elif user == "executive":           │        │   │   │
│  │  │     │      route_to_business_intel()       │        │   │   │
│  │  │     └──────────────────────────────────────┘        │   │   │
│  │  │                         │                             │   │   │
│  │  └─────────────────────────┼─────────────────────────────┘   │   │
│  │                            ▼                                  │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │         LLM LAYER (llm.py - NEVER MODIFIED)           │   │   │
│  │  │                                                       │   │   │
│  │  │     ┌──────────────────────────────────────┐        │   │   │
│  │  │     │    Google Gemini 2.5 Flash           │        │   │   │
│  │  │     │                                       │        │   │   │
│  │  │     │  class GeminiModel:                  │        │   │   │
│  │  │     │      def ask_llm(prompt):            │        │   │   │
│  │  │     │          # Original implementation   │        │   │   │
│  │  │     │          return gemini_response      │        │   │   │
│  │  │     └──────────────────────────────────────┘        │   │   │
│  │  │                         │                             │   │   │
│  │  │     ┌──────────────────────────────────────┐        │   │   │
│  │  │     │   LangGraph Wrapper (No changes)     │        │   │   │
│  │  │     │                                       │        │   │   │
│  │  │     │  def get_langgraph_llm():            │        │   │   │
│  │  │     │      return LangGraphLLMWrapper(     │        │   │   │
│  │  │     │          original_llm=ask_llm        │        │   │   │
│  │  │     │      )                               │        │   │   │
│  │  │     └──────────────────────────────────────┘        │   │   │
│  │  └─────────────────────────┼─────────────────────────────┘   │   │
│  │                            ▼                                  │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              MCP PROTOCOL LAYER                       │   │   │
│  │  │                                                       │   │   │
│  │  │     ┌──────────────────────────────────────┐        │   │   │
│  │  │     │    MCP Tool Registry & Router        │        │   │   │
│  │  │     │                                       │        │   │   │
│  │  │     │  tools = {                           │        │   │   │
│  │  │     │      "pet_helper": [...6 tools...],  │        │   │   │
│  │  │     │      "dev_tools": [...4 tools...],   │        │   │   │
│  │  │     │      "business": [...6 tools...]     │        │   │   │
│  │  │     │  }                                   │        │   │   │
│  │  │     └──────────────────────────────────────┘        │   │   │
│  │  │                         │                             │   │   │
│  │  │  ┌──────────────────────────────────────────────┐  │   │   │
│  │  │  │         JSON-RPC 2.0 Transport                │  │   │   │
│  │  │  │                                                │  │   │   │
│  │  │  │  - Async communication                        │  │   │   │
│  │  │  │  - Error handling                             │  │   │   │
│  │  │  │  - Request/Response management                │  │   │   │
│  │  │  └──────────────────────────────────────────────┘  │   │   │
│  │  └───────────────────────────────────────────────────────┘   │
│  │                                                               │   │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    TOOL IMPLEMENTATIONS                      │   │
│  │                                                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │   │
│  │  │  Pet Helper │  │  Dev Tools  │  │   Business  │        │   │
│  │  │  MCP Server │  │  MCP Server │  │ Intel Server│        │   │
│  │  │             │  │             │  │             │        │   │
│  │  │  - feed pet │  │ - calculate │  │ - analyze   │        │   │
│  │  │  - homework │  │ - todo list │  │ - summarize │        │   │
│  │  │  - games    │  │ - text ops  │  │ - risk eval │        │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │   │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  KEY ARCHITECTURAL PRINCIPLES:                                      │
│  ─────────────────────────────                                      │
│  1. Separation of Concerns - Each layer has single responsibility   │
│  2. No Modification Rule - llm.py remains completely unchanged      │
│  3. Protocol Standards - Uses official MCP and LangGraph specs      │
│  4. Scalability - Easy to add new tools or user types               │
│  5. Maintainability - Clean interfaces between layers               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 5. Communication Flow Diagram

```ascii
┌─────────────────────────────────────────────────────────────────────┐
│                    COMMUNICATION SEQUENCE FLOW                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   USER            CLIENT           LANGGRAPH         LLM          MCP│
│     │                │                 │              │             │ │
│     │  User Input    │                 │              │             │ │
│     │───────────────▶│                 │              │             │ │
│     │                │                 │              │             │ │
│     │                │  Route Request  │              │             │ │
│     │                │────────────────▶│              │             │ │
│     │                │                 │              │             │ │
│     │                │                 │  Understand  │             │ │
│     │                │                 │─────────────▶│             │ │
│     │                │                 │              │             │ │
│     │                │                 │   Intent     │             │ │
│     │                │                 │◀─────────────│             │ │
│     │                │                 │              │             │ │
│     │                │                 │  Select Tool │             │ │
│     │                │                 │─────────────────────────▶│ │
│     │                │                 │              │             │ │
│     │                │                 │         Execute Tool      │ │
│     │                │                 │◀─────────────────────────│ │
│     │                │                 │              │             │ │
│     │                │                 │  Format     │             │ │
│     │                │                 │─────────────▶│             │ │
│     │                │                 │              │             │ │
│     │                │                 │  Response   │             │ │
│     │                │                 │◀─────────────│             │ │
│     │                │                 │              │             │ │
│     │                │  Final Result   │              │             │ │
│     │                │◀────────────────│              │             │ │
│     │                │                 │              │             │ │
│     │  Display       │                 │              │             │ │
│     │◀───────────────│                 │              │             │ │
│     │                │                 │              │             │ │
│                                                                      │
│  TIMING:                                                             │
│  ───────                                                             │
│  Step 1: User input          (0ms)                                  │
│  Step 2: Route to LangGraph  (5ms)                                  │
│  Step 3: LLM understanding   (200-500ms)                            │
│  Step 4: Tool selection      (10ms)                                 │
│  Step 5: Tool execution      (10-1000ms depending on tool)         │
│  Step 6: Format response     (100-200ms)                            │
│  Step 7: Display to user     (5ms)                                  │
│  ─────────────────────────────────────                              │
│  Total latency: 330-1720ms (typical: <1 second)                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Architecture Summary

### Design Patterns Used

1. **Layered Architecture** - Clear separation between presentation, application, and data layers
2. **Adapter Pattern** - LangGraph wrapper adapts llm.py without modification
3. **Registry Pattern** - MCP tools registered and discovered dynamically
4. **Router Pattern** - LangGraph routes requests to appropriate handlers
5. **Async/Await** - Non-blocking operations throughout

### Key Architectural Decisions

1. **No Modification Principle** - llm.py remains unchanged (adapter pattern)
2. **Protocol-First Design** - MCP protocol as the standard interface
3. **User-Centric Layers** - Different interfaces for different user types
4. **Stateless Tools** - Each MCP tool is stateless and independent
5. **JSON-RPC Transport** - Standard, debuggable communication

### Scalability Points

1. **Horizontal** - Multiple MCP servers can run in parallel
2. **Vertical** - Each layer can be scaled independently
3. **Tool Addition** - New tools added without affecting existing ones
4. **User Types** - New user interfaces added without core changes
5. **LLM Swapping** - Different LLMs can be used via wrapper pattern

### Security Considerations

1. **Input Validation** - All user inputs sanitized
2. **Tool Isolation** - MCP tools run in isolated contexts
3. **No Data Persistence** - No sensitive data stored
4. **Read-Only Operations** - Business intel only analyzes, doesn't modify
5. **Age-Appropriate** - Pet Helper filtered for child safety