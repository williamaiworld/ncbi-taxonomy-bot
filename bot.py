#!/usr/bin/env python3

from Bio import Entrez
import xmltodict
from box import Box
from datetime import datetime
from dateutil.parser import parse as parse_date
from pprint import pprint


def get_nodes(start_time: datetime) -> Box:
    """
    Returns a list of nodes that have been created/updated/published after a
    specified date
    """

    start_time = start_time.strftime("%Y/%m/%d")

    # I haven't been able to figure out how to query by hour so we have to
    # parse the times and filter manually. No biggie.
    term = f'"{start_time}"[EDAT] : "3000"[EDAT]'

    node_list = Box(
        xmltodict.parse(Entrez.esearch("taxonomy", term, email="austin@onecodex.com").read())
    )

    # TODO: return an empty list if there are no nodes
    tax_ids = node_list.eSearchResult.IdList.Id

    nodes = Box(
        xmltodict.parse(
            Entrez.efetch(db="taxonomy", id=",".join(tax_ids), email="austin@onecodex.com").read()
        )
    )

    # we should probably munge the dat a bit here and return something
    # more defined

    return [
        Box(
            {
                "id": node.TaxId,
                "name": node.ScientificName,
                "rank": node.Rank,
                "created_at": parse_date(node.CreateDate),
                "updated_at": parse_date(node.UpdateDate),
                "published_at": parse_date(node.PubDate),
                "lineage": node.Lineage,
            }
        )
        for node in nodes.TaxaSet.Taxon
    ]


def format_tweet_for_node(node):

    if "Bacteria" in node.lineage:
        emoji = "🦠"
    else:
        emoji = ""

    return "\n".join([f"{node.name} ({node.rank}) {emoji}".strip(), f"lineage: {node.lineage}"])


start_time = datetime(2020, 2, 17, 0, 0, 0)
nodes = get_nodes(start_time=start_time)

new_nodes = [n for n in nodes if (n.created_at >= start_time) or (n.published_at >= start_time)]
new_nodes = nodes

for node in new_nodes:
    print(format_tweet_for_node(node))
    print()

# every so often
# find a list of new taxa
# if the taxa was created at > the last time we checked
# tweet about
# otherwise, do nothing
# either way, note the latest taxon we saw so that we don't
# tweet again (probably just save this to a file)

# add emojis based on the kingdom / phylum?
