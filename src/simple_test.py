#!/usr/bin/env python3
"""
Simple text search and similarity test without txtai
This demonstrates basic text processing and search functionality
"""

import re
from difflib import SequenceMatcher
from collections import Counter
import json

# Sample data (same as your original test)
data = [
    "US tops 5 million confirmed virus cases",
    "Canada's last fully intact ice shelf has suddenly collapsed, forming a Manhattan-sized iceberg",
    "Beijing mobilises invasion craft along coast as Taiwan tensions escalate",
    "The National Park Service warns against sacrificing slower friends in a bear attack",
    "Maine man wins $1M from $25 lottery ticket",
    "Make huge profits without work, earn up to $100,000 a day"
]

def simple_search(query, texts, threshold=0.3):
    """Simple text search using keyword matching and similarity"""
    query_lower = query.lower()
    results = []
    
    for i, text in enumerate(texts):
        text_lower = text.lower()
        
        # Keyword matching
        query_words = set(query_lower.split())
        text_words = set(text_lower.split())
        keyword_score = len(query_words.intersection(text_words)) / len(query_words)
        
        # String similarity
        similarity_score = SequenceMatcher(None, query_lower, text_lower).ratio()
        
        # Combined score
        combined_score = (keyword_score * 0.7) + (similarity_score * 0.3)
        
        if combined_score > threshold:
            results.append((i, text, combined_score))
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x[2], reverse=True)
    return results

def search_by_category(query, texts):
    """Search by semantic categories"""
    categories = {
        'health': ['virus', 'cases', 'health', 'medical', 'disease'],
        'climate': ['ice', 'shelf', 'climate', 'environment', 'collapse'],
        'politics': ['beijing', 'invasion', 'taiwan', 'mobilises', 'tensions'],
        'nature': ['park', 'bear', 'wildlife', 'nature', 'service'],
        'money': ['wins', 'lottery', 'profits', 'earn', 'million', 'dollar'],
        'positive': ['wins', 'good', 'success', 'happy', 'lucky']
    }
    
    query_lower = query.lower()
    matches = []
    
    for i, text in enumerate(texts):
        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                if any(keyword in query_lower for keyword in keywords):
                    matches.append((i, text, category))
    
    return matches

def main():
    print("Simple Text Search Test")
    print("=" * 50)
    
    # Test queries
    queries = [
        "feel good story",
        "climate change", 
        "public health story",
        "war",
        "wildlife",
        "asia",
        "lucky",
        "dishonest junk"
    ]
    
    print("%-20s %s" % ("Query", "Best Match"))
    print("-" * 50)
    
    for query in queries:
        # Try simple search first
        results = simple_search(query, data)
        
        if results:
            best_match = results[0]
            print("%-20s %s" % (query, best_match[1]))
        else:
            # Fallback to category search
            category_matches = search_by_category(query, data)
            if category_matches:
                print("%-20s %s" % (query, category_matches[0][1]))
            else:
                print("%-20s %s" % (query, "No match found"))

if __name__ == "__main__":
    main()
