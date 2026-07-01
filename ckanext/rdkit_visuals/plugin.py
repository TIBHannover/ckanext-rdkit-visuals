import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint
from ckan.common import request, config
from ckanext.rdkit_visuals.controllers.display_image import RdkitVisualsController
import io
import base64



class RdkitVisualsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer
    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('public/statics', 'ckanext-rdkit-visuals')


    # IBlueprint
    def get_blueprint(self):

        blueprint = Blueprint(self.name, self.__module__)

        blueprint.template_folder = u'templates'
        blueprint.add_url_rule(
            u'/rdkit_visuals/display-image/<package_name>',
            u'display_image',
            RdkitVisualsController.display_image,
            methods=['GET', 'POST']
        )
        return blueprint


    # ITemplate Helpers
    def get_helpers(self):

        return {'rdkit_visuals': RdkitVisualsController.display_image,
                'molecule_data':RdkitVisualsController.molecule_data,
               'alternate_names': RdkitVisualsController.alternames,
               'related_values': RdkitVisualsController.related_resources,}
