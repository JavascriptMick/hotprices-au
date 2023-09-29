from datetime import datetime
import gzip
import json
import pathlib

from .logging import logger
from . import output, sites


def get_canoncial_for(store, raw_items):
    canonical_items = []
    for raw_item in raw_items:
        try:
            canonical_item = sites.sites[store].get_canonical(raw_item)
        except Exception:
            logger.exception(f"Unable to process store '{store}' item: {raw_item}")
            continue
        if canonical_item is None:
            continue
        canonical_item['store'] = store
        canonical_items.append(canonical_item)
    return canonical_items


def dedup_items(items):
    lookup = {}
    dedup_items = []
    duplicates = {}
    for item in items:
        seen_item = lookup.get((item['store'], item['id']))
        if not seen_item:
            lookup[(item['store'], item['id'])] = item
            dedup_items.append(item)
        else:
            duplicates.setdefault(item['store'], 0)
            duplicates[item['store']] += 1

    return dedup_items


def transform_data(day):
    all_items = []
    for store in sites.sites.keys():
        raw_categories = output.load_data(store, day=day)
        for category in raw_categories:
            try:
                raw_items = category['Products']
            except KeyError:
                # Don't have items for this category
                continue

            canonical_items = get_canoncial_for(store, raw_items)
            items = dedup_items(canonical_items)
            all_items += items
    
    latest_canonical_file = pathlib.Path(f"output/latest-canonical.json.gz")
    with gzip.open(latest_canonical_file, 'wt') as fp:
        fp.write(json.dumps(all_items))
    return all_items