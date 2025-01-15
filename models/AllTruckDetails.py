from sqlalchemy import Column, Integer, String, Numeric, Text
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AllTruckDetails(db.Model):
    __tablename__ = "vwAllTruckDetails"
    __table_args__ = {"schema": "exa"}

    assetsid = Column(Integer, primary_key=True)
    moduleid = Column(Integer)
    genericname1 = Column(String(255))
    genericvalue1 = Column(String(255))
    genericname2 = Column(String(255))
    genericvalue2 = Column(String(255))
    genericname3 = Column(String(255))
    genericvalue3 = Column(String(255))
    truck_plate = Column(String(255))
    fuelType = Column(String(255))
    brand = Column(String(255))
    color = Column(String(255))
    model = Column(String(255))
    description = Column(Text)
    subdivision = Column(String(255))
    subdivisionId = Column(Integer)
    year = Column(String(255))
    initial_miles = Column(Numeric(10, 2))
    chassis = Column(String(255))
    engine_no = Column(String(255))
    driverAssigned = Column(String(255))
