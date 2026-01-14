"""
Research Agent Backend - FastAPI Server
Provides API endpoints for the research agent with logging and analytics
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import asyncio
from pathlib import Path

# Import the research agent
from agent import create_agent
from langchain_core.messages import HumanMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Filter out uvicorn reload messages
class NoReloadFilter(logging.Filter):
    def filter(self, record):
        # Filter out uvicorn reload messages
        if 'change detected' in record.getMessage().lower():
            return False
        if 'reloading' in record.getMessage().lower():
            return False
        if 'watchfiles' in record.getMessage().lower():
            return False
        return True

# Apply filter to all handlers
logger = logging.getLogger(__name__)
for handler in logging.getLogger().handlers:
    handler.addFilter(NoReloadFilter())

# Also filter uvicorn logger specifically
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.addFilter(NoReloadFilter())

# Filter watchfiles logger
watchfiles_logger = logging.getLogger("watchfiles")
watchfiles_logger.setLevel(logging.WARNING)

# Request/Response Models
class ResearchRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ResearchResponse(BaseModel):
    success: bool
    answer: str
    session_id: str
    tools_used: List[str]
    processing_time: float
    timestamp: datetime
    token_estimate: Optional[int] = None

class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    session_id: Optional[str] = None

class AnalyticsResponse(BaseModel):
    total_queries: int
    tools_usage: Dict[str, int]
    average_processing_time: float
    recent_queries: List[Dict]
    log_file_size: int
    uptime: str

# Global variables for tracking
query_analytics = {
    "total_queries": 0,
    "tools_usage": {},
    "processing_times": [],
    "recent_queries": [],
    "start_time": datetime.now()
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Research Agent API starting up...")
    
    # Initialize agent
    try:
        global research_agent
        research_agent = create_agent()
        logger.info("✅ Research Agent initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        raise
    
    yield
    
    logger.info("🛑 Research Agent API shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Research Agent API",
    description="Intelligent Research Assistant with Multi-Tool Integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
research_agent = None

def extract_tools_from_messages(messages) -> List[str]:
    """Extract tool names from agent messages"""
    tools_used = []
    for message in messages:
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.get('name', 'unknown_tool')
                if tool_name not in tools_used:
                    tools_used.append(tool_name)
    return tools_used

def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)"""
    return len(text) // 4

def update_analytics(query: str, tools_used: List[str], processing_time: float, session_id: str):
    """Update global analytics"""
    global query_analytics
    
    query_analytics["total_queries"] += 1
    query_analytics["processing_times"].append(processing_time)
    
    # Update tools usage
    for tool in tools_used:
        query_analytics["tools_usage"][tool] = query_analytics["tools_usage"].get(tool, 0) + 1
    
    # Add to recent queries (keep last 10)
    query_analytics["recent_queries"].insert(0, {
        "query": query[:100] + "..." if len(query) > 100 else query,
        "tools_used": tools_used,
        "processing_time": processing_time,
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id
    })
    
    # Keep only last 10 queries
    if len(query_analytics["recent_queries"]) > 10:
        query_analytics["recent_queries"] = query_analytics["recent_queries"][:10]

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "agent_ready": research_agent is not None,
        "version": "1.0.0"
    }

