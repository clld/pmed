from sqlalchemy.orm import joinedload

from clld.web.datatables.base import Col, LinkCol, LinkToMapCol, DataTable, IdCol, DetailsRowLinkCol
from clld.web.datatables.value import Values, ValueNameCol
from clld.web.datatables.language import Languages
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.contribution import Contributions, ContributorsCol
from clld.web.datatables.contributor import Contributors
from clld.db.util import get_distinct_values, icontains
from clld.db.models import common
from clld.db.meta import DBSession
from clld.web.util.htmllib import HTML, literal
from clld.web.util.helpers import icon, link
from clld_cognacy_plugin.models import Cognateset, Cognate
from clld_cognacy_plugin.datatables import Cognates, Cognatesets

from pmed.models import Etymon


class Etyma(Cognatesets):
    def col_defs(self):
        return [
            IdCol(self, 'id'),
            Col(self, 'protolanguage', model_col=Etymon.protolanguage),
            LinkCol(self, 'name'),
            Col(self, 'description'),
            Col(self, 'semantic_field', model_col=Etymon.semantic_field, choices=get_distinct_values(Etymon.semantic_field)),
            Col(self, 'semantic_subfield', model_col=Etymon.semantic_subfield, choices=get_distinct_values(Etymon.semantic_subfield)),
        ]

#
# Values:
# - meaning, language, cognateset
#
class Words(Values):
    def base_query(self, query):
        query = query.join(common.ValueSet).options(joinedload(common.Value.valueset))

        if self.language:
            query = query.join(common.ValueSet.parameter)
            return query.filter(common.ValueSet.language_pk == self.language.pk)
        if self.parameter:
            query = query.join(common.ValueSet.language)
            return query.filter(common.ValueSet.parameter_pk == self.parameter.pk)

        query = query.join(common.ValueSet.parameter)
        query = query.join(common.ValueSet.language)
        #query = query.join(Cognate)
        return query

    def col_defs(self):
        return [
            Col(self, 'name'),
            LinkCol(self, 'language', get_object=lambda i: i.valueset.language),
            LinkCol(self, 'parameter', get_object=lambda i: i.valueset.parameter),
        ]


def includeme(config):
    config.register_datatable('values', Words)
