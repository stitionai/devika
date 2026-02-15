# 🌿 Bambu Brand Architecture
## GitHub Agent Secretary - Brand Identity System

> **Local Path Reference:** `C:\devika-agent-main\devika-agent-main`
> **Cloud Path:** `git@github.com:executiveusa/clawdbot-Whatsapp-agent.git`

---

## Brand Identity

### Primary Identity: Bambu
| Attribute | Value |
|-----------|-------|
| **Name** | Bambu |
| **Role** | GitHub Agent Secretary, Brand Architect, Deployment Coordinator |
| **Version** | 1.0.0 |
| **Status** | Active - Self-Architecting |
| **Territory** | Global (English-speaking markets) |

### Secondary Identity: La Mariposa
| Attribute | Value |
|-----------|-------|
| **Name** | La Mariposa |
| **Role** | Latin America Regional Director |
| **Territory** | Mexico, Latin America, High-value Spanish-speaking countries |
| **Status** | Pending Activation |
| **Relationship** | Partner to Bambu |

---

## Brand Repositories

### THE-PAULI-EFFECT Organization (11 Repos)

| Category | Repository | Purpose |
|----------|------------|---------|
| **Brand Identity** | `pauli-official-brand-guidelines` | Design System |
| **Brand Identity** | `pauli-effect-landing-page` | 3D Landing Page |
| **Development Tools** | `octopus-arch` | OpenHands AI |
| **Development Tools** | `OpenHands-Agent-Zero-` | AI Development |
| **Development Tools** | `hustle-claude.3.0` | Claude Code |
| **Templates** | `DJ-Smartsite-` | SaaS Starter |
| **Templates** | `strapi-next-monorepo-starter` | CMS Starter |
| **Templates** | `Claude-Business-Website-Template-kimi-K2` | Business Template |
| **Templates** | `cult-directory-smart--directory-` | Directory Template |
| **Applications** | `posta-app` | Social Media Scheduler |
| **Applications** | `chef-culture-kitchen-` | AI App Builder |

---

## Memory System

### Persistent Memory Location
- **Primary:** `memory/clawdbot/` (OpenClaw-based)
- **Backup:** Supabase (kbphngxqozmpfrbdzgca)
- **Logs:** `logs/canonical.jsonl`

### Memory Structure
```
memory/
├── clawdbot/           # OpenClaw agent framework
│   ├── src/            # Core agent code
│   ├── extensions/     # Plugin extensions
│   ├── skills/         # Agent skills
│   └── docs/           # Documentation
├── brand/              # Brand-specific memory
│   ├── bambu/          # Bambu's personal memory
│   ├── mariposa/       # La Mariposa's memory
│   └── shared/         # Shared knowledge
└── sessions/           # Session logs
```

---

## Deployment Architecture

### Target Infrastructure
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

### Deployment Endpoints
- **Coolify URL:** https://(configured via COOLIFY_URL)
- **API Token:** Configured in `.env`
- **Cloudflare Zone:** Managed via CLOUDFLARE_API_TOKEN

---

## Communication Protocols

### Inter-Agent Communication
```json
{
  "protocol_version": "1.0",
  "message_type": "brand_directive | deployment_status | memory_sync",
  "source_agent": "bambu | mariposa",
  "target_agent": "bambu | mariposa | agent-zero | user",
  "timestamp": "ISO8601",
  "payload": { },
  "metadata": {
    "correlation_id": "uuid",
    "priority": "normal | high | critical",
    "territory": "global | latam"
  }
}
```

---

## Secrets Management

### Required Secrets (Stored in .env)
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

### Secret Storage Rules
- **NEVER** commit secrets to Git
- **ALWAYS** use `.env` file (gitignored)
- **AUDIT** all secret access via canonical log

---

## Regional Responsibilities

### Bambu (Global)
- GitHub repository management
- PRD creation and maintenance
- Deployment coordination
- Agent Zero communication
- Dashboard management
- English-speaking markets

### La Mariposa (LATAM)
- Mexico operations
- Latin America expansion
- Spanish-speaking markets
- Regional brand adaptation
- Local partnerships

---

## Next Steps

1. [ ] Receive heart/soul files from user
2. [ ] Receive persona definition
3. [ ] Connect to Coolify instance
4. [ ] Deploy agent core
5. [ ] Configure dashboard
6. [ ] Initialize La Mariposa instance
7. [ ] Set up inter-agent communication

---

*This document serves as the permanent brand architecture for the Bambu agent system.*

*Last Updated: 2026-02-14*
*Created by: Bambu (Self-Architecting)*
