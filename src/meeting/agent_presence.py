#!/usr/bin/env python3
"""
Agent Presence Tracker for Visual Agent Meeting Room
Tracks agent online status, heartbeats, and availability
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from .models import AgentPresence, AgentStatus, TimeSlot, ALL_AGENTS


class AgentPresenceTracker:
    """
    Tracks and manages agent presence in the meeting room
    Handles heartbeats, status updates, and availability
    """
    
    def __init__(self, storage_path: str = "data/presence"):
        self.storage_path = storage_path
        self.presence: Dict[str, AgentPresence] = {}
        self.heartbeat_handlers: List[Callable] = []
        self.status_handlers: List[Callable] = []
        
        # Heartbeat timeout in seconds
        self.heartbeat_timeout = 300  # 5 minutes
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize agents
        self._initialize_agents()
        
        # Load saved presence
        self._load_presence()
    
    def _initialize_agents(self):
        """Initialize presence for all known agents"""
        for agent_config in ALL_AGENTS:
            presence = AgentPresence(
                agent_id=agent_config["agent_id"],
                agent_name=agent_config["agent_name"],
                status=AgentStatus.OFFLINE,
                role=agent_config.get("role"),
                avatar_url=agent_config.get("avatar_url"),
                metadata={"capabilities": agent_config.get("capabilities", [])}
            )
            self.presence[presence.agent_id] = presence
    
    def _load_presence(self):
        """Load presence data from storage"""
        presence_file = os.path.join(self.storage_path, "presence.json")
        if os.path.exists(presence_file):
            try:
                with open(presence_file, 'r') as f:
                    data = json.load(f)
                    for agent_id, presence_data in data.get("presence", {}).items():
                        if agent_id in self.presence:
                            # Update with saved data, but reset status to offline
                            saved = AgentPresence.from_dict(presence_data)
                            self.presence[agent_id].last_heartbeat = saved.last_heartbeat
                            self.presence[agent_id].availability = saved.availability
                            # Reset status to offline on restart
                            self.presence[agent_id].status = AgentStatus.OFFLINE
            except Exception as e:
                print(f"Error loading presence: {e}")
    
    def _save_presence(self):
        """Save presence data to storage"""
        presence_file = os.path.join(self.storage_path, "presence.json")
        try:
            data = {
                "presence": {k: v.to_dict() for k, v in self.presence.items()},
                "updated_at": datetime.utcnow().isoformat()
            }
            with open(presence_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving presence: {e}")
    
    def register_heartbeat_handler(self, handler: Callable):
        """Register a callback for heartbeat events"""
        self.heartbeat_handlers.append(handler)
    
    def register_status_handler(self, handler: Callable):
        """Register a callback for status change events"""
        self.status_handlers.append(handler)
    
    async def _emit_heartbeat(self, agent_id: str, presence: AgentPresence):
        """Emit a heartbeat event"""
        for handler in self.heartbeat_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(agent_id, presence.to_dict())
                else:
                    handler(agent_id, presence.to_dict())
            except Exception as e:
                print(f"Error in heartbeat handler: {e}")
    
    async def _emit_status(self, agent_id: str, old_status: AgentStatus, new_status: AgentStatus):
        """Emit a status change event"""
        for handler in self.status_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(agent_id, old_status.value, new_status.value)
                else:
                    handler(agent_id, old_status.value, new_status.value)
            except Exception as e:
                print(f"Error in status handler: {e}")
    
    async def heartbeat(self, agent_id: str) -> bool:
        """
        Process a heartbeat from an agent
        
        Args:
            agent_id: The agent's ID
        
        Returns:
            True if the agent is known
        """
        if agent_id not in self.presence:
            return False
        
        presence = self.presence[agent_id]
        old_status = presence.status
        
        # Update heartbeat
        presence.update_heartbeat()
        
        # If agent was offline, set to online
        if presence.status == AgentStatus.OFFLINE:
            presence.status = AgentStatus.ONLINE
            await self._emit_status(agent_id, old_status, presence.status)
        
        # Emit heartbeat event
        await self._emit_heartbeat(agent_id, presence)
        
        return True
    
    async def set_status(
        self,
        agent_id: str,
        status: AgentStatus,
        current_task: str = None
    ) -> Optional[AgentPresence]:
        """
        Set an agent's status
        
        Args:
            agent_id: The agent's ID
            status: The new status
            current_task: Optional current task description
        
        Returns:
            The updated presence or None
        """
        if agent_id not in self.presence:
            return None
        
        presence = self.presence[agent_id]
        old_status = presence.status
        
        presence.status = status
        presence.current_task = current_task
        presence.update_heartbeat()
        
        # Emit status change
        if old_status != status:
            await self._emit_status(agent_id, old_status, status)
        
        self._save_presence()
        return presence
    
    def get_presence(self, agent_id: str) -> Optional[AgentPresence]:
        """Get an agent's presence info"""
        return self.presence.get(agent_id)
    
    def get_all_presence(self) -> List[AgentPresence]:
        """Get all agent presence info"""
        return list(self.presence.values())
    
    def get_online_agents(self) -> List[AgentPresence]:
        """Get all online agents"""
        return [
            p for p in self.presence.values()
            if p.status != AgentStatus.OFFLINE
        ]
    
    def get_agents_by_status(self, status: AgentStatus) -> List[AgentPresence]:
        """Get agents with a specific status"""
        return [
            p for p in self.presence.values()
            if p.status == status
        ]
    
    def is_available(self, agent_id: str) -> bool:
        """Check if an agent is available"""
        presence = self.presence.get(agent_id)
        return presence.is_available() if presence else False
    
    async def set_availability(
        self,
        agent_id: str,
        slots: List[TimeSlot]
    ) -> Optional[AgentPresence]:
        """
        Set an agent's availability slots
        
        Args:
            agent_id: The agent's ID
            slots: List of available time slots
        
        Returns:
            The updated presence or None
        """
        if agent_id not in self.presence:
            return None
        
        presence = self.presence[agent_id]
        presence.availability = slots
        presence.update_heartbeat()
        
        self._save_presence()
        return presence
    
    def get_availability(self, agent_id: str) -> List[TimeSlot]:
        """Get an agent's availability slots"""
        presence = self.presence.get(agent_id)
        return presence.availability if presence else []
    
    def find_available_agents(self, time_slot: TimeSlot) -> List[AgentPresence]:
        """
        Find agents available during a specific time slot
        
        Args:
            time_slot: The time slot to check
        
        Returns:
            List of available agents
        """
        available = []
        for presence in self.presence.values():
            if presence.status == AgentStatus.OFFLINE:
                continue
            
            # Check if any availability slot overlaps
            for slot in presence.availability:
                if self._slots_overlap(time_slot, slot):
                    available.append(presence)
                    break
        
        return available
    
    def _slots_overlap(self, slot1: TimeSlot, slot2: TimeSlot) -> bool:
        """Check if two time slots overlap"""
        start1 = datetime.fromisoformat(slot1.start.replace('Z', '+00:00').replace('+00:00', ''))
        end1 = datetime.fromisoformat(slot1.end.replace('Z', '+00:00').replace('+00:00', ''))
        start2 = datetime.fromisoformat(slot2.start.replace('Z', '+00:00').replace('+00:00', ''))
        end2 = datetime.fromisoformat(slot2.end.replace('Z', '+00:00').replace('+00:00', ''))
        
        return start1 < end2 and start2 < end1
    
    async def check_stale_agents(self) -> List[str]:
        """
        Check for agents that haven't sent a heartbeat recently
        and mark them as offline
        
        Returns:
            List of agent IDs that went stale
        """
        now = datetime.utcnow()
        stale_agents = []
        
        for agent_id, presence in self.presence.items():
            if presence.status == AgentStatus.OFFLINE:
                continue
            
            last_heartbeat = datetime.fromisoformat(
                presence.last_heartbeat.replace('Z', '+00:00').replace('+00:00', '')
            )
            
            if (now - last_heartbeat).total_seconds() > self.heartbeat_timeout:
                old_status = presence.status
                presence.status = AgentStatus.OFFLINE
                stale_agents.append(agent_id)
                
                await self._emit_status(agent_id, old_status, AgentStatus.OFFLINE)
        
        if stale_agents:
            self._save_presence()
        
        return stale_agents
    
    async def start_heartbeat_monitor(self, interval: int = 60):
        """
        Start a background task to monitor heartbeats
        
        Args:
            interval: Check interval in seconds
        """
        while True:
            await asyncio.sleep(interval)
            stale = await self.check_stale_agents()
            if stale:
                print(f"Agents gone stale: {stale}")
    
    def get_presence_summary(self) -> Dict[str, Any]:
        """Get a summary of all agent presence"""
        return {
            "total_agents": len(self.presence),
            "online": len(self.get_agents_by_status(AgentStatus.ONLINE)),
            "offline": len(self.get_agents_by_status(AgentStatus.OFFLINE)),
            "busy": len(self.get_agents_by_status(AgentStatus.BUSY)),
            "in_meeting": len(self.get_agents_by_status(AgentStatus.IN_MEETING)),
            "idle": len(self.get_agents_by_status(AgentStatus.IDLE)),
            "agents": [
                {
                    "id": p.agent_id,
                    "name": p.agent_name,
                    "status": p.status.value,
                    "last_heartbeat": p.last_heartbeat
                }
                for p in self.presence.values()
            ]
        }


