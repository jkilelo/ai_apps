#!/usr/bin/env python3
"""Fix the ordering issue in data_types.py - ExtendedCrawlResult must come after BrowserExtractionResult"""

import re

with open('data_types.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and extract ExtendedCrawlResult class
extended_crawl_pattern = r'(    class ExtendedCrawlResult\(BaseModel\):.*?errors: List\[str\] = Field\(default_factory=list, description="Errors encountered during crawl"\)\n)'
extended_crawl_match = re.search(extended_crawl_pattern, content, re.DOTALL)

if extended_crawl_match:
    extended_crawl_class = extended_crawl_match.group(1)
    
    # Remove ExtendedCrawlResult from its current position
    content = content.replace(extended_crawl_class + '\n', '')
    
    # Find the end of BrowserExtractionResult class
    browser_result_end_pattern = r'(    class BrowserExtractionResult\(BaseModel\):.*?extraction_strategy: Optional\[ExtractionStrategy\] = None\n)'
    browser_result_match = re.search(browser_result_end_pattern, content, re.DOTALL)
    
    if browser_result_match:
        # Insert ExtendedCrawlResult after BrowserExtractionResult
        insert_pos = browser_result_match.end()
        content = content[:insert_pos] + '\n' + extended_crawl_class + '\n' + content[insert_pos:]
        
        with open('data_types.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("SUCCESS: Moved ExtendedCrawlResult after BrowserExtractionResult")
    else:
        print("ERROR: Could not find BrowserExtractionResult class")
else:
    print("ERROR: Could not find ExtendedCrawlResult class")