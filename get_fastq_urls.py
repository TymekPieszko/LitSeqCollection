import pandas as pd
import numpy as np
import argparse, warnings
warnings.filterwarnings("ignore")
import requests

def remove_whitespace(df):
    for i in df.columns:
        if df[i].dtype == 'object':
            df[i] = df[i].str.strip()

# The sheet URL needs to be modifed for access
sheet_url = "https://docs.google.com/spreadsheets/d/1f9gFjXnZfK1a6hQ7MO7ZWTgpzmxh5XNeOMdvVghkZzM/edit?gid=1574494561#gid=1574494561"

# Convert sheet URL
sheet_url = (
    sheet_url
    .replace("/edit?", "/export?format=csv&")
    .split("#")[0]
)
 
df = pd.read_csv(sheet_url, header=3)
df = df.drop(columns=['Timestamp', 'Corresponder', 'Latitude', 'Longitude', 'Targeted_coverage'])
df.columns = df.columns.str.lower()
remove_whitespace(df)

# Arguments from df columns
parser = argparse.ArgumentParser()
for column in df.columns:
    parser.add_argument(f"--{str(column).lower()}", type=str, required=False)
args = vars(parser.parse_args())

# Filter
for column, category in args.items():
    if category is None:
        continue
    df = df.loc[np.isin(df[column], category.split(","))]

# Useful info
n = len(df)
ids = len(df["biosample_id"].unique())
print("-" * 50)
print(f"Fetching URLs for {n} samples with {ids} unique BioSample IDs...")
print("-" * 50)
if ids < n:
    print("WARNING: duplicate BioSample IDs detected.")
    duplicates = df["biosample_id"][df["biosample_id"].duplicated()]
    print(",".join(duplicates))
    print("-" * 50)

# Get target accessions
id_to_urls = {} # Dictionary to store BioSample ID - FASTQ URLs mapping. There will typically be multiple URLs per BioSample ID.
url_to_size = {} # Dictionary to store the size of a FASTQ file associated with each URL.
biosample_ids = df["biosample_id"]
for id in biosample_ids:
    id = str(id).strip()
    # print(acc)

    # ENA query
    if id.startswith(("SRR", "ERR", "DRR")):
        query = f"run_accession={id}"
    elif id.startswith("SRS"):
        query = f"secondary_sample_accession={id}"
    else:
        query = f"sample_accession={id}"

    url = (
        "https://www.ebi.ac.uk/ena/portal/api/search"
        "?result=read_run"
        f"&query={query}"
        "&fields=run_accession,fastq_ftp,fastq_bytes"
        "&format=json"
    )

    r = requests.get(url)
    rows = r.json()
    
    id_to_urls[id] = []
    for row in rows:
        ftp_field = row.get("fastq_ftp", "")
        size_field = row.get("fastq_bytes", "")
        if ftp_field:
            for ftp, size in zip(ftp_field.split(";"), size_field.split(";")):
                url = "https://" + ftp
                id_to_urls[id].append(url)
                url_to_size[url] = round(int(size) / 1024**3, 3) # This converts raw size in bytes to GiB 

# Write URLs
with open(f"fastq_urls.tsv", "w") as f:
    f.write("sample_id\tspecies\tbiosample_id\tsize_in_gib\tfastq_url\n")
    for id in id_to_urls.keys():
        for url in id_to_urls[id]:
            f.write(df.loc[df["biosample_id"] == id, "sample_id"].values[0] + "\t")
            f.write(df.loc[df["biosample_id"] == id, "species"].values[0] + "\t")
            f.write(id + "\t")
            f.write(str(url_to_size[url]) + "\t")
            f.write(url + "\n")

# Write report
with open(f"fastq_urls.REPORT.tsv", "w") as f:
    f.write("sample_id\tspecies\tbiosample_id\tfastq_num\n")
    for id in id_to_urls.keys():
        f.write(df.loc[df["biosample_id"] == id, "sample_id"].values[0] + "\t")
        f.write(df.loc[df["biosample_id"] == id, "species"].values[0] + "\t")
        f.write(id + "\t")
        f.write(f"{len(id_to_urls[id])}" + "\n") 

# Useful info
print(f"Collected {sum([len(x) for x in id_to_urls.values()])} FASTQ URLs.")
print("-" * 50)