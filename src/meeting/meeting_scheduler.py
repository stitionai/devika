#!/usr/bin/env python3
"""
Meeting Scheduler Service for Visual Agent Meeting Room
Handles scheduling, cron-based recurring meetings, and meeting lifecycle
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from croniter import croniter
import asyncio

from .models import Meeting, MeetingStatus, MeetingMessage


class MeetingScheduler:
    """
    Schedule and manage meetings between agents
    Supports one-time and recurring (cron-based) meetings
    """
    
    def __init__(self, storage_path: str = "data/meetings"):
        self.storage_path = storage_path
        self.meetings: Dict[str, Meeting] = {}
        self.cron_jobs: Dict[str, asyncio.Task] = {}
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing meetings
        self._load_meetings()
    
    def _load_meetings(self):
        """Load meetings from storage"""
        meetings_file = os.path.join(self.storage_path, "meetings.json")
        if os.path.exists(meetings_file):
            try:
                with open(meetings_file, 'r') as f:
                    data = json.load(f)
                    for meeting_data in data.get("meetings", []):
                        meeting = Meeting.from_dict(meeting_data)
                        self.meetings[meeting.meeting_id] = meeting
            except Exception as e:
                print(f"Error loading meetings: {e}")
    
    def _save_meetings(self):
        """Save meetings to storage"""
        meetings_file = os.path.join(self.storage_path, "meetings.json")
        try:
            data = {
                "meetings": [m.to_dict() for m in self.meetings.values()],
                "updated_at": datetime.utcnow().isoformat()
            }
            with open(meetings_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving meetings: {e}")
    
    def create_meeting(
        self,
        title: str,
        scheduled_time: str,
        duration_minutes: int,
        organizer: str,
        attendees: List[str],
        agenda: List[str] = None,
        recurrence: str = None
    ) -> Meeting:
        """
        Create a new meeting
        
        Args:
            title: Meeting title
            scheduled_time: ISO8601 datetime string
            duration_minutes: Meeting duration in minutes
            organizer: Agent ID of the organizer
            attendees: List of agent IDs
            agenda: List of agenda items
            recurrence: Cron expression for recurring meetings
        
        Returns:
            The created Meeting object
        """
        meeting = Meeting.create(
            title=title,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            organizer=organizer,
            attendees=attendees,
            agenda=agenda,
            recurrence=recurrence
        )
        
        self.meetings[meeting.meeting_id] = meeting
        self._save_meetings()
        
        return meeting
    
    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """Get a meeting by ID"""
        return self.meetings.get(meeting_id)
    
    def list_meetings(
        self,
        status: MeetingStatus = None,
        agent_id: str = None,
        upcoming_only: bool = False
    ) -> List[Meeting]:
        """
        List meetings with optional filters
        
        Args:
            status: Filter by meeting status
            agent_id: Filter by agent (organizer or attendee)
            upcoming_only: Only return meetings scheduled in the future
        
        Returns:
            List of matching meetings
        """
        meetings = list(self.meetings.values())
        
        if status:
            meetings = [m for m in meetings if m.status == status]
        
        if agent_id:
            meetings = [
                m for m in meetings 
                if agent_id in m.attendees or m.organizer == agent_id
            ]
        
        if upcoming_only:
            now = datetime.utcnow().isoformat()
            meetings = [m for m in meetings if m.scheduled_time > now]
        
        return sorted(meetings, key=lambda m: m.scheduled_time)
    
    def start_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """Start a meeting"""
        meeting = self.get_meeting(meeting_id)
        if meeting and meeting.status == MeetingStatus.SCHEDULED:
            meeting.start()
            self._save_meetings()
            return meeting
        return None
    
    def end_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """End a meeting"""
        meeting = self.get_meeting(meeting_id)
        if meeting and meeting.status == MeetingStatus.IN_PROGRESS:
            meeting.end()
            self._save_meetings()
            return meeting
        return None
    
    def cancel_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """Cancel a meeting"""
        meeting = self.get_meeting(meeting_id)
        if meeting and meeting.status in [MeetingStatus.SCHEDULED, MeetingStatus.IN_PROGRESS]:
            meeting.cancel()
            self._save_meetings()
            return meeting
        return None
    
    def add_message(
        self,
        meeting_id: str,
        agent_id: str,
        agent_name: str,
        content: str
    ) -> Optional[MeetingMessage]:
        """Add a message to a meeting"""
        meeting = self.get_meeting(meeting_id)
        if meeting and meeting.status == MeetingStatus.IN_PROGRESS:
            message = MeetingMessage.create(
                agent_id=agent_id,
                agent_name=agent_name,
                content=content
            )
            meeting.add_message(message)
            self._save_meetings()
            return message
        return None
    
    def get_upcoming_meetings(self, minutes: int = 60) -> List[Meeting]:
        """
        Get meetings starting within the specified number of minutes
        
        Args:
            minutes: Number of minutes to look ahead
        
        Returns:
            List of upcoming meetings
        """
        now = datetime.utcnow()
        cutoff = now + timedelta(minutes=minutes)
        
        upcoming = []
        for meeting in self.meetings.values():
            if meeting.status == MeetingStatus.SCHEDULED:
                scheduled = datetime.fromisoformat(meeting.scheduled_time.replace('Z', '+00:00').replace('+00:00', ''))
                if now <= scheduled <= cutoff:
                    upcoming.append(meeting)
        
        return sorted(upcoming, key=lambda m: m.scheduled_time)
    
    def get_next_occurrence(self, recurrence: str) -> Optional[datetime]:
        """
        Get the next occurrence of a recurring meeting
        
        Args:
            recurrence: Cron expression
        
        Returns:
            Next occurrence datetime or None if invalid
        """
        try:
            cron = croniter(recurrence, datetime.utcnow())
            return cron.get_next(datetime)
        except Exception:
            return None
    
    def schedule_recurring_meetings(self):
        """
        Create instances for recurring meetings
        Called by the cron job to generate future meeting instances
        """
        now = datetime.utcnow()
        
        for meeting in list(self.meetings.values()):
            if meeting.recurrence and meeting.status == MeetingStatus.SCHEDULED:
                # Check if we need to create the next instance
                scheduled = datetime.fromisoformat(
                    meeting.scheduled_time.replace('Z', '+00:00').replace('+00:00', '')
                )
                
                # If the meeting time has passed, create next occurrence
                if scheduled < now:
                    next_time = self.get_next_occurrence(meeting.recurrence)
                    if next_time:
                        # Create new meeting instance
                        new_meeting = self.create_meeting(
                            title=meeting.title,
                            scheduled_time=next_time.isoformat(),
                            duration_minutes=meeting.duration_minutes,
                            organizer=meeting.organizer,
                            attendees=meeting.attendees,
                            agenda=meeting.agenda,
                            recurrence=meeting.recurrence
                        )
                        # Mark old meeting as completed
                        meeting.status = MeetingStatus.COMPLETED
                        self._save_meetings()
    
    def get_meeting_transcript(self, meeting_id: str) -> List[Dict[str, Any]]:
        """Get the transcript of a meeting"""
        meeting = self.get_meeting(meeting_id)
        if meeting:
            return [m.to_dict() for m in meeting.messages]
        return []
    
    def export_transcript(self, meeting_id: str, format: str = "json") -> Optional[str]:
        """
        Export meeting transcript
        
        Args:
            meeting_id: Meeting ID
            format: Export format (json, markdown, text)
        
        Returns:
            Formatted transcript string or None
        """
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return None
        
        if format == "json":
            return json.dumps({
                "meeting": meeting.to_dict(),
                "transcript": [m.to_dict() for m in meeting.messages]
            }, indent=2)
        
        elif format == "markdown":
            lines = [
                f"# {meeting.title}",
                f"",
                f"**Date:** {meeting.scheduled_time}",
                f"**Duration:** {meeting.duration_minutes} minutes",
                f"**Attendees:** {', '.join(meeting.attendees)}",
                f"",
                f"## Agenda",
                ""
            ]
            for item in meeting.agenda:
                lines.append(f"- {item}")
            
            lines.extend([
                f"",
                f"## Transcript",
                f""
            ])
            for msg in meeting.messages:
                lines.append(f"**{msg.agent_name}** ({msg.timestamp}):")
                lines.append(f"{msg.content}")
                lines.append(f"")
            
            return "\n".join(lines)
        
        elif format == "text":
            lines = [
                f"Meeting: {meeting.title}",
                f"Date: {meeting.scheduled_time}",
                f"Attendees: {', '.join(meeting.attendees)}",
                f"",
                f"---"
            ]
            for msg in meeting.messages:
                lines.append(f"{msg.agent_name}: {msg.content}")
            
            return "\n".join(lines)
        
        return None


# Singleton instance
_scheduler_instance = None

def get_scheduler() -> MeetingScheduler:
    """Get the singleton MeetingScheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = MeetingScheduler()
    return _scheduler_instance


