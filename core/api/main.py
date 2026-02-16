"""
ARCHON X API Server
FastAPI backend for agent coordination and communication
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.pauli import PauliAgent
from agents.synthia import SynthiaAgent

# Initialize FastAPI app
app = FastAPI(
    title="ARCHON X API",
    version="2.6.0",
    description="Dual-Crew Agentic Operating System API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core agents
pauli = PauliAgent()
synthia = SynthiaAgent()


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


# Request models
class AnalyzeRequest(BaseModel):
    data: List[Any]


class SynthesizeRequest(BaseModel):
    inputs: List[str]
    style: str = "informative"


class TaskRequest(BaseModel):
    task: str
    agent: Optional[str] = "auto"


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "ARCHON X API",
        "version": "2.6.0",
        "status": "operational",
        "agents": {
            "pauli": pauli.get_status(),
            "synthia": synthia.get_status()
        },
        "endpoints": {
            "agents": "/agents/status",
            "pauli_analyze": "/agents/pauli/analyze",
            "synthia_synthesize": "/agents/synthia/synthesize",
            "websocket": "/ws"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_online": 2
    }


@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    return {
        "pauli": pauli.get_status(),
        "synthia": synthia.get_status(),
        "total_agents": 2,
        "active_agents": 2
    }


@app.get("/agents/{agent_id}")
async def get_agent_status(agent_id: str):
    """Get status of a specific agent"""
    agents = {
        "pauli": pauli,
        "synthia": synthia
    }
    
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return agents[agent_id].get_status()


@app.post("/agents/pauli/analyze")
async def pauli_analyze(request: AnalyzeRequest):
    """Have Pauli analyze data"""
    result = pauli.analyze_data(request.data)
    
    # Broadcast update to WebSocket clients
    await manager.broadcast({
        "type": "agent_update",
        "agent": "pauli",
        "action": "analyze_complete",
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return result


@app.post("/agents/pauli/diagnostics")
async def pauli_diagnostics():
    """Have Pauli run system diagnostics"""
    result = pauli.run_diagnostics()
    
    await manager.broadcast({
        "type": "agent_update",
        "agent": "pauli",
        "action": "diagnostics_complete",
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return result


@app.post("/agents/synthia/synthesize")
async def synthia_synthesize(request: SynthesizeRequest):
    """Have Synthia synthesize content"""
    result = synthia.synthesize_content(
        inputs=request.inputs,
        style=request.style
    )
    
    await manager.broadcast({
        "type": "agent_update",
        "agent": "synthia",
        "action": "synthesize_complete",
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return result


@app.post("/agents/synthia/generate")
async def synthia_generate(problem: str):
    """Have Synthia generate creative solution"""
    result = synthia.generate_creative_solution(problem)
    
    await manager.broadcast({
        "type": "agent_update",
        "agent": "synthia",
        "action": "generate_complete",
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return result


@app.post("/task/execute")
async def execute_task(request: TaskRequest):
    """Execute a task using the appropriate agent"""
    task_lower = request.task.lower()
    
    # Determine which agent to use based on task type
    if any(word in task_lower for word in ['analyze', 'data', 'compute', 'verify', 'diagnostic']):
        agent = pauli
        agent_name = "pauli"
        result = pauli.analyze_data([request.task])
    else:
        agent = synthia
        agent_name = "synthia"
        result = synthia.synthesize_content([request.task])
    
    await manager.broadcast({
        "type": "task_executed",
        "agent": agent_name,
        "task": request.task,
        "result": result,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {
        "status": "success",
        "agent_used": agent_name,
        "task": request.task,
        "result": result
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial status
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to ARCHON X API",
            "agents": {
                "pauli": pauli.get_status(),
                "synthia": synthia.get_status()
            }
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message.get("type") == "get_status":
                await websocket.send_json({
                    "type": "status_update",
                    "agents": {
                        "pauli": pauli.get_status(),
                        "synthia": synthia.get_status()
                    }
                })
            
            elif message.get("type") == "execute_task":
                task = message.get("task", "")
                task_lower = task.lower()
                
                if any(word in task_lower for word in ['analyze', 'data', 'compute']):
                    result = pauli.analyze_data([task])
                    agent = "pauli"
                else:
                    result = synthia.synthesize_content([task])
                    agent = "synthia"
                
                await websocket.send_json({
                    "type": "task_result",
                    "agent": agent,
                    "task": task,
                    "result": result
                })
            
            else:
                # Broadcast unknown message to all clients
                await manager.broadcast(message)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)