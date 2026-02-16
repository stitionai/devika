#!/usr/bin/env python3
"""
Invitation System for Visual Agent Meeting Room
Handles agent-to-agent invitations for meetings and collaborations
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import asyncio

from .models import AgentInvitation, InvitationStatus


class InvitationSystem:
    """
    Manages invitations between agents
    Agents can invite each other to meetings, collaborations, or ad-hoc discussions
    """
    
    def __init__(self, storage_path: str = "data/invitations"):
        self.storage_path = storage_path
        self.invitations: Dict[str, AgentInvitation] = {}
        self.notification_handlers: List[Callable] = []
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing invitations
        self._load_invitations()
    
    def _load_invitations(self):
        """Load invitations from storage"""
        invitations_file = os.path.join(self.storage_path, "invitations.json")
        if os.path.exists(invitations_file):
            try:
                with open(invitations_file, 'r') as f:
                    data = json.load(f)
                    for inv_data in data.get("invitations", []):
                        invitation = AgentInvitation.from_dict(inv_data)
                        self.invitations[invitation.invitation_id] = invitation
            except Exception as e:
                print(f"Error loading invitations: {e}")
    
    def _save_invitations(self):
        """Save invitations to storage"""
        invitations_file = os.path.join(self.storage_path, "invitations.json")
        try:
            data = {
                "invitations": [i.to_dict() for i in self.invitations.values()],
                "updated_at": datetime.utcnow().isoformat()
            }
            with open(invitations_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving invitations: {e}")
    
    def register_notification_handler(self, handler: Callable):
        """Register a callback for invitation notifications"""
        self.notification_handlers.append(handler)
    
    async def _notify(self, event_type: str, invitation: AgentInvitation):
        """Notify all handlers of an invitation event"""
        for handler in self.notification_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_type, invitation.to_dict())
                else:
                    handler(event_type, invitation.to_dict())
            except Exception as e:
                print(f"Error in notification handler: {e}")
    
    async def send_invitation(
        self,
        from_agent: str,
        to_agent: str,
        message: str = "",
        meeting_id: str = None
    ) -> AgentInvitation:
        """
        Send an invitation from one agent to another
        
        Args:
            from_agent: The inviting agent's ID
            to_agent: The invited agent's ID
            message: Optional message with the invitation
            meeting_id: Optional meeting ID if inviting to a specific meeting
        
        Returns:
            The created invitation
        """
        invitation = AgentInvitation.create(
            from_agent=from_agent,
            to_agent=to_agent,
            message=message,
            meeting_id=meeting_id
        )
        
        self.invitations[invitation.invitation_id] = invitation
        self._save_invitations()
        
        # Notify handlers
        await self._notify("invitation-received", invitation)
        
        return invitation
    
    async def accept_invitation(self, invitation_id: str) -> Optional[AgentInvitation]:
        """
        Accept an invitation
        
        Args:
            invitation_id: The invitation ID
        
        Returns:
            The updated invitation or None
        """
        invitation = self.invitations.get(invitation_id)
        if not invitation:
            return None
        
        if invitation.status != InvitationStatus.PENDING:
            return None
        
        invitation.accept()
        self._save_invitations()
        
        # Notify handlers
        await self._notify("invitation-accepted", invitation)
        
        return invitation
    
    async def decline_invitation(self, invitation_id: str) -> Optional[AgentInvitation]:
        """
        Decline an invitation
        
        Args:
            invitation_id: The invitation ID
        
        Returns:
            The updated invitation or None
        """
        invitation = self.invitations.get(invitation_id)
        if not invitation:
            return None
        
        if invitation.status != InvitationStatus.PENDING:
            return None
        
        invitation.decline()
        self._save_invitations()
        
        # Notify handlers
        await self._notify("invitation-declined", invitation)
        
        return invitation
    
    def get_invitation(self, invitation_id: str) -> Optional[AgentInvitation]:
        """Get an invitation by ID"""
        return self.invitations.get(invitation_id)
    
    def get_pending_invitations(self, agent_id: str = None) -> List[AgentInvitation]:
        """
        Get pending invitations
        
        Args:
            agent_id: Optional filter by agent (as recipient)
        
        Returns:
            List of pending invitations
        """
        pending = [
            i for i in self.invitations.values()
            if i.status == InvitationStatus.PENDING
        ]
        
        if agent_id:
            pending = [i for i in pending if i.to_agent == agent_id]
        
        return sorted(pending, key=lambda i: i.created_at, reverse=True)
    
    def get_sent_invitations(self, from_agent: str) -> List[AgentInvitation]:
        """
        Get invitations sent by an agent
        
        Args:
            from_agent: The sender agent ID
        
        Returns:
            List of sent invitations
        """
        return [
            i for i in self.invitations.values()
            if i.from_agent == from_agent
        ]
    
    def get_received_invitations(self, to_agent: str) -> List[AgentInvitation]:
        """
        Get invitations received by an agent
        
        Args:
            to_agent: The recipient agent ID
        
        Returns:
            List of received invitations
        """
        return [
            i for i in self.invitations.values()
            if i.to_agent == to_agent
        ]
    
    def get_meeting_invitations(self, meeting_id: str) -> List[AgentInvitation]:
        """
        Get all invitations for a specific meeting
        
        Args:
            meeting_id: The meeting ID
        
        Returns:
            List of invitations for the meeting
        """
        return [
            i for i in self.invitations.values()
            if i.meeting_id == meeting_id
        ]
    
    def expire_old_invitations(self, hours: int = 24) -> List[AgentInvitation]:
        """
        Expire invitations older than the specified hours
        
        Args:
            hours: Number of hours after which to expire
        
        Returns:
            List of expired invitations
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=hours)
        expired = []
        
        for invitation in self.invitations.values():
            if invitation.status == InvitationStatus.PENDING:
                created = datetime.fromisoformat(
                    invitation.created_at.replace('Z', '+00:00').replace('+00:00', '')
                )
                if created < cutoff:
                    invitation.expire()
                    expired.append(invitation)
        
        if expired:
            self._save_invitations()
        
        return expired
    
    def cancel_invitation(self, invitation_id: str) -> Optional[AgentInvitation]:
        """
        Cancel an invitation (by the sender)
        
        Args:
            invitation_id: The invitation ID
        
        Returns:
            The cancelled invitation or None
        """
        invitation = self.invitations.get(invitation_id)
        if not invitation:
            return None
        
        if invitation.status != InvitationStatus.PENDING:
            return None
        
        # Remove the invitation
        del self.invitations[invitation_id]
        self._save_invitations()
        
        return invitation
    
    def get_invitation_stats(self, agent_id: str = None) -> Dict[str, Any]:
        """
        Get statistics about invitations
        
        Args:
            agent_id: Optional filter by agent
        
        Returns:
            Dictionary with invitation statistics
        """
        invitations = list(self.invitations.values())
        
        if agent_id:
            invitations = [
                i for i in invitations
                if i.from_agent == agent_id or i.to_agent == agent_id
            ]
        
        return {
            "total": len(invitations),
            "pending": len([i for i in invitations if i.status == InvitationStatus.PENDING]),
            "accepted": len([i for i in invitations if i.status == InvitationStatus.ACCEPTED]),
            "declined": len([i for i in invitations if i.status == InvitationStatus.DECLINED]),
            "expired": len([i for i in invitations if i.status == InvitationStatus.EXPIRED])
        }


