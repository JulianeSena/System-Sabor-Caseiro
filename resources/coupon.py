from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import UserModel
from models.coupon import CouponModel
from resources.user import admin_required

