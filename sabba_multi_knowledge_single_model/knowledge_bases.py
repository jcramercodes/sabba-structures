"""
Knowledge Bases Configuration
Contains predefined knowledge base options for easy access
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class KnowledgeBase:
    """Represents a knowledge base with metadata"""
    id: str
    name: str
    icon_url: str
    brand_color: str
    org_url: str

    def __str__(self) -> str:
        return f"{self.name} ({self.id[:8]}...)"


# Predefined knowledge bases
KNOWLEDGE_BASES = [
    KnowledgeBase(
        id='8be6dfd9-ecaf-4e2b-8414-01aecb67e147',
        name='Blossom Analysis',
        icon_url='images/logos/blossom_analysis.jpg',
        brand_color='#FFFFFF',
        org_url='https://blossomanalysis.com'
    ),
    KnowledgeBase(
        id='f73bbef9-ea3b-4f78-956d-b5fc38de7699',
        name='Lucid News',
        icon_url='images/logos/lucid_news.jpg',
        brand_color='#2712BD',
        org_url='https://lucidnews.com'
    ),
    KnowledgeBase(
        id='f88d9d45-f25e-4051-8a84-a8d7873622b8',
        name='MAPS',
        icon_url='images/logos/maps.jpg',
        brand_color='#2712BD',
        org_url='https://maps.org'
    ),
    KnowledgeBase(
        id='5f6e1ea5-1f3f-431a-8759-b66810582b73',
        name='Psychedelic Alpha',
        icon_url='images/logos/psychedelic_alpha.jpg',
        brand_color='#CFC9E5',
        org_url='https://psychedelicalpha.com'
    ),
    KnowledgeBase(
        id='c34bc3da-d466-4a2d-94c3-2e6fffbe6d1d',
        name='Psychedelics Today',
        icon_url='images/logos/psychedelics_today.jpg',
        brand_color='#FFFFFF',
        org_url='https://psychedelictoday.com'
    ),
]

# Create lookup dictionaries for easy access
KNOWLEDGE_BASES_BY_ID: Dict[str, KnowledgeBase] = {kb.id: kb for kb in KNOWLEDGE_BASES}
KNOWLEDGE_BASES_BY_NAME: Dict[str, KnowledgeBase] = {kb.name.lower(): kb for kb in KNOWLEDGE_BASES}


def get_knowledge_base_by_id(kb_id: str) -> Optional[KnowledgeBase]:
    """Get knowledge base by ID"""
    return KNOWLEDGE_BASES_BY_ID.get(kb_id)


def get_knowledge_base_by_name(name: str) -> Optional[KnowledgeBase]:
    """Get knowledge base by name (case-insensitive)"""
    return KNOWLEDGE_BASES_BY_NAME.get(name.lower())


def list_available_knowledge_bases() -> List[KnowledgeBase]:
    """Get all available knowledge bases"""
    return KNOWLEDGE_BASES.copy()


def get_knowledge_base_ids_by_names(names: List[str]) -> List[str]:
    """Convert knowledge base names to IDs"""
    ids = []
    for name in names:
        kb = get_knowledge_base_by_name(name)
        if kb:
            ids.append(kb.id)
    return ids


def parse_knowledge_base_selection(selection: str) -> List[str]:
    """
    Parse knowledge base selection string.
    Can be either:
    - Comma-separated IDs: "id1,id2,id3"
    - Comma-separated names: "Blossom Analysis,MAPS"
    - Special keyword "all" for all knowledge bases
    """
    if not selection:
        return []
    
    if selection.lower() == "all":
        return [kb.id for kb in KNOWLEDGE_BASES]
    
    items = [item.strip() for item in selection.split(",") if item.strip()]
    ids = []
    
    for item in items:
        # Check if it's an ID (UUID format)
        if len(item) == 36 and item.count('-') == 4:
            ids.append(item)
        else:
            # Assume it's a name
            kb = get_knowledge_base_by_name(item)
            if kb:
                ids.append(kb.id)
            else:
                print(f"⚠️  Warning: Knowledge base '{item}' not found")
    
    return ids


def print_available_knowledge_bases():
    """Print available knowledge bases for user reference"""
    print("📚 Available Knowledge Bases:")
    print("-" * 50)
    for i, kb in enumerate(KNOWLEDGE_BASES, 1):
        print(f"{i}. {kb.name}")
        print(f"   ID: {kb.id}")
        print(f"   URL: {kb.org_url}")
        print()
    
    print("💡 Usage examples:")
    print("  By name: -k \"Blossom Analysis,MAPS\"")
    print("  By ID: -k \"8be6dfd9-ecaf-4e2b-8414-01aecb67e147\"")
    print("  All: -k \"all\"") 