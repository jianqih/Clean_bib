#!/usr/bin/env python3
"""
Comprehensive BibTeX Bibliography Cleaner

This script performs multiple cleaning operations on BibTeX files:
1. Capitalizes journal titles (title case)
2. Capitalizes entry titles (title case)
3. Removes unwanted fields (DOI, URL, file paths, etc.)

Usage:
    python clean_bibliography.py input.bib output.bib [options]

Examples:
    # Full cleaning (journal titles + remove fields)
    python clean_bibliography.py ref.bib ref_cleaned.bib
    
    # Only fix journal titles
    python clean_bibliography.py ref.bib ref_cleaned.bib --journals-only
    
    # Only remove fields
    python clean_bibliography.py ref.bib ref_cleaned.bib --remove-fields-only
    
    # Custom fields to remove
    python clean_bibliography.py ref.bib ref_cleaned.bib --fields doi,url,abstract

Author: Generated for bibliography management
Date: 2026-01-17
"""

import re
import sys
import argparse


# =============================================================================
# JOURNAL TITLE CAPITALIZATION
# =============================================================================

LOWERCASE_WORDS = {
    'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'of',
    'on', 'or', 'the', 'to', 'with', 'from', 'into', 'via', 'nor'
}

UPPERCASE_WORDS = {'US', 'USA', 'UK', 'EU', 'NBER', 'CEO', 'GDP', 'AI', 'IT', 'R&D', 'OECD'}

ABBREV_PATTERN = re.compile(r'\b[A-Z]{2,}\b')


def title_case_text(text, capitalize_last=False):
    """
    Apply title case with common BibTeX-friendly rules.
    """
    # Remove existing braces to normalize casing
    text = re.sub(r'[{}]', '', text)
    words = text.split()
    result = []
    
    for i, word in enumerate(words):
        is_first = i == 0
        is_last = i == len(words) - 1
        # Check if it's an abbreviation or special uppercase word
        if word.upper() in UPPERCASE_WORDS or ABBREV_PATTERN.match(word):
            result.append(word.upper())
        # First word or word after colon/dash should always be capitalized
        elif is_first or (i > 0 and words[i - 1][-1] in ':—-'):
            result.append(word.capitalize())
        elif capitalize_last and is_last:
            result.append(word.capitalize())
        # Check if it should be lowercase
        elif word.lower() in LOWERCASE_WORDS:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    
    return ' '.join(result)


def normalize_bibtex_value(value):
    """
    Strip common BibTeX wrappers like quotes and outer braces.
    """
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1].strip()
    while value.startswith('{') and value.endswith('}'):
        value = value[1:-1].strip()
    return value


def fix_journal_titles(content):
    """
    Fix journal title capitalization in BibTeX content.
    Returns: (modified_content, count_of_changes)
    """
    # Pattern to match journal entries (line-based to avoid brace drift)
    pattern = re.compile(
        r'^(\s*journal\s*=\s*)(.+?)(\s*,\s*)?$',
        re.IGNORECASE | re.MULTILINE
    )
    
    def replace_journal(match):
        prefix = match.group(1)
        journal_text = match.group(2)
        trailing = match.group(3) or ''
        
        # Apply title case
        fixed_title = title_case_text(
            normalize_bibtex_value(journal_text),
            capitalize_last=False
        )
        return f'{prefix}{{{{{fixed_title}}}}}{trailing}'
    
    # Count original journals
    original_journals = pattern.findall(content)
    
    # Replace all journal entries
    fixed_content = pattern.sub(replace_journal, content)
    
    return fixed_content, len(original_journals)


def fix_title_fields(content, field_names):
    """
    Fix entry title capitalization (e.g., title, booktitle) in BibTeX content.
    Returns: (modified_content, count_of_changes)
    """
    total_matches = 0
    
    for field in field_names:
        pattern = re.compile(
            rf'^(\s*{field}\s*=\s*)(.+?)(\s*,\s*)?$',
            re.IGNORECASE | re.MULTILINE
        )
        
        def replace_title(match):
            prefix = match.group(1)
            title_text = match.group(2)
            trailing = match.group(3) or ''
            
            fixed_title = title_case_text(
                normalize_bibtex_value(title_text),
                capitalize_last=True
            )
            return f'{prefix}{{{{{fixed_title}}}}}{trailing}'
        
        total_matches += len(pattern.findall(content))
        content = pattern.sub(replace_title, content)
    
    return content, total_matches


# =============================================================================
# FIELD REMOVAL
# =============================================================================

DEFAULT_FIELDS_TO_REMOVE = [
    'doi',
    'url',
    'urldate',
    'eprint',
    'eprinttype',
    'archiveprefix',
    'file',
    'abstract',
    'keywords',
    'issn',
    'isbn',
    'language',
    'month',
    'shorttitle',
    'annotation',
    'note',
]


