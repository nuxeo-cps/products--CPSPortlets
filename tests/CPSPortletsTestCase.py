from Testing import ZopeTestCase
from Products.CPSDefault.tests.CPSTestCase import CPSTestCase as \
    CPSPortletsTestCase

from Products.ExternalMethod.ExternalMethod import ExternalMethod

ZopeTestCase.installProduct('CPSPortlets')
ZopeTestCase.installProduct('CPSNavigation')
