# -*- coding: utf-8 -*-

"""
Tests for the fixture
"""

from __future__ import absolute_import, print_function, unicode_literals, division
from sqlalchemy_fixture_factory import fix_fact
from sqlalchemy_fixture_factory.fix_fact import BaseFix

from tests import TestCase


class TestFixFact(TestCase):

    def test_basefix_create(self):
        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'

        p = FixPerson(self.fix_fact)

        assert p is not None
        result = p.model()
        test = self.Person(first_name='Franz')

        assert type(result) == type(test)
        assert result.first_name == test.first_name


    def test_basefix_create_w_parameter(self):
        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'

        p = FixPerson(self.fix_fact, first_name = 'Peter')

        assert p is not None
        result = p.model()
        test = self.Person(first_name='Peter')

        assert type(test) == type(result)
        assert test.first_name == result.first_name


    def test_basefix_create_ref(self):
        class FixPersonAccount(BaseFix):
            MODEL = self.Account
            name = 'supercheck'

        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'
            account = fix_fact.subFactoryGet(FixPersonAccount)

        p = FixPerson(self.fix_fact)

        assert p is not None
        result = p.model()
        test = self.Person(first_name='Franz', account=self.Account(name='supercheck'))

        assert type(result) == type(test)
        assert test.first_name == result.first_name
        assert result.account is not None
        assert test.account.name == result.account.name

        p2 = FixPerson(self.fix_fact)

        assert p != p2
        assert p.account == p2.account


    def test_basefix_create_ref_w_parameter(self):
        class FixPersonAccount(BaseFix):
            MODEL = self.Account
            name = 'supercheck'

        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'
            account = fix_fact.subFactoryGet(FixPersonAccount, name='nixcheck')

        p = FixPerson(self.fix_fact, first_name='Peter')

        assert p is not None
        result = p.model()
        test = self.Person(first_name='Peter', account=self.Account(name='nixcheck'))

        assert type(result) == type(test)
        assert test.first_name == result.first_name
        assert result.account is not None
        assert test.account.name == result.account.name

        p2 = FixPerson(self.fix_fact)

        assert p != p2
        assert p.account == p2.account

    def test_basefix_create_copy(self):
        class FixPersonAccount(BaseFix):
            MODEL = self.Account
            name = 'supercheck'

        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'
            account = fix_fact.subFactoryCreate(FixPersonAccount)

        p = FixPerson(self.fix_fact)

        assert p is not None
        result = p.model()
        test = self.Person(first_name='Franz', account=self.Account(name='supercheck'))

        assert type(result) == type(test)
        assert test.first_name == result.first_name
        assert result.account is not None
        assert test.account.name == result.account.name

        p2 = FixPerson(self.fix_fact)

        assert p != p2
        assert p.model().account != p2.model().account

    def test_save_fixture_in_db(self):
        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'

        p = FixPerson(self.fix_fact).create()

        assert p is not None
        # check if primary key is set
        assert p.id is not None

        result = self.db_session.query(self.Person).all()

        assert 1 == len(result)
        assert result[0] == p

        p2 = FixPerson(self.fix_fact).create()

        assert p2 is not None
        # check if primary key is set
        assert p2.id is not None

        result = self.db_session.query(self.Person).all()

        assert 2 == len(result)

    def test_build_fixture_only(self):
        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'

        p = FixPerson(self.fix_fact).get()

        assert p is not None

        result = self.db_session.query(self.Person).all()

        assert 1 == len(result)
        assert result[0] == p

        p2 = FixPerson(self.fix_fact).get()

        assert p2 is not None
        # check if primary key is set
        assert p2.id is not None

        result = self.db_session.query(self.Person).all()

        assert 1 == len(result)


    def test_create_with_reference_list(self):
        class AdminRole(BaseFix):
            MODEL = self.Role
            name = 'admin'

        class FixAccount(BaseFix):
            MODEL = self.Account
            name = 'peter'
            roles = [
                fix_fact.subFactoryGet(AdminRole)
            ]

        a = FixAccount(self.fix_fact).create()

        assert a is not None
        assert a.id is not None

        result = self.db_session.query(self.Account).get(a.id)

        assert 'peter' == result.name
        assert 'admin' == result.roles[0].name

