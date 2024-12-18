# Backend Architecture Refactoring Analysis

## Current Architecture Overview

### Core Components
1. Main Flask Application (devika.py)
   - Handles HTTP endpoints and WebSocket connections
   - Uses threading for concurrent operations
   - Manages agent state and project management

2. Agent System (src/agents/)
   - Multiple specialized agents (Runner, Planner, etc.)
   - Mix of synchronous and asynchronous operations
   - Direct state management through shared objects

3. LLM Integration (src/llm/)
   - Multiple model providers
   - Synchronous inference with timeout handling
   - Print-based debugging

### Identified Issues

#### 1. Logging Implementation
Current Issues:
- Direct print statements used throughout codebase
  ```python
  # Example from llm.py
  print(f"Model: {self.model_id}, Enum: {model_enum}")
  ```
- Inconsistent error handling and logging patterns
- Limited structured logging for debugging

Recommendations:
- Implement structured logging using Python's logging module
- Define log levels (DEBUG, INFO, WARNING, ERROR)
- Add context-specific loggers for different components
- Implement log rotation and persistence

Example Implementation:
```python
import logging

# Component-specific logger
logger = logging.getLogger(__name__)

class LLM:
    def inference(self, prompt: str, project_name: str) -> str:
        logger.info(f"Starting inference for model={self.model_id} project={project_name}")
        try:
            # Inference logic
            logger.debug(f"Model enum resolved: {model_enum}")
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}", exc_info=True)
```

#### 2. State Management
Current Issues:
- Direct shared state access through AgentState class
- Potential race conditions in multi-threaded operations
- No message queue for state updates
- Synchronization issues between WebSocket and HTTP endpoints

Recommendations:
- Implement message queue service (Redis/RabbitMQ)
- Use atomic operations for state updates
- Implement proper locking mechanisms
- Add state versioning for consistency

Example Architecture:
```
[WebSocket/HTTP] -> [Message Queue] -> [State Manager] -> [Agents]
                                   -> [Event Subscribers]
```

Implementation Approach:
```python
from redis import Redis
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentStateEvent:
    project_name: str
    state_type: str
    data: dict
    version: int

class StateManager:
    def __init__(self):
        self.redis = Redis()
        self.pubsub = self.redis.pubsub()

    async def update_state(self, event: AgentStateEvent):
        await self.redis.publish(
            f"state:{event.project_name}",
            event.json()
        )

    async def get_state(self, project_name: str) -> Optional[dict]:
        return await self.redis.get(f"state:{project_name}")
```

#### 3. Thread Race Conditions
Current Issues:
- Multiple threads accessing shared state
- No proper synchronization in handle_message
- Potential deadlocks in agent execution
- Inconsistent state updates

Recommendations:
- Migrate to asyncio-based architecture
- Implement proper locks and semaphores
- Use async/await patterns consistently
- Add request correlation IDs

Example Implementation:
```python
from asyncio import Lock
from contextlib import asynccontextmanager

class AsyncAgentExecutor:
    def __init__(self):
        self._locks = {}
        self._global_lock = Lock()

    @asynccontextmanager
    async def project_lock(self, project_name: str):
        async with self._global_lock:
            if project_name not in self._locks:
                self._locks[project_name] = Lock()

        async with self._locks[project_name]:
            yield

    async def execute(self, message: str, project_name: str):
        async with self.project_lock(project_name):
            # Safe execution logic
            pass
```

#### 4. Asyncio Architecture
Current Issues:
- Mixed sync/async code
- Blocking operations in async context
- Inefficient resource usage
- Complex error handling

Recommendations:
- Full migration to asyncio
- Use FastAPI instead of Flask
- Implement proper connection pooling
- Add proper error boundaries

Example Implementation:
```python
from fastapi import FastAPI, WebSocket
from typing import Dict, Optional

app = FastAPI()

class AsyncDevika:
    def __init__(self):
        self.state_manager = StateManager()
        self.agent_executor = AsyncAgentExecutor()
        self.active_connections: Dict[str, WebSocket] = {}

    async def handle_message(self, websocket: WebSocket, message: dict):
        project_name = message["project_name"]
        async with self.agent_executor.project_lock(project_name):
            try:
                await self.process_message(message)
            except Exception as e:
                await websocket.send_json({
                    "error": str(e),
                    "correlation_id": message.get("correlation_id")
                })

@app.websocket("/ws/{project_name}")
async def websocket_endpoint(websocket: WebSocket, project_name: str):
    await websocket.accept()
    devika = AsyncDevika()
    try:
        while True:
            message = await websocket.receive_json()
            await devika.handle_message(websocket, message)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
```

## Implementation Plan

### Phase 1: Logging Infrastructure
1. Add structured logging
2. Implement log rotation
3. Add correlation IDs
4. Remove print statements

### Phase 2: State Management
1. Set up Redis/RabbitMQ
2. Implement state manager
3. Add message queue patterns
4. Migrate state access

### Phase 3: Thread Safety
1. Add proper locks
2. Implement async executor
3. Add request correlation
4. Fix race conditions

### Phase 4: Asyncio Migration
1. Migrate to FastAPI
2. Implement async patterns
3. Add connection pooling
4. Clean up error handling

## Impact Analysis

### Performance Benefits
- Reduced memory usage
- Better resource utilization
- Improved concurrency
- Lower latency

### Reliability Improvements
- Fewer race conditions
- Better error handling
- Consistent state management
- Improved debugging

### Maintainability Enhancements
- Cleaner code structure
- Better logging
- Easier debugging
- Simplified state management

## Next Steps

1. Create detailed implementation tickets for each phase
2. Set up development environment with new dependencies
3. Create proof-of-concept implementations
4. Plan gradual migration strategy
