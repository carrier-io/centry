# cenry
New Generation of Carrier UI

## Market plugin included:
* Downloads plugins from defined source
* Updates plugins automatically or just notifies
* Installs dependencies for every plugin

All settings located in .yml
* plugin_repo: 'path/to/plugins.json' - _.json file with entries of plugins available_
* requirements:
    raise_on_attention: false - _throws error on non-conflicting requirements that need manual attention_
* auto_update_plugins: true - _updates plugins automatically whenever update detected_