# Singleton instance
_tracker_instance = None

def get_presence_tracker() -> AgentPresenceTracker:
    """Get the singleton AgentPresenceTracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = AgentPresenceTracker()
    return _tracker_instance


def main():
    """Test the presence tracker"""
    import asyncio
    
    async def test():
        print("Agent Presence Tracker Test")
        print("=" * 50)
        
        tracker = AgentPresenceTracker()
        
        # Register handlers
        def on_heartbeat(agent_id, data):
            print(f"[HEARTBEAT] {agent_id}")
        
        def on_status(agent_id, old, new):
            print(f"[STATUS] {agent_id}: {old} -> {new}")
        
        tracker.register_heartbeat_handler(on_heartbeat)
        tracker.register_status_handler(on_status)
        
        # Bambu comes online
        await tracker.heartbeat("bambu-executiveusa")
        
        # Pauli comes online
        await tracker.heartbeat("pauli-planner")
        
        # Set Bambu as busy
        await tracker.set_status(
            "bambu-executiveusa",
            AgentStatus.BUSY,
            "Analyzing repository structure"
        )
        
        # Get summary
        summary = tracker.get_presence_summary()
        print(f"\nPresence Summary:")
        print(f"  Online: {summary['online']}")
        print(f"  Offline: {summary['offline']}")
        print(f"  Busy: {summary['busy']}")
        
        # Get online agents
        print(f"\nOnline Agents:")
        for presence in tracker.get_online_agents():
            print(f"  {presence.agent_name}: {presence.status.value}")
    
    asyncio.run(test())


if __name__ == "__main__":
    main()