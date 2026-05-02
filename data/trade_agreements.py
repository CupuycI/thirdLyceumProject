import sqlalchemy
import datetime

from .db_session import SqlAlchemyBase


class TradeAgreement(SqlAlchemyBase):
    __tablename__ = "trade_agreements"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    profit = sqlalchemy.Column(sqlalchemy.Integer)
    second_user = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    hours = sqlalchemy.Column(sqlalchemy.Integer, default=5)
    date = sqlalchemy.Column(sqlalchemy.String, default=datetime.datetime.now)