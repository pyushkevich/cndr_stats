# Penn Image Computing and Science Lab CNDR Statistics Package

This is a helper package for processing autopsy data from the Penn Center for Neurodegenerative Disease Research (CNDR) in Python. It simplifies importing data from the CNDR InQuery system and reformats some fields to facilitate analysis.

## Installation

To install this package, run

``` sh
pip install git+https://github.com/pyushkevich/cndr_stats.git
```

Of if you want to edit the code and still use the package

``` sh
git clone https://github.com/pyushkevich/cndr_stats.git
cd cndr_stats
pip install -e .
```

## Usage

Add this to your preamble

``` python
import pandas as pd
from cndr_stats.dataimport import read_inquery_excel, clean_cndr_dataset, add_diagnostic_categories
```

Then use this code to import from InQuery:

``` python
# Import the dataset - wrapper around pd.read_xlsx
df = read_inquery_excel('inquery_output.xlsx')

# Make semi-quantitative ratings numeric, merge 3 and 6-point Braak scores
df = clean_cndr_dataset(df)

# Add diagnostic categories like is_ad_cont and ADNC_severity
df = add_diagnostic_categories(df)
```

Please see documentation of individual functions for fields that are added.
