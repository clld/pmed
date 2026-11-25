from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models import common
from clld_cognacy_plugin.models import Cognateset
from clld_cognacy_plugin.interfaces import ICognateset

#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------

@implementer(interfaces.ILanguage)
class Variety(CustomModelMixin, common.Language):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    glottocode = Column(Unicode)


#
# FIXME: Cognateset with proto-lang!
#
@implementer(ICognateset)
class Etymon(CustomModelMixin, Cognateset):
    pk = Column(Integer, ForeignKey('cognateset.pk'), primary_key=True)
    protolanguage = Column(Unicode)
    semantic_field = Column(Unicode)
    semantic_subfield = Column(Unicode)


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, common.Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    concepticon_id = Column(Unicode)

