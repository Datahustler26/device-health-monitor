"""Seed devices script for testing."""

import argparse
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.device import Base, Device
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Device templates
DEVICE_TYPES = ["barcode_scanner", "printer", "mobile_computer"]
MODELS = {
    "barcode_scanner": ["DS3678", "DS3678-ER", "LS3678"],
    "printer": ["ZD410", "ZD510", "ZD620"],
    "mobile_computer": ["TC70", "TC75", "TC77"]
}
LOCATIONS = [
    "Warehouse Zone A", "Warehouse Zone B", "Warehouse Zone C",
    "Shipping Dept", "Receiving Dept", "Office 1st Floor", "Office 2nd Floor"
]


def create_sample_device(count: int):
    """Create sample devices."""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        created = 0
        for i in range(count):
            device_type = random.choice(DEVICE_TYPES)
            model = random.choice(MODELS[device_type])
            
            device = Device(
                device_id=f"ZBR-{device_type[:2].upper()}-{i+1:05d}",
                device_name=f"{device_type.title()} Unit {i+1}",
                device_type=device_type,
                model=model,
                firmware_version=f"{random.randint(0,1):02d}.{random.randint(0,9):02d}.{random.randint(0,9):02d}",
                serial_number=f"SN{random.randint(100000, 999999)}",
                location=random.choice(LOCATIONS),
                status="ACTIVE"
            )
            
            # Check if already exists
            existing = db.query(Device).filter(Device.device_id == device.device_id).first()
            if not existing:
                db.add(device)
                created += 1
            
            if (i + 1) % 50 == 0:
                logger.info(f"Created {i + 1} devices...")
        
        db.commit()
        logger.info(f"✅ Successfully created {created} devices")
        
    except Exception as e:
        logger.error(f"❌ Error creating devices: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed sample devices")
    parser.add_argument("--count", type=int, default=100, help="Number of devices to create")
    args = parser.parse_args()
    
    create_sample_device(args.count)