def remove_fields(content, fields_to_remove):
    """
    Remove specified fields from BibTeX content.
    Returns: (modified_content, count_of_removed_fields)
    """
    removed_count = 0
    
    for field in fields_to_remove:
        # Pattern for single-line fields
        pattern_simple = rf'^\s*{field}\s*=\s*[{{"]([^}}"]*)[}}"]\s*,?\s*$'
        
        # Count matches before removal
        matches_simple = re.findall(pattern_simple, content, re.MULTILINE | re.IGNORECASE)
        removed_count += len(matches_simple)
        
        # Remove single-line fields
        content = re.sub(pattern_simple, '', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Pattern for multi-line fields (more complex)
        pattern_complex = rf'^\s*{field}\s*=\s*\{{(?:[^{{}}]|\{{[^}}]*\}})*\}},?\s*\n'
        matches_complex = re.findall(pattern_complex, content, re.MULTILINE | re.IGNORECASE)
        removed_count += len(matches_complex)
        content = re.sub(pattern_complex, '', content, flags=re.MULTILINE | re.IGNORECASE)
    
    # Clean up any double blank lines that might result
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Clean up trailing commas before closing braces
    content = re.sub(r',(\s*\n\s*\})', r'\1', content)
    
    return content, removed_count


def remove_blank_lines(content):
    """
    Remove empty or whitespace-only lines from BibTeX content.
    """
    return re.sub(r'^[ \t]*\n', '', content, flags=re.MULTILINE)


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def clean_bibliography(input_file, output_file, args):
    """
    Main cleaning function that combines all operations.
    """
    print("=" * 70)
    print("BibTeX Bibliography Cleaner")
    print("=" * 70)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print("-" * 70)
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    
    # Track what was done
    operations = []
    
    # 1. Fix journal titles (unless --remove-fields-only)
    if not args.remove_fields_only:
        content, journal_count = fix_journal_titles(content)
        operations.append(f"✓ Fixed {journal_count} journal title(s)")
        print(f"✓ Fixed {journal_count} journal title(s)")
        
        # 1b. Fix entry titles unless journals-only is requested
        if not args.journals_only:
            content, title_count = fix_title_fields(content, ['title'])
            operations.append(f"✓ Fixed {title_count} entry title(s)")
            print(f"✓ Fixed {title_count} entry title(s)")
    
    # 2. Remove unwanted fields (unless --journals-only)
    if not args.journals_only:
        if args.fields:
            fields_to_remove = [f.strip() for f in args.fields.split(',')]
            print(f"✓ Removing custom fields: {', '.join(fields_to_remove)}")
        else:
            fields_to_remove = DEFAULT_FIELDS_TO_REMOVE
            print(f"✓ Removing default fields: {', '.join(DEFAULT_FIELDS_TO_REMOVE[:5])}...")
        
        content, removed_count = remove_fields(content, fields_to_remove)
        operations.append(f"✓ Removed {removed_count} unwanted field(s)")
        print(f"✓ Removed {removed_count} unwanted field entries")

    # 3. Remove blank lines left after cleaning
    content = remove_blank_lines(content)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content)
    reduction = original_length - new_length
    
    print("-" * 70)
    print(f"✓ Successfully cleaned bibliography!")
    print(f"✓ File size reduced by {reduction:,} bytes ({reduction/original_length*100:.1f}%)")
    print(f"✓ Output written to: {output_file}")
    print("=" * 70)
    print("\n⚠️  Please review the output file before using it!")
    
    return True


def main():
    """Parse arguments and run the cleaner."""
    parser = argparse.ArgumentParser(
        description='Clean and format BibTeX bibliography files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full cleaning (journal titles + remove fields)
  python clean_bibliography.py ref.bib ref_cleaned.bib
  
  # Only fix journal titles
  python clean_bibliography.py ref.bib ref_cleaned.bib --journals-only
  
  # Only remove fields
  python clean_bibliography.py ref.bib ref_cleaned.bib --remove-fields-only
  
  # Custom fields to remove
  python clean_bibliography.py ref.bib ref_cleaned.bib --fields doi,url,abstract
        """
    )
    
    parser.add_argument('input', help='Input .bib file')
    parser.add_argument('output', help='Output .bib file')
    parser.add_argument('--journals-only', action='store_true',
                        help='Only fix journal titles (skip field removal)')
    parser.add_argument('--remove-fields-only', action='store_true',
                        help='Only remove fields (skip journal title fixing)')
    parser.add_argument('--fields', type=str,
                        help='Comma-separated list of fields to remove (overrides defaults)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.journals_only and args.remove_fields_only:
        print("Error: Cannot use --journals-only and --remove-fields-only together")
        sys.exit(1)
    
    try:
        clean_bibliography(args.input, args.output, args)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
