from typing import Optional
from app import db
import sqlalchemy as sqla
from sqlalchemy import func, Table 
import sqlalchemy.orm as sqlo
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

combat_player_group = Table('combat_player_group', db.Model.metadata,
    sqla.Column('combat_id', sqla.String(9), sqla.ForeignKey('combat.id'), primary_key=True),
    sqla.Column('player_group_id', sqla.String(9), sqla.ForeignKey('player_group.id'), primary_key=True)
)

combat_monster_group = Table('combat_monster_group', db.Model.metadata,
    sqla.Column('combat_id', sqla.String(9), sqla.ForeignKey('combat.id'), primary_key=True),
    sqla.Column('monster_group_id', sqla.String(9), sqla.ForeignKey('monster_group.id'), primary_key=True)
)

class MonsterGroup(db.Model):
    id : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(9), primary_key=True)
    challenge_rating : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float())
    quantity : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer())
    power : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer())

    user_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer, sqla.ForeignKey('user.id'))
    user = sqlo.relationship('User', back_populates='monster_groups')
    #combat : sqlo.Mapped['Combat'] = sqlo.relationship('Combat', back_populates='monster_groups')
    combats : sqlo.Mapped['Combat'] = sqlo.relationship('Combat', secondary=combat_monster_group, back_populates='monster_groups')

    CR_POWER_MAPPING = {
        0.125: 5, 0.25: 10, 0.5: 16, 1: 22, 2: 28, 3: 37, 4: 48, 5: 60,
        6: 65, 7: 70, 8: 85, 9: 85, 10: 95, 11: 105, 12: 115, 13: 120,
        14: 125, 15: 130, 16: 140, 17: 150, 18: 160, 19: 165, 20: 180,
        21: 200, 22: 225, 23: 250, 24: 275, 25: 300, 26: 325, 27: 350,
        28: 375, 29: 400, 30: 425
    }

    def __init__(self, challenge_rating, quantity, user_id):
        self.challenge_rating = challenge_rating
        self.quantity = quantity
        self.user_id = user_id 
        self.set_power()
        

    def set_power(self):
        self.power = self.CR_POWER_MAPPING.get(self.challenge_rating, 0)

    def get_total_group_power(self):
        return self.quantity * self.power

    @classmethod
    def calculate_total_power(cls):
        return db.session.query(func.sum(cls.quantity * cls.power)).scalar() or 0
    
class User(db.Model, UserMixin):
    id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer, primary_key=True)
    username : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(40), unique=True)
    password_hash : sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(256))

    player_groups : sqlo.Mapped[str] = sqlo.relationship('PlayerGroup', back_populates='user', cascade='all, delete-orphan')
    monster_groups : sqlo.Mapped[str] = sqlo.relationship('MonsterGroup', back_populates='user', cascade='all, delete-orphan')
    combats : sqlo.Mapped[str] = sqlo.relationship('Combat', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def check_password(self, password):
        return check_password_hash(pwhash=self.password_hash, password=password)

class PlayerGroup(db.Model):
    id : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(9), primary_key=True)
    level : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer())
    quantity : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer())
    power : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer())

    user_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer, sqla.ForeignKey('user.id'))
    user = sqlo.relationship('User', back_populates='player_groups')
    #combat : sqlo.Mapped['Combat'] = sqlo.relationship('Combat', back_populates='player_groups')
    combats : sqlo.Mapped['Combat'] = sqlo.relationship('Combat', secondary=combat_player_group, back_populates='player_groups')

    Level_Power_mapping = {
            1:11, 2:14, 3:18, 4:23, 5:32,
            6:35, 7:41, 8:44, 9:49, 10:53, 11:62, 12:68, 
            13:71, 14:74, 15:82, 16:84, 17:103, 18:119, 19:131, 20:141 
        }

    def __init__(self, level, quantity, user_id):
        self.level = level
        self.quantity = quantity
        self.user_id = user_id
        self.set_power()

    def set_power(self):
        self.power = self.Level_Power_mapping.get(self.level, 0)
    
    def get_total_group_power(self):
        return self.quantity * self.power
    
    @classmethod
    def calculate_total_power(cls):
        return db.session.query(func.sum(cls.quantity * cls.power)).scalar() or 0


class Combat(db.Model):
    id : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(9), primary_key=True)
    multiplier : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float())
    cost : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer())

    user_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer, sqla.ForeignKey('user.id'))
    user = sqlo.relationship('User', back_populates='combats')
    
    player_groups : sqlo.Mapped[list['PlayerGroup']] = sqlo.relationship(
        'PlayerGroup', 
        secondary=combat_player_group, 
        back_populates='combats',
        collection_class=list,
    )
    monster_groups : sqlo.Mapped[list['MonsterGroup']] = sqlo.relationship(
        'MonsterGroup', 
        secondary=combat_monster_group, 
        back_populates='combats',
        collection_class=list,
    )

    def __init__(self, id, user_id, multiplier=0.0, cost=0):
        self.id = id
        self.multiplier = multiplier
        self.cost = cost
        self.user_id = user_id
        self.player_groups = []
        self.monster_groups = []

    def calc_multiplier(self):
        total_player_power = sum(group.get_total_group_power() for group in self.player_groups)
        total_monster_power = sum(group.get_total_group_power() for group in self.monster_groups)
        if total_player_power == 0:
            self.multiplier = 0
        else:
            self.multiplier = (total_monster_power ** 2) / (total_player_power ** 2)

    def set_cost(self):
        if self.multiplier:
            if self.multiplier < .40:
                self.cost = 2
            elif self.multiplier < .60:
                self.cost = 4
            elif self.multiplier < .75:
                self.cost = 6
            elif self.multiplier < .90:
                self.cost = 8
            elif self.multiplier < 1.01:
                self.cost = 10

    @classmethod
    def total_cost(cls):
        return db.session.query(func.sum(cls.cost)).scalar() or 0


