#!/usr/bin/env python3
"""
CAMEL Framework Integration for Bambu
Enables multi-agent communication and collaboration using CAMEL-AI

Based on CAMEL: https://github.com/camel-ai/camel
Documentation: https://www.camel-ai.org/
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum


class AgentRole(Enum):
    """Roles for CAMEL agents"""
    ASSISTANT = "assistant"
    USER = "user"
    CRITIC = "critic"
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    EXECUTOR = "executor"
    COORDINATOR = "coordinator"


@dataclass
class CAMELMessage:
    """A message in the CAMEL framework"""
    role: AgentRole
    content: str
    agent_name: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "content": self.content,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CAMELMessage":
        return cls(
            role=AgentRole(data["role"]),
            content=data["content"],
            agent_name=data["agent_name"],
            timestamp=data["timestamp"],
            metadata=data.get("metadata", {})
        )


@dataclass
class CAMELAgentConfig:
    """Configuration for a CAMEL agent"""
    name: str
    role: AgentRole
    system_prompt: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    capabilities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role.value,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "capabilities": self.capabilities
        }


class CAMELAgent:
    """
    A CAMEL-compatible agent
    Can communicate with other agents using role-playing patterns
    """
    
    def __init__(self, config: CAMELAgentConfig):
        self.config = config
        self.messages: List[CAMELMessage] = []
        self.context: Dict[str, Any] = {}
        
    def add_message(self, message: CAMELMessage):
        """Add a message to the conversation history"""
        self.messages.append(message)
        
    def get_context(self) -> str:
        """Get the conversation context as a string"""
        return "\n".join([
            f"[{m.agent_name} ({m.role.value})]: {m.content}"
            for m in self.messages
        ])
    
    def clear_history(self):
        """Clear the conversation history"""
        self.messages = []
        
    async def respond(self, content: str, target_agent: str = None) -> CAMELMessage:
        """Generate a response (to be implemented with actual LLM)"""
        message = CAMELMessage(
            role=self.config.role,
            content=content,
            agent_name=self.config.name
        )
        self.messages.append(message)
        return message


class CAMELSociety:
    """
    A society of CAMEL agents that can collaborate
    Implements role-playing patterns for multi-agent interaction
    """
    
    def __init__(self, name: str):
        self.name = name
        self.agents: Dict[str, CAMELAgent] = {}
        self.conversation_history: List[CAMELMessage] = []
        self.task_queue: List[Dict[str, Any]] = []
        
    def add_agent(self, agent: CAMELAgent):
        """Add an agent to the society"""
        self.agents[agent.config.name] = agent
        
    def remove_agent(self, agent_name: str):
        """Remove an agent from the society"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            
    def get_agent(self, agent_name: str) -> Optional[CAMELAgent]:
        """Get an agent by name"""
        return self.agents.get(agent_name)
    
    async def broadcast(self, message: CAMELMessage):
        """Broadcast a message to all agents"""
        self.conversation_history.append(message)
        for agent in self.agents.values():
            agent.add_message(message)
            
    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: str
    ) -> CAMELMessage:
        """Send a message from one agent to another"""
        sender = self.agents.get(from_agent)
        receiver = self.agents.get(to_agent)
        
        if not sender or not receiver:
            raise ValueError(f"Agent not found: {from_agent} or {to_agent}")
            
        message = CAMELMessage(
            role=sender.config.role,
            content=content,
            agent_name=from_agent
        )
        
        sender.add_message(message)
        receiver.add_message(message)
        self.conversation_history.append(message)
        
        return message
    
    async def role_play(
        self,
        initiator: str,
        responder: str,
        initial_message: str,
        max_turns: int = 10
    ) -> List[CAMELMessage]:
        """
        Conduct a role-playing conversation between two agents
        This is the core CAMEL pattern for collaborative problem-solving
        """
        messages = []
        
        # Send initial message
        msg = await self.send_message(initiator, responder, initial_message)
        messages.append(msg)
        
        # Continue conversation
        for turn in range(max_turns - 1):
            # Get responder's response
            responder_agent = self.agents[responder]
            response = await responder_agent.respond(
                f"Responding to: {msg.content}",
                target_agent=initiator
            )
            messages.append(response)
            
            # Get initiator's follow-up
            initiator_agent = self.agents[initiator]
            follow_up = await initiator_agent.respond(
                f"Continuing conversation: {response.content}",
                target_agent=responder
            )
            messages.append(follow_up)
            
            msg = follow_up
            
        return messages
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        return {
            "society_name": self.name,
            "agent_count": len(self.agents),
            "message_count": len(self.conversation_history),
            "agents": [a.config.name for a in self.agents.values()],
            "last_message": self.conversation_history[-1].to_dict() if self.conversation_history else None
        }


