"""
Helper functions for loading manga data from manga_data/*.json files
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def load_manga_by_slug(slug: str, manga_data_dir: Path) -> Optional[Dict]:
    """
    Load a single manga's data from manga_data/{slug}.json
    
    Args:
        slug: The manga slug (filename without .json)
        manga_data_dir: Path to the manga_data directory
        
    Returns:
        Dict with manga data or None if not found
    """
    manga_file = manga_data_dir / f"{slug}.json"
    if not manga_file.exists():
        logger.debug(f"Manga file not found: {manga_file}")
        return None
    
    try:
        with open(manga_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading manga {slug}: {e}")
        return None


def load_all_manga(manga_data_dir: Path, slugs: Optional[List[str]] = None) -> List[Dict]:
    """
    Load all manga data from manga_data directory.
    
    Args:
        manga_data_dir: Path to the manga_data directory
        slugs: Optional list of slugs to load. If None, loads all.
        
    Returns:
        List of manga dictionaries
    """
    all_manga = []
    
    if slugs:
        # Load only specified slugs
        for slug in slugs:
            manga = load_manga_by_slug(slug, manga_data_dir)
            if manga:
                all_manga.append(manga)
    else:
        # Load all manga files
        for manga_file in sorted(manga_data_dir.glob("*.json")):
            try:
                with open(manga_file, 'r', encoding='utf-8') as f:
                    manga = json.load(f)
                    all_manga.append(manga)
            except Exception as e:
                logger.error(f"Error loading {manga_file.name}: {e}")
                continue
    
    return all_manga


def build_catalog_from_manga_data(manga_data_dir: Path, slugs: Optional[List[str]] = None) -> List[Dict]:
    """
    Build a catalog (list of manga summaries) from manga_data files.
    This extracts only the fields needed for the catalog view.
    
    Args:
        manga_data_dir: Path to the manga_data directory
        slugs: Optional list of slugs to include. If None, includes all.
        
    Returns:
        List of manga catalog entries with essential fields
    """
    all_manga = load_all_manga(manga_data_dir, slugs)
    catalog = []
    
    for manga in all_manga:
        catalog_entry = {
            "slug": manga.get("slug"),
            "title": manga.get("title"),
            "author": manga.get("author", ""),
            "thumbnail": manga.get("thumbnail", ""),
            "status": manga.get("status", ""),
            "genres": manga.get("genres", []),
            "bookmarked": manga.get("bookmarked", 0),
            "total_chapters": manga.get("total_chapters", 0),
            "latest_chapters": manga.get("latest_chapters", [])
        }
        catalog.append(catalog_entry)
    
    return catalog


def get_manga_chapter(slug: str, chapter_num: int, manga_data_dir: Path) -> Optional[Dict]:
    """
    Get a specific chapter from a manga.
    
    Args:
        slug: The manga slug
        chapter_num: The chapter number
        manga_data_dir: Path to the manga_data directory
        
    Returns:
        Chapter data dict or None if not found
    """
    manga = load_manga_by_slug(slug, manga_data_dir)
    if not manga:
        return None
    
    chapters = manga.get("chapters", [])
    for chapter in chapters:
        if chapter.get("number") == chapter_num:
            return chapter
    
    return None


def load_catalog_slugs(catalog_file: Path) -> List[str]:
    """
    Load the simple catalog.json file which now contains just slugs.
    
    Args:
        catalog_file: Path to catalog.json
        
    Returns:
        List of manga slugs
    """
    if not catalog_file.exists():
        logger.warning(f"Catalog file not found: {catalog_file}")
        return []
    
    try:
        with open(catalog_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
            
        # Handle both old format (list of dicts) and new format (list of strings)
        if isinstance(catalog, list):
            if len(catalog) > 0 and isinstance(catalog[0], dict):
                # Old format - extract slugs
                return [m["slug"] for m in catalog if "slug" in m]
            else:
                # New format - already slugs
                return catalog
        
        return []
    except Exception as e:
        logger.error(f"Error loading catalog: {e}")
        return []
