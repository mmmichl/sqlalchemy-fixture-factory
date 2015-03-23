SQLAlchemy-Fixture-Factory
==========================

|Build Status| |Version Status|

A fixture factory for SQLAlchemy ORM mapper to easily build test scenarios for unit or integration testing.
Inspired by Ruby's `factory_girl <https://github.com/thoughtbot/factory_girl>`_

Installation
------------

    pip install sqlalchemy-fixture-factory


Usage
-----

Assume following plain SQLAlchemy ORM models:

.. code-block:: python

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

Initialize SQLAlchemy-Fixture-Factory:

.. code-block:: python

    # SQLAlechemy DB session generated from SessionPool
    fix_fact = SqlaFixFact(db_session)

Define a simple person fixture:

.. code-block:: python
  
    class FranzPerson(BaseFix):
        MODEL = Person
        first_name = 'Franz'

The property ``MODEL`` needs to be set with the desired ORM class. Then simply set the fields as desired. 
In this example the ``first_name`` with ``Franz``.
  
Use this fixture:

.. code-block:: python

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
    
Alternatively, retrieve the model without instantiating the fixture, but create the dependencies with ``.model()``

.. code-block:: python

    # retrieve only the (altered) model
    franz_model_alt_name = FranzPerson(fix_fact, first_name='Hugo').model()
    
    print ("Person count with first_name 'Hugo':",
           db_session.query(Person).filter(Person.first_name == "Hugo").count())
    # output: 0
    
    db_session.add(franz_model_alt_name)
    
    print ("Person count with first_name 'Hugo':",
           db_session.query(Person).filter(Person.first_name == "Hugo").count())
    # output: 1

If you need the same instance in different fixtures, use ``.get()``

.. code-block:: python

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

Build a more complex scenario:

.. code-block:: python

    class ViewRole(BaseFix):
        MODEL = Role
        name = "View Role"
    
    class EditRole(BaseFix):
        MODEL = Role
        name = "Edit Role"
    
    class ArnoldAccount(BaseFix):
        MODEL = Account
        name = "arney"
        # Use get to reference to the roles, as only one instance in the DB is desired
        roles = [sqla_fix_fact.subFactoryGet(ViewRole), sqla_fix_fact.subFactoryGet(EditRole)]
    
    class ArnoldPerson(BaseFix):
        MODEL = Person
        name = "Arnold"
        account = sqla_fix_fact.subFactoryModel(ArnoldAccount)

To instantiate the ``ArnoldPerson`` fixture, following line is sufficient to create the person with all dependencies:

.. code-block:: python

    arnold_fix = ArnoldPerson(fix_fact).create()

Query the DB to see if everything is in place as expected:

.. code-block:: python

    arnold_db = db_session.query(Person).get(arnold_fix.id)
    
    print ("Account name of Arnold:", arnold_db.account.name)
    # output: arney
    print ("Roles of Arnold:", [r.name for r in arnold_db.account.roles])
    # output: ['View Role', 'Edit Role']

You can find this examples ready to play around in ``readme_examples.py``

Resources
---------

- `Issue Tracker <https://github.com/mmmichl/sqlalchemy-fixture-factory/issues>`_
- `Code <https://github.com/mmmichl/sqlalchemy-fixture-factory/>`_


.. |Build Status| image:: https://travis-ci.org/mmmichl/sqlalchemy-fixture-factory.svg?branch=master
   :target: https://travis-ci.org/mmmichl/sqlalchemy-fixture-factory
.. |Version Status| image:: https://pypip.in/version/SQLAlchemy-Fixture-Factory/badge.svg
   :target: https://pypi.python.org/pypi/SQLAlchemy-Fixture-Factory/
   :alt: Latest Version

