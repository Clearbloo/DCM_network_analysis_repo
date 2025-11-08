from pybliometrics.scopus import (
    AuthorSearch,
    AuthorRetrieval,
    config,
    AuthorRetrieval,
    ScopusSearch,
    AbstractRetrieval,
)
from pybliometrics.scopus.exception import Scopus429Error
import csv
import pandas as pd

from collections import defaultdict
from itertools import combinations
from tqdm import tqdm
from dataclasses import dataclass

from typing import Iterable

config["Authentication"]["APIKey"] = "24642bce15a7a6e69757c7a945095542"


class AuthorsNotFoundError(Exception):
    pass


@dataclass
class AuthorDetails:
    author_id: int
    freq: int
    h_index: int
    name: str | None
    total_docs: int
    citation_count: int
    citation_ratio: float
    country: str
    institute: str | None
    institute_id: int
    average_coauthors: float


def is_prolific(freq: int, total_docs: int) -> bool:
    return freq >= 5 or (freq >= (0.1 * total_docs) and freq >= 2)


def get_author_ids(paper_title: str) -> set[int]:
    """
    Searches for papers of given title on Scopus database and retrieves the author ids.
    Raises
    ---
        Scopus errors

        AuthorsNotFoundError
            If there are no authors on the abstract
    """
    article_search_list = ScopusSearch(f"TITLE({paper_title})")
    eid = article_search_list.get_eids()
    eid = eid[0]
    ab = AbstractRetrieval(eid, view="FULL")

    if not ab.authorgroup:
        raise AuthorsNotFoundError

    return {auth.auid for auth in ab.authorgroup}


# these 2 functions are useful for calculating information about connected authors, eg the number of countries an author is connected to
def calculate_connected_clusters(
    author_links, author_details: dict[int, AuthorDetails]
) -> dict[int, tuple[int, int]]:
    connected_cntry_and_inst_by_author = {}

    for author in author_details:
        coauthor_countries = set()
        coauthor_inst = set()
        # TODO this is like O(n^99999)
        for pair in author_links:
            if author not in pair:
                continue

            if pair[0] == author:
                coauthor = pair[1]
            else:
                coauthor = pair[0]
            coauthor_countries.add(author_details[coauthor].country)
            coauthor_inst.add(author_details[coauthor].institute)

        if None in coauthor_inst or "NA" in coauthor_countries:
            raise NotImplementedError(
                "How to handle authors with no country or institute?"
            )

        connected_cntry_and_inst_by_author[author] = (
            len(coauthor_countries),
            len(coauthor_inst),
        )

    return connected_cntry_and_inst_by_author


def calculate_av_coauthors(linkslist, author_details: dict[int, AuthorDetails]):
    author_averages = {}
    for author in author_details:
        author_total_freq = 0
        author_total_h_index = 0
        num_coauthors = 0
        for link in linkslist:
            if author not in link:
                continue

            if link[0] == author:
                coauthor = link[1]
            else:
                coauthor = link[0]

            coauthor_h_index = author_details[coauthor].h_index
            coauthor_freq = author_details[coauthor].freq

            num_coauthors += 1
            author_total_freq += coauthor_freq
            author_total_h_index += coauthor_h_index
        if num_coauthors == 0:
            author_averages[author] = (0, 0)
        else:
            author_averages[author] = (
                author_total_h_index,
                num_coauthors,
                author_total_freq / num_coauthors,
            )
    return author_averages


