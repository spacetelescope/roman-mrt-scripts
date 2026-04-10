import os
import argparse
from getpass import getpass
from astroquery.mast import MastMissions
from datetime import datetime


def parse_args():
    """Parse script command line arguments.

    Options:
    -p, --program-ids:
        list of program IDs to query

    -l, --limit:
        limit for the number of returned observations (default: 50000)

    -t, --token:
        MAST API Token. This can be passed as an argument, read from the
        environment variables, or entered into a prompt.
    """
    parser = argparse.ArgumentParser(description="Query Roman MAST programs.")
    parser.add_argument(
        "-p", "--program-ids",
        nargs="+",
        #type=int,
        required=True,
        help="List of program IDs to query"
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
    args = parser.parse_args()
    program_ids = args.program_ids
    limit = args.limit
    token = parse_token(args.token)

    if token is None:
        try:
            token = os.environ["MAST_API_TOKEN"]
        except KeyError:
            token = getpass("MAST API Token: ")

    return program_ids, limit, token


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


def max_product_level(prod):
    return max([int(p) for p in prod.replace(',', ' ').split()])


def count(r, pid):
    """Query MissionMast for Roman data and print file counts.

    Arguments:
    program (int): program ID to query

    **kw: keyword arguments to pass to `query_criteria`.
    """
    # queries a specific program, prints out number of observations, and number of WFI01 observations
    # (this is analogous to the number of exposures)
    rr = r.query('program == @pid')
    max_prod = rr["productLevel"].apply(max_product_level).value_counts()

    n = len(rr)
    n1 = len(rr.query("detector == 'WFI01'"))
    print(f"Program {pid}: {n} datasets for {n1} exposures")
    
    for i in sorted(max_prod.keys()):
        print(f"  {max_prod[i]} processed to L{i}")


if __name__ == "__main__":
    program_ids, limit, token = parse_args()

    m = MastMissions(mission="roman")
    m.login(token=token)

    r = m.query_criteria(program=program_ids, limit=limit, 
        select_cols=["program", "productLevel", "optical_element"]
        ).to_pandas()

    print(f"{datetime.now()} - total datasets: {len(r)}")

    counts = r.value_counts(subset=["program", "productLevel", "optical_element"]).sort_index()

    for pid, x in counts.groupby("program"):
        print(f"Program {pid}: {x.sum()} Datasets")
        print(x.loc[pid])
        print("")

    m.logout()
