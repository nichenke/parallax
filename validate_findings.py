#!/usr/bin/env python3
"""
Ground Truth Validation UI for Parallax Eval Framework

Provides a browser-based interface for human validation of design review findings.
Reads Critical findings from JSONL, presents them one-by-one for classification,
and saves validated results incrementally.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuration
INPUT_FILE = "/Users/nic/src/design-parallax/parallax/docs/reviews/parallax-review-v1/findings-v3-all.jsonl"
OUTPUT_DIR = Path("datasets/v3_review_validated")
OUTPUT_FILE = OUTPUT_DIR / "critical_findings.jsonl"
VALIDATOR_ID = "nic"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_findings():
    """Load all Critical findings from input JSONL file."""
    findings = []

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    with open(INPUT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                finding = json.loads(line)
                if finding.get('severity') == 'Critical':
                    findings.append(finding)

    return findings


def load_validated_findings():
    """Load previously validated findings if they exist."""
    if not OUTPUT_FILE.exists():
        return {}

    validated = {}
    with open(OUTPUT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                finding = json.loads(line)
                validated[finding['id']] = finding

    return validated


def save_finding(finding):
    """Save a single validated finding (append mode for auto-save)."""
    # Load existing validated findings
    validated = load_validated_findings()

    # Update or add this finding
    validated[finding['id']] = finding

    # Rewrite entire file to maintain consistency
    with open(OUTPUT_FILE, 'w') as f:
        for fid in sorted(validated.keys()):
            f.write(json.dumps(validated[fid]) + '\n')


@app.route('/')
def index():
    """Serve the validation UI."""
    return render_template('index.html')


@app.route('/api/findings', methods=['GET'])
def get_findings():
    """Return all Critical findings with validation status."""
    try:
        critical_findings = load_findings()
        validated = load_validated_findings()

        # Merge validation status into findings
        for finding in critical_findings:
            fid = finding['id']
            if fid in validated:
                finding.update({
                    'validated': validated[fid].get('validated'),
                    'validation_status': validated[fid].get('validation_status'),
                    'validation_notes': validated[fid].get('validation_notes'),
                    'validator_id': validated[fid].get('validator_id'),
                    'validation_date': validated[fid].get('validation_date')
                })
            else:
                finding['validated'] = False

        return jsonify({
            'success': True,
            'findings': critical_findings,
            'total': len(critical_findings)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate_finding():
    """Save a validated finding."""
    try:
        data = request.json

        # Create validated finding object
        validated_finding = {
            # Original fields
            'id': data['id'],
            'title': data['title'],
            'issue': data['issue'],
            'suggestion': data['suggestion'],
            'severity': data['severity'],
            'reviewer': data.get('reviewer'),
            'confidence': data.get('confidence'),

            # Validation fields
            'validated': True,
            'validation_status': data['validation_status'],
            'validation_notes': data.get('validation_notes', ''),
            'validator_id': VALIDATOR_ID,
            'validation_date': datetime.now().strftime('%Y-%m-%d')
        }

        # Save incrementally
        save_finding(validated_finding)

        return jsonify({
            'success': True,
            'message': 'Finding validated and saved'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Return validation summary statistics."""
    try:
        validated = load_validated_findings()

        stats = {
            'real_flaw': 0,
            'false_positive': 0,
            'ambiguous': 0,
            'total_validated': len(validated)
        }

        for finding in validated.values():
            status = finding.get('validation_status', '')
            if status in stats:
                stats[status] += 1

        total_findings = len(load_findings())
        stats['remaining'] = total_findings - stats['total_validated']
        stats['total'] = total_findings

        return jsonify({
            'success': True,
            'summary': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print(f"Loading findings from: {INPUT_FILE}")
    print(f"Output will be saved to: {OUTPUT_FILE}")
    print("\nStarting validation UI on http://localhost:5000")
    print("Press Ctrl+C to stop\n")

    app.run(debug=True, port=5000)
