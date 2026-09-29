"""
#############################################################################
### Main backend file
###
### @file main.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module initializes the FastAPI backend locally for development.
It sets up routers, custom logger, rate limiter, and loads environment variables.
"""

#Native imports
import os
from contextlib import asynccontextmanager

#Third-party imports
import uvicorn
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
load_dotenv()

#Other files imports
from src.utils.request_limiter import rate_limit_handler
from src.utils.custom_logger import log_handler
from src.utils.limiter import limiter

#Json files
from src.core_specs.configuration.config_loader import config_loader
from src.core_specs.data.data_loader import data_loader

#Resources imports
from src.resources.cache.redis_client import close_redis

#Endpoints imports
from src.api_endpoints.root_endpoint import router as root_router
from src.api_endpoints.routers.specific_router_group_1.example_router import router as example_router_1
from src.api_endpoints.routers.specific_router_group_2.example_router import router as example_router_2

"""API APP-----------------------------------------------------------"""
#Lifespan event manager (startup and shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    port = config_loader["network"]["server_port"]
    log_handler.info(f"REST API Template server starting on port {port}")
    yield
    close_redis()
    log_handler.info("REST API Template server shutting down")

#Create FastAPI app
app = FastAPI(
    lifespan=lifespan, 
    title=os.getenv("API_TITLE", "REST API Template"),
    version=os.getenv("API_VERSION", "1.0.0"),
    description=os.getenv("API_DESCRIPTION", "A template for building REST APIs with FastAPI")
)

"""VARIOUS-----------------------------------------------------------"""
#Setup rate limiter
app.state.limiter = limiter

#Add global exception handler for rate limits
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

"""Routers-----------------------------------------------------------"""
#Root
app.include_router(root_router)

#Example router (see src/api_endpoints/routers/specific_router_group/example_router.py)
app.include_router(example_router_1)
app.include_router(example_router_2)

"""Start server-----------------------------------------------------------"""
if __name__ == "__main__":
    port = config_loader["network"]["server_port"]
    
    uvicorn.run(
        config_loader["network"]["uvicorn_app_reference"],
        host=config_loader["network"]["host"],
        port=config_loader["network"]["server_port"],
        reload=config_loader["network"]["reload"],
        workers=config_loader["network"]["workers"],
        proxy_headers=config_loader["network"]["proxy_headers"]
    )
    
    log_handler(f"Loaded configuration: \n {config_loader}")
    log_handler(f"Loaded data: \n {data_loader}")
    #available at: http://127.0.0.1:8000/docs
