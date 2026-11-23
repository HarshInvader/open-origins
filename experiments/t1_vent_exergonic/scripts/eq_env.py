"""Shared eQuilibrator setup for T1. Redirects pooch's cache so any Zenodo download
(compound DB escalation, CC parameters) lands in raw/equilibrator_cache/ inside the
experiment, not ~/Library/Caches. Import this BEFORE importing equilibrator_api.

TIER: 'bundled' = mini DB shipped in equilibrator-cache-data (escalates to the full
~1.3 GB zenodo.4128543 DB on a miss); 'full' = the full DB from the start."""
import os, pathlib
import pooch

EXP = pathlib.Path(__file__).resolve().parent.parent
CACHE = EXP / 'raw' / 'equilibrator_cache'
CACHE.mkdir(parents=True, exist_ok=True)
_orig = pooch.os_cache


def _os_cache(project):
    return CACHE / project


pooch.os_cache = _os_cache


def make_cc(tier='bundled'):
    from equilibrator_cache import create_compound_cache_from_zenodo
    from equilibrator_api import ComponentContribution
    return ComponentContribution(ccache=create_compound_cache_from_zenodo(tier=tier))


def versions():
    from importlib.metadata import version
    return {p: version(p) for p in ('equilibrator-api', 'equilibrator-cache',
                                    'equilibrator-cache-data', 'component-contribution')}
