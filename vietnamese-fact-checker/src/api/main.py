from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.schemas import ClaimRequest, ClaimResponse, HealthResponse
from services.fact_checker import VietnameseFactChecker
from core.system_config import system_config, reload_config
import asyncio

app = FastAPI(
    title="Vietnamese Fact Checker API",
    description="Vietnamese fact-checking system using MiniCheck and web search. Includes configuration API for future Web UI.",
    version="2.0.0"
)

# Config update request model
class ConfigUpdateRequest(BaseModel):
    section: str  # brave_search, translation, minicheck, evidence, logging, performance, response, error_handling
    updates: Dict[str, Any]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize fact checker
fact_checker = VietnameseFactChecker()

@app.post("/check", response_model=ClaimResponse)
async def check_claim(request: ClaimRequest):
    """Check a Vietnamese claim"""
    if not request.claim or len(request.claim.strip()) < 10:
        raise HTTPException(status_code=400, detail="Claim too short (minimum 10 characters)")
    
    try:
        result = await fact_checker.check_claim(request.claim)
        return ClaimResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        method="minicheck_web_search",
        components={
            "web_search": "ready",
            "translator": "ready",
            "minicheck": "ready"
        }
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vietnamese Fact Checker API",
        "version": "2.0.0",
        "endpoints": {
            "check": "/check - Check a Vietnamese claim",
            "health": "/health - Health check",
            "config": "/config - Get all configurations",
            "config/{section}": "/config/{section} - Get specific config section",
            "docs": "/docs - API documentation"
        }
    }

# ==================== CONFIG API ENDPOINTS ====================
# These endpoints are for future Web UI configuration management

@app.get("/config")
async def get_all_config():
    """Get all system configurations (for Web UI)"""
    return {
        "status": "success",
        "config": system_config.to_dict(),
        "sections": [
            "brave_search",
            "translation", 
            "minicheck",
            "evidence",
            "logging",
            "performance",
            "api",
            "response",
            "error_handling"
        ]
    }

@app.get("/config/summary")
async def get_config_summary():
    """Get a summary of all service configurations"""
    from services.brave_search_client import brave_search_client
    from services.minicheck_client import minicheck_client
    from services.translation_client import translation_client
    
    return {
        "status": "success",
        "services": {
            "brave_search": brave_search_client.get_config_summary(),
            "minicheck": minicheck_client.get_config_summary(),
            "translation": translation_client.get_config_summary()
        }
    }

@app.get("/config/{section}")
async def get_config_section(section: str):
    """Get specific configuration section"""
    config_dict = system_config.to_dict()
    
    if section not in config_dict:
        raise HTTPException(
            status_code=404, 
            detail=f"Config section '{section}' not found. Available: {list(config_dict.keys())}"
        )
    
    return {
        "status": "success",
        "section": section,
        "config": config_dict[section]
    }

@app.post("/config/{section}")
async def update_config_section(section: str, request: ConfigUpdateRequest):
    """
    Update specific configuration section (for Web UI)
    Note: Changes are temporary and reset on server restart.
    For persistent changes, update the .env file or config JSON.
    """
    config_dict = system_config.to_dict()
    
    if section not in config_dict:
        raise HTTPException(
            status_code=404,
            detail=f"Config section '{section}' not found"
        )
    
    # Get the config object for the section
    section_map = {
        "brave_search": system_config.brave_search,
        "translation": system_config.translation,
        "minicheck": system_config.minicheck,
        "evidence": system_config.evidence,
        "logging": system_config.logging,
        "performance": system_config.performance,
        "api": system_config.api,
        "response": system_config.response,
        "error_handling": system_config.error_handling,
    }
    
    config_obj = section_map.get(section)
    if not config_obj:
        raise HTTPException(status_code=404, detail=f"Section '{section}' not found")
    
    # Apply updates
    updated_fields = []
    for key, value in request.updates.items():
        if hasattr(config_obj, key):
            setattr(config_obj, key, value)
            updated_fields.append(key)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid config key '{key}' for section '{section}'"
            )
    
    return {
        "status": "success",
        "message": f"Updated {len(updated_fields)} config(s) in '{section}'",
        "updated_fields": updated_fields,
        "new_config": config_obj.model_dump() if hasattr(config_obj, 'model_dump') else vars(config_obj)
    }

@app.post("/config/reload")
async def reload_all_config():
    """Reload all configurations from environment"""
    try:
        reload_config()
        return {
            "status": "success",
            "message": "Configuration reloaded from environment"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload config: {str(e)}")

@app.post("/config/save")
async def save_config_to_file():
    """Save current configuration to JSON file"""
    try:
        filepath = "config_backup.json"
        system_config.save_to_file(filepath)
        return {
            "status": "success",
            "message": f"Configuration saved to {filepath}",
            "filepath": filepath
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
