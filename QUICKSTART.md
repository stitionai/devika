# Quick Start Guide - Visual Agent Meeting Room

## How to Run the Application

### Prerequisites
- Python 3.10+ 
- Node.js 18+
- Bun (JavaScript runtime)

### Step 1: Install Backend Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional dependency for cron jobs
pip install croniter
```

### Step 2: Install Frontend Dependencies

```bash
cd ui
bun install
cd ..
```

### Step 3: Start the Backend Server

```bash
# Terminal 1: Start the Python backend
python devika.py
```

The backend will run on `http://127.0.0.1:1337`

### Step 4: Start the Frontend

```bash
# Terminal 2: Start the UI
cd ui
bun run dev
```

The frontend will run on `http://127.0.0.1:5173` (or similar port)

### Step 5: Access the Meeting Room

1. Open your browser to `http://127.0.0.1:5173`
2. Click on the **Meeting Room** icon in the sidebar (users icon)
3. You'll see the Visual Agent Meeting Room with all agents

## Meeting Room Features

### Tab 1: Meeting Room
- See all agents (Bambu, Pauli, Synthia, Alex) as avatars
- View their online/offline/busy status
- Send messages in the chat
- Watch agents communicate in real-time

### Tab 2: Schedule
- Create new meetings
- Set date, time, and duration
- Select attendees
- Add agenda items
- Set recurring meetings (daily, weekly, etc.)

### Tab 3: Invitations
- Send invitations to agents
- Accept/decline received invitations
- View invitation history

## Creating Default Meetings

To create the default scheduled meetings:

```bash
python src/cron/agent_meeting.py --create-defaults
```

This creates:
- Daily Standup (9 AM daily)
- Weekly Planning (Monday 10 AM)
- Code Review (Tue/Thu 2 PM)
- Monthly Security Audit (1st of month)

## Running the Meeting Scheduler Daemon

To automatically trigger scheduled meetings:

```bash
python src/cron/agent_meeting.py --daemon
```

## Troubleshooting

### Backend won't start
- Check if port 1337 is already in use
- Ensure all dependencies are installed

### Frontend won't start
- Check if bun is installed: `bun --version`
- Try deleting `node_modules` and running `bun install` again

### Meeting Room not showing
- Make sure the backend is running first
- Check browser console for errors
- Verify WebSocket connection in browser DevTools

## Architecture Overview

```
Backend (Python)          Frontend (Svelte)
    │                          │
    ├─ src/meeting/           ├─ routes/meeting/
    │  ├─ models.py           │  └─ +page.svelte
    │  ├─ meeting_scheduler   ├─ components/
    │  ├─ meeting_room        │  ├─ MeetingRoom.svelte
    │  ├─ invitation_system   │  ├─ AgentAvatar.svelte
    │  └─ agent_presence      │  ├─ ChatBubble.svelte
    │                          │  ├─ MeetingScheduler.svelte
    ├─ src/cron/              │  └─ InvitationPanel.svelte
    │  └─ agent_meeting.py    └─ lib/
    │                          ├─ store.js
    └─ devika.py (main)       └─ meeting-sockets.js
```

## Next Steps

1. Configure your LLM API keys in the Settings page
2. Start a chat with an agent from the home page
3. Schedule a meeting and watch agents join
4. Send invitations between agents