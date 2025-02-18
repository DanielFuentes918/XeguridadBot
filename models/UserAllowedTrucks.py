from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserAllowedTrucks(db.Model):
    __tablename__ = "vwUserAllowedTrucks"  # Nombre de la vista en la base de datos
    __table_args__ = {"schema": "exa"}  # Esquema en el que se encuentra la vista

    userId = db.Column(db.Integer, primary_key=True)  # Parte de la clave primaria
    allowedSubdivisionId = db.Column(db.Integer, primary_key=True)  # Parte de la clave primaria
    truckId = db.Column(db.Integer, primary_key=True)  # Parte de la clave primaria
    userEmail = db.Column(db.String(255), nullable=False)
    truckPlate = db.Column(db.String(255), nullable=False)
    subdivisionName = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=True)
    model = db.Column(db.String(255), nullable=True)