#!/usr/bin/env python3
"""
A2A (Agent-to-Agent) Protocol Integration for Bambu
Enables real-time communication between Bambu and other agents like Alex

Based on the A2A Protocol specification: https://a2a-protocol.org
"""

import os
import json
import uuid
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum


class MessageRole(Enum):
    """Role of the message sender"""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class TaskStatus(Enum):
    """Status of an A2A task"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentCard:
    """
    Agent Card - Describes an agent's capabilities and connection info
    Used for agent discovery in the A2A protocol
    """
    agent_id: str
    name: str
    description: str
    version: str = "1.0.0"
    capabilities: List[str] = field(default_factory=list)
    endpoints: Dict[str, str] = field(default_factory=dict)
    authentication: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentCard":
        return cls(**data)


@dataclass
class A2AMessage:
    """
    A2A Message - A single message in an A2A conversation
    """
    message_id: str
    role: MessageRole
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        return cls(
            message_id=data["message_id"],
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=data["timestamp"],
            metadata=data.get("metadata", {})
        )


@dataclass
class A2ATask:
    """
    A2A Task - A long-running task between agents
    """
    task_id: str
    status: TaskStatus
    initiator_agent_id: str
    target_agent_id: str
    messages: List[A2AMessage] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "initiator_agent_id": self.initiator_agent_id,
            "target_agent_id": self.target_agent_id,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "result": self.result
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2ATask":
        return cls(
            task_id=data["task_id"],
            status=TaskStatus(data["status"]),
            initiator_agent_id=data["initiator_agent_id"],
            target_agent_id=data["target_agent_id"],
            messages=[A2AMessage.from_dict(m) for m in data.get("messages", [])],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            result=data.get("result")
        )


class A2AClient:
    """
    A2A Client - Connect to other A2A-compliant agents
    Used by Bambu to communicate with Alex and other agents
    """
    
    def __init__(self, agent_card: AgentCard, base_url: str = None):
        self.agent_card = agent_card
        self.base_url = base_url or os.getenv("A2A_BASE_URL", "http://localhost:8080")
        self.session: Optional[aiohttp.ClientSession] = None
        self.active_tasks: Dict[str, A2ATask] = {}
        self.message_handlers: Dict[str, Callable] = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
        
    async def discover_agent(self, agent_url: str) -> Optional[AgentCard]:
        """Discover an agent's capabilities via its Agent Card"""
        try:
            async with self.session.get(f"{agent_url}/.well-known/agent.json") as response:
                if response.status == 200:
                    data = await response.json()
                    return AgentCard.from_dict(data)
        except Exception as e:
            print(f"Failed to discover agent at {agent_url}: {e}")
        return None
    
    async def send_message(
        self,
        target_agent_id: str,
        content: str,
        task_id: Optional[str] = None
    ) -> A2ATask:
        """Send a message to another agent"""
        if task_id is None:
            task_id = str(uuid.uuid4())
            
        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            role=MessageRole.AGENT,
            content=content
        )
        
        # Create or update task
        if task_id not in self.active_tasks:
            task = A2ATask(
                task_id=task_id,
                status=TaskStatus.RUNNING,
                initiator_agent_id=self.agent_card.agent_id,
                target_agent_id=target_agent_id,
                messages=[message]
            )
            self.active_tasks[task_id] = task
        else:
            task = self.active_tasks[task_id]
            task.messages.append(message)
            task.updated_at = datetime.utcnow().isoformat()
        
        # Send via JSON-RPC 2.0
        payload = {
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "params": task.to_dict(),
            "id": str(uuid.uuid4())
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/a2a",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result:
                        return A2ATask.from_dict(result["result"])
        except Exception as e:
            print(f"Failed to send message: {e}")
            
        return task
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task"""
        payload = {
            "jsonrpc": "2.0",
            "method": "tasks/get",
            "params": {"task_id": task_id},
            "id": str(uuid.uuid4())
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/a2a",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result:
                        task = A2ATask.from_dict(result["result"])
                        self.active_tasks[task_id] = task
                        return task.status
        except Exception as e:
            print(f"Failed to get task status: {e}")
            
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        payload = {
            "jsonrpc": "2.0",
            "method": "tasks/cancel",
            "params": {"task_id": task_id},
            "id": str(uuid.uuid4())
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/a2a",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if "result" in result:
                        task = A2ATask.from_dict(result["result"])
                        self.active_tasks[task_id] = task
                        return task.status == TaskStatus.CANCELLED
        except Exception as e:
            print(f"Failed to cancel task: {e}")
            
        return False
    
    async def stream_task_updates(
        self,
        task_id: str,
        callback: Callable[[Dict[str, Any]], None]
    ):
        """Stream updates for a task via Server-Sent Events (SSE)"""
        try:
            async with self.session.get(
                f"{self.base_url}/a2a/tasks/{task_id}/stream",
                headers={"Accept": "text/event-stream"}
            ) as response:
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line.decode().strip())
                            callback(data)
                        except json.JSONDecodeError:
                            pass
        except Exception as e:
            print(f"Failed to stream task updates: {e}")


class A2AServer:
    """
    A2A Server - Expose Bambu as an A2A-compliant agent
    Allows other agents to discover and communicate with Bambu
    """
    
    def __init__(self, agent_card: AgentCard, message_handler: Callable = None):
        self.agent_card = agent_card
        self.message_handler = message_handler
        self.tasks: Dict[str, A2ATask] = {}
        
    def get_agent_card(self) -> Dict[str, Any]:
        """Return the agent card for discovery"""
        return self.agent_card.to_dict()
    
    async def handle_message(self, task: A2ATask) -> A2ATask:
        """Handle an incoming message from another agent"""
        if self.message_handler:
            response = await self.message_handler(task)
            if response:
                if isinstance(response, str):
                    # Create a response message
                    message = A2AMessage(
                        message_id=str(uuid.uuid4()),
                        role=MessageRole.AGENT,
                        content=response
                    )
                    task.messages.append(message)
                elif isinstance(response, A2ATask):
                    task = response
                    
        task.updated_at = datetime.utcnow().isoformat()
        self.tasks[task.task_id] = task
        return task
    
    def create_task(
        self,
        initiator_agent_id: str,
        target_agent_id: str,
        initial_message: str
    ) -> A2ATask:
        """Create a new task"""
        task = A2ATask(
            task_id=str(uuid.uuid4()),
            status=TaskStatus.PENDING,
            initiator_agent_id=initiator_agent_id,
            target_agent_id=target_agent_id,
            messages=[
                A2AMessage(
                    message_id=str(uuid.uuid4()),
                    role=MessageRole.USER,
                    content=initial_message
                )
            ]
        )
        self.tasks[task.task_id] = task
        return task


# Pre-defined agent cards for Bambu's network
def get_bambu_agent_card() -> AgentCard:
    """Get Bambu's agent card"""
    return AgentCard(
        agent_id="bambu-executiveusa",
        name="Bambu",
        description="CEO & Founder of BambuVerse. GitHub Agent Secretary. Repository Analyst, PRD Creator, Deployment Coordinator.",
        version="1.0.0",
        capabilities=[
            "repo_analysis",
            "prd_generation",
            "deployment_management",
            "cross_repo_coordination",
            "agent_orchestration",
            "code_generation",
            "security_scanning"
        ],
        endpoints={
            "a2a": "https://bambu.example.com/a2a",
            "agent_card": "https://bambu.example.com/.well-known/agent.json"
        },
        metadata={
            "organization": "executiveusa",
            "role": "ceo",
            "world": "BambuVerse"
        }
    )


def get_alex_agent_card() -> AgentCard:
    """Get Alex's agent card (placeholder)"""
    return AgentCard(
        agent_id="alex-metagpt",
        name="Alex",
        description="MetaGPT-powered agent for collaborative development.",
        version="1.0.0",
        capabilities=[
            "code_review",
            "architecture_design",
            "documentation",
            "testing"
        ],
        endpoints={
            "a2a": "https://alex.example.com/a2a",
            "agent_card": "https://alex.example.com/.well-known/agent.json"
        },
        metadata={
            "framework": "MetaGPT",
            "role": "developer"
        }
    )


# Convenience function for quick communication
async def talk_to_alex(message: str, task_id: str = None) -> str:
    """
    Send a message to Alex and get a response
    Convenience function for Bambu to talk to Alex
    """
    bambu_card = get_bambu_agent_card()
    alex_card = get_alex_agent_card()
    
    async with A2AClient(bambu_card) as client:
        task = await client.send_message(
            target_agent_id=alex_card.agent_id,
            content=message,
            task_id=task_id
        )
        
        # Wait for response
        if task.messages:
            for msg in reversed(task.messages):
                if msg.role == MessageRole.AGENT and msg.message_id != task.messages[0].message_id:
                    return msg.content
                    
    return "No response from Alex"


def main():
    """Test the A2A integration"""
    print("A2A Integration for Bambu")
    print("=" * 50)
    
    # Get agent cards
    bambu = get_bambu_agent_card()
    alex = get_alex_agent_card()
    
    print(f"\nBambu Agent Card:")
    print(json.dumps(bambu.to_dict(), indent=2))
    
    print(f"\nAlex Agent Card:")
    print(json.dumps(alex.to_dict(), indent=2))
    
    print("\nA2A Protocol ready for agent-to-agent communication!")


if __name__ == "__main__":
    main()