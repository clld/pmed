import itertools
import collections

from clldutils.misc import nfilter
from clldutils.color import qualitative_colors
from clld.cliutil import Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib import bibtex
from clld_cognacy_plugin.models import Cognate, Cognateset

from pycldf import Sources


import pmed
from pmed import models


def main(args):
    data = Data()
    data.add(
        common.Dataset,
        pmed.__name__,
        id=pmed.__name__,
        domain='pmed.clld.org',

        publisher_name="Max Planck Institute for Evolutionary Anthropology",
        publisher_place="Leipzig",
        publisher_url="http://www.eva.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'},

    )


    contrib = data.add(
        common.Contribution,
        None,
        id='cldf',
        name=args.cldf.properties.get('dc:title'),
        description=args.cldf.properties.get('dc:bibliographicCitation'),
    )

    for lang in args.cldf.iter_rows('LanguageTable', 'id', 'glottocode', 'name', 'latitude', 'longitude'):
        data.add(
            models.Variety,
            lang['id'],
            id=lang['id'],
            name=lang['name'],
            latitude=lang['latitude'],
            longitude=lang['longitude'],
            glottocode=lang['glottocode'],
        )

    for rec in bibtex.Database.from_file(args.cldf.bibpath, lowercase=True):
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

    refs = collections.defaultdict(list)


    for param in args.cldf.iter_rows('ParameterTable', 'id', 'concepticonReference', 'name'):
        data.add(
            models.Concept,
            param['id'],
            id=param['id'],
            name='{} [{}]'.format(param['name'], param['id']),
        )
    f2c = {}

    for form in args.cldf.iter_rows('FormTable', 'id', 'form', 'languageReference', 'parameterReference', 'source'):
        f2c[form['ID']] = data['Concept'][form['Parameter_ID']].name
        vsid = (form['languageReference'], form['parameterReference'])
        vs = data['ValueSet'].get(vsid)
        if not vs:
            vs = data.add(
                common.ValueSet,
                vsid,
                id='-'.join(vsid),
                language=data['Variety'][form['languageReference']],
                parameter=data['Concept'][form['parameterReference']],
                contribution=contrib,
            )
        for ref in form.get('source', []):
            sid, pages = Sources.parse(ref)
            refs[(vsid, sid)].append(pages)
        data.add(
            common.Value,
            form['id'],
            id=form['id'],
            name=form['form'],
            valueset=vs,
        )

    for (vsid, sid), pages in refs.items():
        DBSession.add(common.ValueSetReference(
            valueset=data['ValueSet'][vsid],
            source=data['Source'][sid],
            description='; '.join(nfilter(pages))
        ))

    meaning = None
    for row in args.cldf['CognatesetTable']:
        #
        # FIXME: take over meaning from previous cognateset if empty!
        #
        if row['Description'] and row['Description'] != 'None':
            meaning = row['Description']
        name = (row['Name'] or '').split()
        if len(name) == 0:
            plang, reconstruction = '-', '-'
        elif len(name) == 1:
            plang, reconstruction = name[0], '-'
        else:
            plang = name[0]
            reconstruction = ' '.join(name[1:])
        data.add(
            models.Etymon, row['ID'],
            id=row['ID'].rjust(4, '0'),
            name=reconstruction,
            semantic_field=row['Semantic_Field'],
            semantic_subfield=row['Semantic_Subfield'],
            protolanguage=plang,
            description=meaning)

    for row in args.cldf['CognateTable']:
        data.add(
            Cognate,
            row['ID'],
            cognateset=data['Cognateset'].get(row['Cognateset_ID']),
            counterpart=data['Value'][row['Form_ID']],
            doubt=row['Doubt'],
        )


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
