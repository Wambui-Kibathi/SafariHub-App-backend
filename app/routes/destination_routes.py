from flask import Blueprint, request, jsonify
from app.models.destination import Destination
from app.schemas.destination_schema import DestinationSchema
from app.extensions import db
from app.utils.role_required import role_required

destination_bp = Blueprint("destination_bp", __name__)
destination_schema = DestinationSchema()
destinations_schema = DestinationSchema(many=True)

# GET all destinations (public)
@destination_bp.route("/", methods=["GET"])
def get_destinations():
    destinations = Destination.query.all()
    return destinations_schema.dump(destinations), 200

# GET single destination by id
@destination_bp.route("/<int:id>", methods=["GET"])
def get_destination(id):
    destination = db.session.get(Destination, id)
    if not destination:
        return {"message": "Destination not found"}, 404
    return destination_schema.dump(destination), 200

# ADMIN CRUD routes
@destination_bp.route("/", methods=["POST"])
@role_required("admin")
def create_destination():
    data = request.get_json()
    destination = Destination(
        name=data["name"],
        country=data["country"],
        description=data["description"],
        image_url=data["image_url"],
        price=data["price"]
    )
    db.session.add(destination)
    db.session.commit()
    return destination_schema.dump(destination), 201

@destination_bp.route("/<int:id>", methods=["PATCH"])
@role_required("admin")
def update_destination(id):
    destination = db.session.get(Destination, id)
    if not destination:
        return {"message": "Destination not found"}, 404
    data = request.get_json()
    for field in ["name", "country", "description", "image_url", "price"]:
        if field in data:
            setattr(destination, field, data[field])
    db.session.commit()
    return destination_schema.dump(destination), 200

@destination_bp.route("/<int:id>", methods=["DELETE"])
@role_required("admin")
def delete_destination(id):
    destination = db.session.get(Destination, id)
    if not destination:
        return {"message": "Destination not found"}, 404
    db.session.delete(destination)
    db.session.commit()
    return {"message": "Destination deleted successfully"}, 200
