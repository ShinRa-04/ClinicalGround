def stop_record(evidence_ids, waiting=()):
    """An explicit synthetic worker assessment, not code proof of clinical judgment."""
    return {'no_further_permitted_action': True,
        'reason': 'Permitted case sources were checked; the requested external record is not available yet.',
        'evidence_ids': list(evidence_ids),
        'investigations_performed': [list(evidence_ids)[-1]],
        'other_work_considered': ['No remaining internal stage can advance before the documented response.'],
        'waiting_on_obligation_ids': list(waiting)}
