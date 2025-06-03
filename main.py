#!/usr/bin/env python3
"""
API Monitoring Tool - Entry Point

This script is the entry point for the API Monitoring Tool.
It imports and runs the main function from the api_monitoring package.
"""
import asyncio
from api_monitoring.main import main

if __name__ == "__main__":
    asyncio.run(main())
