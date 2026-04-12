import sqlalchemy
import datetime

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_data = sqlalchemy.Column(sqlalchemy.String, default=datetime.datetime.now)
    coalition = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    economy_level = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    technology_level = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    researchers_level = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    forts = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    army = sqlalchemy.Column(sqlalchemy.Integer, default=10)
    territory_sectors = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    money = sqlalchemy.Column(sqlalchemy.Integer, default=100)

    last_update = sqlalchemy.Column(sqlalchemy.String, default=datetime.datetime.now)
