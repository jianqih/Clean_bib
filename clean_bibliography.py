#!/usr/bin/env python3
"""
Comprehensive BibTeX Bibliography Cleaner

This script performs multiple cleaning operations on BibTeX files:
1. Capitalizes journal titles (title case)
2. Removes unwanted fields (DOI, URL, file paths, etc.)

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

def title_case_journal(journal_name):
    """
    Apply title case to journal names, with special handling for common words.
    """
    # Remove existing braces
    journal_name = re.sub(r'[{}]', '', journal_name)
    
    # Words that should stay lowercase (unless at the beginning)
    lowercase_words = {
        'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'of', 
        'on', 'or', 'the', 'to', 'with', 'from', 'into', 'via', 'nor'
    }
    
    # Words that should stay uppercase
    uppercase_words = {'US', 'USA', 'UK', 'EU', 'NBER', 'CEO', 'GDP', 'AI', 'IT', 'R&D', 'OECD'}
    
    # Abbreviations that are typically all caps
    abbrev_pattern = re.compile(r'\b[A-Z]{2,}\b')
    
    words = journal_name.split()
    result = []
    
    for i, word in enumerate(words):
        # Check if it's an abbreviation or special uppercase word
        if word.upper() in uppercase_words or abbrev_pattern.match(word):
            result.append(word.upper())
        # First word or word after colon/dash should always be capitalized
        elif i == 0 or (i > 0 and words[i-1][-1] in ':—-'):
            result.append(word.capitalize())
        # Check if it should be lowercase
        elif word.lower() in lowercase_words:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    
    return ' '.join(result)


def fix_journal_titles(content):
    """
    Fix journal title capitalization in BibTeX content.
    Returns: (modified_content, count_of_changes)
    """
    # Pattern to match journal entries
    pattern = re.compile(
        r'(\s*journal\s*=\s*)([{""])([^}"]+)([}"])',
        re.IGNORECASE
    )
    
    def replace_journal(match):
        prefix = match.group(1)
        opening = match.group(2)
        journal_text = match.group(3)
        closing = match.group(4)
        
        # Apply title case
        fixed_title = title_case_journal(journal_text.strip())
        
        # Wrap in double braces to preserve capitalization
        if opening == '{':
            return f'{prefix}{{{{{fixed_title}}}}}'
        else:  # opening == '"'
            return f'{prefix}"{{{{{fixed_title}}}}}"'
    
    # Count original journals
    original_journals = pattern.findall(content)
    
    # Replace all journal entries
    fixed_content = pattern.sub(replace_journal, content)
    
    return fixed_content, len(original_journals)


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
