"""Explicit runtime-only differences; currently none after status-label alignment.

Each future entry must be {role_id: {field: value}} and documented with a reason
in Progress/ROLE_AUTHORITY.md. Never change a boundary through an override.
"""
RUNTIME_OVERRIDES = {}


def runtime_catalogue(roles):
    from copy import deepcopy
    result = deepcopy(roles)
    assert set(RUNTIME_OVERRIDES) <= {r['id'] for r in result}
    for role in result:
        updates = RUNTIME_OVERRIDES.get(role['id'], {})
        assert 'boundary' not in updates
        role.update(updates)
    return result