# Singleton instance
_invitation_instance = None

def get_invitation_system() -> InvitationSystem:
    """Get the singleton InvitationSystem instance"""
    global _invitation_instance
    if _invitation_instance is None:
        _invitation_instance = InvitationSystem()
    return _invitation_instance


def main():
    """Test the invitation system"""
    import asyncio
    
    async def test():
        print("Invitation System Test")
        print("=" * 50)
        
        system = InvitationSystem()
        
        # Register notification handler
        def on_notification(event_type, data):
            print(f"[NOTIFICATION] {event_type}: {data['invitation_id']}")
        
        system.register_notification_handler(on_notification)
        
        # Bambu invites Pauli to a meeting
        invitation = await system.send_invitation(
            from_agent="bambu-executiveusa",
            to_agent="pauli-planner",
            message="Hey Pauli, let's discuss the sprint planning.",
            meeting_id="meeting-123"
        )
        print(f"\nSent invitation: {invitation.invitation_id}")
        print(f"Status: {invitation.status.value}")
        
        # Pauli accepts
        accepted = await system.accept_invitation(invitation.invitation_id)
        print(f"\nPauli accepted! Status: {accepted.status.value}")
        
        # Bambu invites Synthia
        invitation2 = await system.send_invitation(
            from_agent="bambu-executiveusa",
            to_agent="synthia-executor",
            message="Can you join the deployment review?"
        )
        
        # Get pending invitations for Synthia
        pending = system.get_pending_invitations("synthia-executor")
        print(f"\nPending invitations for Synthia: {len(pending)}")
        
        # Get stats
        stats = system.get_invitation_stats("bambu-executiveusa")
        print(f"\nBambu's invitation stats: {stats}")
    
    asyncio.run(test())


if __name__ == "__main__":
    main()