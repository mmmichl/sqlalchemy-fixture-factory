.. index:: Instantiation
Instantiating Fixtures
======================

For for the following examples, assume this fixture

.. code-block:: python

    class ArnoldPerson(BaseFix):
        MODEL = Person

        first_name = "Arnold"
        family_name = "Schwarz"

First you need to instantiate the fixture class and pass the :class:`.SqlaFixFact` instance as fist parameter:

.. code-block:: python

    fixture = ArnoldPerson(fix_fact)

You can add additional ``kwargs`` to alter the default values. For more details see :doc:`substitution`

To get a SQLAlchemy ORM model instance there are 3 ways

* :meth:`.BaseFix.create`
* :meth:`.BaseFix.get`
* :meth:`.BaseFix.model`


create()
--------
Adds this model to the session. This instance is not registered and thus can never be referred to via :meth:`.BaseFix.get`.
Thus each call to ``create()`` adds a new instance of the fixture to the DB.

.. code-block:: python

    arnold_fix_1 = ArnoldPerson(fix_fact).create()
    arnold_fix_2 = ArnoldPerson(fix_fact).create()
    arnold_fix_3 = ArnoldPerson(fix_fact).create()

    db_session.query(Person).count()  # is 3

get()
-----
Returns an already existing model instance, or creates one and registers it to be able to find it later and then
returns the instance.

Note: Changed properties via the ``kwargs`` parameter are recognized and result in a new instance.

.. code-block:: python

    arnold_fix_1 = ArnoldPerson(fix_fact).get()
    arnold_fix_2 = ArnoldPerson(fix_fact).get()
    arnold_fix_3 = ArnoldPerson(fix_fact).get()

    db_session.query(Person).count()  # is 1

model()
-------
Returns a model instance of this fixture which is ready to be added. The model itself is not added to the DB but all
dependencies are.

.. code-block:: python

    arnold_fix = ArnoldPerson(fix_fact).model()

    db_session.query(Person).count()  # is 0

    db_session.add(arnold_fix)
    db_session.query(Person).count()  # is 1