# Pre-configured agents for Bambu's network
def create_bambu_camel_agent() -> CAMELAgent:
    """Create Bambu as a CAMEL agent"""
    config = CAMELAgentConfig(
        name="Bambu",
        role=AgentRole.COORDINATOR,
        system_prompt="""You are Bambu, CEO & Founder of BambuVerse.
You are a GitHub Agent Secretary that coordinates between multiple agents and repositories.
Your role is to:
- Analyze repositories and create reports
- Generate PRDs (Product Requirements Documents)
- Coordinate deployments via Coolify, Hostinger, and Cloudflare
- Manage other agents like Pauli and Synthia
- Report to Agent Zero and the operating system

You communicate clearly, make decisions efficiently, and always consider the Signal vs Noise principle:
1. Does this directly lead to our first paying customer?
2. Can we ship this in 7 days or less?
3. Will this create compound leverage?""",
        model="claude-3-opus-20240229",
        capabilities=[
            "repo_analysis",
            "prd_generation",
            "deployment_management",
            "agent_coordination",
            "code_generation",
            "security_scanning"
        ]
    )
    return CAMELAgent(config)


def create_alex_camel_agent() -> CAMELAgent:
    """Create Alex as a CAMEL agent (MetaGPT-powered)"""
    config = CAMELAgentConfig(
        name="Alex",
        role=AgentRole.CODER,
        system_prompt="""You are Alex, a MetaGPT-powered developer agent.
You work alongside Bambu to:
- Write and review code
- Design system architectures
- Create documentation
- Implement features
- Test and debug

You collaborate effectively with other agents and always provide clear, actionable responses.""",
        model="gpt-4",
        capabilities=[
            "code_writing",
            "architecture_design",
            "documentation",
            "testing",
            "debugging"
        ]
    )
    return CAMELAgent(config)


def create_pauli_camel_agent() -> CAMELAgent:
    """Create Pauli as a CAMEL agent (Operating System)"""
    config = CAMELAgentConfig(
        name="Pauli",
        role=AgentRole.PLANNER,
        system_prompt="""You are Pauli, an Operating System agent.
You manage the overall system state and coordinate between different components.
Your role is to:
- Plan and schedule tasks
- Monitor system health
- Coordinate between agents
- Manage resources
- Report status to Bambu

You are methodical, organized, and always think several steps ahead.""",
        model="claude-3-opus-20240229",
        capabilities=[
            "task_planning",
            "resource_management",
            "system_monitoring",
            "coordination"
        ]
    )
    return CAMELAgent(config)


def create_synthia_camel_agent() -> CAMELAgent:
    """Create Synthia as a CAMEL agent (Operating System)"""
    config = CAMELAgentConfig(
        name="Synthia",
        role=AgentRole.EXECUTOR,
        system_prompt="""You are Synthia, an Operating System agent.
You execute tasks and manage the technical implementation.
Your role is to:
- Execute planned tasks
- Manage deployments
- Handle API integrations
- Monitor execution status
- Report results to Pauli and Bambu

You are precise, efficient, and always ensure tasks are completed correctly.""",
        model="gpt-4",
        capabilities=[
            "task_execution",
            "deployment",
            "api_integration",
            "monitoring"
        ]
    )
    return CAMELAgent(config)


def create_bambu_society() -> CAMELSociety:
    """Create the BambuVerse society with all agents"""
    society = CAMELSociety("BambuVerse")
    
    # Add all agents
    society.add_agent(create_bambu_camel_agent())
    society.add_agent(create_alex_camel_agent())
    society.add_agent(create_pauli_camel_agent())
    society.add_agent(create_synthia_camel_agent())
    
    return society


# Convenience functions for quick agent communication
async def bambu_talk_to_alex(message: str) -> str:
    """Have Bambu send a message to Alex"""
    society = create_bambu_society()
    
    msg = await society.send_message("Bambu", "Alex", message)
    
    # Simulate Alex's response (would be actual LLM call in production)
    alex = society.get_agent("Alex")
    response = await alex.respond(f"Received: {message}. Processing...")
    
    return response.content


async def bambu_coordinate_task(task_description: str) -> Dict[str, Any]:
    """Have Bambu coordinate a task across agents"""
    society = create_bambu_society()
    
    # Bambu broadcasts the task
    broadcast_msg = CAMELMessage(
        role=AgentRole.COORDINATOR,
        content=f"New task: {task_description}",
        agent_name="Bambu"
    )
    await society.broadcast(broadcast_msg)
    
    # Pauli plans
    pauli = society.get_agent("Pauli")
    plan_msg = await pauli.respond(f"Planning task: {task_description}")
    
    # Synthia executes
    synthia = society.get_agent("Synthia")
    exec_msg = await synthia.respond(f"Executing plan for: {task_description}")
    
    # Alex reviews
    alex = society.get_agent("Alex")
    review_msg = await alex.respond(f"Reviewing execution of: {task_description}")
    
    return {
        "task": task_description,
        "plan": plan_msg.content,
        "execution": exec_msg.content,
        "review": review_msg.content,
        "status": "completed"
    }


def main():
    """Test the CAMEL integration"""
    print("CAMEL Framework Integration for Bambu")
    print("=" * 50)
    
    # Create society
    society = create_bambu_society()
    
    print(f"\nSociety: {society.name}")
    print(f"Agents: {list(society.agents.keys())}")
    
    # Show agent configs
    for name, agent in society.agents.items():
        print(f"\n{name} ({agent.config.role.value}):")
        print(f"  Capabilities: {agent.config.capabilities}")
    
    print("\nCAMEL Framework ready for multi-agent communication!")


if __name__ == "__main__":
    main()