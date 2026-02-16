#!/usr/bin/env python3
"""
Data Models for Visual Agent Meeting Room
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class MeetingStatus(Enum):
    """Status of a meeting"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AgentStatus(Enum):
    """Status of an agent's presence"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    IN_MEETING = "in_meeting"
    IDLE = "idle"


class InvitationStatus(Enum):
    """Status of an invitation"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


@dataclass
class TimeSlot:
    """A time slot for availability"""
    start: str  # ISO8601 datetime
    end: str    # ISO8601 datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeSlot":
        return cls(**data)


@dataclass
class MeetingMessage:
    """A message in a meeting"""
    message_id: str
    agent_id: str
    agent_name: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeetingMessage":
        return cls(**data)
    
    @classmethod
    def create(cls, agent_id: str, agent_name: str, content: str) -> "MeetingMessage":
        return cls(
            message_id=str(uuid.uuid4()),
            agent_id=agent_id,
            agent_name=agent_name,
            content=content
        )


@dataclass
class Meeting:
    """
    A meeting between agents
    """
    meeting_id: str
    title: str
    scheduled_time: str  # ISO8601 datetime
    duration_minutes: int
    organizer: str  # Agent ID
    attendees: List[str]  # Agent IDs
    status: MeetingStatus
    agenda: List[str] = field(default_factory=list)
    messages: List[MeetingMessage] = field(default_factory=list)
    recurrence: Optional[str] = None  # Cron expression
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "meeting_id": self.meeting_id,
            "title": self.title,
            "scheduled_time": self.scheduled_time,
            "duration_minutes": self.duration_minutes,
            "organizer": self.organizer,
            "attendees": self.attendees,
            "status": self.status.value,
            "agenda": self.agenda,
            "messages": [m.to_dict() for m in self.messages],
            "recurrence": self.recurrence,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Meeting":
        return cls(
            meeting_id=data["meeting_id"],
            title=data["title"],
            scheduled_time=data["scheduled_time"],
            duration_minutes=data["duration_minutes"],
            organizer=data["organizer"],
            attendees=data["attendees"],
            status=MeetingStatus(data["status"]),
            agenda=data.get("agenda", []),
            messages=[MeetingMessage.from_dict(m) for m in data.get("messages", [])],
            recurrence=data.get("recurrence"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            started_at=data.get("started_at"),
            ended_at=data.get("ended_at"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def create(
        cls,
        title: str,
        scheduled_time: str,
        duration_minutes: int,
        organizer: str,
        attendees: List[str],
        agenda: List[str] = None,
        recurrence: str = None
    ) -> "Meeting":
        return cls(
            meeting_id=str(uuid.uuid4()),
            title=title,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            organizer=organizer,
            attendees=attendees,
            status=MeetingStatus.SCHEDULED,
            agenda=agenda or [],
            recurrence=recurrence
        )
    
    def add_message(self, message: MeetingMessage):
        """Add a message to the meeting"""
        self.messages.append(message)
    
    def start(self):
        """Start the meeting"""
        self.status = MeetingStatus.IN_PROGRESS
        self.started_at = datetime.utcnow().isoformat()
    
    def end(self):
        """End the meeting"""
        self.status = MeetingStatus.COMPLETED
        self.ended_at = datetime.utcnow().isoformat()
    
    def cancel(self):
        """Cancel the meeting"""
        self.status = MeetingStatus.CANCELLED
    
    def add_attendee(self, agent_id: str):
        """Add an attendee to the meeting"""
        if agent_id not in self.attendees:
            self.attendees.append(agent_id)
    
    def remove_attendee(self, agent_id: str):
        """Remove an attendee from the meeting"""
        if agent_id in self.attendees:
            self.attendees.remove(agent_id)


@dataclass
class AgentPresence:
    """
    Presence information for an agent
    """
    agent_id: str
    agent_name: str
    status: AgentStatus
    last_heartbeat: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    current_task: Optional[str] = None
    current_meeting: Optional[str] = None  # Meeting ID if in meeting
    availability: List[TimeSlot] = field(default_factory=list)
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "last_heartbeat": self.last_heartbeat,
            "current_task": self.current_task,
            "current_meeting": self.current_meeting,
            "availability": [a.to_dict() for a in self.availability],
            "avatar_url": self.avatar_url,
            "role": self.role,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentPresence":
        return cls(
            agent_id=data["agent_id"],
            agent_name=data["agent_name"],
            status=AgentStatus(data["status"]),
            last_heartbeat=data.get("last_heartbeat", datetime.utcnow().isoformat()),
            current_task=data.get("current_task"),
            current_meeting=data.get("current_meeting"),
            availability=[TimeSlot.from_dict(a) for a in data.get("availability", [])],
            avatar_url=data.get("avatar_url"),
            role=data.get("role"),
            metadata=data.get("metadata", {})
        )
    
    def update_heartbeat(self):
        """Update the heartbeat timestamp"""
        self.last_heartbeat = datetime.utcnow().isoformat()
    
    def set_status(self, status: AgentStatus):
        """Set the agent's status"""
        self.status = status
        self.update_heartbeat()
    
    def is_available(self) -> bool:
        """Check if the agent is available"""
        return self.status in [AgentStatus.ONLINE, AgentStatus.IDLE]


@dataclass
class AgentInvitation:
    """
    An invitation from one agent to another
    """
    invitation_id: str
    from_agent: str  # Agent ID
    to_agent: str    # Agent ID
    meeting_id: Optional[str] = None
    message: str = ""
    status: InvitationStatus = InvitationStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    responded_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "invitation_id": self.invitation_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "meeting_id": self.meeting_id,
            "message": self.message,
            "status": self.status.value,
            "created_at": self.created_at,
            "responded_at": self.responded_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentInvitation":
        return cls(
            invitation_id=data["invitation_id"],
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            meeting_id=data.get("meeting_id"),
            message=data.get("message", ""),
            status=InvitationStatus(data.get("status", "pending")),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            responded_at=data.get("responded_at")
        )
    
    @classmethod
    def create(
        cls,
        from_agent: str,
        to_agent: str,
        message: str = "",
        meeting_id: str = None
    ) -> "AgentInvitation":
        return cls(
            invitation_id=str(uuid.uuid4()),
            from_agent=from_agent,
            to_agent=to_agent,
            meeting_id=meeting_id,
            message=message
        )
    
    def accept(self):
        """Accept the invitation"""
        self.status = InvitationStatus.ACCEPTED
        self.responded_at = datetime.utcnow().isoformat()
    
    def decline(self):
        """Decline the invitation"""
        self.status = InvitationStatus.DECLINED
        self.responded_at = datetime.utcnow().isoformat()
    
    def expire(self):
        """Expire the invitation"""
        self.status = InvitationStatus.EXPIRED


# Pre-defined agent configurations
BAMBU_AGENT = {
    "agent_id": "bambu-executiveusa",
    "agent_name": "Bambu",
    "role": "CEO & Coordinator",
    "avatar_url": "/static/assets/bambu-avatar.png",
    "capabilities": [
        "repo_analysis",
        "prd_generation",
        "deployment_management",
        "agent_coordination"
    ]
}

PAULI_AGENT = {
    "agent_id": "pauli-planner",
    "agent_name": "Pauli",
    "role": "Planner",
    "avatar_url": "/static/assets/pauli-avatar.png",
    "capabilities": [
        "task_planning",
        "resource_management",
        "coordination"
    ]
}

SYNTHIA_AGENT = {
    "agent_id": "synthia-executor",
    "agent_name": "Synthia",
    "role": "Executor",
    "avatar_url": "/static/assets/synthia-avatar.png",
    "capabilities": [
        "task_execution",
        "deployment",
        "api_integration"
    ]
}

ALEX_AGENT = {
    "agent_id": "alex-metagpt",
    "agent_name": "Alex",
    "role": "Developer (MetaGPT)",
    "avatar_url": "/static/assets/alex-avatar.png",
    "capabilities": [
        "code_writing",
        "architecture_design",
        "documentation",
        "testing"
    ]
}

ALL_AGENTS = [BAMBU_AGENT, PAULI_AGENT, SYNTHIA_AGENT, ALEX_AGENT]