# centry
New Generation of Carrier UI

## Deployment

* First step is to create an entrypoint for the app e.g. `app.py` and set up environment variables in `.env` to toggle development mode, paths to docker containers and location of pylon `.yml` config
  * *_consider using python-dotenv to load variables if launching locally_
* Install requirements for centry with `pip install -r requirements.txt`
* Locate and edit pylon `.yml` config as indicated in `.env` variable `CORE_CONFIG_SEED`
    * _defaults can be found in `./config/pylon-example.yml`_
* Make sure your `plugins` _*(default)_ folder matches the config and contains the `market` plugin inside
* Execute `pylon.main()` inside of entrypoint
    * _make sure you load env **!before!** importing `main()` from `pylon`_


## Creating a new plugin
* Make a new package folder in `plugin` directory with `__init__.py`
* Create `metadata.json` following structure:
    ```json
    {
      "name": "My new awesome plugin",
      "version": "0.1",
      "module": "plugins.plugin_name",
      "extract": false,
      "depends_on": ["required_plugin"],
      "init_after": []
    }
    ```
* Create config file for you plugin `config.yml`
* Create `module.py` with class Module, inherited from pylon `ModuleModel`
* define `init` and `deinit` methods
* `__init__` method should look like:
    ```python
    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context
    ```
  * `settings`  - _contains config data from your `config.yml`_
  * `context`   - _contains data from pylon. Global pylon settings are accessible via `context.settings`_
  * `root_path` - _prefix for plugin blueprints_
* Optionally create `requirements.txt` with special modules required by your plugin
    * upon launch requirements will be installed automatically into `./site-packages` folder in plugin directory

## Market plugin info:
* Downloads plugins from defined source
* Updates plugins automatically or just notifies
* Installs dependencies for every plugin

All settings located in .yml
* plugin_repo: 'path/to/plugins.json' - _.json file http url with entries of plugins available_
* requirements:
    raise_on_attention: false - _throws error on non-conflicting requirements that need manual attention_
* auto_update_plugins: true - _updates plugins automatically whenever update detected_
* preordered_plugins:
  - 'auth_root'
  - 'projects' - _used to set plugins that you require regardless of dependencies_
    _can also be set in PREORDERED_PLUGINS env variable in `auth_root,projects` format_

#### plugins.json format:
```json
{
  "projects": {
    "metadata": "https://raw.githubusercontent.com/carrier-io/projects/main/metadata.json",
    "requirements": "https://raw.githubusercontent.com/carrier-io/projects/main/requirements.txt",
    "data": "https://github.com/carrier-io/projects/archive/refs/heads/main.zip"
  },
  "shared": {
    "metadata": "https://raw.githubusercontent.com/carrier-io/shared/main/metadata.json",
    "requirements": "https://raw.githubusercontent.com/carrier-io/shared/main/requirements.txt",
    "data": "https://github.com/carrier-io/shared/archive/refs/heads/main.zip"
  }
}
```