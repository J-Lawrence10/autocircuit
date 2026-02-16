#!/usr/bin/env python3
"""
AI-Assisted Feature Annotation Tool

Uses decision tree logic to automatically suggest categories, confidence levels,
and notes for each feature. User can review and approve/modify suggestions.

Usage:
    python annotate_features_assisted.py --input ../semantic_taxonomy_annotations.csv --output ../semantic_taxonomy_annotations_completed.csv
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class FeatureAnnotationAssistant:
    """AI-powered assistant for semantic taxonomy annotation."""

    def __init__(self):
        self.syntax_indicators = {
            'special_tokens': ['<bos>', '<eos>', '<pad>', '<unk>', '▁'],
            'punctuation': ['{', '}', '[', ']', '(', ')', ';', ':', ',', '.', '!', '?'],
            'code_syntax': ['def', 'class', 'import', 'return', 'if', 'for', 'while'],
            'brackets': ['{{', '}}', '[[', ']]', '((', '))'],
            'operators': ['++', '--', '&&', '||', '==', '!=', '<=', '>=']
        }

        self.semantic_indicators = {
            'geographic': ['country', 'city', 'capital', 'north', 'south', 'east', 'west',
                          'border', 'located', 'geographic', 'جغرافيا', 'Geografia'],
            'temporal': ['time', 'day', 'year', 'hour', 'before', 'after', 'during',
                        'yesterday', 'tomorrow', 'century', 'decade'],
            'entity': ['person', 'people', 'president', 'staff', 'leader', 'organization',
                      'company', 'Personensuche', 'Personendaten'],
            'concept': ['incoming', 'coming', 'assume', 'consider', 'means', 'network',
                       'front', 'side', 'free', 'practical'],
            'code': ['Command', 'Builder', 'Helper', 'Style', 'Init', 'Create', 'Write',
                    'Read', 'Get', 'Set', 'Add', 'Delete', 'Update', 'Query', 'Interface']
        }

    def analyze_feature(self, activation_examples: str, activation_count: int) -> Dict:
        """
        Apply decision tree to analyze a feature.

        Returns dict with:
        - category: SYNTAX | SEMANTICS:* | POLYSEMANTIC
        - confidence: HIGH | MEDIUM | LOW
        - reasoning: List of reasons for categorization
        """
        if not activation_examples or activation_count == 0:
            return {
                'category': 'UNKNOWN',
                'confidence': 'LOW',
                'reasoning': ['No activation examples available']
            }

        examples = [ex.strip() for ex in activation_examples.split(';') if ex.strip()]

        # Q1: Is >70% syntax?
        syntax_score = self._calculate_syntax_score(examples)
        if syntax_score >= 0.7:
            return {
                'category': 'SYNTAX',
                'confidence': 'HIGH' if syntax_score >= 0.9 else 'MEDIUM',
                'reasoning': [
                    f'Q1: {syntax_score:.0%} syntax indicators (special tokens, punctuation, code syntax)',
                    f'Examples: {", ".join(examples[:3])}'
                ]
            }

        # Q2: Is >70% semantic with coherent theme?
        semantic_result = self._calculate_semantic_score(examples)
        if semantic_result['score'] >= 0.7:
            subcategory = semantic_result['dominant_type']
            confidence = 'HIGH' if semantic_result['score'] >= 0.9 else 'MEDIUM'

            return {
                'category': f'SEMANTICS:{subcategory.upper()}',
                'confidence': confidence,
                'reasoning': [
                    f'Q2: {semantic_result["score"]:.0%} semantic content with {subcategory} theme',
                    f'Examples: {", ".join(examples[:3])}',
                    f'Pattern: {semantic_result["explanation"]}'
                ]
            }

        # Q3: Mix of syntax AND semantics?
        if syntax_score > 0.2 and semantic_result['score'] > 0.2:
            return {
                'category': 'POLYSEMANTIC',
                'confidence': 'MEDIUM',
                'reasoning': [
                    f'Q3: Mixed signals - {syntax_score:.0%} syntax, {semantic_result["score"]:.0%} semantics',
                    f'Examples: {", ".join(examples[:3])}',
                    'Contains both structural and semantic patterns'
                ]
            }

        # Q4: Multiple unrelated semantic domains?
        if self._has_multiple_semantic_domains(examples):
            return {
                'category': 'POLYSEMANTIC',
                'confidence': 'MEDIUM',
                'reasoning': [
                    'Q4: Multiple unrelated semantic domains detected',
                    f'Examples: {", ".join(examples[:3])}',
                    'No coherent theme across examples'
                ]
            }

        # Default: Lean toward semantics if examples are words
        if all(self._is_word_like(ex) for ex in examples):
            # Try to infer subcategory
            subcategory = semantic_result['dominant_type'] if semantic_result['dominant_type'] else 'CONCEPT'
            return {
                'category': f'SEMANTICS:{subcategory.upper()}',
                'confidence': 'LOW',
                'reasoning': [
                    'Default: Word-like examples without clear pattern',
                    f'Examples: {", ".join(examples[:3])}',
                    f'Tentative classification as {subcategory}'
                ]
            }
        else:
            return {
                'category': 'POLYSEMANTIC',
                'confidence': 'LOW',
                'reasoning': [
                    'Unclear pattern - mixed or ambiguous examples',
                    f'Examples: {", ".join(examples[:3])}'
                ]
            }

    def _calculate_syntax_score(self, examples: List[str]) -> float:
        """Calculate what percentage of examples are syntax-related."""
        if not examples:
            return 0.0

        syntax_count = 0
        for example in examples:
            # Check special tokens
            if any(token in example for token in self.syntax_indicators['special_tokens']):
                syntax_count += 1
                continue

            # Check if mostly punctuation (>50% of characters)
            if example:
                punct_chars = sum(1 for c in example if not c.isalnum() and not c.isspace())
                if punct_chars / len(example) > 0.5:
                    syntax_count += 1
                    continue

            # Check code syntax keywords
            if any(keyword in example.lower() for keyword in self.syntax_indicators['code_syntax']):
                syntax_count += 1
                continue

        return syntax_count / len(examples)

    def _calculate_semantic_score(self, examples: List[str]) -> Dict:
        """
        Calculate semantic score and identify dominant semantic type.

        Returns:
        - score: 0.0-1.0 (how semantic vs syntax)
        - dominant_type: geographic | temporal | entity | concept | code
        - explanation: Why this type was chosen
        """
        if not examples:
            return {'score': 0.0, 'dominant_type': None, 'explanation': 'No examples'}

        # Count semantic indicators by type
        type_counts = {
            'geographic': 0,
            'temporal': 0,
            'entity': 0,
            'concept': 0,
            'code': 0
        }

        for example in examples:
            example_lower = example.lower()

            # Check each semantic type
            for sem_type, indicators in self.semantic_indicators.items():
                if any(indicator.lower() in example_lower for indicator in indicators):
                    type_counts[sem_type] += 1

        # Find dominant type
        total_semantic_signals = sum(type_counts.values())

        if total_semantic_signals == 0:
            # No clear semantic indicators, check if code-like
            if self._is_code_identifier(examples):
                return {
                    'score': 0.7,
                    'dominant_type': 'code',
                    'explanation': 'Programming identifiers (camelCase/PascalCase patterns)'
                }

            # Check if multilingual
            if self._is_multilingual(examples):
                return {
                    'score': 0.8,
                    'dominant_type': 'concept',
                    'explanation': 'Multilingual text - likely semantic content'
                }

            return {
                'score': 0.5,
                'dominant_type': 'concept',
                'explanation': 'General semantic content without specific type indicators'
            }

        dominant_type = max(type_counts.items(), key=lambda x: x[1])[0]
        dominant_count = type_counts[dominant_type]

        # Score based on how many examples match dominant type
        score = dominant_count / len(examples)

        # Explanation
        matching_examples = [ex for ex in examples
                            if any(ind.lower() in ex.lower()
                                  for ind in self.semantic_indicators[dominant_type])]

        explanation = f'{dominant_type} indicators in {dominant_count}/{len(examples)} examples'
        if matching_examples:
            explanation += f' (e.g., "{matching_examples[0]}")'

        return {
            'score': score,
            'dominant_type': dominant_type,
            'explanation': explanation
        }

    def _has_multiple_semantic_domains(self, examples: List[str]) -> bool:
        """Check if examples span multiple unrelated semantic domains."""
        type_counts = {sem_type: 0 for sem_type in self.semantic_indicators.keys()}

        for example in examples:
            example_lower = example.lower()
            for sem_type, indicators in self.semantic_indicators.items():
                if any(indicator.lower() in example_lower for indicator in indicators):
                    type_counts[sem_type] += 1

        # Multiple domains if 2+ types each have examples
        active_domains = sum(1 for count in type_counts.values() if count > 0)
        return active_domains >= 2

    def _is_word_like(self, text: str) -> bool:
        """Check if text looks like a word rather than syntax."""
        if not text:
            return False

        # Remove leading/trailing punctuation
        text_clean = text.strip('.,;:!?()[]{}')

        # Must have some alphanumeric content
        if not any(c.isalnum() for c in text_clean):
            return False

        # Check if mostly letters (>60%)
        letter_count = sum(1 for c in text_clean if c.isalpha())
        if text_clean and letter_count / len(text_clean) > 0.6:
            return True

        return False

    def _is_code_identifier(self, examples: List[str]) -> bool:
        """Check if examples follow code identifier patterns."""
        code_patterns = [
            r'^[a-z]+[A-Z]',  # camelCase
            r'^[A-Z][a-z]+[A-Z]',  # PascalCase
            r'[A-Z_]+$',  # UPPER_SNAKE_CASE
            r'[a-z_]+$',  # lower_snake_case
        ]

        code_count = 0
        for example in examples:
            if any(re.search(pattern, example) for pattern in code_patterns):
                code_count += 1

        return code_count / len(examples) > 0.5 if examples else False

    def _is_multilingual(self, examples: List[str]) -> bool:
        """Check if examples contain non-Latin scripts (likely multilingual)."""
        non_latin_count = 0
        for example in examples:
            # Check for non-Latin Unicode ranges
            if any(ord(c) > 127 and c.isalpha() for c in example):
                non_latin_count += 1

        return non_latin_count > 0

    def generate_notes(self, category: str, confidence: str, reasoning: List[str],
                      auto_category: str) -> str:
        """Generate concise notes based on analysis."""
        notes_parts = []

        # Add main reasoning (first item)
        if reasoning:
            notes_parts.append(reasoning[0].replace('Q1: ', '').replace('Q2: ', '').replace('Q3: ', '').replace('Q4: ', ''))

        # Add confidence qualifier if not HIGH
        if confidence == 'MEDIUM':
            notes_parts.append('Some ambiguity in examples.')
        elif confidence == 'LOW':
            notes_parts.append('Low confidence - unclear pattern.')

        # Note disagreement with auto_category
        if category != auto_category:
            notes_parts.append(f'Disagree with auto ({auto_category}).')

        return ' '.join(notes_parts)


def annotate_csv_interactive(input_file: Path, output_file: Path, start_row: int = 2):
    """
    Interactively annotate CSV with AI assistance.

    Args:
        input_file: Path to input CSV
        output_file: Path to output CSV (will be updated progressively)
        start_row: Row number to start from (2 = skip header, start at first feature)
    """
    assistant = FeatureAnnotationAssistant()

    # Read CSV
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print("=" * 80)
    print("AI-ASSISTED FEATURE ANNOTATION")
    print("=" * 80)
    print(f"\nTotal features: {len(rows)}")
    print(f"Starting from row {start_row} (feature #{start_row - 1})")
    print("\nCommands:")
    print("  [Enter]  - Accept suggestion")
    print("  m <cat>  - Modify category (e.g., 'm SEMANTICS:TEMPORAL')")
    print("  c <conf> - Modify confidence (e.g., 'c LOW')")
    print("  n <text> - Modify notes (e.g., 'n Different reasoning here')")
    print("  s        - Skip this feature")
    print("  q        - Quit and save progress")
    print("\n" + "=" * 80 + "\n")

    annotated_count = 0
    skipped_features = []

    for idx, row in enumerate(rows[start_row - 2:], start=start_row):  # Adjust for 0-indexing
        feature_label = row['feature_label']
        layer = row['layer']
        feature_id = row['feature_id']
        activation_examples = row['activation_examples']
        activation_count = int(row['activation_count']) if row['activation_count'] else 0
        auto_category = row['auto_category']

        # Skip if already annotated
        if row.get('manual_category') and row.get('confidence') and row.get('notes'):
            print(f"[{idx}/{len(rows) + 1}] {feature_label} - ALREADY ANNOTATED (skipping)")
            annotated_count += 1
            continue

        # Get AI suggestion
        analysis = assistant.analyze_feature(activation_examples, activation_count)
        suggested_category = analysis['category']
        suggested_confidence = analysis['confidence']
        suggested_notes = assistant.generate_notes(
            suggested_category,
            suggested_confidence,
            analysis['reasoning'],
            auto_category
        )

        # Display feature info
        print(f"\n[{idx}/{len(rows) + 1}] {feature_label} (Layer {layer})")
        print("-" * 80)
        print(f"Examples: {activation_examples}")
        print(f"Count: {activation_count}")
        print(f"Auto Category: {auto_category}")
        print("\nAI SUGGESTION:")
        print(f"  Category:   {suggested_category}")
        print(f"  Confidence: {suggested_confidence}")
        print(f"  Notes:      {suggested_notes}")
        print("\nReasoning:")
        for reason in analysis['reasoning']:
            print(f"  - {reason}")
        print("-" * 80)

        # Get user input
        while True:
            user_input = input("\nAction ([Enter]=accept, m/c/n=modify, s=skip, q=quit): ").strip()

            if user_input == '':
                # Accept suggestion
                row['manual_category'] = suggested_category
                row['confidence'] = suggested_confidence
                row['notes'] = suggested_notes
                annotated_count += 1
                print(f"✓ Accepted suggestion for {feature_label}")
                break

            elif user_input.lower() == 's':
                # Skip
                skipped_features.append(feature_label)
                print(f"⊘ Skipped {feature_label}")
                break

            elif user_input.lower() == 'q':
                # Quit
                print(f"\nQuitting. Progress saved to {output_file}")
                save_csv(rows, output_file)
                print(f"\nAnnotated: {annotated_count}/{len(rows)}")
                print(f"Skipped: {len(skipped_features)}")
                return

            elif user_input.lower().startswith('m '):
                # Modify category
                new_category = user_input[2:].strip().upper()
                suggested_category = new_category
                print(f"  → Category changed to: {suggested_category}")

            elif user_input.lower().startswith('c '):
                # Modify confidence
                new_confidence = user_input[2:].strip().upper()
                if new_confidence in ['HIGH', 'MEDIUM', 'LOW']:
                    suggested_confidence = new_confidence
                    print(f"  → Confidence changed to: {suggested_confidence}")
                else:
                    print(f"  ✗ Invalid confidence. Use HIGH, MEDIUM, or LOW.")

            elif user_input.lower().startswith('n '):
                # Modify notes
                new_notes = user_input[2:].strip()
                suggested_notes = new_notes
                print(f"  → Notes changed to: {suggested_notes}")

            else:
                print("  ✗ Invalid command. Try again.")

        # Save progress every 5 annotations
        if annotated_count % 5 == 0:
            save_csv(rows, output_file)
            print(f"  [Progress saved: {annotated_count}/{len(rows)}]")

    # Final save
    save_csv(rows, output_file)
    print("\n" + "=" * 80)
    print("ANNOTATION COMPLETE!")
    print("=" * 80)
    print(f"Annotated: {annotated_count}/{len(rows)}")
    print(f"Skipped: {len(skipped_features)}")
    if skipped_features:
        print(f"\nSkipped features: {', '.join(skipped_features)}")
    print(f"\nOutput saved to: {output_file}")


def save_csv(rows: List[Dict], output_file: Path):
    """Save annotated rows to CSV."""
    if not rows:
        return

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(
        description='AI-assisted feature annotation with decision tree logic'
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
        '--start-row',
        type=int,
        default=2,
        help='Row number to start from (default: 2, first feature after header)'
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    annotate_csv_interactive(args.input, args.output, args.start_row)


if __name__ == '__main__':
    main()
