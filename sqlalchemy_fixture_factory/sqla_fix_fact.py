# -*- coding: utf-8 -*-

"""
Fixture Factory for SQLAlchemy

Copyright (c) 2005, Michael Pickelbauer
License: MIT (see LICENSE for details)
"""
from sqlalchemy import inspect
from sqlalchemy.ext import hybrid
from sqlalchemy.orm import class_mapper

METHOD_MODEL = 'model'
METHOD_CREATE = 'create'
METHOD_GET = 'get'

class SqlaFixFact():
    db_session = None
    instances = None

    def __init__(self, db_session):
        assert db_session, 'Passed in DB session is None!'
        self.db_session = db_session
        self.instances = {}

    def get_db_session(self):
        return self.db_session

    def merge(self, instance, Fixture, kwargs):
        assert self.db_session, 'DB session not initialized yet'
        inst = self.db_session.merge(instance)
        self.db_session.flush()

        self.instances[(Fixture.__name__, str(kwargs))] = inst

        return inst

    def get(self, Fixture, **kwargs):
        inst = self.instances.get((Fixture.__name__, str(kwargs)))

        if not inst:
            inst = Fixture(self, **kwargs).model()

        return self.merge(inst, Fixture, kwargs)

####
# sub factory things
######
def subFactoryGet(fixture, **kwargs):
    return SubFactory(fixture, METHOD_GET, **kwargs)

def subFactoryCreate(fixture, **kwargs):
    return SubFactory(fixture, METHOD_CREATE, **kwargs)

def subFactoryModel(fixture, **kwargs):
    return SubFactory(fixture, METHOD_MODEL, **kwargs)


class SubFactory():
    fixture = None
    kwargs = None

    def __init__(self, fixture, method, **kwargs):
        self.fixture = fixture
        self.method = method
        self.kwargs = kwargs


class BaseFix():
    MODEL = None
    _fix_fact = None
    _kwargs = None

    def __init__(self, fix_fact, **kwargs):
        if not self.MODEL:
            raise AttributeError('self.MODEL is not defined')

        self._fix_fact = fix_fact
        self._kwargs = kwargs

        for rel in self.MODEL._sa_class_manager.mapper.relationships:
            attr = getattr(self, rel.key, None)
            if attr:
                list_type_error = False
                try:
                    if False in [isinstance(a, SubFactory) for a in attr]:
                        raise AttributeError('References in fixtures must be declared with "SubFactory": ' + rel.key)
                except TypeError as e:
                    # ok, attr is not iterable, maybe its directly a SubFactory
                    if not isinstance(attr, SubFactory):
                        raise AttributeError('References in fixtures must be declared with "SubFactory": ' + rel.key)

    def model(self):
        # INFOs
        # attr + relations:
        # [f.key for f in Group._sa_class_manager.attributes]
        #
        # Attributes
        # [(a.key, getattr(self, a.key)) for a in self.MODEL._sa_class_manager.mapper.column_attrs]
        #
        # relations
        # [a.key for a in Group._sa_class_manager.mapper.relationships]

        attributes = self.getAttributes()
        if hasattr(self.MODEL(), 'update'):
            model = self.MODEL()
            model.update(**attributes)
        else:
            model = self.MODEL(**attributes)
        return model

    def create(self):
        """
        Adds this model to the session. This instance is not registered and thus can never be
        referred to via get

        :return:
        """

        model = self.model()
        self._fix_fact.get_db_session().add(model)
        self._fix_fact.get_db_session().flush()
        self._fix_fact.get_db_session().expunge(model)

        # in order to have the right values for all fields updated directly by the DB, we have to load the model again
        id_attr = class_mapper(self.MODEL).primary_key[0].name
        id = getattr(model, id_attr)
        return self._fix_fact.get_db_session().query(self.MODEL).get(id)

    def get(self):
        """
        returns an already existing model instance or creates one, registers it to be able to
        find it later and then returns the instance

        :return:
        """
        return self._fix_fact.get(self.__class__, **self._kwargs)

    def getAttributes(self):
        def getAttr(key):
            if key in self._kwargs:
                return self._kwargs[key]
            else:
                return getattr(self, key, None)

        attrs = dict([(a.key, getAttr(a.key)) for a in self.MODEL._sa_class_manager.mapper.attrs if (getAttr(a.key) is not None)])

        # add hybrids
        for a in inspect(self.MODEL).all_orm_descriptors.keys():
            if (getAttr(a) is not None) and a != '__mapper__':
                attrs[a] = getAttr(a)

        def resolveSubFactory(attr):
            if isinstance(attr, SubFactory):
                if attr.method == METHOD_GET:
                    return attr.fixture(self._fix_fact, **attr.kwargs).get()
                elif attr.method == METHOD_CREATE:
                    return attr.fixture(self._fix_fact, **attr.kwargs).create()
                elif attr.method == METHOD_MODEL:
                    return attr.fixture(self._fix_fact, **attr.kwargs).model()

            return None

        for rel in self.MODEL._sa_class_manager.mapper.relationships:
            attr = attrs.get(rel.key, None)


            try:
                converted = []
                for a in attr:
                    a = resolveSubFactory(a)
                    if a:
                        converted.append(a)
#                converted = [a for resolveSubFactory(a) in attr if a]

            except TypeError as e:
                # seems not be a list, try it as an attribute
                converted = resolveSubFactory(attr)

            if converted:
                attrs[rel.key] = converted

        # also add hybrid properties
        for hyb in inspect(self.MODEL).all_orm_descriptors.keys():
            if inspect(self.MODEL).all_orm_descriptors[hyb].extension_type is hybrid.HYBRID_PROPERTY:
                attr = attrs.get(hyb, None)

                try:
                    converted = []
                    for a in attr:
                        a = resolveSubFactory(a)
                        if a:
                            converted.append(a)
                        #                converted = [a for resolveSubFactory(a) in attr if a]

                except TypeError as e:
                    # seems not be a list, try it as an attribute
                    converted = resolveSubFactory(attr)

                if converted:
                    attrs[hyb] = converted

        return attrs
