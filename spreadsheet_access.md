## Accessing the spreadhseet from R/Python

One advantange of an online spreasheet is that sequencing metadata can be distributed without the need for local copies. Very helpfully, the spreasheet can be read directly into R/Python:

```R
### R example

sheet_url <- "https://docs.google.com/spreadsheets/d/1f9gFjXnZfK1a6hQ7MO7ZWTgpzmxh5XNeOMdvVghkZzM/edit?gid=1574494561#gid=1574494561"

# Convert sheet URL - 
sheet_url <- sub("/edit\\?", "/export?format=csv&", sheet_url)
sheet_url <- strsplit(sheet_url, "#")[[1]][1]

# Read data
df <- read.csv(sheet_url, header=TRUE, skip=3)
```

```Python
### Python example
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

