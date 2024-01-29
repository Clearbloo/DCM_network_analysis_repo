import requests
import os
import os.path as osp
from tqdm import tqdm
CWD = os.getcwd()
DATA_DIR = osp.join(CWD, "data")
# Define the base URL for the PubMed API
base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# Define the search term and maximum number of returns
search_term = "degenerative cervical myelopathy"
retmax = 100

# Define the search URL
search_url = (
    f"{base_url}esearch.fcgi?db=pubmed&term={search_term}&retmode=json&retmax={retmax}"
)

# Send a GET request to the PubMed API
response = requests.get(search_url)


# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    results = response.json()

    # Extract the list of PubMed IDs (PMIDs)
    pmids = results["esearchresult"]["idlist"]
    count = results["esearchresult"]["count"]

    # Join the list of PMIDs into a comma-separated string
    id_string = ",".join(pmids)

    # Request the summary for all PMIDs
    summary_url = f"{base_url}esummary.fcgi?db=pubmed&id={id_string}&retmode=json"
    summary_response = requests.get(summary_url)

    if summary_response.status_code == 200:
        summary_results = summary_response.json()
        
        separator = ";"
        csv_path = os.path.join(DATA_DIR, "new_papers.txt")
        with open(csv_path, "w") as f:
            f.write(f"sep={separator}\n")
            headings = "Journal; Year; Authors; Title; Paper Ref; Country\n"
            f.write(headings)
        
        # Extract and print the titles
        for pmid in tqdm(pmids):
            paper = summary_results["result"][pmid]
            journal = paper["fulljournalname"]
            year = paper["epubdate"]
            authors = [a["name"] for a in paper["authors"]]
            title = paper["title"]
            # country = summary_results["locationlabel"]
            line = f"{journal}; {year}; {authors}; {title}; {pmid}\n"

            with open(csv_path, "a") as f:
                f.write(line)

        print(f"Fetch successful with status code {summary_response.status_code}")
        print(f"Found {count} papers. Written to {csv_path}")
    else:
        print(
            f"Failed to fetch summary details with status code {summary_response.status_code}"
        )

else:
    print(f"Request failed with status code {response.status_code}")
