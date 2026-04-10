import os
import argparse
import requests
from getpass import getpass
from pandas import DataFrame
from datetime import datetime


cassi_url = "https://mast.stsci.edu/cassi/api/v0.1/roman/search/GW1"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Query Roman CASSI API for supplemental and telemetry data."
    )
    parser.add_argument(
        "-s", "--start-date",
        type=str,
        help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "-e", "--end-date",
        type=str,
        default=None,
        help="Optional end date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=50000,
        help="Limit for number of results (default: 50000)"
    )
    parser.add_argument(
        "-t", "--token",
        type=str,
        help="MAST API token",
        default=None,
    )
    parser.add_argument(
        "--list-visits",
        action="store_true",
        help="Print a list of all visits"
    )
    args = parser.parse_args()

    start_date = args.start_date
    end_date = args.end_date
    limit = args.limit
    token = parse_token(args.token)
    list_visits = args.list_visits

    return start_date, end_date, limit, token, list_visits


def parse_token(token):
    """Parse API token.

    If token is not passed as an argument, try reading it from the
    environment variables. If it's not set, prompt the user for it.
    """
    if token is None:
        try:
            token = os.environ["MAST_API_TOKEN"]
        except KeyError:
            token = getpass("MAST API Token: ")
    return token


def query_cassi_gw_face_l1(start_date, end_date, limit, token):
    """Query Roman CASSI API for guide window & FACE L1 files and return the response.

    Arguments:
    start_date (str): Start date in YYYY-MM-DD format
    end_date (str or None): Optional end date in YYYY-MM-DD format
    limit (int): Limit for number of results
    token (str): MAST API token

    Returns:
    response (requests.Response): Response object from the CASSI API request
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {token}"
    }
    if end_date:
        date_range = f">={start_date},<={end_date}"
    else:
        date_range = f">={start_date}"
    payload = {
        "conditions": [
            {"source": "GW1"},
            {"dataGroup": "GW1"},
            {"ingestCompletionDate": date_range}
        ],
        "limit": limit,
        "select_cols": [
            "fileType", "archiveFileName",
        ]
    }

    response = requests.post(cassi_url, headers=headers, json=payload)
    response.raise_for_status()
    return response


def count_results(response, n_rjust=8, list_visits=False):
    """Count the files of different types returned by the CaSSI query.

    n_rjust is the number of spaces between the end of the longest file 
    type and its file count.
    """
    data = response.json()
    results = DataFrame(data.get("results", []))
    if len(results) == 0:
        print("No files!")
        return
    
    # Add gwFileNameBase:
    results["gwFileNameBase"] = results.archiveFileName.str[:22]

    counts = results.value_counts("fileType")
    n_longest = max([len(c) for c in counts.keys()]) + 1

    print("Total files:".ljust(n_longest), str(len(results)).rjust(n_rjust))
    for c in counts.keys():
        print(f"{c}:".ljust(n_longest), str(counts[c]).rjust(n_rjust))

    if list_visits:
        print("\n\nVisits-GSAq:")
        print("--------------------")
        for vgsaq in sorted(results['gwFileNameBase'].drop_duplicates().to_list()):
            print(vgsaq)
        print("")


if __name__ == "__main__":
    start_date, end_date, limit, token, list_visits = parse_args()
    results = query_cassi_gw_face_l1(
        start_date, end_date, limit, token,
    )
    print(f"{datetime.now()} - CaSSI Guide Window & FACE L1")
    count_results(results, list_visits=list_visits)
