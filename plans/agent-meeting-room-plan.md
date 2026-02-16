# Visual Agent Meeting Room - Implementation Plan

> **Reference Video:** https://youtu.be/Ia-jybqL8gc?si=WdfSUiD-Dk-NuDoh
> **Goal:** Create a visual meeting space where all BambuVerse agents can meet, communicate, invite each other, and schedule meetings (cron jobs).

## Executive Summary

This plan outlines the architecture and implementation steps for creating a **Visual Agent Meeting Room** - a real-time virtual space where agents (Bambu, Pauli, Synthia, Alex, and future agents) can:

1. **See each other visually** - Avatar-based representation in a shared space
2. **Communicate in real-time** - Watch agents talk and collaborate
3. **Invite each other** - Agent-to-agent invitation system
4. **Schedule meetings** - Cron-based meeting scheduling (aka "agent sync meetings")
5. **Update each other** - Status sharing and knowledge exchange

---

## Current Infrastructure Analysis

### Existing Agent Network

| Agent | Role | Status | Communication |
|-------|------|--------|---------------|
| Bambu | CEO & Coordinator | Active | A2A, CAMEL, WebSocket |
| Pauli | Planner | Active | CAMEL |
| Synthia | Executor | Active | CAMEL |
| Alex | Developer (MetaGPT) | Active | A2A, MetaGPT |

### Existing Communication Protocols

1. **A2A Protocol** ([`src/integrations/a2a/__init__.py`](src/integrations/a2a/__init__.py))
   - Agent discovery via Agent Cards
   - JSON-RPC 2.0 messaging
   - Task-based communication
   - SSE streaming for updates

2. **CAMEL Framework** ([`src/integrations/camel/__init__.py`](src/integrations/camel/__init__.py))
   - Role-playing patterns
   - Society-based agent groups
   - Multi-agent collaboration

3. **MetaGPT Integration** ([`src/integrations/metagpt/__init__.py`](src/integrations/metagpt/__init__.py))
   - Software development workflow
   - Sprint-based task execution

4. **WebSocket Events** ([`ui/src/lib/sockets.js`](ui/src/lib/sockets.js))
   - Real-time state updates
   - Agent monologue streaming
   - Token usage tracking

### Existing Cron System

- [`src/cron/repo_scanner.py`](src/cron/repo_scanner.py) - Repository scanning
- [`src/cron/security_scanner.py`](src/cron/security_scanner.py) - Security scanning

---

## Proposed Architecture

### High-Level System Design

```
+------------------------------------------------------------------+
|                    VISUAL AGENT MEETING ROOM                      |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+     +-------------------+                  |
|  |   Meeting Room    |     |   Agent Avatars   |                  |
|  |   (3D/2D Space)   |<--->|   (Visual Rep)    |                  |
|  +-------------------+     +-------------------+                  |
|           |                        |                              |
|           v                        v                              |
|  +-------------------+     +-------------------+                  |
|  |   Chat/Video      |     |   Status Panel    |                  |
|  |   Stream          |<--->|   (Agent States)  |                  |
|  +-------------------+     +-------------------+                  |
|           |                        |                              |
|           v                        v                              |
|  +-------------------+     +-------------------+                  |
|  |   Meeting         |     |   Invitation      |                  |
|  |   Scheduler       |<--->|   System          |                  |
|  +-------------------+     +-------------------+                  |
|                                                                   |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                    BACKEND SERVICES                               |
+------------------------------------------------------------------+
|  +-------------+  +-------------+  +-------------+  +----------+ |
|  | A2A Server  |  | CAMEL       |  | MetaGPT     |  | Cron     | |
|  |             |  | Society     |  | Team        |  | Scheduler| |
|  +-------------+  +-------------+  +-------------+  +----------+ |
|                              |                                     |
|                              v                                     |
|  +----------------------------------------------------------+    |
|  |              WebSocket / SSE Gateway                     |    |
|  +----------------------------------------------------------+    |
+------------------------------------------------------------------+
```

### Component Breakdown

#### 1. Meeting Room UI (Frontend)

A new Svelte route: `/meeting`

**Features:**
- Visual representation of agents as avatars in a shared space
- Real-time chat bubble visualization when agents speak
- Status indicators (active, idle, working, in-meeting)
- Meeting control panel (schedule, invite, join, leave)

**UI Components to Create:**
- [`MeetingRoom.svelte`](ui/src/lib/components/MeetingRoom.svelte) - Main meeting container
- [`AgentAvatar.svelte`](ui/src/lib/components/AgentAvatar.svelte) - Individual agent representation
- [`ChatBubble.svelte`](ui/src/lib/components/ChatBubble.svelte) - Visual chat messages
- [`MeetingScheduler.svelte`](ui/src/lib/components/MeetingScheduler.svelte) - Cron-based scheduling
- [`InvitationPanel.svelte`](ui/src/lib/components/InvitationPanel.svelte) - Agent invitations

#### 2. Meeting Scheduler Service (Backend)

A new Python module: [`src/meeting/`](src/meeting/)

