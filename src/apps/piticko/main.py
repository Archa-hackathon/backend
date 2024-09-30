from flask import Blueprint, jsonify, request

piticko = Blueprint("bar", __name__)

ORDERS = []  # Will be a database later?


@piticko.route("/create_order", methods=["POST"])
def create_order():
    data = request.get_json()


# ADMIN

@piticko.route("/finish_order", methods=["POST"])
def create_order():
    data = request.get_json()