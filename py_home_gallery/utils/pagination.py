"""
Pagination utilities for Py Home Gallery.

This module contains utility functions for handling pagination
in gallery views.
"""

from typing import List, Tuple, TypeVar, Dict, Optional

T = TypeVar('T')


def paginate_items(items: List[T], page: int, items_per_page: int) -> Tuple[List[T], int]:
    """
    Paginate a list of items.
    
    Args:
        items: The list of items to paginate
        page: The current page number (1-based)
        items_per_page: Number of items per page
        
    Returns:
        tuple: (paginated_items, total_pages)
    """
    start = (page - 1) * items_per_page
    end = start + items_per_page
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    return items[start:end], total_pages


def get_pagination_info(total_items: int, page: int, items_per_page: int) -> Dict[str, Optional[int]]:
    """
    Get pagination information.
    
    Args:
        total_items: Total number of items
        page: Current page number (1-based)
        items_per_page: Number of items per page
        
    Returns:
        dict: Pagination information containing:
            - total_items: Total number of items
            - total_pages: Total number of pages
            - page: Current page number
            - items_per_page: Items per page
            - has_prev: Whether there is a previous page
            - has_next: Whether there is a next page
            - prev_page: Previous page number (or None)
            - next_page: Next page number (or None)
    """
    total_pages = (total_items + items_per_page - 1) // items_per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return {
        'total_items': total_items,
        'total_pages': total_pages,
        'page': page,
        'items_per_page': items_per_page,
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_page': page - 1 if has_prev else None,
        'next_page': page + 1 if has_next else None,
    }
