#!/usr/bin/env python3
"""
Automatic Feature Annotation Tool

Uses decision tree logic to automatically annotate all features.
User can review the results afterward and make corrections.

Usage:
    python annotate_features_auto.py --input ../semantic_taxonomy_annotations.csv --output ../semantic_taxonomy_annotations_auto.csv
"""

import argparse
import csv
import sys
import io
from pathlib import Path
from typing import List, Dict

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Import the decision tree logic from the assisted version
import importlib.util
spec = importlib.util.spec_from_file_location(
    "annotate_assisted",
    Path(__file__).parent / "annotate_features_assisted.py"
)
annotate_assisted = importlib.util.module_from_spec(spec)
spec.loader.exec_module(annotate_assisted)

FeatureAnnotationAssistant = annotate_assisted.FeatureAnnotationAssistant


def annotate_csv_automatic(input_file: Path, output_file: Path):
    """
    Automatically annotate all features in CSV using decision tree.

    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV
    """
    assistant = FeatureAnnotationAssistant()

    # Read CSV
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print("=" * 80)
    print("AUTOMATIC FEATURE ANNOTATION")
    print("=" * 80)
    print(f"\nTotal features: {len(rows)}")
    print("Applying decision tree to all features...\n")

    annotated_count = 0
    category_counts = {}

    for idx, row in enumerate(rows, start=1):
        feature_label = row['feature_label']
        activation_examples = row['activation_examples']
        activation_count = int(row['activation_count']) if row['activation_count'] else 0
        auto_category = row['auto_category']

        # Skip if already annotated
        if row.get('manual_category') and row.get('confidence') and row.get('notes'):
            print(f"[{idx}/{len(rows)}] {feature_label} - ALREADY ANNOTATED (skipping)")
            annotated_count += 1
            category = row['manual_category']
            category_counts[category] = category_counts.get(category, 0) + 1
            continue

        # Get AI annotation
        analysis = assistant.analyze_feature(activation_examples, activation_count)
        category = analysis['category']
        confidence = analysis['confidence']
        notes = assistant.generate_notes(category, confidence, analysis['reasoning'], auto_category)

        # Update row
        row['manual_category'] = category
        row['confidence'] = confidence
        row['notes'] = notes

        # Track stats
        annotated_count += 1
        category_counts[category] = category_counts.get(category, 0) + 1

        # Display progress
        status_symbol = "✓" if confidence == "HIGH" else "~" if confidence == "MEDIUM" else "?"
        agreement = "✓" if category == auto_category else "✗"
        print(f"[{idx}/{len(rows)}] {status_symbol} {feature_label}: {category} ({confidence}) [Auto:{agreement}]")

    # Save results
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "=" * 80)
    print("ANNOTATION COMPLETE!")
    print("=" * 80)
    print(f"\nAnnotated: {annotated_count}/{len(rows)}")
    print("\nCategory Distribution:")
    for category, count in sorted(category_counts.items()):
        percentage = count / annotated_count * 100
        print(f"  {category:30s}: {count:3d} ({percentage:5.1f}%)")

    print(f"\nOutput saved to: {output_file}")
    print("\nNext steps:")
    print("1. Review the annotated CSV in your spreadsheet editor")
    print("2. Look for LOW confidence annotations and verify them")
    print("3. Check disagreements with auto_category")
    print("4. Make manual corrections as needed")


def generate_annotation_summary(csv_file: Path):
    """Generate summary statistics from annotated CSV."""
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Calculate statistics
    total = len(rows)
    category_counts = {}
    confidence_counts = {}
    agreement_count = 0

    for row in rows:
        manual_cat = row.get('manual_category', '')
        confidence = row.get('confidence', '')
        auto_cat = row.get('auto_category', '')

        if manual_cat:
            category_counts[manual_cat] = category_counts.get(manual_cat, 0) + 1
        if confidence:
            confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1
        if manual_cat and auto_cat and manual_cat == auto_cat:
            agreement_count += 1

    print("\n" + "=" * 80)
    print("ANNOTATION SUMMARY")
    print("=" * 80)

    print(f"\nTotal features: {total}")

    print("\n--- Category Distribution ---")
    for category, count in sorted(category_counts.items()):
        percentage = count / total * 100
        bar_length = int(percentage / 2)
        bar = "█" * bar_length
        print(f"{category:30s}: {count:3d} ({percentage:5.1f}%) {bar}")

    print("\n--- Confidence Distribution ---")
    for confidence in ['HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']:
        count = confidence_counts.get(confidence, 0)
        percentage = count / total * 100 if total > 0 else 0
        bar_length = int(percentage / 2)
        bar = "█" * bar_length
        print(f"{confidence:10s}: {count:3d} ({percentage:5.1f}%) {bar}")

    print("\n--- Agreement with Auto-Category ---")
    agreement_rate = agreement_count / total * 100 if total > 0 else 0
    print(f"Exact matches: {agreement_count}/{total} ({agreement_rate:.1f}%)")
    if agreement_rate >= 85:
        print("✓ Target achieved (>85%)")
    else:
        print(f"⚠ Below target (need {85 - agreement_rate:.1f}pp more)")

    # Semantic sub-category breakdown
    semantic_categories = {cat: count for cat, count in category_counts.items()
                          if cat.startswith('SEMANTICS:')}
    if semantic_categories:
        print("\n--- Semantic Sub-Categories ---")
        semantic_total = sum(semantic_categories.values())
        for category, count in sorted(semantic_categories.items()):
            percentage = count / semantic_total * 100
            print(f"{category:30s}: {count:3d} ({percentage:5.1f}% of semantics)")


def main():
    parser = argparse.ArgumentParser(
        description='Automatically annotate features using decision tree logic'
    )
    parser.add_argument(
        '--input',
        type=Path,
        required=True,
        help='Input CSV file with features to annotate'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output CSV file for annotated features'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Generate summary statistics after annotation'
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Perform automatic annotation
    annotate_csv_automatic(args.input, args.output)

    # Generate summary if requested
    if args.summary:
        generate_annotation_summary(args.output)


if __name__ == '__main__':
    main()
