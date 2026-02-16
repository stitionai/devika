#!/usr/bin/env python3
"""
Visual Agent Meeting Room Module for Bambu
Enables agents to meet, communicate, invite each other, and schedule meetings
"""

from .models import (
    Meeting,
    MeetingStatus,
    MeetingMessage,
    AgentPresence,
    AgentStatus,
    AgentInvitation,
    InvitationStatus,
    TimeSlot
)
from .meeting_scheduler import MeetingScheduler
from .meeting_room import MeetingRoom
from .invitation_system import InvitationSystem
from .agent_presence import AgentPresenceTracker

__all__ = [
    # Models
    "Meeting",
    "MeetingStatus",
    "MeetingMessage",
    "AgentPresence",
    "AgentStatus",
    "AgentInvitation",
    "InvitationStatus",
    "TimeSlot",
    # Services
    "MeetingScheduler",
    "MeetingRoom",
    "InvitationSystem",
    "AgentPresenceTracker",
]

__version__ = "1.0.0"