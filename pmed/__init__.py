import collections

from pyramid.config import Configurator
from clld.interfaces import IMapMarker, IValueSet, IValue, IDomainElement
from clld.web.icon import MapMarker
from clldutils.svg import pie, icon, data_url
from clld_cognacy_plugin.models import Cognate
from clld_cognacy_plugin.interfaces import ICognate

# we must make sure custom models are known at database initialization!
from pmed import models





def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.include('clld_cognacy_plugin')
    config.include('clldmpg')
    config.register_resource('cognate', Cognate, ICognate, with_index=True)

    return config.make_wsgi_app()
