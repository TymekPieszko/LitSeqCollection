## Download instructions for LitSeqCollection

Contact: t.pieszko@ucl.ac.uk

**(1)** Create a Python environment:

```bash
python -m venv $DATA/envs/litto-seq
source $DATA/envs/litto-seq/bin/activate
pip install pandas numpy requests tqdm
```

**(2)** Download the `get_fastq_urls.py`, `get_fastq_files.py` and `move_to_subdirs.py` scripts:

```bash
wget https://raw.githubusercontent.com/TymekPieszko/littorina-seq/main/get_fastq_urls.py &&
wget https://raw.githubusercontent.com/TymekPieszko/littorina-seq/main/get_fastq_files.py &&
wget https://raw.githubusercontent.com/TymekPieszko/littorina-seq/main/move_to_subdirs.py

# Make scripts readable/writable/executable
chmod +rwx *
```

**(3)** Fetch FASTQ URLs for all (or a subset of) BioSample IDs. You can subset the dataset by most categorical columns, except:
`Timestamp`, `Corresponder`, `Latitude`, `Longitude`, and `Targeted_coverage`. Request multiple categories by providing a comma-delimited list.

```bash
# Fetch URLs
# Note that the flags (but not the categories) are in lowercase

# Example 1 - fetch URLs for just L. saxatilis and L. arcana from the NRS project
python get_fastq_urls.py \
--project_id NRS \
--species saxatilis,arcana \
# Restrict to single-individual WGS only; no pool-seq
--sequence_type WGS_single_individual

# Example 2 - fetch URLs for just 3 samples of interest
python get_fastq_urls.py \
--sample_id AMB_5_3,BH_10_1,BH_8_2
```

The script produces two output files: `fastq_urls.tsv` with the URLs and `fastq_urls.REPORT.tsv` which reports on the number of FASTQ files per sample.

**(4)** Download the actual FASTQ files; use bash or the `get_fastq_files.py` script. The Python script will additionally go through the requested samples one-by-one, allowing you to inspect the associated files and flag potential problems. With 24 cores, downloading the whole NRS dataset took 1 h 50 min. 

```bash
# Bash example
mkdir fastq
cd fastq
# '-c' enables rerunning from partial downloads in case of failure
# '-P 24' allows up to 24 downloads to run in parallel
tail -n +2 ../fastq_urls.tsv | cut -f5 | xargs -n 1 -P 24 wget -c --tries=5 # Can be rerun to resume partial downloads

# Python script version
python get_fastq_files.py --fastq_dir fastq --url_file fastq_urls.tsv --cores 24
```

`get_fastq_files.py` downloads FASTQ files into the specified directory and records the user-rejected samples in `skipped_samples.txt`. If the download is interrupted (or fails for some URLs), simply rerun the script to complete partial downloads.

**(5)** Finally, you can move the downloaded FASTQ files into per-sample directories:

```bash
python move_to_subdirs.py --fastq_dir fastq --url_file fastq_urls.tsv
``` 