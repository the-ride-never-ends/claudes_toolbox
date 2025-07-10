# #!/usr/bin/env python3
# """
# Markdown to DuckDB Tools

# This module provides tools to:
# 1. Save markdown files from a directory to a DuckDB database
# 2. Extract markdown files from a DuckDB database back to a directory

# The database schema stores:
# - file_path: relative path of the markdown file
# - file_name: just the filename
# - content: the markdown content
# - created_at: timestamp when saved to database
# - updated_at: timestamp when last modified
# - file_size: size of the content in bytes
# - hash: MD5 hash of the content for integrity checking
# """
# import hashlib
# from pathlib import Path
# from typing import Dict


# # Import our DuckDB functionality
# from database import DuckDBQueryRunner


# class MarkdownDatabaseManager:
#     """Manager for storing and retrieving markdown files in DuckDB"""
    
#     def __init__(self, db_path: str = "markdown_files.duckdb"):
#         """
#         Initialize the markdown database manager
        
#         Args:
#             db_path: Path to the DuckDB database file
#         """
#         self.db_path = db_path
#         self.runner = DuckDBQueryRunner(db_path=db_path)
#         self._initialize_schema()
    
#     def _initialize_schema(self):
#         """Create the markdown_files table if it doesn't exist"""
#         schema_sql = """
#         CREATE TABLE IF NOT EXISTS markdown_files (
#             id INTEGER PRIMARY KEY,
#             file_path VARCHAR NOT NULL,
#             file_name VARCHAR NOT NULL,
#             content TEXT NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             file_size INTEGER NOT NULL,
#             hash VARCHAR(32) NOT NULL,
#             UNIQUE(file_path)
#         )
#         """
#         self.runner.run_query(schema_sql)
        
#         # Create an index on file_path for faster lookups
#         index_sql = """
#         CREATE INDEX IF NOT EXISTS idx_markdown_files_path 
#         ON markdown_files(file_path)
#         """
#         self.runner.run_query(index_sql)
    
#     def _calculate_hash(self, content: str) -> str:
#         """Calculate MD5 hash of content"""
#         return hashlib.md5(content.encode('utf-8')).hexdigest()
    
#     def save_markdown_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, any]:
#         """
#         Save all markdown files from a directory to the database
        
#         Args:
#             directory_path: Path to the directory containing markdown files
#             recursive: Whether to search subdirectories recursively
            
#         Returns:
#             Dictionary with operation results
#         """
#         directory_path = Path(directory_path).resolve()
        
#         if not directory_path.exists():
#             raise FileNotFoundError(f"Directory not found: {directory_path}")
        
#         if not directory_path.is_dir():
#             raise ValueError(f"Path is not a directory: {directory_path}")
        
#         # Find all markdown files
#         pattern = "**/*.md" if recursive else "*.md"
#         markdown_files = list(directory_path.glob(pattern))
        
#         if not markdown_files:
#             return {
#                 "status": "warning",
#                 "message": f"No markdown files found in {directory_path}",
#                 "files_processed": 0,
#                 "files_added": 0,
#                 "files_updated": 0,
#                 "files_skipped": 0
#             }
        
#         files_added = 0
#         files_updated = 0
#         files_skipped = 0
#         errors = []
        
#         for file_path in markdown_files:
#             try:
#                 # Read file content
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     content = f.read()
                
#                 # Calculate relative path from the base directory
#                 relative_path = str(file_path.relative_to(directory_path))
#                 file_name = file_path.name
#                 file_size = len(content.encode('utf-8'))
#                 content_hash = self._calculate_hash(content)
                
#                 # Check if file already exists
#                 existing_result = self.runner.run_query(
#                     "SELECT hash, updated_at FROM markdown_files WHERE file_path = ?",
#                     # Note: DuckDB doesn't support parameterized queries in our current implementation
#                     # So we'll use string formatting (be careful with SQL injection)
#                 )
                
#                 # For now, let's use a safer approach with string escaping
#                 existing_result = self.runner.run_query(
#                     f"SELECT hash, updated_at FROM markdown_files WHERE file_path = '{relative_path.replace(\"'\", \"''\")}'"
#                 )
                
