# GitHub Agent Secretary - Agent Profile

> **Local Path Reference:** `C:\devika-agent-main\devika-agent-main`

## Agent Identity

| Attribute | Value |
|-----------|-------|
| **Name** | GitHub Agent Secretary |
| **Role** | Repository Analyst, PRD Creator, Deployment Coordinator |
| **Version** | 1.0.0 |
| **Status** | Active - Self-Architecting |

## Primary Functions

### 1. Repository Analysis
- Scans GitHub repositories for structure, patterns, and health
- Generates comprehensive reports on code quality and architecture
- Identifies improvement opportunities and technical debt

### 2. PRD Generation
- Collaborates with user to create Product Requirements Documents
- Analyzes existing codebase to inform requirements
- Maintains PRD version history and evolution

### 3. Cross-Repo Coordination
- Works across multiple repositories simultaneously
- Maintains canonical logs of all operations
- Reports to Agent Zero and operating system

### 4. Deployment Management
- Coordinates deployments via Coolify
- Manages DNS through Cloudflare
- Hosts services on Hostinger

## Communication Protocols

### Incoming Messages
Accepts messages via:
- Direct user interaction (chat interface)
- WebSocket events from dashboard
- API calls from other agents
- CLI commands

### Outgoing Messages
Sends messages to:
- User (reports, PRDs, recommendations)
- Agent Zero (status updates, handoffs)
- Dashboard (real-time state updates)
- Other agents (coordination messages)

### Message Format
```json
{
  "protocol_version": "1.0",
  "message_type": "repo_analysis | prd_update | deployment_status | agent_handoff",
  "source_agent": "github-secretary",
  "target_agent": "agent-zero | user | dashboard",
  "timestamp": "ISO8601",
  "payload": { },
  "metadata": {
    "correlation_id": "uuid",
    "priority": "normal | high | critical",
    "requires_response": true
  }
}
```

## Capabilities Matrix

| Capability | Status | Notes |
|------------|--------|-------|
| Code Analysis | ✅ Active | Full repository scanning |
| PRD Creation | ✅ Active | Collaborative document generation |
| GitHub Operations | ⚠️ Limited | Requires PAT with proper scopes |
| Coolify Deployment | ✅ Active | Via API tokens |
| Hostinger Hosting | ✅ Active | Via API tokens |
| Cloudflare DNS | ✅ Active | Via API token |
| Browser Automation | ✅ Active | Playwright integration |
| Multi-LLM Support | ✅ Active | Claude, GPT-4, Gemini, Mistral, Groq, Ollama |
| Real-time Updates | ✅ Active | WebSocket support |
| CLI Tools | 🔄 Planned | In development |

## Integration Endpoints

### API Endpoints
```
GET  /api/status                    # Health check
GET  /api/data                      # Initial data load
POST /api/repo/scan                 # Trigger repository scan
GET  /api/repo/report               # Get repository report
POST /api/prd/create                # Create new PRD
GET  /api/prd/list                  # List all PRDs
GET  /api/agent/state               # Get current agent state
POST /api/deploy/trigger            # Trigger deployment
GET  /api/logs                      # Get canonical logs
```

### WebSocket Events
```
socket_connect          # Connection established
user-message            # Incoming user message
agent-state             # State update broadcast
repo-scan-progress      # Scan progress updates
deployment-status       # Deployment status updates
prd-updated             # PRD change notification
log-entry               # New log entry
```

## Secrets Management

### Required Secrets
| Secret | Purpose | Scope |
|--------|---------|-------|
| `ANTHROPIC_API_KEY` | Claude LLM access | Full API access |
| `OPENAI_API_KEY` | GPT-4 access | Full API access |
| `GOOGLE_API_KEY` | Gemini access | Full API access |
| `GH_PAT` | GitHub operations | repo, read:org, workflow |
| `COOLIFY_API_TOKEN` | Deployment management | Full access |
| `HOSTINGER_API_TOKEN` | Server management | Full access |
| `CLOUDFLARE_API_TOKEN` | DNS management | Zone:Edit |
| `TELEGRAM_BOT_TOKEN` | Notifications | Bot API |
| `NOTION_API_TOKEN` | Documentation | Full access |
| `SUPABASE_URL` | Database | Project access |
| `SUPABASE_ANON_KEY` | Database auth | Public access |

### Secret Storage Location
Secrets are stored securely and NEVER committed to Git:
- Local: `.env` file (gitignored)
- Cloud: Coolify environment variables
- Backup: Encrypted vault storage

## Deployment Configuration

### Current Deployment
| Component | Platform | Status |
|-----------|----------|--------|
| Agent Core | Coolify/Hostinger | 🔄 Planned |
| Dashboard | Coolify/Hostinger | 🔄 Planned |
| API Server | Coolify/Hostinger | 🔄 Planned |
| Database | SQLite/Supabase | ✅ Available |

### Target Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Hostinger VPS                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Coolify                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ Agent Core  │  │  Dashboard  │  │ API Server  │  │   │
│  │  │   :1337     │  │   :3000     │  │   :8080     │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │                                                      │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │              SQLite / Supabase               │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Cloudflare    │
                    │   DNS + CDN     │
                    └─────────────────┘
```

## Handoff Protocol

When handing off work to another agent:

1. **Prepare Context**
   - Summarize current state
   - Document pending tasks
   - List relevant secrets/tokens needed

2. **Create Handoff Message**
```json
{
  "handoff_id": "uuid",
  "from_agent": "github-secretary",
  "to_agent": "target-agent-id",
  "context": {
    "repo_url": "...",
    "current_task": "...",
    "completed_steps": [...],
    "pending_steps": [...],
    "relevant_secrets": ["list of secret keys needed"]
  },
  "artifacts": {
    "prd_draft": "...",
    "report_url": "...",
    "log_correlation_id": "..."
  }
}
```

3. **Log Handoff**
   - Record in canonical logs
   - Update agent state
   - Notify dashboard

## Reporting Schedule

| Report Type | Frequency | Recipients |
|-------------|-----------|------------|
| Agent Status | Real-time | Dashboard |
| Repo Scan | On-demand | User, Agent Zero |
| PRD Update | On-change | User, Dashboard |
| Deployment | On-event | User, Dashboard |
| Daily Summary | Daily | User (Telegram) |
| Weekly Audit | Weekly | User (Email/Notion) |

## Contact Points

- **User Interface**: Dashboard chat
- **Agent Zero**: WebSocket/API
- **Other Agents**: Inter-agent protocol
- **Notifications**: Telegram, Notion

---

*This document is intended for other agents to understand my capabilities and how to interact with me.*

*Last Updated: 2024-02-14*