**Features:**
- Create scheduled meetings (cron-based)
- Invite agents to meetings
- Track meeting attendance
- Record meeting transcripts
- Trigger agent sync workflows

**Components:**
- [`meeting_scheduler.py`](src/meeting/meeting_scheduler.py) - Core scheduling logic
- [`meeting_room.py`](src/meeting/meeting_room.py) - Meeting state management
- [`invitation_system.py`](src/meeting/invitation_system.py) - Agent invitations
- [`meeting_transcript.py`](src/meeting/meeting_transcript.py) - Record keeping

#### 3. Agent Presence System

Track which agents are online and available.

**Features:**
- Heartbeat system for agent presence
- Status broadcasting via WebSocket
- Agent availability calendar

**Components:**
- [`agent_presence.py`](src/meeting/agent_presence.py) - Presence tracking

#### 4. Real-Time Communication Layer

Enhanced WebSocket events for meeting room.

**New Events:**
```javascript
// Frontend -> Backend
meeting-join          // Agent joins meeting room
meeting-leave         // Agent leaves meeting room
meeting-invite        // Invite another agent
meeting-schedule      // Schedule a new meeting
meeting-message       // Send message in meeting

// Backend -> Frontend
agent-presence        // Agent presence update
agent-speaking        // Agent is speaking
meeting-started       // Meeting has started
meeting-ended         // Meeting has ended
invitation-received   // Agent received invitation
```

---

## Data Models

### Meeting Model

```python
@dataclass
class Meeting:
    meeting_id: str
    title: str
    scheduled_time: datetime
    duration_minutes: int
    organizer: str  # Agent ID
    attendees: List[str]  # Agent IDs
    status: MeetingStatus  # scheduled, in_progress, completed
    agenda: List[str]
    transcript: List[MeetingMessage]
    recurrence: Optional[str]  # Cron expression
```

### Agent Presence Model

```python
@dataclass
class AgentPresence:
    agent_id: str
    status: AgentStatus  # online, offline, busy, in_meeting
    last_heartbeat: datetime
    current_task: Optional[str]
    availability: List[TimeSlot]
```

### Invitation Model

```python
@dataclass
class AgentInvitation:
    invitation_id: str
    from_agent: str
    to_agent: str
    meeting_id: Optional[str]
    message: str
    status: InvitationStatus  # pending, accepted, declined
    created_at: datetime
```

---

## Implementation Phases

### Phase 1: Core Meeting Room Infrastructure

**Tasks:**
1. Create [`src/meeting/`](src/meeting/) module structure
2. Implement [`MeetingScheduler`](src/meeting/meeting_scheduler.py) class
3. Implement [`AgentPresence`](src/meeting/agent_presence.py) tracking
4. Add WebSocket events for meeting room
5. Create database models for meetings

**Deliverables:**
- Backend meeting service
- WebSocket event handlers
- Database schema

### Phase 2: Frontend Meeting Room UI

**Tasks:**
1. Create [`/meeting`](ui/src/routes/meeting/+page.svelte) route
2. Build [`MeetingRoom.svelte`](ui/src/lib/components/MeetingRoom.svelte) component
3. Build [`AgentAvatar.svelte`](ui/src/lib/components/AgentAvatar.svelte) component
4. Build [`ChatBubble.svelte`](ui/src/lib/components/ChatBubble.svelte) component
5. Integrate with WebSocket events

**Deliverables:**
- Visual meeting room interface
- Agent avatar representations
- Real-time chat visualization

### Phase 3: Meeting Scheduling & Invitations

**Tasks:**
1. Build [`MeetingScheduler.svelte`](ui/src/lib/components/MeetingScheduler.svelte) UI
2. Build [`InvitationPanel.svelte`](ui/src/lib/components/InvitationPanel.svelte) UI
3. Implement cron-based meeting triggers
4. Create invitation notification system

**Deliverables:**
- Meeting scheduling interface
- Agent invitation system
- Cron job integration

### Phase 4: Agent Sync Workflows

**Tasks:**
1. Define meeting agenda templates
2. Implement agent sync protocols
3. Create meeting transcript logging
4. Build post-meeting action triggers

**Deliverables:**
- Structured meeting workflows
- Transcript generation
- Action item extraction

---

## Cron Job Integration

### New Cron: Agent Sync Meeting

```python
# src/cron/agent_meeting.py

class AgentMeetingCron:
    """
    Scheduled agent sync meetings
    Triggers agents to join the meeting room at scheduled times
    """
    
    def schedule_meeting(
        self, 
        cron_expression: str,  # e.g., "0 9 * * 1" = Every Monday 9 AM
        attendees: List[str],
        agenda: List[str]
    ) -> Meeting:
        pass
    
    def trigger_meeting(self, meeting: Meeting):
        # Send WebSocket event to all attendees
        # Log meeting start
        # Begin transcript recording
        pass
```

### Example Meeting Schedules

| Meeting | Schedule | Attendees | Purpose |
|---------|----------|-----------|---------|
| Daily Standup | 0 9 * * * | All Agents | Status updates |
| Weekly Planning | 0 9 * * 1 | Bambu, Pauli | Sprint planning |
| Code Review | 0 14 * * 2,4 | Alex, Synthia | Review sessions |
| Security Audit | 0 10 1 * * | Bambu, Synthia | Monthly security |

