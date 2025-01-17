from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserAllowedTrucks(db.Model):
    __tablename__ = "vwUserAllowedTrucks"  # Nombre de la vista en la base de datos
    __table_args__ = {"schema": "exa"}  # Esquema en el que se encuentra la vista

    userId = db.Column(db.Integer, primary_key=True)  # Identificador único del usuario
    userEmail = db.Column(db.Text, nullable=False)  # Cambiado a Text
    allowedSubdivisionId = db.Column(db.Integer, nullable=False)  # ID de la subdivisión permitida
    truckId = db.Column(db.Integer, nullable=False)  # ID del camión
    truckPlate = db.Column(db.Text, nullable=False)  # Cambiado a Text
    subdivisionName = db.Column(db.Text, nullable=False)  # Cambiado a Text
    brand = db.Column(db.Text, nullable=True)  # Cambiado a Text
    model = db.Column(db.Text, nullable=True)  # Cambiado a Text