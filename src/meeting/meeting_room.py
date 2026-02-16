#!/usr/bin/env python3
"""
Meeting Room Service for Visual Agent Meeting Room
Manages the real-time state of the meeting room and agent interactions
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field

from .models import Meeting, MeetingStatus, MeetingMessage, AgentPresence, AgentStatus


@dataclass
class RoomState:
    """Current state of the meeting room"""
    room_id: str
    active_meeting_id: Optional[str] = None
    agents_in_room: Set[str] = field(default_factory=set)
    speaking_agent: Optional[str] = None
    last_activity: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_id": self.room_id,
            "active_meeting_id": self.active_meeting_id,
            "agents_in_room": list(self.agents_in_room),
            "speaking_agent": self.speaking_agent,
            "last_activity": self.last_activity
        }


class MeetingRoom:
    """
    Manages the real-time meeting room where agents can join, leave, and interact
    """
    
    def __init__(self, room_id: str = "main"):
        self.room_id = room_id
        self.state = RoomState(room_id=room_id)
        self.presence: Dict[str, AgentPresence] = {}
        self.message_handlers: List[Callable] = []
        self.presence_handlers: List[Callable] = []
        self.meeting_handlers: List[Callable] = []
        
        # Storage
        self.storage_path = "data/meeting_room"
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Initialize with known agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize presence for known agents"""
        from .models import ALL_AGENTS
        
        for agent_config in ALL_AGENTS:
            presence = AgentPresence(
                agent_id=agent_config["agent_id"],
                agent_name=agent_config["agent_name"],
                status=AgentStatus.OFFLINE,
                role=agent_config.get("role"),
                avatar_url=agent_config.get("avatar_url")
            )
            self.presence[presence.agent_id] = presence
    
    def register_message_handler(self, handler: Callable):
        """Register a callback for message events"""
        self.message_handlers.append(handler)
    
    def register_presence_handler(self, handler: Callable):
        """Register a callback for presence events"""
        self.presence_handlers.append(handler)
    
    def register_meeting_handler(self, handler: Callable):
        """Register a callback for meeting events"""
        self.meeting_handlers.append(handler)
    
    async def _emit_message(self, event_type: str, data: Dict[str, Any]):
        """Emit a message event to all handlers"""
        for handler in self.message_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_type, data)
                else:
                    handler(event_type, data)
            except Exception as e:
                print(f"Error in message handler: {e}")
    
    async def _emit_presence(self, event_type: str, data: Dict[str, Any]):
        """Emit a presence event to all handlers"""
        for handler in self.presence_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_type, data)
                else:
                    handler(event_type, data)
            except Exception as e:
                print(f"Error in presence handler: {e}")
    
    async def _emit_meeting(self, event_type: str, data: Dict[str, Any]):
        """Emit a meeting event to all handlers"""
        for handler in self.meeting_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_type, data)
                else:
                    handler(event_type, data)
            except Exception as e:
                print(f"Error in meeting handler: {e}")
    
    async def agent_join(self, agent_id: str) -> Optional[AgentPresence]:
        """
        An agent joins the meeting room
        
        Args:
            agent_id: The agent's ID
        
        Returns:
            The agent's presence info or None if unknown
        """
        if agent_id not in self.presence:
            return None
        
        presence = self.presence[agent_id]
        presence.set_status(AgentStatus.ONLINE)
        self.state.agents_in_room.add(agent_id)
        self.state.last_activity = datetime.utcnow().isoformat()
        
        # Emit presence event
        await self._emit_presence("agent-joined", {
            "agent_id": agent_id,
            "presence": presence.to_dict(),
            "room_state": self.state.to_dict()
        })
        
        return presence
    
    async def agent_leave(self, agent_id: str) -> bool:
        """
        An agent leaves the meeting room
        
        Args:
            agent_id: The agent's ID
        
        Returns:
            True if the agent was in the room
        """
        if agent_id not in self.state.agents_in_room:
            return False
        
        presence = self.presence.get(agent_id)
        if presence:
            presence.set_status(AgentStatus.OFFLINE)
        
        self.state.agents_in_room.discard(agent_id)
        
        # Clear speaking if this agent was speaking
        if self.state.speaking_agent == agent_id:
            self.state.speaking_agent = None
        
        self.state.last_activity = datetime.utcnow().isoformat()
        
        # Emit presence event
        await self._emit_presence("agent-left", {
            "agent_id": agent_id,
            "room_state": self.state.to_dict()
        })
        
        return True
    
    async def agent_speak(
        self,
        agent_id: str,
        content: str,
        meeting_id: str = None
    ) -> Optional[MeetingMessage]:
        """
        An agent speaks in the meeting room
        
        Args:
            agent_id: The agent's ID
            content: The message content
            meeting_id: Optional meeting ID (uses active meeting if not provided)
        
        Returns:
            The created message or None
        """
        if agent_id not in self.state.agents_in_room:
            return None
        
        presence = self.presence.get(agent_id)
        if not presence:
            return None
        
        # Set speaking agent
        self.state.speaking_agent = agent_id
        self.state.last_activity = datetime.utcnow().isoformat()
        
        # Create message
        message = MeetingMessage.create(
            agent_id=agent_id,
            agent_name=presence.agent_name,
            content=content
        )
        
        # Emit message event
        await self._emit_message("agent-speaking", {
            "message": message.to_dict(),
            "room_state": self.state.to_dict()
        })
        
        # Clear speaking after a short delay (simulated)
        await asyncio.sleep(0.1)
        if self.state.speaking_agent == agent_id:
            self.state.speaking_agent = None
        
        return message
    
    async def agent_typing(self, agent_id: str, is_typing: bool = True):
        """
        Indicate that an agent is typing
        
        Args:
            agent_id: The agent's ID
            is_typing: Whether the agent is typing
        """
        if agent_id not in self.presence:
            return
        
        await self._emit_presence("agent-typing", {
            "agent_id": agent_id,
            "is_typing": is_typing
        })
    
    def get_presence(self, agent_id: str) -> Optional[AgentPresence]:
        """Get an agent's presence info"""
        return self.presence.get(agent_id)
    
    def get_all_presence(self) -> List[AgentPresence]:
        """Get all agent presence info"""
        return list(self.presence.values())
    
    def get_agents_in_room(self) -> List[str]:
        """Get list of agents currently in the room"""
        return list(self.state.agents_in_room)
    
    def get_room_state(self) -> Dict[str, Any]:
        """Get the current room state"""
        return self.state.to_dict()
    
    async def start_meeting(self, meeting: Meeting):
        """
        Start a meeting in the room
        
        Args:
            meeting: The meeting to start
        """
        self.state.active_meeting_id = meeting.meeting_id
        self.state.last_activity = datetime.utcnow().isoformat()
        
        # Update presence for attendees
        for agent_id in meeting.attendees:
            if agent_id in self.presence:
                self.presence[agent_id].status = AgentStatus.IN_MEETING
                self.presence[agent_id].current_meeting = meeting.meeting_id
        
        await self._emit_meeting("meeting-started", {
            "meeting": meeting.to_dict(),
            "room_state": self.state.to_dict()
        })
    
    async def end_meeting(self, meeting: Meeting):
        """
        End the current meeting
        
        Args:
            meeting: The meeting to end
        """
        if self.state.active_meeting_id == meeting.meeting_id:
            self.state.active_meeting_id = None
        
        # Update presence for attendees
        for agent_id in meeting.attendees:
            if agent_id in self.presence:
                self.presence[agent_id].status = AgentStatus.ONLINE
                self.presence[agent_id].current_meeting = None
        
        self.state.last_activity = datetime.utcnow().isoformat()
        
        await self._emit_meeting("meeting-ended", {
            "meeting": meeting.to_dict(),
            "room_state": self.state.to_dict()
        })
    
    def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus,
        current_task: str = None
    ):
        """
        Update an agent's status
        
        Args:
            agent_id: The agent's ID
            status: The new status
            current_task: Optional current task description
        """
        if agent_id not in self.presence:
            return
        
        presence = self.presence[agent_id]
        presence.status = status
        presence.current_task = current_task
        presence.update_heartbeat()
    
    def heartbeat(self, agent_id: str) -> bool:
        """
        Process a heartbeat from an agent
        
        Args:
            agent_id: The agent's ID
        
        Returns:
            True if the agent is known
        """
        if agent_id not in self.presence:
            return False
        
        self.presence[agent_id].update_heartbeat()
        return True
    
    def check_stale_agents(self, timeout_seconds: int = 300) -> List[str]:
        """
        Check for agents that haven't sent a heartbeat recently
        
        Args:
            timeout_seconds: Timeout in seconds
        
        Returns:
            List of stale agent IDs
        """
        now = datetime.utcnow()
        stale_agents = []
        
        for agent_id, presence in self.presence.items():
            if presence.status != AgentStatus.OFFLINE:
                last_heartbeat = datetime.fromisoformat(
                    presence.last_heartbeat.replace('Z', '+00:00').replace('+00:00', '')
                )
                if (now - last_heartbeat).total_seconds() > timeout_seconds:
                    stale_agents.append(agent_id)
                    presence.status = AgentStatus.OFFLINE
        
        return stale_agents
    
    def save_state(self):
        """Save the room state to disk"""
        state_file = os.path.join(self.storage_path, f"{self.room_id}_state.json")
        try:
            with open(state_file, 'w') as f:
                json.dump({
                    "state": self.state.to_dict(),
                    "presence": {k: v.to_dict() for k, v in self.presence.items()},
                    "saved_at": datetime.utcnow().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving room state: {e}")
    
    def load_state(self):
        """Load the room state from disk"""
        state_file = os.path.join(self.storage_path, f"{self.room_id}_state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    # Restore presence
                    for agent_id, presence_data in data.get("presence", {}).items():
                        if agent_id in self.presence:
                            self.presence[agent_id] = AgentPresence.from_dict(presence_data)
            except Exception as e:
                print(f"Error loading room state: {e}")


# Singleton instance
_room_instance = None

def get_meeting_room() -> MeetingRoom:
    """Get the singleton MeetingRoom instance"""
    global _room_instance
    if _room_instance is None:
        _room_instance = MeetingRoom()
    return _room_instance


def main():
    """Test the meeting room"""
    import asyncio
    
    async def test():
        print("Meeting Room Test")
        print("=" * 50)
        
        room = MeetingRoom()
        
        # Register event handlers
        def on_message(event_type, data):
            print(f"[MESSAGE] {event_type}: {data}")
        
        def on_presence(event_type, data):
            print(f"[PRESENCE] {event_type}: {data}")
        
        room.register_message_handler(on_message)
        room.register_presence_handler(on_presence)
        
        # Bambu joins
        await room.agent_join("bambu-executiveusa")
        print(f"\nAgents in room: {room.get_agents_in_room()}")
        
        # Pauli joins
        await room.agent_join("pauli-planner")
        print(f"Agents in room: {room.get_agents_in_room()}")
        
        # Bambu speaks
        await room.agent_speak("bambu-executiveusa", "Hello team! Welcome to the meeting room.")
        
        # Pauli speaks
        await room.agent_speak("pauli-planner", "Hi Bambu! Ready to coordinate some tasks.")
        
        # Get all presence
        print(f"\nAll Agent Presence:")
        for presence in room.get_all_presence():
            print(f"  {presence.agent_name}: {presence.status.value}")
        
        # Pauli leaves
        await room.agent_leave("pauli-planner")
        print(f"\nAgents in room: {room.get_agents_in_room()}")
    
    asyncio.run(test())


if __name__ == "__main__":
    main()