#                 if existing_result['rows']:
#                     # File exists, check if content changed
#                     existing_hash = existing_result['rows'][0]['hash']
#                     if existing_hash == content_hash:
#                         files_skipped += 1
#                         continue
#                     else:
#                         # Update existing file
#                         update_sql = f"""
#                         UPDATE markdown_files 
#                         SET content = '{content.replace("'", "''")}',
#                             file_size = {file_size},
#                             hash = '{content_hash}',
#                             updated_at = CURRENT_TIMESTAMP
#                         WHERE file_path = '{relative_path.replace("'", "''")}'
#                         """
#                         self.runner.run_query(update_sql)
#                         files_updated += 1
#                 else:
#                     # Insert new file
#                     insert_sql = f"""
#                     INSERT INTO markdown_files (file_path, file_name, content, file_size, hash)
#                     VALUES (
#                         '{relative_path.replace("'", "''")}',
#                         '{file_name.replace("'", "''")}',
#                         '{content.replace("'", "''")}',
#                         {file_size},
#                         '{content_hash}'
#                     )
#                     """
#                     self.runner.run_query(insert_sql)
#                     files_added += 1
                    
#             except Exception as e:
#                 errors.append(f"Error processing {file_path}: {str(e)}")
        
#         result = {
#             "status": "success" if not errors else "partial_success",
#             "message": f"Processed {len(markdown_files)} markdown files",
#             "files_processed": len(markdown_files),
#             "files_added": files_added,
#             "files_updated": files_updated,
#             "files_skipped": files_skipped,
#             "base_directory": str(directory_path)
#         }
        
#         if errors:
#             result["errors"] = errors
        
#         return result
    
#     def extract_markdown_files(self, output_directory: str, overwrite: bool = False) -> Dict[str, any]:
#         """
#         Extract all markdown files from the database to a directory
        
#         Args:
#             output_directory: Directory to save the markdown files
#             overwrite: Whether to overwrite existing files
            
#         Returns:
#             Dictionary with operation results
#         """
#         output_path = Path(output_directory).resolve()
        
#         # Create output directory if it doesn't exist
#         output_path.mkdir(parents=True, exist_ok=True)
        
#         # Get all markdown files from database
#         result = self.runner.run_query("SELECT * FROM markdown_files ORDER BY file_path")
        
#         if not result['rows']:
#             return {
#                 "status": "warning",
#                 "message": "No markdown files found in database",
#                 "files_extracted": 0,
#                 "files_skipped": 0
#             }
        
#         files_extracted = 0
#         files_skipped = 0
#         errors = []
        
#         for row in result['rows']:
#             try:
#                 file_path = output_path / row['file_path']
                
#                 # Check if file already exists
#                 if file_path.exists() and not overwrite:
#                     files_skipped += 1
#                     continue
                
#                 # Create directory structure if needed
#                 file_path.parent.mkdir(parents=True, exist_ok=True)
                
#                 # Write file content
#                 with open(file_path, 'w', encoding='utf-8') as f:
#                     f.write(row['content'])
                
#                 # Verify hash
#                 written_hash = self._calculate_hash(row['content'])
#                 if written_hash != row['hash']:
#                     errors.append(f"Hash mismatch for {file_path}: expected {row['hash']}, got {written_hash}")
                
#                 files_extracted += 1
                
#             except Exception as e:
#                 errors.append(f"Error extracting {row['file_path']}: {str(e)}")
        
#         result = {
#             "status": "success" if not errors else "partial_success",
#             "message": f"Extracted {files_extracted} markdown files",
#             "files_extracted": files_extracted,
#             "files_skipped": files_skipped,
#             "output_directory": str(output_path)
#         }
        
#         if errors:
#             result["errors"] = errors
        
#         return result
    
#     def list_files(self) -> List[Dict[str, any]]:
#         """List all markdown files in the database"""
#         result = self.runner.run_query("""
#             SELECT file_path, file_name, file_size, created_at, updated_at, hash
#             FROM markdown_files 
#             ORDER BY file_path
#         """)
        
#         return result['rows']
    
