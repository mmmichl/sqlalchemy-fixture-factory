# -*- coding: utf-8 -*-

"""
Tests for the fixture
"""

from __future__ import absolute_import, print_function, unicode_literals, division
from sqlalchemy_fixture_factory import sqla_fix_fact
from sqlalchemy_fixture_factory.sqla_fix_fact import BaseFix

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
            account = sqla_fix_fact.subFactoryGet(FixPersonAccount)

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
            account = sqla_fix_fact.subFactoryGet(FixPersonAccount, name='nixcheck')

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
            account = sqla_fix_fact.subFactoryCreate(FixPersonAccount)

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
                sqla_fix_fact.subFactoryGet(AdminRole)
            ]

        a = FixAccount(self.fix_fact).create()

        assert a is not None
        assert a.id is not None

        result = self.db_session.query(self.Account).get(a.id)

        assert 'peter' == result.name
        assert 'admin' == result.roles[0].name

    def test_sub_factory_get_delivers_same_instance_on_multiple_instantiations(self):
        class FixPersonAccount(BaseFix):
            MODEL = self.Account
            name = 'supercheck'

        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'
            account = sqla_fix_fact.subFactoryGet(FixPersonAccount)

        fix_person_1 = FixPerson(self.fix_fact).create()

        assert fix_person_1 is not None
        assert fix_person_1.id is not None
        assert fix_person_1.account is not None

        assert 1 == self.db_session.query(self.Person).count()
        assert 1 == self.db_session.query(self.Account).count()

        fix_person_2 = FixPerson(self.fix_fact).create()
        fix_person_3 = FixPerson(self.fix_fact).create()

        assert 3 == self.db_session.query(self.Person).count()
        assert 1 == self.db_session.query(self.Account).count()

    def test_model_instantiates_but_does_not_save_in_db(self):
        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'

        fix_model = FixPerson(self.fix_fact).model()

        assert fix_model is not None
        assert 0 == self.db_session.query(self.Person).count()

    def test_model_does_creates_sub_factories_create_references_in_db(self):
        class FixPersonAccount(BaseFix):
            MODEL = self.Account
            name = 'supercheck'

        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'
            account = sqla_fix_fact.subFactoryCreate(FixPersonAccount)

        fix_model = FixPerson(self.fix_fact).model()

        assert fix_model is not None
        assert 0 == self.db_session.query(self.Person).count()
        assert 1 == self.db_session.query(self.Account).count()

        account_entry = self.db_session.query(self.Account).all()[0]

        assert account_entry == fix_model.account

    def test_model_does_not_create_sub_factories_model_references_in_db(self):
        class FixPersonAccount(BaseFix):
            MODEL = self.Account
            name = 'supercheck'

        class FixPerson(BaseFix):
            MODEL = self.Person
            first_name = 'Franz'
            account = sqla_fix_fact.subFactoryModel(FixPersonAccount)

        fix_model = FixPerson(self.fix_fact).model()

        assert fix_model is not None
        assert 0 == self.db_session.query(self.Person).count()
        assert 0 == self.db_session.query(self.Account).count()
