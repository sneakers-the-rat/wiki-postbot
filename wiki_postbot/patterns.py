"""
Regex patterns
"""
import re

WIKILINK = re.compile(r'\[\[(.*?)\]\]', re.IGNORECASE)