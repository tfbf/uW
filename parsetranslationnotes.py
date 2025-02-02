# -*- coding: utf-8 -*-
"""ParseTranslationNotes.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_1hXeATKVdZBNsoNPKcHMifvWtHaOTRw

## USFM
[USFM Documentation](https://ubsicap.github.io/usfm/)
## Input file
[Input Repo](https://git.door43.org/Door43-Catalog/hi_tn)
## Expected output
```
\id TIT                                     # Book Id. Must be the first line of the output. Only one **\id** is permitted in the output.
\c 1                                        # Chapter No. Occurs once for each chapter
\p                                          # Para placeholder
\v 1                                        # Verse No
\b                                          # Table separator
\tr                                         # Row Begin
\tc1 Son of God                             # Column: GLQuote
\tc2 Υἱοῦ Θεοῦ                              # Column: OrigQuote
\tc3 guidelines-sonofgodprinciples          # Column: SupportReference
\tr                                         # Row Begin
\tc1-3 यह यीशु के लिए एक महत्वपूर्ण पदवी है।           # Merged-Column: OccurrenceNote
\b                                          # Table separator
\tr                                         # Row Begin
\tc1 that agrees with godliness             # Column: GLQuote
\tc2 τῆς κατ’ εὐσέβειαν                     # Column: OrigQuote
\tc3                                        # Column: SupportReference
\tr                                         # Row Begin
\tc1-3 जो परमेश्वर को आदर देने के लिए उपयुक्त हो       # Merged-Column: OccurrenceNote
\p                                          # Para placeholder

```

# Implemenatation

### Import Python Packages Here
"""

import io
import pandas as pd
import requests

"""### Program Configurations"""

col_dtypes = {
    "Book": "category",
    "Chapter": "category",
    "Verse": "category",
    "SupportReference": "object",
    "OrigQuote": "object",
    "GLQuote": "object",
    "OccurrenceNote": "object"
}
columns = list(col_dtypes.keys())
group_by_cols = ["Book", "Chapter", "Verse"]

sep="\t"

src_path = "https://git.door43.org/Door43-Catalog/hi_tn/raw/branch/master/"
src_files = ["hi_tn_42-MRK.tsv", "hi_tn_48-2CO.tsv", "hi_tn_49-GAL.tsv", "hi_tn_57-TIT.tsv", "hi_tn_58-PHM.tsv",
             "hi_tn_61-1PE.tsv", "hi_tn_63-1JN.tsv", "hi_tn_64-2JN.tsv", "hi_tn_65-3JN.tsv", "hi_tn_66-JUD.tsv"]

"""### Function (_df_to_usfm_) to Convert _pandas_ DataFrame to USFM format"""

use_newline = False       # Make this flag True to get the output with added newlines as in the Sample given above

def gdf_to_usfm_each(gdf):
  gdf = gdf.sort_values("Index", axis = 0, ascending = True)
  # print(gdf[group_by_cols + ["Index", "GroupOrder"]].head(20))
  df = gdf.reset_index(drop=True)

  usfm_each = "\\tr\n\\tc1 {0}\n\\tc2 {1}\n\\tc3 {2}\n\\tr\n\\tc1-3 {3}" if use_newline \
              else "\\tr \\tc1 {0} \\tc2 {1} \\tc3 {2}\n\\tr \\tc1-3 {3}"

  verse = None
  chapter = None
  body = []

  for i, r in df.iterrows():
    if verse is None or chapter is None:
      verse = r["Verse"]
      chapter = r["Chapter"]
    body.append(usfm_each.format(r["GLQuote"], r["OrigQuote"], r["SupportReference"], r["OccurrenceNote"]))
  
  return (chapter, "\\v {0}\n\\b\n".format(verse) + "\n\\b\n".join(body))

def df_to_usfm(df, sep_group=False): # sep_group flag when true will separate each Verse group by an extra Newline for better understanding
  # Add an Index column to preserve order of individual records
  df["Index"] = df.index
  # Group Order column to preserver group order
  df["GroupOrder"] = pd.factorize(df["Chapter"].str.cat(df["Verse"], sep =":|:"))[0]
  
  group_df = df.groupby(["Book", "GroupOrder"])
  # group_df = df.query('Chapter=="1" and Verse=="1"').groupby(["Book", "GroupOrder"])   # Just testing with Chapter 1 and Verse 1

  bk = None
  ch = None
  output = ""
  vs = []

  for i, each in group_df.apply(gdf_to_usfm_each).iteritems():
    if bk is None or bk != i[0]:
      bk = i[0]
      output += ("\\id {0}".format(bk))
    if ch is None or ch != each[0]:
      ch = each[0]
      output += ("\n\\p\n".join(vs))
      output += ("\n\\c {0}\n".format(ch))
      vs = []
    vs.append(each[1])

  output += ("\n\\p\n".join(vs))
  return (output)

"""### _df_to_usfm_ Output"""

for src_file in src_files: 
    # Fetch data from Url
    s = requests.get(src_path + src_file).content
    # Load pandas DataFrame
    tnotes = pd.read_csv(io.StringIO(s.decode('utf-8')), delimiter=sep)
    
    # Filter with the given columns
    tnotes = tnotes[columns]
    # Fill NaN with empty string
    tnotes = tnotes.fillna("")
    # Enforce the given Col datatypes for better performance and data stability
    tnotes = tnotes.astype(col_dtypes)

    # Convert tnotes dataframe to usfm data
    tnotes_usfm = df_to_usfm(tnotes, sep_group=True)
    
    # Save the usfm data to the following file path
    save_file = "{0}.usfm".format(src_file.split('.')[0])
    with open(save_file, "w", encoding="utf-8") as f:
      f.write(tnotes_usfm)

"""# Solution Sample Output

### Load test data (Letter to Titus: "TIT") for Sample output
"""

s = requests.get(src_path + src_files[3:4][0]).content
tnotes = pd.read_csv(io.StringIO(s.decode('utf-8')), delimiter=sep)

"""### Display sample records in DataFrame"""

tnotes.head(20)

"""### Describe dataset"""

"Books", tnotes.Book.unique(), "Chapters", tnotes.Chapter.unique()

"""### DataFrame column types"""

tnotes.dtypes

"""### Grouped by Book, Chapter and Verse"""

tnotes.groupby(group_by_cols).describe().head(20)

"""### Iterate through each file and apply the function"""

print(df_to_usfm(tnotes, sep_group=True))    # This function can be used in the loop above where we read the data from input tsv files