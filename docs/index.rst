.. SQLAlchemy Fixture Factory documentation master file

.. index:: Introduction

Introduction
============

Automatic testing of services which involves database access gets quite quickly cumbersome, especially
the preparation of the database. By the time the system matures, complex scenarios need to be covered. A predefined
test scenario helps with the setup, but is not very flexible. On the search for a solution quite quickly
`factory_girl <https://github.com/thoughtbot/factory_girl>`_ appeared on the radar. But nothing similar could be found
for Python.

With this library quick, obvious and easily understandable test scenarios can be created which are flexible, easily to
maintain and to extend.

Word of truth must be spoken: *it only works with SQLAlchemy's ORM mapper!* (`see doc <http://docs.sqlalchemy.org/en/latest/>`_)

.. index:: Installation

Installation
------------
The library is hosted on `PyPI <https://pypi.python.org/pypi/SQLAlchemy-Fixture-Factory/>`_ and can be installed via

.. code-block:: bash

    pip install sqlalchemy-fixture-factory

.. Features
.. --------

Quick Example
-------------

Assume following ORM definitions:

.. code-block:: python

    class Account(Base):
        __tablename__ = 'account'

        id = Column(Integer, primary_key=True)
        name = Column('name', Unicode)

    class Person(Base):
        __tablename__ = 'person'

        id = Column(Integer, primary_key=True)
        first_name = Column('first_name', Unicode)
        account_id = Column(Integer, ForeignKey('account.id'))
        account = relationship(Account)

definition of a fixture for a person. It includes an account:

.. code-block:: python

    class ArnoldAccount(BaseFix):
        MODEL = Account
        name = "arney"

    class ArnoldPerson(BaseFix):
        MODEL = Person
        name = "Arnold"
        account = sqla_fix_fact.subFactoryModel(ArnoldAccount)

now the usage (I assume SQLAlchemy is properly initialized):

.. code-block:: python

    # initialize the fixture factory
    fix_fact = SqlaFixFact(db_session)

    # create a fxiture
    arnold_fix = ArnoldPerson(fix_fact).create()

    # or more of them
    while i in xrange(3):
        arnold_fix = ArnoldPerson(fix_fact).create()

    # test
    assert 4 == db_session.query(Person).count()


Table of Contents
-----------------

.. toctree::
    :maxdepth: 2

    instantiation
    referencing
    substitution
    api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
