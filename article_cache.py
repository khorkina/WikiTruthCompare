import os
import json
import time
from collections import OrderedDict

# This is a simple in-memory cache with a TTL
class ArticleCache:
    """
    A simple in-memory cache for article content to avoid storing
    large amounts of data in the session cookie.
    """
    def __init__(self, max_size=20, ttl=3600):
        """
        Initialize the cache with a maximum size and time-to-live
        
        Args:
            max_size (int): Maximum number of items to store in the cache
            ttl (int): Time to live in seconds for cache items
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        
    def get(self, key):
        """
        Get an item from the cache
        
        Args:
            key (str): The cache key
            
        Returns:
            The cached value or None if not found or expired
        """
        if key not in self.cache:
            return None
            
        value, timestamp = self.cache[key]
        
        # Check if item has expired
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            return None
            
        # Move to the end to mark as recently used
        self.cache.move_to_end(key)
        
        return value
        
    def set(self, key, value):
        """
        Set an item in the cache
        
        Args:
            key (str): The cache key
            value: The value to store
        """
        # Remove oldest items if we're at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            self.cache.popitem(last=False)
            
        # Store item with timestamp
        self.cache[key] = (value, time.time())
        
    def delete(self, key):
        """
        Delete an item from the cache
        
        Args:
            key (str): The cache key
        """
        if key in self.cache:
            del self.cache[key]
            
    def clear(self):
        """Clear all items from the cache"""
        self.cache.clear()
        
    def generate_key(self, lang_codes, titles):
        """
        Generate a consistent key for a set of articles
        
        Args:
            lang_codes (list): List of language codes
            titles (list): List of article titles
            
        Returns:
            str: A consistent key for the articles
        """
        if len(lang_codes) != len(titles):
            raise ValueError("lang_codes and titles must have the same length")
            
        # Sort by language code to ensure consistent keys
        pairs = sorted(zip(lang_codes, titles))
        
        # Generate a string representation of the articles
        key_parts = [f"{lang}:{title}" for lang, title in pairs]
        return ":".join(key_parts)

# Create a global instance
article_cache = ArticleCache()