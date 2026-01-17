# BibTeX Bibliography Cleaner

A comprehensive Python script for cleaning and formatting BibTeX bibliography files.

## Features

This script performs three main operations:

1. **Journal Title Capitalization**: Converts journal names to proper title case and wraps them in double braces to preserve capitalization
2. **Field Removal**: Removes unwanted fields (DOI, URL, file paths, abstracts, etc.) to create cleaner, publication-ready bibliographies
3. **Surname Uppercasing** (optional): Converts author/editor surnames to uppercase using `\MakeUppercase{}`

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)

## Usage

### Basic Usage

```bash
# Full cleaning (journal titles + remove fields)
python clean_bibliography.py input.bib output.bib

# Example
python clean_bibliography.py doc/ref.bib doc/ref_cleaned.bib
```

### Advanced Options

```bash
# Include uppercase surnames
python clean_bibliography.py doc/ref.bib doc/ref_cleaned.bib --uppercase-surnames

# Only fix journal titles (keep all fields)
python clean_bibliography.py doc/ref.bib doc/ref_cleaned.bib --journals-only

# Only remove fields (don't touch journal titles)
python clean_bibliography.py doc/ref.bib doc/ref_cleaned.bib --remove-fields-only

# Custom fields to remove
python clean_bibliography.py doc/ref.bib doc/ref_cleaned.bib --fields doi,url,abstract
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `input` | Input .bib file (required) |
| `output` | Output .bib file (required) |
| `--uppercase-surnames` | Uppercase author/editor surnames using `\MakeUppercase` |
| `--journals-only` | Only fix journal titles (skip field removal) |
| `--remove-fields-only` | Only remove fields (skip journal title fixing) |
| `--fields FIELDS` | Comma-separated list of fields to remove (overrides defaults) |
| `--help` | Show help message |

## Default Fields Removed

By default, the script removes these fields:

- `doi` - Digital Object Identifiers
- `url` - Web URLs
- `urldate` - Date URLs were accessed
- `eprint` / `eprinttype` - Preprint identifiers
- `archiveprefix` - Archive information
- `file` - Local file paths
- `abstract` - Paper abstracts
- `keywords` - Keywords
- `issn` / `isbn` - Serial numbers
- `language` - Language tags
- `shorttitle` - Short titles
- `annotation` - Annotations
- `note` - Notes

## Examples

### Example 1: Full Cleaning

**Input:**
```bibtex
@article{acemoglu1998,
  title = {Technical Change and Inequality},
  author = {Acemoglu, Daron},
  year = 1998,
  journal = {The quarterly journal of economics},
  volume = {113},
  doi = {10.1162/003355398555531},
  url = {https://doi.org/10.1162/003355398555531},
  urldate = {2025-01-17},
  file = {/Users/me/Papers/Acemoglu1998.pdf},
  language = {en}
}
```

**Command:**
```bash
python clean_bibliography.py input.bib output.bib
```

**Output:**
```bibtex
@article{acemoglu1998,
  title = {Technical Change and Inequality},
  author = {Acemoglu, Daron},
  year = 1998,
  journal = {{The Quarterly Journal of Economics}},
  volume = {113}
}
```

### Example 2: With Uppercase Surnames

**Command:**
```bash
python clean_bibliography.py input.bib output.bib --uppercase-surnames
```

**Output:**
```bibtex
@article{acemoglu1998,
  title = {Technical Change and Inequality},
  author = {{\MakeUppercase{Acemoglu}}, Daron},
  year = 1998,
  journal = {{The Quarterly Journal of Economics}},
  volume = {113}
}
```

This renders as: **ACEMOGLU**, Daron (1998) "Technical Change and Inequality"

## Output Statistics

The script provides detailed statistics:

```
======================================================================
BibTeX Bibliography Cleaner
======================================================================
Input:  doc/ref.bib
Output: doc/ref_cleaned.bib
----------------------------------------------------------------------
✓ Fixed 132 journal title(s)
✓ Uppercased 170 author/editor surname(s)
✓ Removed 421 unwanted field entries
----------------------------------------------------------------------
✓ Successfully cleaned bibliography!
✓ File size reduced by 54,095 bytes (47.0%)
✓ Output written to: doc/ref_cleaned.bib
======================================================================
```

## Journal Title Capitalization Rules

The script applies intelligent title case:

- **Capitalizes**: First word, proper nouns, major words
- **Lowercase**: Articles (a, an, the), conjunctions (and, or), prepositions (of, in, to)
- **Preserves**: Acronyms (US, GDP, AI, CEO, etc.)
- **Protects**: Uses double braces `{{...}}` to prevent BibTeX from changing case

Examples:
- `the quarterly journal of economics` → `{{The Quarterly Journal of Economics}}`
- `journal of political economy` → `{{Journal of Political Economy}}`
- `american economic review` → `{{American Economic Review}}`

## Troubleshooting

### Issue: Journal titles still showing wrong case

**Solution**: Make sure you're using the cleaned `.bib` file in your LaTeX document:
```latex
\bibliography{ref_cleaned}  % Not ref_cleaned.bib
```

### Issue: Surnames not appearing in uppercase

**Solution**: If you used `--uppercase-surnames`, make sure your bibliography style supports `\MakeUppercase`. Most modern styles do, but you may need to compile multiple times:
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Issue: Some fields I want to keep are being removed

**Solution**: Use the `--fields` option to specify exactly which fields to remove:
```bash
python clean_bibliography.py input.bib output.bib --fields doi,url
```

## Integration with LaTeX

After cleaning your bibliography:

1. Update your `.tex` file to use the cleaned file:
   ```latex
   \bibliography{ref_cleaned}
   ```

2. Compile multiple times:
   ```bash
   pdflatex main.tex
   bibtex main
   pdflatex main.tex
   pdflatex main.tex
   ```

3. Your bibliography should now appear clean and properly formatted!

## Version History

- **v1.0** (2026-01-17): Initial release
  - Journal title capitalization
  - Field removal
  - Optional surname uppercasing
  - Comprehensive documentation

## Author

Generated for bibliography management and formatting in economics research papers.

## License

Free to use and modify for academic and research purposes.

