from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class TokenType(db.Model):
    __tablename__ = 'tokenTypes'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    i = db.Column(db.String(255), nullable=False, unique=True)
    b = db.Column(db.String(255), nullable=False)
    color = db.Column(db.String(255))
    description = db.Column(db.String(255))
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)


class LearnSentence(db.Model):
    __tablename__ = 'learnSentences'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    sentence = db.Column(JSONB, nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)





