# -*- coding: utf-8 -*-

"""
Executable file with the samples from README.rst
"""

from __future__ import absolute_import, print_function, unicode_literals, division

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Table, create_engine, Column, Integer, ForeignKey, Unicode
from sqlalchemy_fixture_factory import sqla_fix_fact
from sqlalchemy_fixture_factory.sqla_fix_fact import SqlaFixFact, BaseFix


# Set up SQLAlchemy
Base = declarative_base()

engine = create_engine('sqlite:///', echo=False)
connection = engine.connect()
SessionPool = sessionmaker(bind=engine)
db_session = SessionPool()


# association table
account_role = Table('account_role', Base.metadata,
                     Column('id_account', Integer, ForeignKey('account.id')),
                     Column('id_role', Integer, ForeignKey('role.id')))

class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)

class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
    name = Column('name', Unicode)

    roles = relationship(Role, secondary=account_role)

class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    first_name = Column('first_name', Unicode)
    account_id = Column(Integer, ForeignKey('account.id'))
    account = relationship(Account)

# create the tables
Base.metadata.create_all(connection)


## Initialize SQLAlchemy-Fixture-Factory:

# SQLAlechemy DB session generated from SessionPool
fix_fact = SqlaFixFact(db_session)

## Define a simple person fixture:

class FranzPerson(BaseFix):
    MODEL = Person
    first_name = 'Franz'

## The property `MODEL` needs to be set with the desired ORM class. Then simply set the fields as desired.
## In this example the `first_name` with `Franz`.

## Use this fixture:

franz_fix = FranzPerson(fix_fact).create()

print ("Person count:", db_session.query(Person).count())
# output: 1

# create more instances of the same fixture
franz_fix_2 = FranzPerson(fix_fact).create()
franz_fix_3 = FranzPerson(fix_fact).create()

print ("Person count:", db_session.query(Person).count())
# output: 3

print ("Instances and id's are different:",
       franz_fix != franz_fix_2 != franz_fix_3,
       franz_fix.id != franz_fix_2.id != franz_fix_3.id)
# output: True True

# alter fields at instantiation time
franz_fix_alt_name = FranzPerson(fix_fact, first_name='Sepp').create()

print ("Person count with first_name 'Sepp':",
       db_session.query(Person).filter(Person.first_name == "Sepp").count())
# output: 1


## Alternatively, retrieve the model without instantiating the fixture, but create the dependencies with `.model()`

# retrieve only the (altered) model
franz_model_alt_name = FranzPerson(fix_fact, first_name='Hugo').model()

print ("Person count with first_name 'Hugo':",
       db_session.query(Person).filter(Person.first_name == "Hugo").count())
# output: 0

db_session.add(franz_model_alt_name)

print ("Person count with first_name 'Hugo':",
       db_session.query(Person).filter(Person.first_name == "Hugo").count())
# output: 1


## If you need the same instance in different fixtures, use `.get()`

# clean up the DB
Base.metadata.drop_all(connection)
Base.metadata.create_all(connection)

# first call creates the fixture and caches the reference
franz_get = FranzPerson(fix_fact).get()
franz_get_2 = FranzPerson(fix_fact).get()
franz_get_3 = FranzPerson(fix_fact).get()

print ("Person count:", db_session.query(Person).count())
# output: 1

print ("Instances and id's are the same:",
       franz_get == franz_get_2 == franz_get_3,
       franz_get.id == franz_get_2.id == franz_get_3.id)
# output: True True

## Build a more complex scenario

class ViewRole(BaseFix):
    MODEL = Role
    name = "View Role"

class EditRole(BaseFix):
    MODEL = Role
    name = "Edit Role"

class ArnoldAccount(BaseFix):
    MODEL = Account
    name = "arney"
    # Reference to other fixtures
    roles = [sqla_fix_fact.subFactoryGet(ViewRole), sqla_fix_fact.subFactoryGet(EditRole)]

class ArnoldPerson(BaseFix):
    MODEL = Person
    name = "Arnold"
    account = sqla_fix_fact.subFactoryModel(ArnoldAccount)


# now create the factory in one line
arnold_fix = ArnoldPerson(fix_fact).create()

# get it from the DB
arnold_db = db_session.query(Person).get(arnold_fix.id)

print ("Account name of Arnold:", arnold_db.account.name)
# output: arney
print ("Roles of Arnold:", [r.name for r in arnold_db.account.roles])
# output: ['View Role', 'Edit Role']

