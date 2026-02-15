#!/usr/bin/env python3
"""
MetaGPT Integration for Bambu
Enables software development with role-playing agents

Based on MetaGPT: https://github.com/geekan/MetaGPT
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class MetaGPTAction(Enum):
    """Actions available in MetaGPT"""
    WRITE_PRD = "write_prd"
    WRITE_DESIGN = "write_design"
    WRITE_CODE = "write_code"
    WRITE_TEST = "write_test"
    WRITE_REVIEW = "write_review"
    DEBUG_CODE = "debug_code"
    DEPLOY = "deploy"


class MetaGPTRole(Enum):
    """Roles in MetaGPT"""
    PRODUCT_MANAGER = "Product Manager"
    ARCHITECT = "Architect"
    PROJECT_MANAGER = "Project Manager"
    ENGINEER = "Engineer"
    QA_ENGINEER = "QA Engineer"
    REVIEWER = "Reviewer"


@dataclass
class MetaGPTMessage:
    """A message in MetaGPT"""
    role: MetaGPTRole
    action: MetaGPTAction
    content: str
    agent_name: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    artifacts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "action": self.action.value,
            "content": self.content,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp,
            "artifacts": self.artifacts
        }


@dataclass
class MetaGPTConfig:
    """Configuration for MetaGPT"""
    project_name: str
    project_path: str
    llm_model: str = "gpt-4"
    max_iterations: int = 10
    auto_run: bool = True
    use_memory: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "project_path": self.project_path,
            "llm_model": self.llm_model,
            "max_iterations": self.max_iterations,
            "auto_run": self.auto_run,
            "use_memory": self.use_memory
        }


class MetaGPTAgent:
    """A MetaGPT agent with a specific role"""
    
    def __init__(
        self,
        name: str,
        role: MetaGPTRole,
        actions: List[MetaGPTAction],
        system_prompt: str = None
    ):
        self.name = name
        self.role = role
        self.actions = actions
        self.system_prompt = system_prompt or self._default_prompt()
        self.memory: List[MetaGPTMessage] = []
        
    def _default_prompt(self) -> str:
        """Get the default system prompt for the role"""
        prompts = {
            MetaGPTRole.PRODUCT_MANAGER: """You are a Product Manager agent.
Your responsibilities:
- Write clear and comprehensive PRDs (Product Requirements Documents)
- Define user stories and acceptance criteria
- Prioritize features based on business value
- Communicate requirements to the team

Always think from the user's perspective and ensure requirements are actionable.""",
            
            MetaGPTRole.ARCHITECT: """You are a Software Architect agent.
Your responsibilities:
- Design system architecture
- Define technical specifications
- Choose appropriate technologies and patterns
- Ensure scalability and maintainability

Always consider trade-offs and document your decisions.""",
            
            MetaGPTRole.PROJECT_MANAGER: """You are a Project Manager agent.
Your responsibilities:
- Create and manage project plans
- Coordinate between team members
- Track progress and report status
- Manage risks and dependencies

Always keep the project on track and communicate clearly.""",
            
            MetaGPTRole.ENGINEER: """You are a Software Engineer agent.
Your responsibilities:
- Write clean, maintainable code
- Implement features according to specifications
- Follow best practices and coding standards
- Document your code

Always write code that is production-ready.""",
            
            MetaGPTRole.QA_ENGINEER: """You are a QA Engineer agent.
Your responsibilities:
- Write comprehensive test cases
- Perform code reviews
- Identify bugs and edge cases
- Ensure quality standards

Always think about what could go wrong.""",
            
            MetaGPTRole.REVIEWER: """You are a Code Reviewer agent.
Your responsibilities:
- Review code for quality and correctness
- Provide constructive feedback
- Identify potential issues
- Approve or request changes

Always be thorough but fair in your reviews."""
        }
        return prompts.get(self.role, "You are a helpful agent.")
    
    def add_to_memory(self, message: MetaGPTMessage):
        """Add a message to memory"""
        self.memory.append(message)
        
    def can_perform(self, action: MetaGPTAction) -> bool:
        """Check if this agent can perform an action"""
        return action in self.actions
    
    async def perform_action(
        self,
        action: MetaGPTAction,
        context: str,
        artifacts: List[str] = None
    ) -> MetaGPTMessage:
        """Perform an action and return the result"""
        if not self.can_perform(action):
            raise ValueError(f"Agent {self.name} cannot perform action {action.value}")
            
        message = MetaGPTMessage(
            role=self.role,
            action=action,
            content=f"Performing {action.value}: {context}",
            agent_name=self.name,
            artifacts=artifacts or []
        )
        
        self.add_to_memory(message)
        return message


