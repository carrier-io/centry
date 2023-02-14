# centry
New Generation of Carrier UI

## (New!) Deployment
* GNU make >=4.3 should be installed
* docker, installed according to [official installation guide](https://docs.docker.com/desktop/)
* Run: `make` and **read** instructions carefully

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
* Create config file for you plugin named `config.yml` right inside the plugin directory
* Create `module.py` with class Module, inherited from pylon `ModuleModel`
  ```python
  class Module(module.ModuleModel):
    """ Pylon module """
  ```
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
* `def deinit(self): ...` is just a destructor, so place there whatever is needed for your plugin
* Optionally create `requirements.txt` with special modules required by your plugin
    * upon launch requirements will be installed automatically into `./site-packages` folder in plugin directory

## Market plugin info:
* Downloads plugins from defined source
  * supported sources are `git` and `http` containing zipped plugin
* Updates plugins automatically _(if set)_ or just notifies
* Installs dependencies for every plugin

All settings located in .yml
*  ```yaml
    plugin_repo:
      type: file
      path: './config/plugins_local.json'
    ```
    ```yaml
    plugin_repo:
      type: http
      path: 'https://raw.githubusercontent.com/carrier-io/centry/main/config/plugins.json'
    ```
   _.json file with entries of plugins available. Supported types: `file`, `http`_

* ```yaml
  requirements:
    raise_on_attention: false
  ```
  _throws error on non-conflicting requirements that need manual attention_

* ```yaml
  auto_update_plugins: false
  ```
  _updates plugins automatically whenever update detected_

* ```yaml
  ignore_updates:
    - plugin_1
    - plugin_3
  ```  
  _ignores checks for updates for indicated plugins_

* ```yaml
  preordered_plugins:
    - plugin_1
    - plugin_3
  ```
   _used to set plugins that you require regardless of dependencies.
   This option can also be set in PREORDERED_PLUGINS env variable in `plugin_1,plugin_3` format_

* ```yaml
  git_config:
    default:
      username:
      password:
      key:
      key_data:
    plugin_1:
      username: us3r
      password: passw0rd
  ```
  _sets git configuration for market's git manager.
  `default` is used globally, but special settings can be set for each plugin individually with named section like `plugin_1`_


#### plugins.json format:
```json
 {
  "plugin_1": {
    "source": {
      "type": "git",
      "url": "https://my/git/url/plugin_1.git"
    },
    "objects": {
      "metadata": "https://url/to/plugin/metadata/metadata.json"
    }
  },
  "plugin_2": {
    "source": {
      "type": "git",
      "url": "https://my/git/url/plugin_1.git",
      "branch": "dev"
    },
    "objects": {
      "metadata": "https://url/to/plugin/metadata/metadata.json"
    }
  },
  "plugin_3": {
    "source": {
      "type": "http",
      "url": "https://my/zip/url/plugin_3.zip"
    },
    "objects": {
      "metadata": "https://url/to/plugin/metadata/metadata.json"
    }
  }
}
```
