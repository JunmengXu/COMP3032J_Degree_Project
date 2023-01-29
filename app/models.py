from datetime import datetime
from sqlalchemy import inspect
from app import db


class Property(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tradeTime = db.Column(db.String(4), default='2021')
	followers = db.Column(db.Integer)
	price = db.Column(db.Integer)
	square = db.Column(db.Integer)
	bedroom = db.Column(db.Integer)
	livingroom = db.Column(db.Integer)
	kitchen = db.Column(db.Integer)
	bathroom = db.Column(db.Integer)
	buildingType = db.Column(db.Integer)
	constructionTime = db.Column(db.String(4))
	renovationCondition = db.Column(db.Integer)
	buildingStructure = db.Column(db.Integer)
	ladderRatio	= db.Column(db.Float, default=0.5)
	elevator = db.Column(db.Integer)
	fiveYearsProperty = db.Column(db.Integer)
	subway = db.Column(db.Integer)
	district = db.Column(db.String(512))
	communityAverage = db.Column(db.Integer)
	business = db.Column(db.String(512), default='Beijing')
	town = db.Column(db.String(512))
	floorType = db.Column(db.Integer)
	floorHeight = db.Column(db.Integer)
	lng = db.Column(db.String(50))
	lat = db.Column(db.String(50))
	community = db.Column(db.String(500))
	status = db.Column(db.String(50))
	agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Agent(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	name = db.Column(db.String(64), index=True, unique=True)
	phone_number = db.Column(db.String(20), index=True,unique=True)
	email = db.Column(db.String(50), index=True, unique=True)
	avatar = db.Column(db.String(3), index=True, unique=True)

	properties = db.relationship("Property", backref="agent",lazy='dynamic')

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	properties = db.relationship("Property", backref="owner",lazy='dynamic')

class Community(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	construction_time = db.Column(db.String(4))
	district = db.Column(db.String(50))
	lng = db.Column(db.String(50))
	lat = db.Column(db.String(50))
	name = db.Column(db.String(50))
	price = db.Column(db.Integer)
	town = db.Column(db.String(50))
	type = db.Column(db.String(50))

class FavoriteProperty(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer)
	property_id = db.Column(db.Integer)

