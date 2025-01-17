from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserAllowedTrucks(db.Model):
    __tablename__ = "vwUserAllowedTrucks"
    __table_args__ = {"schema": "exa"}  # Esquema `exa`

    userId = db.Column(db.Integer, primary_key=True)  # Clave primaria
    userEmail = db.Column(db.String(255), nullable=False)  # Correo del usuario
    allowedSubdivisionId = db.Column(db.Integer, nullable=False)  # Subdivisión permitida
    truckId = db.Column(db.Integer, nullable=False)  # ID del camión
    truckPlate = db.Column(db.String(255), nullable=False)  # Placa del camión
    subdivisionName = db.Column(db.String(255), nullable=False)  # Nombre de la subdivisión
    brand = db.Column(db.String(255), nullable=True)  # Marca del camión
    model = db.Column(db.String(255), nullable=True)  # Modelo del camión