"""
Memory system implementation with structured and semantic memory
"""

import asyncio
import sqlite3
import json
import pickle
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import hashlib
import os


class MemoryType(Enum):
    """Types of memory in the system"""
    SESSION_CONTEXT = "session_context"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    POLICY = "policy"
    PATTERN = "pattern"


@dataclass
class MemoryEntry:
    """Structure for memory entries"""
    key: str
    value: Any
    memory_type: MemoryType
    created_at: datetime
    ttl: Optional[timedelta] = None
    tags: Optional[List[str]] = None
    importance: float = 0.5  # 0.0 to 1.0 scale


class StructuredMemory:
    """SQL-based structured memory for transactional data"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the SQLite database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # Create memory_entries table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS memory_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value_json TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP,
                tags_json TEXT,
                importance REAL DEFAULT 0.5,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_key ON memory_entries(key)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_type ON memory_entries(memory_type)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_expires ON memory_entries(expires_at)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memory_entries(importance)')
        
        self.conn.commit()
    
    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry in the database"""
        try:
            expires_at = None
            if entry.ttl:
                expires_at = (entry.created_at + entry.ttl).isoformat()
            
            tags_json = json.dumps(entry.tags) if entry.tags else None
            
            self.conn.execute('''
                INSERT OR REPLACE INTO memory_entries 
                (key, value_json, memory_type, created_at, expires_at, tags_json, importance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.key,
                json.dumps(entry.value, default=str),
                entry.memory_type.value,
                entry.created_at.isoformat(),
                expires_at,
                tags_json,
                entry.importance
            ))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error storing memory entry: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by key"""
        try:
            cursor = self.conn.execute('''
                SELECT key, value_json, memory_type, created_at, expires_at, tags_json, importance, last_accessed
                FROM memory_entries WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)
            ''', (key, datetime.now().isoformat()))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Update last accessed
            self.conn.execute('UPDATE memory_entries SET last_accessed = ? WHERE key = ?', 
                            (datetime.now().isoformat(), key))
            self.conn.commit()
            
            # Parse the retrieved data
            value = json.loads(row[1])
            memory_type = MemoryType(row[2])
            created_at = datetime.fromisoformat(row[3])
            
            tags = None
            if row[5]:
                tags = json.loads(row[5])
            
            return MemoryEntry(
                key=row[0],
                value=value,
                memory_type=memory_type,
                created_at=created_at,
                ttl=None,  # TTL not preserved in this format
                tags=tags,
                importance=row[6]
            )
        except Exception as e:
            print(f"Error retrieving memory entry: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a memory entry by key"""
        try:
            cursor = self.conn.execute('DELETE FROM memory_entries WHERE key = ?', (key,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting memory entry: {e}")
            return False
    
    def cleanup_expired(self) -> int:
        """Remove expired memory entries"""
        try:
            cursor = self.conn.execute('''
                DELETE FROM memory_entries 
                WHERE expires_at IS NOT NULL AND expires_at < ?
            ''', (datetime.now().isoformat(),))
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error cleaning up expired entries: {e}")
            return 0
    
    def search_by_type(self, memory_type: MemoryType, limit: int = 100) -> List[MemoryEntry]:
        """Search memory entries by type"""
        try:
            cursor = self.conn.execute('''
                SELECT key, value_json, memory_type, created_at, expires_at, tags_json, importance
                FROM memory_entries 
                WHERE memory_type = ? AND (expires_at IS NULL OR expires_at > ?)
                ORDER BY importance DESC
                LIMIT ?
            ''', (memory_type.value, datetime.now().isoformat(), limit))
            
            entries = []
            for row in cursor.fetchall():
                value = json.loads(row[1])
                created_at = datetime.fromisoformat(row[3])
                
                tags = None
                if row[5]:
                    tags = json.loads(row[5])
                
                entries.append(MemoryEntry(
                    key=row[0],
                    value=value,
                    memory_type=MemoryType(row[2]),
                    created_at=created_at,
                    ttl=None,
                    tags=tags,
                    importance=row[6]
                ))
            
            return entries
        except Exception as e:
            print(f"Error searching memory entries: {e}")
            return []
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()


class SemanticMemory:
    """Vector-based semantic memory for pattern recognition"""
    
    def __init__(self):
        self.entries = {}  # key -> (embedding, data)
        self.embeddings_index = []  # List of (key, embedding) tuples
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate a simple embedding for text (mock implementation)"""
        # This is a mock embedding generator
        # In a real implementation, this would use a proper embedding model
        hash_obj = hashlib.md5(text.encode())
        hex_dig = hash_obj.hexdigest()
        
        # Convert hex digest to float values
        embedding = []
        for i in range(0, len(hex_dig), 2):
            byte_val = int(hex_dig[i:i+2], 16)
            normalized_val = (byte_val / 255.0) * 2 - 1  # Normalize to [-1, 1]
            embedding.append(normalized_val)
        
        # Pad or truncate to fixed size (e.g., 16 dimensions)
        while len(embedding) < 16:
            embedding.append(0.0)
        embedding = embedding[:16]
        
        return embedding
    
    def store(self, entry: MemoryEntry) -> bool:
        """Store an entry in semantic memory"""
        try:
            # Create embedding from the value (convert to string representation)
            text_repr = json.dumps(entry.value, default=str)
            embedding = self._generate_embedding(text_repr)
            
            self.entries[entry.key] = (embedding, entry)
            self.embeddings_index.append((entry.key, embedding))
            return True
        except Exception as e:
            print(f"Error storing semantic memory: {e}")
            return False
    
    def find_similar(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar entries based on semantic similarity"""
        try:
            query_embedding = self._generate_embedding(query)
            similarities = []
            
            for key, stored_embedding in self.embeddings_index:
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                similarities.append((key, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
        except Exception as e:
            print(f"Error finding similar entries: {e}")
            return []
    
    def retrieve(self, key: str) -> Optional[MemoryEntry]:
        """Retrieve an entry by key"""
        if key in self.entries:
            _, entry = self.entries[key]
            return entry
        return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)


class AgentMemoryManager:
    """Main memory manager that coordinates structured and semantic memory"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.structured_memory = StructuredMemory(db_path)
        self.semantic_memory = SemanticMemory()
        self.cleanup_interval = timedelta(minutes=5)
    
    def store(self, key: str, value: Any, memory_type: MemoryType, 
              ttl: Optional[timedelta] = None, tags: Optional[List[str]] = None, 
              importance: float = 0.5) -> bool:
        """Store a memory entry in both structured and semantic memory"""
        entry = MemoryEntry(
            key=key,
            value=value,
            memory_type=memory_type,
            created_at=datetime.now(),
            ttl=ttl,
            tags=tags,
            importance=importance
        )
        
        # Store in structured memory
        struct_success = self.structured_memory.store(entry)
        
        # Store in semantic memory
        semantic_success = self.semantic_memory.store(entry)
        
        return struct_success and semantic_success
    
    def retrieve(self, key: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry"""
        # Try structured memory first
        entry = self.structured_memory.retrieve(key)
        if entry:
            return entry
        
        # Fall back to semantic memory
        return self.semantic_memory.retrieve(key)
    
    def find_similar_context(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """Find memory entries similar to the query"""
        similar_keys = self.semantic_memory.find_similar(query, top_k)
        results = []
        
        for key, _ in similar_keys:
            entry = self.retrieve(key)
            if entry:
                results.append(entry)
        
        return results
    
    def search_by_type(self, memory_type: MemoryType, limit: int = 100) -> List[MemoryEntry]:
        """Search memory entries by type"""
        return self.structured_memory.search_by_type(memory_type, limit)
    
    def cleanup_expired(self) -> int:
        """Clean up expired memory entries"""
        return self.structured_memory.cleanup_expired()
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get statistics about memory usage"""
        struct_entries = len(self.structured_memory.conn.execute(
            'SELECT COUNT(*) FROM memory_entries'
        ).fetchone())
        
        return {
            "structured_entries": struct_entries,
            "semantic_entries": len(self.semantic_memory.entries),
            "total_entries": struct_entries + len(self.semantic_memory.entries)
        }
    
    def close(self):
        """Close memory resources"""
        self.structured_memory.close()


class MemorySystem:
    """Main memory system interface for the AI AP Employee"""
    
    def __init__(self, db_path: str = ":memory:"):
        self.manager = AgentMemoryManager(db_path)
        self.initialized = False
    
    async def initialize_memory(self):
        """Initialize the memory system with default policies and patterns"""
        print("[MEMORY] Initializing AI AP Employee memory system...")
        
        # Store default company policies
        self.manager.store(
            key="company_policy_purchase_threshold",
            value={
                "amount_threshold": 1000,
                "approval_required": True,
                "approver_role": "department_manager"
            },
            memory_type=MemoryType.POLICY,
            importance=0.9
        )
        
        self.manager.store(
            key="company_policy_vat_validation",
            value={
                "require_vat_validation": True,
                "eu_compliance_required": True,
                "validation_methods": ["tax_id_match", "vat_number_check"]
            },
            memory_type=MemoryType.POLICY,
            importance=0.9
        )
        
        # Store common vendor patterns
        self.manager.store(
            key="vendor_payment_pattern_ACME",
            value={
                "vendor_id": "VEND-ACME-001",
                "avg_payment_time_days": 25,
                "preferred_payment_method": "BACS",
                "payment_history": [
                    {"date": "2025-12-20", "amount": 1100.00},
                    {"date": "2026-01-20", "amount": 1250.75}
                ]
            },
            memory_type=MemoryType.PATTERN,
            importance=0.7
        )
        
        # Store common invoice processing patterns
        self.manager.store(
            key="processing_pattern_month_end",
            value={
                "high_volume_period": True,
                "processing_time_increase": 1.5,
                "additional_validation": True,
                "recommended_actions": ["prioritize_important_vendors", "extend_deadlines"]
            },
            memory_type=MemoryType.PATTERN,
            importance=0.6
        )
        
        # Store default approval hierarchies
        self.manager.store(
            key="approval_hierarchy_default",
            value={
                "thresholds": {
                    "up_to_500": "self_approve",
                    "up_to_1000": "supervisor",
                    "up_to_5000": "manager", 
                    "up_to_25000": "director",
                    "above_25000": "executive"
                },
                "exceptions": ["critical_suppliers", "contracted_rates"]
            },
            memory_type=MemoryType.POLICY,
            importance=0.9
        )
        
        print("[MEMORY] Memory system initialized with default policies and patterns")
        self.initialized = True
        return True
    
    def get_memory_manager(self):
        """Get the memory manager instance"""
        return self.manager
    
    async def shutdown(self):
        """Shutdown the memory system"""
        self.manager.close()
        self.initialized = False