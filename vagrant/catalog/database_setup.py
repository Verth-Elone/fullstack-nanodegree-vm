import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
db = 'catalog'
psql_user = 'vagrant'
psql_pass = 'vagrant'
drop_db = True

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Item(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    # path location of image stored as string
    image = Column(String(None))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

if __name__ == '__main__':

    conn_str = 'postgresql+psycopg2://{u}:{p}@localhost/catalog'.format(
        u=psql_user, p=psql_pass)
    engine = create_engine(conn_str)

    Base.metadata.create_all(engine)