@app.post("/api/research", response_model=ResearchResponse)
async def research_query(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Main research endpoint"""
    if not research_agent:
        raise HTTPException(status_code=500, detail="Research agent not initialized")
    
    session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    start_time = datetime.now()
    
    logger.info(f"=" * 60)
    logger.info(f"NEW RESEARCH QUERY | SESSION: {session_id}")
    logger.info(f"QUERY: {request.query}")
    logger.info(f"=" * 60)
    
    try:
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=request.query)]
        }
        
        # Run the agent
        result = research_agent.invoke(initial_state)
        
        # Extract final answer
        final_message = result["messages"][-1]
        
        if hasattr(final_message, 'content'):
            if isinstance(final_message.content, list):
                answer = ""
                for item in final_message.content:
                    if isinstance(item, dict) and 'text' in item:
                        answer += item['text']
                    elif isinstance(item, str):
                        answer += item
            else:
                answer = final_message.content
        else:
            answer = "No response generated"
        
        # Extract tools used
        tools_used = extract_tools_from_messages(result["messages"])
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Estimate tokens
        total_text = request.query + answer + str(result["messages"])
        token_estimate = estimate_tokens(total_text)
        
        logger.info(f"RESEARCH COMPLETED | SESSION: {session_id}")
        logger.info(f"TOOLS USED: {', '.join(tools_used)}")
        logger.info(f"PROCESSING TIME: {processing_time:.2f}s")
        logger.info(f"TOKEN ESTIMATE: {token_estimate}")
        logger.info(f"ANSWER LENGTH: {len(answer)} chars")
        logger.info(f"=" * 60)
        
        # Update analytics in background
        background_tasks.add_task(
            update_analytics, 
            request.query, 
            tools_used, 
            processing_time, 
            session_id
        )
        
        return ResearchResponse(
            success=True,
            answer=answer,
            session_id=session_id,
            tools_used=tools_used,
            processing_time=processing_time,
            timestamp=datetime.now(),
            token_estimate=token_estimate
        )
        
    except Exception as e:
        logger.error(f"RESEARCH FAILED | SESSION: {session_id} | ERROR: {str(e)}")
        logger.info(f"=" * 60)
        
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(e)}"
        )

@app.get("/api/logs")
async def get_logs(lines: int = 100):
    """Get recent log entries"""
    log_file = Path("agent.log")
    
    if not log_file.exists():
        return {"logs": [], "total_lines": 0}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        # Get last N lines
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        # Parse log entries
        logs = []
        for line in recent_lines:
            line = line.strip()
            if line:
                # Try to parse timestamp and level
                parts = line.split(' - ', 2)
                if len(parts) >= 3:
                    timestamp = parts[0]
                    level_and_logger = parts[1]
                    message = parts[2]
                    
                    # Extract level
                    level = "INFO"
                    if " - " in level_and_logger:
                        level = level_and_logger.split(" - ")[-1]
                    
                    logs.append({
                        "timestamp": timestamp,
                        "level": level,
                        "message": message
                    })
                else:
                    # Fallback for malformed lines
                    logs.append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": line
                    })
        
        return {
            "logs": logs,
            "total_lines": len(all_lines),
            "requested_lines": lines,
            "returned_lines": len(logs)
        }
        
    except Exception as e:
        logger.error(f"Failed to read logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")

@app.get("/api/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """Get system analytics and statistics"""
    global query_analytics
    
    # Calculate average processing time
    avg_time = 0
    if query_analytics["processing_times"]:
        avg_time = sum(query_analytics["processing_times"]) / len(query_analytics["processing_times"])
    
    # Calculate uptime
    uptime_delta = datetime.now() - query_analytics["start_time"]
    uptime_str = str(uptime_delta).split('.')[0]  # Remove microseconds
    
    # Get log file size
    log_file = Path("agent.log")
    log_size = log_file.stat().st_size if log_file.exists() else 0
    
    return AnalyticsResponse(
        total_queries=query_analytics["total_queries"],
        tools_usage=query_analytics["tools_usage"],
        average_processing_time=avg_time,
        recent_queries=query_analytics["recent_queries"],
        log_file_size=log_size,
        uptime=uptime_str
    )

@app.get("/api/download-logs")
async def download_logs():
    """Download the complete log file"""
    log_file = Path("agent.log")
    
    if not log_file.exists():
        raise HTTPException(status_code=404, detail="Log file not found")
    
    return FileResponse(
        path=str(log_file),
        filename=f"research_agent_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        media_type='text/plain'
    )

@app.delete("/api/clear-logs")
async def clear_logs():
    """Clear the log file (admin function)"""
    log_file = Path("agent.log")
    
    try:
        if log_file.exists():
            # Backup current logs
            backup_name = f"agent_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            backup_path = log_file.parent / backup_name
            
            # Copy to backup
            import shutil
            shutil.copy2(log_file, backup_path)
            
            # Clear the main log file
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"# Log cleared at {datetime.now()}\n")
            
            logger.info(f"Log file cleared. Backup saved as: {backup_name}")
            
            return {
                "success": True,
                "message": "Logs cleared successfully",
                "backup_file": backup_name
            }
        else:
            return {
                "success": True,
                "message": "No log file to clear"
            }
            
    except Exception as e:
        logger.error(f"Failed to clear logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear logs: {str(e)}")

@app.get("/")
async def root():
    """Redirect to API documentation"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    
    # Additional logging configuration to suppress reload messages
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
        access_log=False,  # Disable access logs
        reload_excludes=["*.log", "*.tmp", "__pycache__", "*.pyc"],  # Exclude more file types
        reload_dirs=["./"],  # Only watch current directory
        use_colors=False  # Disable colors in logs
    )