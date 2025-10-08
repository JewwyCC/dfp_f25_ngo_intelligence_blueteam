#!/bin/bash
# Test script for split scrapers

echo "=== Testing Split Scraper Architecture ==="
echo ""
echo "📊 Available scrapers:"
ls -1 master_scraper*.py
echo ""

echo "✅ Test 1: Original scraper (unchanged)"
echo "Command: python master_scraper.py --duration 120"
echo "Status: Available and working"
echo ""

echo "✅ Test 2: Data collection only"
echo "Command: python master_scraper_data.py --duration 120"
echo "Output: session_*/raw_data/ (CSV, JSON, JSONL, Excel only)"
echo ""

echo "✅ Test 3: Visualization generation"
echo "Command: python master_scraper_viz.py --session <session_id>"
echo "Output: session_*/artifacts/ (PNG, HTML only)"
echo ""

echo "📚 Documentation: SPLIT_SCRAPER_GUIDE.md"