def main():
    """Test the meeting scheduler"""
    print("Meeting Scheduler Test")
    print("=" * 50)
    
    scheduler = MeetingScheduler()
    
    # Create a test meeting
    meeting = scheduler.create_meeting(
        title="Daily Agent Standup",
        scheduled_time=datetime.utcnow().isoformat(),
        duration_minutes=15,
        organizer="bambu-executiveusa",
        attendees=["bambu-executiveusa", "pauli-planner", "synthia-executor", "alex-metagpt"],
        agenda=[
            "Status updates from each agent",
            "Blockers and dependencies",
            "Next steps"
        ],
        recurrence="0 9 * * *"  # Daily at 9 AM
    )
    
    print(f"\nCreated meeting: {meeting.meeting_id}")
    print(f"Title: {meeting.title}")
    print(f"Status: {meeting.status.value}")
    print(f"Attendees: {meeting.attendees}")
    
    # Start the meeting
    scheduler.start_meeting(meeting.meeting_id)
    print(f"\nMeeting started!")
    
    # Add some messages
    scheduler.add_message(
        meeting.meeting_id,
        "bambu-executiveusa",
        "Bambu",
        "Good morning team! Let's start our daily standup."
    )
    scheduler.add_message(
        meeting.meeting_id,
        "pauli-planner",
        "Pauli",
        "I've prepared the sprint backlog for review."
    )
    
    # Export transcript
    print(f"\nTranscript (Markdown):")
    print(scheduler.export_transcript(meeting.meeting_id, "markdown"))


if __name__ == "__main__":
    main()