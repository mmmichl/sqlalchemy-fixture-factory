.. index:: Substitution
.. _substitution:
Substitution of Values
======================

To generate a slightly different fixture than a defined one, does not need a new fixture definition. It is possible to
alter properties on instantiation time.

Assume following model and fixture for this page

.. code-block:: python

    class Account(Base):
        __tablename__ = 'account'

        id = Column(Integer, primary_key=True)
        name = Column('name', Unicode)

    class Person(Base):
        __tablename__ = 'person'

        id = Column(Integer, primary_key=True)
        first_name = Column('first_name', Unicode)
        family_name = Column('first_name', Unicode)
        account_id = Column(Integer, ForeignKey('account.id'))
        account = relationship(Account)

    # Fixtures
    class ArnoldAccount(BaseFix):
        MODEL = Account
        name = "arney"

    class ArnoldAdminAccount(BaseFix):
        MODEL = Account
        name = "arney-admin"

    class ArnoldPerson(BaseFix):
        MODEL = Person

        first_name = "Arnold"
        family_name = "Schwarz"
        account = sqla_fix_fact.subFactoryModel(ArnoldAccount)


To substitute a property simply add a key word argument to the constructor

.. code-block:: python

    arnold_fix = ArnoldPerson(fix_fact, first_name="Franz").create()

    assert arnold_fix.first_name == "Franz"

Of course more than one substitution is possible

.. code-block:: python

    arnold_fix = ArnoldPerson(fix_fact, first_name="Franz", family_name="Egger").create()

    assert arnold_fix.first_name == "Franz"
    assert arnold_fix.family_name == "Egger"

Even references to other factories can be substituted. In this case you need to use one of the sub-factory definition functions!

.. code-block:: python

    arnold_fix = ArnoldPerson(fix_fact, account=sqla_fix_fact.subFactoryModel(ArnoldAdminAccount)).create()

    assert arnold_fix.account.name == "arney-admin"
