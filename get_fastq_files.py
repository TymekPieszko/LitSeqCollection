from pathlib import Path
from urllib.parse import urlparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import argparse, subprocess, csv, shutil


def download(out_dir, url):
    result = subprocess.run(
        ["wget", "-q", "-c", "--tries=3", "-P", out_dir, url]
    )

    if result.returncode != 0:
        return url

    return None


def filename_from_url(url):
    return Path(urlparse(url).path).name


parser = argparse.ArgumentParser()
parser.add_argument("--fastq_dir", required=True)
parser.add_argument("--url_file", required=True)
parser.add_argument("--cores", type=int, required=True)
args = parser.parse_args()


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
samples_to_skip = []
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
            samples_to_skip.append(sample)
            break
        else:
            print("Please enter Y or N.")
    count += 1

# Write skipped samples to file
with open("skipped_samples.txt", "w") as f:
    for s in samples:
        f.write(s + "\n") 

print("-" * 50)
print(f"Selected {len(urls_to_download)} files for download.")


# Create output dir
Path(args.fastq_dir).mkdir(exist_ok=True)

# Download selected URLs
with ThreadPoolExecutor(max_workers=args.cores) as ex:
    futures = [ex.submit(download, args.fastq_dir, url) for url in urls_to_download]

    for future in tqdm(as_completed(futures), total=len(futures)):
        failed_url = future.result()

        if failed_url is not None:
            print(f"\nFAILED: {failed_url}")

print("-" * 50)
print(f"All done!")
print("-" * 50)

# # Move FASTQs to per-sample subdirectories
# print("-" * 50)
# print(f"Moving FASTQs to per-sample directories...")

# with open(args.url_file) as f:

#     next(f)  # skip header

#     for line in f:

#         fields = line.rstrip().split("\t")

#         sample = fields[0]
#         url = fields[-1]

#         filename = Path(url).name

#         src = Path("fastq") / filename
#         dst = Path("fastq") / sample / filename

#         dst.parent.mkdir(exist_ok=True)

#         shutil.move(src, dst)

# print("-" * 50)
# print(f"All done!")
# print("-" * 50)