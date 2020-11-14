from models.instances import Account


def get_instances_from_filters(state: Account, filters: list) -> set:
    """
    This will try to find filters in instanceId and tags
    Parameters:
      state: Account object to extract data from
      filters: list of filters.
    Return:
      set of instanceId
    """

    filtered_instanceId = [vm.instanceId for vm in state.vms if any(f in vm.instanceId for f in filters)]
    flattened_tags = dict()

    for vm in state.vms:
        flattened_tags[vm.instanceId] = list()
        for tag in vm.tags:
            for i in tag:
                flattened_tags[vm.instanceId].append(tag[i])

    filtered_tags = [
        vm.instanceId for vm in state.vms
        if any(
                f in tag for f in filters
                for tag in flattened_tags[vm.instanceId]
            )
    ]

    filtered_id = set(filtered_instanceId + filtered_tags)

    return filtered_id or {vm.instanceId for vm in state.vms}


def get_tags_from_instanceId(state: Account, instanceId: str) -> list:

    for vm in state.vms:
        if vm.instanceId == instanceId:
            break

    return vm.tags or list()


def get_tags_from_instanceIds(state: Account, instanceIds: list) -> dict:

    flattened_tags = dict()
    for i in instanceIds:
        flattened_tags[i] = get_tags_from_instanceId(state, i)

    return flattened_tags
