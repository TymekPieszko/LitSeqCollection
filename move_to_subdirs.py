from pathlib import Path
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--fastq_dir", required=True)
parser.add_argument("--url_file", required=True)
args = parser.parse_args()

fastq_dir = Path(args.fastq_dir)

with open(args.url_file) as f:

    next(f)  # skip header

    for line in f:

        fields = line.rstrip().split("\t")

        sample = fields[0]
        url = fields[-1]

        filename = Path(url).name

        src = fastq_dir / filename
        dst = fastq_dir / sample / filename

        if src.exists():
            dst.parent.mkdir(exist_ok=True)
            shutil.move(src, dst)