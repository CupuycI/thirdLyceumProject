import sqlalchemy
import datetime

from .db_session import SqlAlchemyBase


class Coalition(SqlAlchemyBase):
    __tablename__ = "coalitions"

    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    members = sqlalchemy.Column(sqlalchemy.String, default=None)
    army = sqlalchemy.Column(sqlalchemy.Integer)
    enemies = sqlalchemy.Column(sqlalchemy.String, default=None)
    modified_data = sqlalchemy.Column(sqlalchemy.String, default=datetime.datetime.now)
