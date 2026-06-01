## Accessing LitSeqCollection from R/Python

One advantage of using an online spreadsheet is that sequencing metadata can be distributed without requiring users to download, edit, or store local copies. LitSeqCollection can be read directly into R or Python.

Note that the Google Sheets view URL is converted into a CSV export URL so that the table can be read by `read.csv()` (in R) or `pandas.read_csv()` (in Python).

### R example

```r
sheet_url <- "https://docs.google.com/spreadsheets/d/1f9gFjXnZfK1a6hQ7MO7ZWTgpzmxh5XNeOMdvVghkZzM/edit?gid=1574494561#gid=1574494561"

# Convert sheet URL
sheet_url <- sub("/edit\\?", "/export?format=csv&", sheet_url)
sheet_url <- strsplit(sheet_url, "#")[[1]][1]

# Read data
df <- read.csv(sheet_url, header = TRUE, skip = 3)
```

### Python example

```python
import pandas as pd

sheet_url = "https://docs.google.com/spreadsheets/d/1f9gFjXnZfK1a6hQ7MO7ZWTgpzmxh5XNeOMdvVghkZzM/edit?gid=1574494561#gid=1574494561"

# Convert sheet URL
sheet_url = (
    sheet_url
    .replace("/edit?", "/export?format=csv&")
    .split("#")[0]
)

# Read data
df = pd.read_csv(sheet_url, header=3)
```