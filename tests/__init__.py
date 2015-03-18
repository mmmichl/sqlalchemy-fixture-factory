# -*- coding: utf-8 -*-

"""

"""

from __future__ import absolute_import, print_function, unicode_literals, division
from sqlalchemy import Table, Column, Integer, ForeignKey, Unicode, create_engine
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_fixture_factory.sqla_fix_fact import SqlaFixFact


class TestCase(object):
    Base = None

    # tables
    Role = None
    Account = None
    Person = None

    def setup_method(self, method):
        self.Base = declarative_base()

        self.engine = create_engine('sqlite:///')
        # self.engine.echo = True
        self.create_models()

        sqlalchemy.orm.configure_mappers()
        self.connection = self.engine.connect()

        self.create_tables()

        SessionPool = sessionmaker(bind=self.engine)
        self.db_session = SessionPool()

        # initialize SQLAlchemy Fixture Factory with the DB session
        self.fix_fact = SqlaFixFact(self.db_session)


    def create_tables(self):
        self.Base.metadata.create_all(self.connection)

    def drop_tables(self):
        self.Base.metadata.drop_all(self.connection)

    def teardown_method(self, method):
        self.db_session.close_all()
        self.db_session.expunge_all()
        self.drop_tables()
        self.engine.dispose()
        self.connection.close()

    def create_models(self):
        # association table, only required once
        account_role = Table('account_role', self.Base.metadata,
                             Column('id_account', Integer, ForeignKey('account.id')),
                             Column('id_role', Integer, ForeignKey('role.id')))

        class Role(self.Base):
            __tablename__ = 'role'

            id = Column(Integer, primary_key=True)
            name = Column(Unicode)

        class Account(self.Base):
            __tablename__ = 'account'

            id = Column(Integer, primary_key=True)
            name = Column('name', Unicode)

            roles = relationship(Role, secondary=account_role)

        class Person(self.Base):
            __tablename__ = 'person'

            id = Column(Integer, primary_key=True)
            first_name = Column('first_name', Unicode)
            account_id = Column(Integer, ForeignKey('account.id'))
            account = relationship(Account)

        self.Role = Role
        self.Account = Account
        self.Person = Person