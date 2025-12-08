#!/usr/bin/env python3
"""
Promethium Database Setup Script

This script initializes the database schema and creates default data
for the Promethium framework.

Usage:
    python scripts/setup_db.py [--drop] [--seed]

Options:
    --drop      Drop existing tables before creating new ones
    --seed      Populate database with sample data

Copyright (c) 2025 Olaf Yunus Laitinen Imanov
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from promethium.core.database import engine, Base
from promethium.core.logging import get_logger

logger = get_logger(__name__)


async def create_tables(drop_existing: bool = False) -> None:
    """Create all database tables."""
    async with engine.begin() as conn:
        if drop_existing:
            logger.warning("Dropping existing tables...")
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def seed_database() -> None:
    """Populate database with sample data."""
    logger.info("Seeding database with sample data...")
    # Add seed data logic here
    logger.info("Database seeding completed")


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize Promethium database"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing tables before creating"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed database with sample data"
    )
    
    args = parser.parse_args()
    
    await create_tables(drop_existing=args.drop)
    
    if args.seed:
        await seed_database()
    
    logger.info("Database setup completed")


if __name__ == "__main__":
    asyncio.run(main())
