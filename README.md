# centry
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

#### plugins.json format:
```json
{
  "auth_root": {
    "metadata": "https://raw.githubusercontent.com/Aspect13/auth_root/main/metadata.json",
    "requirements": "https://raw.githubusercontent.com/Aspect13/auth_root/main/requirements.txt",
    "data": "https://github.com/Aspect13/auth_root/archive/refs/heads/main.zip"
  },
  "shared": {
    "metadata": "https://raw.githubusercontent.com/Aspect13/shared/main/metadata.json",
    "requirements": "https://raw.githubusercontent.com/Aspect13/shared/main/requirements.txt",
    "data": "https://github.com/Aspect13/shared/archive/refs/heads/main.zip"
  }
}
```