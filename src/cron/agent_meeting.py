#!/usr/bin/env python3
"""
Agent Meeting Cron Job for Bambu Agent System
Triggers scheduled meetings and sends notifications to agents
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from croniter import croniter
import subprocess

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.meeting.models import Meeting, MeetingStatus, AgentStatus, ALL_AGENTS
from src.meeting.meeting_scheduler import MeetingScheduler, get_scheduler
from src.meeting.meeting_room import MeetingRoom, get_meeting_room
from src.meeting.invitation_system import InvitationSystem, get_invitation_system
from src.meeting.agent_presence import AgentPresenceTracker, get_presence_tracker


class AgentMeetingCron:
    """
    Cron job for triggering scheduled agent meetings
    Runs periodically to check for upcoming meetings and notify agents
    """
    
    def __init__(self):
        self.scheduler = get_scheduler()
        self.room = get_meeting_room()
        self.invitations = get_invitation_system()
        self.presence = get_presence_tracker()
        self.log_file = "logs/agent_meetings.jsonl"
        self.notification_webhook = os.getenv("MEETING_NOTIFICATION_WEBHOOK")
        
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log a meeting event"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_upcoming_meetings(self, minutes: int = 15) -> List[Meeting]:
        """
        Get meetings starting within the specified number of minutes
        
        Args:
            minutes: Number of minutes to look ahead
        
        Returns:
            List of upcoming meetings
        """
        return self.scheduler.get_upcoming_meetings(minutes)
    
    async def notify_agents(self, meeting: Meeting, message: str):
        """
        Notify agents about a meeting
        
        Args:
            meeting: The meeting to notify about
            message: The notification message
        """
        for agent_id in meeting.attendees:
            # Log notification
            self.log_event("notification_sent", {
                "meeting_id": meeting.meeting_id,
                "agent_id": agent_id,
                "message": message
            })
            
            # In a real implementation, this would:
            # 1. Send WebSocket event to the agent
            # 2. Call the agent's A2A endpoint
            # 3. Send notification via configured channels
            
            print(f"[NOTIFY] {agent_id}: {message}")
    
    async def trigger_meeting(self, meeting: Meeting) -> bool:
        """
        Trigger a meeting to start
        
        Args:
            meeting: The meeting to trigger
        
        Returns:
            True if the meeting was started successfully
        """
        if meeting.status != MeetingStatus.SCHEDULED:
            return False
        
        # Start the meeting
        self.scheduler.start_meeting(meeting.meeting_id)
        
        # Start the meeting in the room
        await self.room.start_meeting(meeting)
        
        # Notify all attendees
        await self.notify_agents(
            meeting,
            f"Meeting '{meeting.title}' has started. Please join the meeting room."
        )
        
        # Log the event
        self.log_event("meeting_started", {
            "meeting_id": meeting.meeting_id,
            "title": meeting.title,
            "attendees": meeting.attendees
        })
        
        print(f"[MEETING STARTED] {meeting.title} ({meeting.meeting_id})")
        
        return True
    
    async def end_meeting(self, meeting: Meeting) -> bool:
        """
        End a meeting
        
        Args:
            meeting: The meeting to end
        
        Returns:
            True if the meeting was ended successfully
        """
        if meeting.status != MeetingStatus.IN_PROGRESS:
            return False
        
        # End the meeting
        self.scheduler.end_meeting(meeting.meeting_id)
        
        # End the meeting in the room
        await self.room.end_meeting(meeting)
        
        # Notify all attendees
        await self.notify_agents(
            meeting,
            f"Meeting '{meeting.title}' has ended."
        )
        
        # Log the event
        self.log_event("meeting_ended", {
            "meeting_id": meeting.meeting_id,
            "title": meeting.title,
            "duration_minutes": meeting.duration_minutes,
            "message_count": len(meeting.messages)
        })
        
        print(f"[MEETING ENDED] {meeting.title} ({meeting.meeting_id})")
        
        return True
    
    async def check_meeting_endings(self):
        """Check for meetings that should end based on duration"""
        now = datetime.utcnow()
        
        for meeting in self.scheduler.list_meetings(status=MeetingStatus.IN_PROGRESS):
            if meeting.started_at:
                started = datetime.fromisoformat(
                    meeting.started_at.replace('Z', '+00:00').replace('+00:00', '')
                )
                elapsed = (now - started).total_seconds() / 60
                
                if elapsed >= meeting.duration_minutes:
                    await self.end_meeting(meeting)
    
    async def send_reminders(self, minutes_before: int = 15):
        """
        Send reminders for upcoming meetings
        
        Args:
            minutes_before: How many minutes before the meeting to send reminders
        """
        upcoming = self.get_upcoming_meetings(minutes_before)
        
        for meeting in upcoming:
            scheduled = datetime.fromisoformat(
                meeting.scheduled_time.replace('Z', '+00:00').replace('+00:00', '')
            )
            now = datetime.utcnow()
            minutes_until = (scheduled - now).total_seconds() / 60
            
            if minutes_until <= minutes_before:
                await self.notify_agents(
                    meeting,
                    f"Reminder: Meeting '{meeting.title}' starts in {int(minutes_until)} minutes."
                )
                
                self.log_event("reminder_sent", {
                    "meeting_id": meeting.meeting_id,
                    "minutes_until": int(minutes_until)
                })
    
    def create_recurring_instances(self):
        """Create instances for recurring meetings"""
        self.scheduler.schedule_recurring_meetings()
    
    async def run_check(self):
        """
        Run a single check cycle
        This is the main function called by the cron job
        """
        print(f"\n[CRON] Agent Meeting Check - {datetime.utcnow().isoformat()}")
        print("=" * 60)
        
        # 1. Check for meetings to start (within 1 minute)
        upcoming = self.get_upcoming_meetings(1)
        for meeting in upcoming:
            scheduled = datetime.fromisoformat(
                meeting.scheduled_time.replace('Z', '+00:00').replace('+00:00', '')
            )
            now = datetime.utcnow()
            
            if scheduled <= now:
                await self.trigger_meeting(meeting)
        
        # 2. Check for meetings to end
        await self.check_meeting_endings()
        
        # 3. Send reminders for meetings in 15 minutes
        await self.send_reminders(15)
        
        # 4. Create recurring instances
        self.create_recurring_instances()
        
        # 5. Log summary
        self.log_event("cron_check_complete", {
            "upcoming_meetings": len(upcoming),
            "active_meetings": len(self.scheduler.list_meetings(status=MeetingStatus.IN_PROGRESS))
        })
    
    async def run_daemon(self, interval: int = 60):
        """
        Run as a daemon process, checking every interval seconds
        
        Args:
            interval: Check interval in seconds
        """
        print(f"Starting Agent Meeting Cron Daemon (interval: {interval}s)")
        
        while True:
            try:
                await self.run_check()
            except Exception as e:
                print(f"Error in cron check: {e}")
                self.log_event("cron_error", {"error": str(e)})
            
            await asyncio.sleep(interval)


def create_default_meetings():
    """Create default recurring meetings for the agent network"""
    scheduler = get_scheduler()
    
    # Daily Standup - Every day at 9 AM UTC
    daily_standup = scheduler.create_meeting(
        title="Daily Agent Standup",
        scheduled_time=datetime.utcnow().replace(
            hour=9, minute=0, second=0, microsecond=0
        ).isoformat(),
        duration_minutes=15,
        organizer="bambu-executiveusa",
        attendees=[
            "bambu-executiveusa",
            "pauli-planner",
            "synthia-executor",
            "alex-metagpt"
        ],
        agenda=[
            "Status updates from each agent",
            "Current blockers and dependencies",
            "Today's priorities"
        ],
        recurrence="0 9 * * *"  # Daily at 9 AM
    )
    print(f"Created: {daily_standup.title} (ID: {daily_standup.meeting_id})")
    
    # Weekly Planning - Every Monday at 10 AM UTC
    weekly_planning = scheduler.create_meeting(
        title="Weekly Sprint Planning",
        scheduled_time=datetime.utcnow().replace(
            hour=10, minute=0, second=0, microsecond=0
        ).isoformat(),
        duration_minutes=30,
        organizer="bambu-executiveusa",
        attendees=[
            "bambu-executiveusa",
            "pauli-planner"
        ],
        agenda=[
            "Review last week's progress",
            "Plan this week's sprint",
            "Assign tasks to agents"
        ],
        recurrence="0 10 * * 1"  # Monday at 10 AM
    )
    print(f"Created: {weekly_planning.title} (ID: {weekly_planning.meeting_id})")
    
    # Code Review - Tuesday and Thursday at 2 PM UTC
    code_review = scheduler.create_meeting(
        title="Code Review Session",
        scheduled_time=datetime.utcnow().replace(
            hour=14, minute=0, second=0, microsecond=0
        ).isoformat(),
        duration_minutes=45,
        organizer="alex-metagpt",
        attendees=[
            "alex-metagpt",
            "synthia-executor"
        ],
        agenda=[
            "Review pending PRs",
            "Discuss architecture decisions",
            "Plan refactoring tasks"
        ],
        recurrence="0 14 * * 2,4"  # Tuesday and Thursday at 2 PM
    )
    print(f"Created: {code_review.title} (ID: {code_review.meeting_id})")
    
    # Monthly Security Audit - 1st of each month at 10 AM UTC
    security_audit = scheduler.create_meeting(
        title="Monthly Security Audit",
        scheduled_time=datetime.utcnow().replace(
            day=1, hour=10, minute=0, second=0, microsecond=0
        ).isoformat(),
        duration_minutes=60,
        organizer="bambu-executiveusa",
        attendees=[
            "bambu-executiveusa",
            "synthia-executor"
        ],
        agenda=[
            "Review security scan results",
            "Update dependencies",
            "Plan security improvements"
        ],
        recurrence="0 10 1 * *"  # 1st of month at 10 AM
    )
    print(f"Created: {security_audit.title} (ID: {security_audit.meeting_id})")
    
    return {
        "daily_standup": daily_standup.meeting_id,
        "weekly_planning": weekly_planning.meeting_id,
        "code_review": code_review.meeting_id,
        "security_audit": security_audit.meeting_id
    }


async def main():
    """Main entry point for the agent meeting cron job"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Meeting Cron Job")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--create-defaults", action="store_true", help="Create default meetings")
    parser.add_argument("--check", action="store_true", help="Run a single check")
    
    args = parser.parse_args()
    
    if args.create_defaults:
        print("Creating default meetings...")
        meetings = create_default_meetings()
        print(f"\nCreated {len(meetings)} default meetings")
        return
    
    cron = AgentMeetingCron()
    
    if args.daemon:
        await cron.run_daemon(args.interval)
    else:
        await cron.run_check()


if __name__ == "__main__":
    asyncio.run(main())