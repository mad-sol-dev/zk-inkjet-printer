#!/usr/bin/env python3
"""
Evidence Link Validator
Validates that evidence entries in evidence_*.md files have correct source references.
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class EvidenceValidator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.research_dir = repo_root / "research"
        self.chats_dir = self.research_dir / "Chats"

    def parse_evidence_file(self, evidence_file: Path) -> List[Dict]:
        """Parse evidence markdown file and extract entries."""
        content = evidence_file.read_text(encoding='utf-8')
        entries = []

        # Pattern to match evidence entries
        # Looks for: ### E-{SUBSYS}-{NUM}: {Title}
        entry_pattern = r'### (E-\w+-\d+):'

        current_entry = None
        for line in content.split('\n'):
            # New entry starts
            match = re.match(entry_pattern, line)
            if match:
                if current_entry:
                    entries.append(current_entry)
                current_entry = {
                    'id': match.group(1),
                    'quote': None,
                    'source': None,
                    'date': None,
                    'type': None,
                    'raw_lines': []
                }

            if current_entry:
                current_entry['raw_lines'].append(line)

                # Extract fields
                if line.startswith('- **Quote:**'):
                    current_entry['quote'] = line.replace('- **Quote:**', '').strip().strip('"')
                elif line.startswith('- **Source:**'):
                    current_entry['source'] = line.replace('- **Source:**', '').strip()
                elif line.startswith('- **Date:**'):
                    current_entry['date'] = line.replace('- **Date:**', '').strip()
                elif line.startswith('- **Type:**'):
                    current_entry['type'] = line.replace('- **Type:**', '').strip()

        # Don't forget last entry
        if current_entry:
            entries.append(current_entry)

        return entries

    def parse_source_reference(self, source: str) -> Optional[Tuple[str, int]]:
        """Parse source reference like 'Chats/833_GPT_...json#msg=2' into (filename, msg_index)."""
        if not source:
            return None

        # Pattern: Chats/{filename}#msg={number}
        match = re.search(r'Chats/([^#]+)#msg=(\d+)', source)
        if match:
            filename = match.group(1)
            msg_index = int(match.group(2))
            return (filename, msg_index)

        return None

    def validate_entry(self, entry: Dict) -> Dict:
        """Validate a single evidence entry."""
        result = {
            'id': entry['id'],
            'status': 'unknown',
            'message': '',
            'quote_found': False,
            'match_quality': 0.0
        }

        # Parse source reference
        parsed = self.parse_source_reference(entry['source'])
        if not parsed:
            result['status'] = 'error'
            result['message'] = f"Could not parse source: {entry['source']}"
            return result

        filename, msg_index = parsed
        chat_file = self.chats_dir / filename

        # Check if chat file exists
        if not chat_file.exists():
            result['status'] = 'error'
            result['message'] = f"Chat file not found: {filename}"
            return result

        # Load chat JSON
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f"Failed to load JSON: {e}"
            return result

        # Find message by index
        messages = chat_data.get('messages', [])
        target_msg = None
        for msg in messages:
            if msg.get('index') == msg_index:
                target_msg = msg
                break

        if not target_msg:
            result['status'] = 'error'
            result['message'] = f"Message index {msg_index} not found in {filename}"
            return result

        # Check if quote appears in message content
        msg_content = target_msg.get('content', '')
        quote = entry['quote']

        if not quote:
            result['status'] = 'warning'
            result['message'] = "No quote specified in evidence entry"
            return result

        # Exact match
        if quote in msg_content:
            result['status'] = 'valid'
            result['quote_found'] = True
            result['match_quality'] = 1.0
            result['message'] = "Exact quote match found"
            return result

        # Fuzzy match - check if major parts of quote appear
        # Split quote into words, check how many appear
        quote_words = [w.lower() for w in re.findall(r'\w+', quote) if len(w) > 3]
        content_lower = msg_content.lower()
        matched_words = sum(1 for word in quote_words if word in content_lower)

        if quote_words:
            match_ratio = matched_words / len(quote_words)
            result['match_quality'] = match_ratio

            if match_ratio > 0.7:
                result['status'] = 'partial'
                result['message'] = f"Partial match: {matched_words}/{len(quote_words)} key words found"
            else:
                result['status'] = 'mismatch'
                result['message'] = f"Quote not found (only {matched_words}/{len(quote_words)} words match)"
        else:
            result['status'] = 'warning'
            result['message'] = "Quote too short to validate"

        return result

    def validate_evidence_file(self, evidence_file: Path) -> Dict:
        """Validate all entries in an evidence file."""
        print(f"\n{'='*80}")
        print(f"Validating: {evidence_file.name}")
        print(f"{'='*80}\n")

        entries = self.parse_evidence_file(evidence_file)
        results = []

        stats = {
            'total': len(entries),
            'valid': 0,
            'partial': 0,
            'mismatch': 0,
            'error': 0,
            'warning': 0
        }

        for entry in entries:
            result = self.validate_entry(entry)
            results.append(result)

            status = result['status']
            if status in stats:
                stats[status] += 1

            # Print result
            status_symbol = {
                'valid': '✅',
                'partial': '⚠️ ',
                'mismatch': '❌',
                'error': '🔴',
                'warning': '⚡',
                'unknown': '❓'
            }.get(status, '?')

            print(f"{status_symbol} {result['id']:20s} | {result['message']}")

        print(f"\n{'='*80}")
        print(f"Summary: {evidence_file.name}")
        print(f"{'='*80}")
        print(f"Total entries:    {stats['total']}")
        print(f"✅ Valid:         {stats['valid']}")
        print(f"⚠️  Partial:       {stats['partial']}")
        print(f"❌ Mismatch:      {stats['mismatch']}")
        print(f"🔴 Error:         {stats['error']}")
        print(f"⚡ Warning:       {stats['warning']}")

        success_rate = (stats['valid'] + stats['partial']) / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"\nSuccess rate: {success_rate:.1f}%")

        return {
            'file': evidence_file.name,
            'stats': stats,
            'results': results
        }

def main():
    # Find repository root
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent.parent

    validator = EvidenceValidator(repo_root)

    # Find all evidence files
    evidence_dir = repo_root / "research" / "evidence"

    if not evidence_dir.exists():
        print(f"Error: Evidence directory not found at {evidence_dir}")
        sys.exit(1)

    evidence_files = list(evidence_dir.glob("evidence_*.md"))

    if not evidence_files:
        print(f"No evidence_*.md files found in {evidence_dir}")
        sys.exit(1)

    # Validate each file
    all_results = []
    for evidence_file in sorted(evidence_files):
        result = validator.validate_evidence_file(evidence_file)
        all_results.append(result)

    # Overall summary
    if len(all_results) > 1:
        print(f"\n{'='*80}")
        print(f"OVERALL SUMMARY")
        print(f"{'='*80}")
        total_entries = sum(r['stats']['total'] for r in all_results)
        total_valid = sum(r['stats']['valid'] for r in all_results)
        total_partial = sum(r['stats']['partial'] for r in all_results)
        overall_success = (total_valid + total_partial) / total_entries * 100 if total_entries > 0 else 0

        print(f"Files validated:   {len(all_results)}")
        print(f"Total entries:     {total_entries}")
        print(f"✅ Valid:          {total_valid}")
        print(f"⚠️  Partial:        {total_partial}")
        print(f"Overall success:   {overall_success:.1f}%")

if __name__ == '__main__':
    main()