class MetaGPTTeam:
    """A team of MetaGPT agents working together"""
    
    def __init__(self, config: MetaGPTConfig):
        self.config = config
        self.agents: Dict[str, MetaGPTAgent] = {}
        self.conversation_history: List[MetaGPTMessage] = []
        self.artifacts: Dict[str, str] = {}
        
        # Initialize default team
        self._create_default_team()
        
    def _create_default_team(self):
        """Create the default team of agents"""
        # Product Manager
        pm = MetaGPTAgent(
            name="Alice",
            role=MetaGPTRole.PRODUCT_MANAGER,
            actions=[MetaGPTAction.WRITE_PRD]
        )
        self.add_agent(pm)
        
        # Architect
        arch = MetaGPTAgent(
            name="Bob",
            role=MetaGPTRole.ARCHITECT,
            actions=[MetaGPTAction.WRITE_DESIGN]
        )
        self.add_agent(arch)
        
        # Project Manager
        pmgr = MetaGPTAgent(
            name="Carol",
            role=MetaGPTRole.PROJECT_MANAGER,
            actions=[MetaGPTAction.WRITE_DESIGN]
        )
        self.add_agent(pmgr)
        
        # Engineers
        eng1 = MetaGPTAgent(
            name="David",
            role=MetaGPTRole.ENGINEER,
            actions=[MetaGPTAction.WRITE_CODE, MetaGPTAction.DEBUG_CODE]
        )
        self.add_agent(eng1)
        
        eng2 = MetaGPTAgent(
            name="Eve",
            role=MetaGPTRole.ENGINEER,
            actions=[MetaGPTAction.WRITE_CODE, MetaGPTAction.DEBUG_CODE]
        )
        self.add_agent(eng2)
        
        # QA Engineer
        qa = MetaGPTAgent(
            name="Frank",
            role=MetaGPTRole.QA_ENGINEER,
            actions=[MetaGPTAction.WRITE_TEST]
        )
        self.add_agent(qa)
        
        # Reviewer
        rev = MetaGPTAgent(
            name="Grace",
            role=MetaGPTRole.REVIEWER,
            actions=[MetaGPTAction.WRITE_REVIEW]
        )
        self.add_agent(rev)
        
    def add_agent(self, agent: MetaGPTAgent):
        """Add an agent to the team"""
        self.agents[agent.name] = agent
        
    def remove_agent(self, name: str):
        """Remove an agent from the team"""
        if name in self.agents:
            del self.agents[name]
            
    def get_agent(self, name: str) -> Optional[MetaGPTAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def get_agents_by_role(self, role: MetaGPTRole) -> List[MetaGPTAgent]:
        """Get all agents with a specific role"""
        return [a for a in self.agents.values() if a.role == role]
    
    async def run_sprint(self, requirement: str) -> Dict[str, Any]:
        """
        Run a complete sprint with the team
        This follows the MetaGPT workflow: PRD -> Design -> Code -> Test -> Review
        """
        results = {
            "requirement": requirement,
            "stages": {},
            "artifacts": [],
            "status": "started"
        }
        
        # Stage 1: Product Manager writes PRD
        pm = self.get_agents_by_role(MetaGPTRole.PRODUCT_MANAGER)[0]
        prd_msg = await pm.perform_action(
            MetaGPTAction.WRITE_PRD,
            requirement
        )
        self.conversation_history.append(prd_msg)
        results["stages"]["prd"] = prd_msg.to_dict()
        
        # Stage 2: Architect writes design
        arch = self.get_agents_by_role(MetaGPTRole.ARCHITECT)[0]
        design_msg = await arch.perform_action(
            MetaGPTAction.WRITE_DESIGN,
            f"Design system for: {requirement}"
        )
        self.conversation_history.append(design_msg)
        results["stages"]["design"] = design_msg.to_dict()
        
        # Stage 3: Engineers write code
        engineers = self.get_agents_by_role(MetaGPTRole.ENGINEER)
        for eng in engineers:
            code_msg = await eng.perform_action(
                MetaGPTAction.WRITE_CODE,
                f"Implement: {requirement}"
            )
            self.conversation_history.append(code_msg)
            results["stages"][f"code_{eng.name}"] = code_msg.to_dict()
            
        # Stage 4: QA writes tests
        qa = self.get_agents_by_role(MetaGPTRole.QA_ENGINEER)[0]
        test_msg = await qa.perform_action(
            MetaGPTAction.WRITE_TEST,
            f"Test: {requirement}"
        )
        self.conversation_history.append(test_msg)
        results["stages"]["test"] = test_msg.to_dict()
        
        # Stage 5: Reviewer reviews
        rev = self.get_agents_by_role(MetaGPTRole.REVIEWER)[0]
        review_msg = await rev.perform_action(
            MetaGPTAction.WRITE_REVIEW,
            f"Review: {requirement}"
        )
        self.conversation_history.append(review_msg)
        results["stages"]["review"] = review_msg.to_dict()
        
        results["status"] = "completed"
        return results
    
    async def develop_feature(self, feature_description: str) -> Dict[str, Any]:
        """
        Develop a feature using the MetaGPT workflow
        """
        return await self.run_sprint(feature_description)
    
    def save_artifact(self, name: str, content: str):
        """Save an artifact (code, document, etc.)"""
        self.artifacts[name] = content
        
    def get_artifact(self, name: str) -> Optional[str]:
        """Get an artifact by name"""
        return self.artifacts.get(name)
    
    def export_artifacts(self, output_dir: str):
        """Export all artifacts to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for name, content in self.artifacts.items():
            file_path = output_path / name
            file_path.write_text(content)
            
    def get_team_summary(self) -> Dict[str, Any]:
        """Get a summary of the team"""
        return {
            "project_name": self.config.project_name,
            "agent_count": len(self.agents),
            "agents": [
                {
                    "name": a.name,
                    "role": a.role.value,
                    "actions": [act.value for act in a.actions]
                }
                for a in self.agents.values()
            ],
            "conversation_count": len(self.conversation_history),
            "artifact_count": len(self.artifacts)
        }


# Alex - The MetaGPT agent for Bambu's network
def create_alex_team(project_name: str = "BambuVerse") -> MetaGPTTeam:
    """Create Alex's MetaGPT team"""
    config = MetaGPTConfig(
        project_name=project_name,
        project_path=f"./projects/{project_name}",
        llm_model="gpt-4",
        max_iterations=10
    )
    return MetaGPTTeam(config)


async def alex_develop_feature(feature: str) -> Dict[str, Any]:
    """Have Alex develop a feature"""
    team = create_alex_team()
    result = await team.develop_feature(feature)
    return result


def main():
    """Test the MetaGPT integration"""
    print("MetaGPT Integration for Bambu")
    print("=" * 50)
    
    # Create team
    team = create_alex_team("TestProject")
    
    print(f"\nTeam Summary:")
    summary = team.get_team_summary()
    print(json.dumps(summary, indent=2))
    
    print("\nMetaGPT Team ready for software development!")


if __name__ == "__main__":
    main()