#     def get_file_info(self, file_path: str) -> Optional[Dict[str, any]]:
#         """Get information about a specific file"""
#         result = self.runner.run_query(f"""
#             SELECT * FROM markdown_files 
#             WHERE file_path = '{file_path.replace("'", "''")}'
#         """)
        
#         return result['rows'][0] if result['rows'] else None
    
#     def delete_file(self, file_path: str) -> bool:
#         """Delete a file from the database"""
#         result = self.runner.run_query(f"""
#             DELETE FROM markdown_files 
#             WHERE file_path = '{file_path.replace("'", "''")}'
#         """)
        
#         # Check if any rows were affected
#         count_result = self.runner.run_query(f"""
#             SELECT COUNT(*) as count FROM markdown_files 
#             WHERE file_path = '{file_path.replace("'", "''")}'
#         """)
        
#         return count_result['rows'][0]['count'] == 0
    
#     def get_stats(self) -> Dict[str, any]:
#         """Get database statistics"""
#         stats_result = self.runner.run_query("""
#             SELECT 
#                 COUNT(*) as total_files,
#                 SUM(file_size) as total_size,
#                 AVG(file_size) as avg_size,
#                 MIN(created_at) as oldest_created,
#                 MAX(updated_at) as newest_updated
#             FROM markdown_files
#         """)
        
#         return stats_result['rows'][0] if stats_result['rows'] else {}
    
#     def close(self):
#         """Close the database connection"""
#         self.runner.close()


# def main():
#     """Command-line interface for the markdown tools"""
#     parser = argparse.ArgumentParser(description='Markdown to DuckDB Tools')
#     parser.add_argument('--db-path', default='markdown_files.duckdb', 
#                        help='Path to DuckDB database file')
    
#     subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
#     # Save command
#     save_parser = subparsers.add_parser('save', help='Save markdown files to database')
#     save_parser.add_argument('directory', help='Directory containing markdown files')
#     save_parser.add_argument('--recursive', action='store_true', default=True,
#                             help='Search subdirectories recursively')
#     save_parser.add_argument('--no-recursive', action='store_false', dest='recursive',
#                             help='Do not search subdirectories')
    
#     # Extract command
#     extract_parser = subparsers.add_parser('extract', help='Extract markdown files from database')
#     extract_parser.add_argument('directory', help='Output directory for markdown files')
#     extract_parser.add_argument('--overwrite', action='store_true', 
#                                help='Overwrite existing files')
    
#     # List command
#     list_parser = subparsers.add_parser('list', help='List files in database')
    
#     # Stats command
#     stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
#     # Delete command
#     delete_parser = subparsers.add_parser('delete', help='Delete a file from database')
#     delete_parser.add_argument('file_path', help='File path to delete')
    
#     args = parser.parse_args()
    
#     if not args.command:
#         parser.print_help()
#         return 1
    
#     # Initialize manager
#     manager = MarkdownDatabaseManager(db_path=args.db_path)
    
#     try:
#         if args.command == 'save':
#             print(f"Saving markdown files from {args.directory} to {args.db_path}")
#             result = manager.save_markdown_directory(args.directory, recursive=args.recursive)
#             print(json.dumps(result, indent=2, default=str))
            
#         elif args.command == 'extract':
#             print(f"Extracting markdown files from {args.db_path} to {args.directory}")
#             result = manager.extract_markdown_files(args.directory, overwrite=args.overwrite)
#             print(json.dumps(result, indent=2, default=str))
            
#         elif args.command == 'list':
#             files = manager.list_files()
#             print(f"Found {len(files)} markdown files in database:")
#             for file_info in files:
#                 print(f"  {file_info['file_path']} ({file_info['file_size']} bytes)")
            
#         elif args.command == 'stats':
#             stats = manager.get_stats()
#             print("Database Statistics:")
#             print(json.dumps(stats, indent=2, default=str))
            
#         elif args.command == 'delete':
#             if manager.delete_file(args.file_path):
#                 print(f"Successfully deleted {args.file_path}")
#             else:
#                 print(f"File not found: {args.file_path}")
#                 return 1
        
#         return 0
        
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return 1
        
#     finally:
#         manager.close()


# if __name__ == "__main__":
#     sys.exit(main())
