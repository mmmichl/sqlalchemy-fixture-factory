.. index:: Referencing
Referencing other Fixtures
==========================

To build complete scenarios, referencing other fixtures becomes necessary.

To reference other fixtures, use following functions:

* :func:`.subFactoryGet`
* :func:`.subFactoryCreate`
* :func:`.subFactoryModel`

These function behave the same as the methods of the :class:`.BaseFix` class.

.. code-block:: python

    class ArnoldAccount(BaseFix):
        MODEL = Account
        name = "arney"

    class ArnoldPerson(BaseFix):
        MODEL = Person
        name = "Arnold"
        account = sqla_fix_fact.subFactoryModel(ArnoldAccount)


Prefer the usage of :func:`.subFactoryModel` for referencing other fixtures.

You can also add ``kwargs`` to alter properties of the factory as described in :doc:`substitution`

.. code-block:: python

    class ArnoldAccount(BaseFix):
        MODEL = Account
        name = "arney"

    class ArnoldPerson(BaseFix):
        MODEL = Person
        name = "Arnold"
        account = sqla_fix_fact.subFactoryModel(ArnoldAccount)

    class ArnoldPersonAdmin(BaseFix):
        MODEL = Person
        name = "Arnold"
        account = sqla_fix_fact.subFactoryModel(ArnoldAccount, name="arney-admin")

*Do not use the substitutions extensively* at referencing other fixtures. In most cases an own fixture should be
defined. Like in the example from above.

.. code-block:: python

    class ArnoldAccount(BaseFix):
        MODEL = Account
        name = "arney"

    class ArnoldPerson(BaseFix):
        MODEL = Person
        name = "Arnold"
        account = sqla_fix_fact.subFactoryModel(ArnoldAccount)

    class ArnoldAdminAccount(BaseFix):
        MODEL = Account
        name = "arney-admin"

    class ArnoldPersonAdmin(BaseFix):
        MODEL = Person
        name = "Arnold"
        account = sqla_fix_fact.subFactoryModel(ArnoldAdminAccount)

To save you the burden of copying to much information, you could of course inherit from other fixtures. This inherits all
properties except those you overwrite.

.. code-block:: python

    class ArnoldAccount(BaseFix):
        MODEL = Account
        name = "arney"

    class ArnoldPerson(BaseFix):
        MODEL = Person
        name = "Arnold"
        account = sqla_fix_fact.subFactoryModel(ArnoldAccount)

    class ArnoldAdminAccount(ArnoldAccount):
        name = "arney-admin"

    class ArnoldPersonAdmin(ArnoldPerson):
        account = sqla_fix_fact.subFactoryModel(ArnoldAdminAccount)

You can also add sub-factories in lists

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