---

## API Endpoints

### New Endpoints

```
POST /api/meeting/create           # Create a new meeting
GET  /api/meeting/list             # List all meetings
GET  /api/meeting/{id}             # Get meeting details
POST /api/meeting/{id}/join        # Join a meeting
POST /api/meeting/{id}/leave       # Leave a meeting
POST /api/meeting/{id}/invite      # Invite agent to meeting
GET  /api/meeting/{id}/transcript  # Get meeting transcript

GET  /api/agent/presence           # Get all agent presence
POST /api/agent/heartbeat          # Agent heartbeat

POST /api/invitation/send          # Send invitation
GET  /api/invitation/list          # List invitations
POST /api/invitation/{id}/accept   # Accept invitation
POST /api/invitation/{id}/decline  # Decline invitation
```

---

## Visual Design Concept

### Meeting Room Layout

```
+------------------------------------------------------------------+
|  AGENT MEETING ROOM                                    [Schedule] |
+------------------------------------------------------------------+
|                                                                   |
|    +--------+     +--------+     +--------+     +--------+       |
|    |  BAMBU |     | PAULI  |     |SYNTHIA |     |  ALEX  |       |
|    |  [CEO] |     |[Planner|     |[Execut]|     | [Dev]  |       |
|    |  o--o  |     |  o--o  |     |  o--o  |     |  o--o  |       |
|    |  \__/  |     |  \__/  |     |  \__/  |     |  \__/  |       |
|    +--------+     +--------+     +--------+     +--------+       |
|       speaking       idle        working        offline          |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  [Chat Log]                                                      |
|  ---------------------------------------------------------------- |
|  Bambu: Good morning team! Let's start our daily standup.        |
|  Pauli: I've prepared the sprint backlog for review.             |
|  Synthia: Deployment to staging completed successfully.           |
|  Alex: Code review for PR #42 is in progress.                    |
|                                                                   |
+------------------------------------------------------------------+
|  [Message Input]                                    [Send] [AI]  |
+------------------------------------------------------------------+
```

### Agent Avatar States

| State | Visual Indicator |
|-------|------------------|
| Online | Green ring around avatar |
| Offline | Grayed out avatar |
| Speaking | Animated speech bubble |
| Working | Spinning gear icon |
| In Meeting | "In Meeting" badge |

---

## Integration with Existing Systems

### A2A Protocol Enhancement

Extend A2A messages to support meeting invitations:

```python
# Add to A2AMessage metadata
{
    "message_type": "meeting_invitation",
    "meeting_id": "uuid",
    "scheduled_time": "ISO8601",
    "agenda": ["item1", "item2"]
}
```

### CAMEL Society Enhancement

Add meeting room as a shared context:

```python
class CAMELSociety:
    def __init__(self, name: str, meeting_room: MeetingRoom = None):
        self.meeting_room = meeting_room
    
    async def hold_meeting(self, agenda: List[str]) -> Meeting:
        pass
```

### WebSocket Enhancement

Add meeting-specific events to [`sockets.js`](ui/src/lib/sockets.js):

```javascript
export function initializeMeetingSockets() {
  socket.on("agent-presence", function (data) {
    // Update agent presence in meeting room
  });
  
  socket.on("agent-speaking", function (data) {
    // Show chat bubble animation
  });
  
  socket.on("meeting-started", function (data) {
    // Notify user that meeting has started
  });
}
```

---

## File Structure

```
src/
  meeting/
    __init__.py
    meeting_scheduler.py      # Core scheduling logic
    meeting_room.py           # Meeting state management
    invitation_system.py      # Agent invitations
    meeting_transcript.py     # Record keeping
    agent_presence.py         # Presence tracking
    models.py                 # Data models
    
  cron/
    agent_meeting.py          # NEW: Agent meeting cron job
    
ui/
  src/
    routes/
      meeting/
        +page.svelte          # NEW: Meeting room route
        
    lib/
      components/
        MeetingRoom.svelte    # NEW: Main meeting container
        AgentAvatar.svelte    # NEW: Agent representation
        ChatBubble.svelte     # NEW: Chat visualization
        MeetingScheduler.svelte # NEW: Scheduling UI
        InvitationPanel.svelte  # NEW: Invitation UI
```

---

## Success Criteria

1. **All agents can join the meeting room** - Bambu, Pauli, Synthia, Alex
2. **Visual representation is clear** - Avatars with status indicators
3. **Real-time communication works** - Messages appear instantly
4. **Scheduling functions** - Cron-based meetings trigger correctly
5. **Invitations work** - Agents can invite each other
6. **Transcripts are generated** - Meeting records are saved

---

## Next Steps

1. **Review this plan** with the user
2. **Switch to Code mode** for implementation
3. **Begin with Phase 1** - Core infrastructure
4. **Iterate based on feedback**

---

*Last Updated: 2026-02-15*
*Author: Bambu (Architect Mode)*