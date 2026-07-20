from pathlib import Path
from urllib.parse import urlparse
from collections import defaultdict
from multiprocessing import Pool
from tqdm import tqdm
import argparse, subprocess, csv

#####################################
def download_worker(args):
    out_dir, url = args
    result = subprocess.run(
        ["wget", "-q", "-c", "--tries=3", "-P", out_dir, url]
    )

    if result.returncode != 0:
        return url

    return None


def filename_from_url(url):
    return Path(urlparse(url).path).name
#####################################

parser = argparse.ArgumentParser()
parser.add_argument("--out_dir", required=True)
parser.add_argument("--url_file", required=True)
parser.add_argument("--cores", type=int, required=True)
args = parser.parse_args()
Path(args.out_dir).mkdir(parents=True, exist_ok=True)

# Read URL table
samples = defaultdict(list)
with open(args.url_file) as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        sample = row["sample_id"]
        samples[sample].append(row)
# print(samples)

# Ask user which samples to download
urls_to_download = []
skipped_samples = []
count = 1
for sample, rows in samples.items():
    print("-" * 50)
    print(f"Sample [{count}/{len(samples.keys())}]: {sample}")
    print(f"Files: {len(rows)}")
    print()

    for r in rows:
        url = r["fastq_url"]
        name = filename_from_url(url)
        print(f"  {name}\t{r['size_in_gib']} GB")
    print()
    
    while True:
        answer = input("Download FASTQs for this sample? [Y/N]: ").strip().lower()
        if answer == "y":
            urls_to_download.extend([r["fastq_url"] for r in rows])
            break
        elif answer == "n":
            skipped_samples.append(sample)
            break
        else:
            print("Please enter Y or N.")
    count += 1

# Write skipped samples to file
with open("skipped_samples.txt", "w") as f:
    for s in skipped_samples:
        f.write(s + "\n") 

print("-" * 50)
print(f"Selected {len(urls_to_download)} files for download.")

# Download selected URLs
tasks = [(args.out_dir, url) for url in urls_to_download]
with Pool(processes=args.cores) as pool:
    for outcome in tqdm(pool.imap_unordered(download_worker, tasks), total=len(tasks)):
        if outcome is not None:
            print(f"\nFAILED: {outcome}")

print("-" * 50)
print(f"All done!")
print("-" * 50)

# Validate downloaded files (gzip integrity: catches truncated/corrupt downloads)
def validate(fastq):
    result = subprocess.run(["gzip", "-t", fastq], stderr=subprocess.DEVNULL)
    return fastq if result.returncode != 0 else None

files = [str(Path(args.out_dir) / filename_from_url(url)) for url in urls_to_download]
print("Validating downloaded files...")
with Pool(processes=args.cores) as pool:
    for bad in tqdm(pool.imap_unordered(validate, files), total=len(files)):
        if bad is not None:
            print(f"\nCORRUPT: {bad}")
print("Validation complete.")
