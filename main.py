import collections
import datetime
import json
import os
import sys
import time

import dotenv
import github
import github.PaginatedList

from typing import Any, DefaultDict, Dict, List, Set, TextIO

search_terms: List[str] = [
    "adventofcode21",
    "adventofcode2021",
    "advent-of-code21",
    "advent-of-code2021",
    "advent-of-code-21",
    "advent-of-code-2021",
    "aoc21",
    "aoc2021",
    "aoc-21",
    "aoc-2021",
]

dotenv.load_dotenv()

# Put your access token in a .env file
github_api = github.Github(os.getenv("GITHUB_ACCESS_TOKEN"), per_page=100)

def combine_search_term_results(search_terms: List[str]) -> Dict[str, int]:
    """
    Querys Github's API, searching for repos that match a list of search terms, and then creates a dictionary
    mapping the names of programming languages to their prevalence in the results.

    Args:
        search_terms: A list of search terms to use to find repositories.

    Returns:
        A dictionary mapping the string names of programming language to their int prevalence in the search results.
    """
    results: Set[github.PaginatedList.PaginatedList] = {github_api.search_repositories(term) for term in search_terms}
    result_dict: DefaultDict[str, int] = collections.defaultdict(int)
    for result in results:
        try:
            for repo in result:
                result_dict[repo.language] += 1
        except github.RateLimitExceededException:
            time.sleep(60) # Gotta wait to appease the almighty rate limiter ¯\_(ツ)_/¯
    return result_dict

def collect_and_rank_results(prevalence_dict: Dict[str, int]) -> List[str]:
    return sorted(prevalence_dict, key=lambda key: prevalence_dict.get(key, 0), reverse=True)

def save_to_file(dict_to_save: Dict[Any, Any]) -> None:
    file_stamp: str = datetime.datetime.now().isoformat(timespec="seconds")
    with open(f"github-results-{file_stamp}.json", mode="w") as f:
        json.dump(dict_to_save, f, indent=4)

def main(out_stream: TextIO) -> None:
    results = combine_search_term_results(search_terms)
    save_to_file(results) # TODO: Make this configurable by command-line args
    for lang in collect_and_rank_results(results):
        out_stream.write(lang)

if __name__ == "__main__":
    main(sys.stdout)