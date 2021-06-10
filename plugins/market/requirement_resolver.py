import pkg_resources


from plugins.market.utils.plugin import Plugin


def add_entries(plugin_list):
	for plugin in map(Plugin, plugin_list):
		plugin.add_entry()


def update_pending_requirements(plugin: Plugin, pending_requirements, req_status) -> None:
	try:
		reqs = pkg_resources.parse_requirements(plugin.requirements.open().readlines())
	except FileNotFoundError:
		return
	# pkg_resources.working_set.resolve(reqs, installer=plugin.installer, env=plugin.environment)
	for r in reqs:
		try:
			pkg_resources.working_set.resolve([r])
		except pkg_resources.VersionConflict as e:
			req_status['conflict'][e.req.project_name].append({
				'plugin': plugin,
				'requirement': e.req
			})
			req_status['conflict'][e.dist.project_name].append({
				'plugin': 'CORE',
				'requirement': e.dist
			})
			# raise e
		except pkg_resources.DistributionNotFound as e:
			pending_requirements[e.req.project_name].append({
				'plugin': plugin,
				'requirement': e.req
			})


def resolve_version_conflicts(pending_requirements, req_status):
	for req_name in pending_requirements:
		if len(pending_requirements[req_name]) > 1:
			req_status[resolve_version_conflict(pending_requirements[req_name])][req_name].extend(pending_requirements[req_name])
		else:
			req_status['safe'][req_name].extend(pending_requirements[req_name])


def resolve_version_conflict(requirers):
	status = 'safe'
	for spec1, spec2 in map(lambda a, b: (a['requirement'].specifier, b['requirement'].specifier), requirers, requirers[1:]):
		if spec1 != spec2:
			if spec1 and spec2:
				status = 'conflict'
				break
			else:
				status = 'attention'
	return status
