from Testing import ZopeTestCase
from Products.CPSDefault.tests import CPSTestCase

from Products.ExternalMethod.ExternalMethod import ExternalMethod

CPSPortletsTestCase = CPSTestCase.CPSTestCase

ZopeTestCase.installProduct('CPSPortlets')