def main():
    with open("papers.csv") as papers_csv:
        # opens csv of all papers. Only the paper titles are used. Creates list of paper titles
        papers = csv.DictReader(papers_csv)
        paper_titles = []
        for row in papers:
            paper_titles.append(row["Title"].replace(".", ""))
        print(len(paper_titles))

    successful_papers = 0
    author_freq: defaultdict[int, int] = defaultdict(int)
    tot_coauthorships: defaultdict[int, int] = defaultdict(int)

    unique_author_combos: set[tuple[int, int]] = set()
    for paper_title in tqdm(paper_titles):
        authors = get_author_ids(paper_title)
        num_authors = len(authors)
        author_combinations = set(combinations(authors, 2))

        # searches for papers throughout list, then creates the links list and authors list
        # and counts paper frequency and total coauthors for each author
        successful_papers += 1
        unique_author_combos.update(author_combinations)

        for author_id in authors:
            author_freq[author_id] += 1
            tot_coauthorships[author_id] += num_authors - 1

    prolific_author_details: dict[int, AuthorDetails] = {}

    for author_id, freq in tqdm(author_freq.items()):
        # gathers relevant data about each author
        co_authorships = tot_coauthorships[author_id]
        aq = AuthorRetrieval(author_id)

        total_docs = aq.document_count
        country = "NA"
        institute = None
        institute_id = None
        if aq.affiliation_current is not None:
            # Assume the main affiliation is the first
            affiliation = aq.affiliation_current[0]
            country = affiliation.country or country
            institute = affiliation.parent_preferred_name or affiliation.preferred_name
            institute_id: int = affiliation.id

        author_details = AuthorDetails(
            author_id,
            freq,
            int(aq.h_index or 0),
            aq.indexed_name,
            total_docs,
            aq.citation_count,
            aq.citation_count / total_docs,
            country,
            institute,
            institute_id,
            co_authorships / freq,
        )

        if is_prolific(freq, total_docs):
            prolific_author_details[author_id] = author_details

    prolific_author_links = [
        pair
        for pair in unique_author_combos
        if pair[0] in prolific_author_details and pair[1] in prolific_author_details
    ]

    # gathering more author data
    cntry_and_inst_connections = calculate_connected_clusters(
        prolific_author_links, prolific_author_details
    )

    avg_h_idx_and_freq_of_coauthors = calculate_av_coauthors(
        prolific_author_links, prolific_author_details
    )

    for author_id in prolific_author_details:
        # saving more author data to the author details list
        country_connections, inst_connections = cntry_and_inst_connections[author_id]
        prolific_author_details[author_id].country_connections = country_connections
        prolific_author_details[author_id].inst_connections = inst_connections

        avg_h_idx, avg_freq = avg_h_idx_and_freq_of_coauthors[author_id]
        prolific_author_details[author_id].avg_h_idx = avg_h_idx
        prolific_author_details[author_id].avg_freq = avg_freq

    for author_details in prolific_author_details.values():
        # classifies authors. This is useful for a predictive program which qualitatively groups authors.
        # The data made here is not actually used, but was explored (see discussion)
        if author_details.h_index >= 40 and author_details.freq >= 10:
            author_details.author_classification = 0
        elif author_details.h_index >= 30 and author_details.freq >= 5:
            author_details.author_classification = 1
        elif author_details.h_index >= 10 or author_details.citation_count >= 200:
            author_details.author_classification = 2
        else:
            author_details.author_classification = 3

    print(f"{successful_papers} papers of {len(paper_titles)} successfully analysed")

    # processes data of prolific authors, relevant to research, for network analysis. The non-prolific authors are disregarded
    prolific_links_df = pd.DataFrame(prolific_author_links, columns=["from", "to"])
    assert prolific_links_df == prolific_links_df.drop_duplicates(
        subset=["from", "to"], inplace=False
    )
    prolific_links_df.to_csv("Python_links_prolific.csv", index=False)

    prolific_authors_df = pd.DataFrame(
        [dets.__dict__ for dets in prolific_author_details],
        columns=[
            "author_ID",
            "paper_freq",
            "h_index",
            "name_of_author",
            "total_papers",
            "citation_count",
            "average_citations",
            "country",
            "institute",
            "institute_ID",
            "average_coauthors",
            "connected_countries",
            "connected_institutes",
            "average_h_index_of_coauthors",
            "average_DCM_papers_of_coauthors",
            "author_classification",
        ],
    )
    print(prolific_authors_df)
    prolific_authors_df.to_csv("Python_authors_prolific.csv", index=False)


if __name__ == "__main__":
    main()
