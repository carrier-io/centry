#!/usr/bin/python
# coding=utf-8

#     Copyright 2020 getcarrier.io
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

""" Vault tools """

import hvac  # pylint: disable=E0401
from requests.exceptions import ConnectionError
import plugins.base.constants as c
from ..models.vault import Vault


def init_vault():
    """ Initialize Vault """
    # Get Vault client
    try:
        client = hvac.Client(url=c.VAULT_URL)
        # Initialize it if needed
        if not client.sys.is_initialized():
            vault = Vault.query.get(c.VAULT_DB_PK)
            # Remove stale DB keys
            if vault is not None:
                Vault.apply_full_delete_by_pk(pk=c.VAULT_DB_PK)
            # Initialize Vault
            vault_data = client.sys.initialize()
            # Save keys to DB
            vault = Vault(id=c.VAULT_DB_PK, unseal_json=vault_data)
            vault.insert()
        # Unseal if needed
        unseal(client)
        # Enable AppRole auth method if needed
        client = get_root_client()
        auth_methods = client.sys.list_auth_methods()
        if "carrier-approle/" not in auth_methods["data"].keys():
            client.sys.enable_auth_method(
                method_type="approle",
                path="carrier-approle",
            )
    except ConnectionError:
        return 0


def unseal(client):
    if client.sys.is_sealed():
        try:
            vault = Vault.query.get(c.VAULT_DB_PK)
            client.sys.submit_unseal_keys(keys=vault.unseal_json["keys"])
        except AttributeError:
            init_vault()


def create_client():
    client = hvac.Client(url=c.VAULT_URL)
    unseal(client)
    return client


def get_root_client():
    """ Get "root" Vault client instance """
    # Get Vault client
    client = create_client()
    # Get root token from DB
    vault = Vault.query.get(c.VAULT_DB_PK)
    # Add auth info to client
    client.token = vault.unseal_json["root_token"]
    # Done
    return client
