# Roman MRT Scripts

This repository hosts some convenient scripts for file accounting during Roman Mission Readiness Tests. Currently it contains:

- `query_mm.py`
- `query_cassi.py`

The scripts are very specific to Roman Archive Operations uses. Use outside of this context is not recommended at this time, but the scripts can be adapted for other goals.

### Requirements

- `os` for reading environment variables
- `argparse` for parsing command line arguments
- `getpass` for prompting the user for MAST API tokens
- `requests` for sending queries to MAST
- `astroquery` for querying MAST
- `pandas` for easily counting table values

## Querying Roman MissionMAST Data

The script `query_mm.py` is set up to search Roman MissionMAST for science datasets and return file counts. Search for a single program ID or a list of IDs. The following example searches for datasets from programs 171, 172, and 173, using a limit of 5,000 observations for each query.

```bash
$ python query_mm.py -p 171 172 173 --limit 5000
```

Each program ID is queried independently, and two counts are printed to the terminal. The first is the number of datasets returned by the query, and the second is the number of datasets with the `detector` field set to `"WFI01"`, which is analogous to the number of visits present in the results.

The script accepts these command line arguments:

- `-p`, `--program_ids` (required): a sequence of program IDs separated by spaces
- `-l`, `--limit` (optional): the limit for the number of returned observations (default: 50,000)
- `-t`, `--token` (optional): the MAST API token

## Querying CaSSI Supplemental & Telemetry Data

The script `query_cassi.py` searches the CaSSI Supplemental & Telemetry Data archive and return counts of all present file types. Users provide an ingest start date or date range in which to look for files. The following example counts the files ingested between June 1 and 30, 2025.

```bash
$ python query_cassi.py -s 2025-06-01 -e 2025-06-30
```

The script accepts these command line arguments:

- `-s`, `--start-date` (required): the earliest ingest date in YYYY-MM-DD format
- `-e`, `--end-date` (optional): the latest ingest date in YYYY-MM-DD format
- `-l`, `--limit` (optional): the limit for the number of returned observations (default: 50,000)
- `-t`, `--token` (optional): the MAST API token

## MAST API Tokens

Querying Roman data through MAST requires authorization via a [MAST API token](https://auth.mast.stsci.edu/tokens). These scripts allow users to pass their token as a command line argument, via an environment variable, or interactively via a prompt.

### 1. Command Line Argument

The scripts accept a MAST API token as a command line argument using `-t` or `--token`:

```bash
$ python query_mm.py --program-ids 171 172 --token <your MAST token>
```

### 2. Environment Variable

If no token is passed via command line, the script will check for an environment variable called `MAST_API_TOKEN`.

### 3. Enter When Prompted

Finally, if no token is passed and the `MAST_API_TOKEN` environment variable is set, the script will prompt you for the token:

```bash
$ Enter MAST API token: 
```

This prompt is set up using the `getpass` Python package, which accepts input without echoing the input to the screen. This allows you to type or paste your API token securely.