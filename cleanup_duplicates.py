#!/usr/bin/env python3
import os
import sys
import hashlib
import sqlite3
from datetime import datetime

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
    except FileNotFoundError:
        return None
    return sha256_hash.hexdigest()

def main():
    db_path = "/Users/overspread/Developer/ai-analyse/backend/ai_analyse.db"
    upload_dir = "/Users/overspread/Developer/ai-analyse/backend/uploads"
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # To access columns by name
    cursor = conn.cursor()
    
    # Get all documents with missing hash
    cursor.execute("""
        SELECT id, original_filename, file_size, file_path, created_at 
        FROM documents 
        WHERE file_hash IS NULL OR file_hash = ''
        ORDER BY created_at
    """)
    documents = cursor.fetchall()
    
    print(f"Found {len(documents)} documents with missing hash")
    
    # Process each document
    hash_to_docs = {}
    files_to_check = set()
    
    for doc in documents:
        doc_id = doc['id']
        file_path = doc['file_path']
        
        # Make path absolute if it's relative
        if not os.path.isabs(file_path):
            file_path = os.path.join("/Users/overspread/Developer/ai-analyse/backend", file_path)
        
        files_to_check.add(file_path)
        
        # Calculate hash if file exists
        if os.path.exists(file_path):
            file_hash = calculate_file_hash(file_path)
            if file_hash:
                if file_hash not in hash_to_docs:
                    hash_to_docs[file_hash] = []
                hash_to_docs[file_hash].append({
                    'id': doc_id,
                    'file_path': file_path,
                    'created_at': doc['created_at'],
                    'original_filename': doc['original_filename']
                })
            else:
                print(f"Could not calculate hash for {file_path}")
        else:
            print(f"File not found on disk: {file_path}")
    
    print(f"\nFound {len(hash_to_docs)} unique file hashes among existing files")
    
    # Identify duplicates and decide which to keep
    docs_to_delete = []
    files_to_delete = []
    
    for file_hash, docs in hash_to_docs.items():
        if len(docs) > 1:
            # Sort by creation time (oldest first)
            docs_sorted = sorted(docs, key=lambda x: x['created_at'])
            # Keep the oldest one
            to_keep = docs_sorted[0]
            # Mark the rest for deletion
            for doc in docs_sorted[1:]:
                docs_to_delete.append(doc['id'])
                print(f"Will delete duplicate: ID {doc['id']} ({doc['original_filename']}) created at {doc['created_at']}")
                print(f"  Keeping: ID {to_keep['id']} created at {to_keep['created_at']}")
        else:
            # Single file, just update its hash
            doc = docs[0]
            print(f"Single file: ID {doc['id']} ({doc['original_filename']})")
    
    # Also handle documents whose files don't exist on disk
    # These should be deleted entirely as they're orphaned
    orphaned_docs = []
    for doc in documents:
        doc_id = doc['id']
        file_path = doc['file_path']
        if not os.path.isabs(file_path):
            file_path = os.path.join("/Users/overspread/Developer/ai-analyse/backend", file_path)
        if not os.path.exists(file_path):
            orphaned_docs.append(doc_id)
            print(f"Orphaned document (file missing): ID {doc_id} ({doc['original_filename']})")
    
    # Update database: set hashes for kept documents
    print("\nUpdating database with file hashes...")
    for file_hash, docs in hash_to_docs.items():
        if docs:
            # Keep the oldest
            doc_to_keep = sorted(docs, key=lambda x: x['created_at'])[0]
            cursor.execute(
                "UPDATE documents SET file_hash = ? WHERE id = ?",
                (file_hash, doc_to_keep['id'])
            )
            print(f"Set hash for document ID {doc_to_keep['id']}")
    
    # Delete duplicate documents and their associated data
    print(f"\nDeleting {len(docs_to_delete)} duplicate documents...")
    for doc_id in docs_to_delete:
        # Get file path before deleting record
        cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        if row and row[0]:
            file_path = row[0]
            if not os.path.isabs(file_path):
                file_path = os.path.join("/Users/overspread/Developer/ai-analyse/backend", file_path)
            # Delete file from disk if it exists
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"  Deleted file: {file_path}")
                except Exception as e:
                    print(f"  Error deleting file {file_path}: {e}")
        
        # Delete document record (this should cascade to delete vectors if foreign keys are set up)
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        print(f"  Deleted document record ID {doc_id}")
    
    # Delete orphaned documents
    print(f"\nDeleting {len(orphaned_docs)} orphaned documents...")
    for doc_id in orphaned_docs:
        cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        if row and row[0]:
            file_path = row[0]
            if not os.path.isabs(file_path):
                file_path = os.path.join("/Users/overspread/Developer/ai-analyse/backend", file_path)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"  Deleted orphaned file: {file_path}")
                except Exception as e:
                    print(f"  Error deleting orphaned file {file_path}: {e}")
        
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        print(f"  Deleted orphaned document record ID {doc_id}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\nCleanup completed!")

if __name__ == "__main__":
    main()