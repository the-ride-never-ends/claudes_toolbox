#!/usr/bin/env python

import logging
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager, contextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from mcp.server.fastmcp import FastMCP, Context
import duckdb
import sys
import argparse

# Setup logging to file in subservers directory
LOG_DIR = os.path.join(os.path.dirname(__file__), "..")
LOG_PATH = os.path.abspath(os.path.join(LOG_DIR, "subservers", "database_debug.log"))
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("server")

# DuckDB Query Runner implementation
class DuckDBQueryRunner:
    """DuckDB query runner that provides database operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        logger.debug(f"Initializing DuckDBQueryRunner with db_path={db_path}")
        self.db_path = db_path or ":memory:"
        self.connection = None
        self._connect()

    def __enter__(self):
        logger.debug("Entering DuckDBQueryRunner context manager")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug("Exiting DuckDBQueryRunner context manager")
        self.close()

    def _connect(self):
        logger.debug(f"Connecting to DuckDB at {self.db_path}")
        try:
            self.connection = duckdb.connect(self.db_path)
            logger.debug("DuckDB connection established")
        except Exception as e:
            logger.error(f"Failed to connect to DuckDB: {str(e)}")
            raise Exception(f"Failed to connect to DuckDB: {str(e)}")
    
    def test_connection(self):
        logger.debug("Testing DuckDB connection")
        try:
            self.connection.execute("SELECT 1").fetchone()
            logger.debug("DuckDB connection test successful")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            raise Exception(f"Connection test failed: {str(e)}")
    
    def run_query(self, query: str) -> Dict[str, Any]:
        logger.debug(f"Running query: {query}")
        try:
            result = self.connection.execute(query)
            columns = []
            if result.description:
                for i, desc in enumerate(result.description):
                    columns.append({
                        'name': desc[0],
                        'friendly_name': desc[0],
                        'type': str(desc[1]) if len(desc) > 1 else 'unknown'
                    })
            rows = result.fetchall()
            row_dicts = []
            if columns and rows:
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        row_dict[col['name']] = row[i] if i < len(row) else None
                    row_dicts.append(row_dict)
            logger.debug(f"Query executed successfully, {len(rows)} rows returned")
            return {
                'columns': columns,
                'rows': row_dicts,
                'row_count': len(rows)
            }
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise Exception(f"Query execution failed: {str(e)}")
    
    def get_schema(self) -> List[Dict[str, Any]]:
        logger.debug("Getting database schema")
        with self.cursor() as cursor:
            try:
                tables_result = cursor.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
                ).fetchall()
                schema = []
                for (table_name,) in tables_result:
                    columns_result = cursor.execute(
                        f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
                    ).fetchall()
                    columns = []
                    for col_name, col_type in columns_result:
                        columns.append({
                            'name': col_name,
                            'type': col_type
                        })
                    schema.append({
                        'name': table_name,
                        'columns': columns
                    })
                logger.debug(f"Schema fetched for {len(schema)} tables")
                return schema
            except Exception as e:
                logger.warning(f"information_schema not available, falling back: {str(e)}")
                try:
                    tables_result = cursor.execute("SHOW TABLES").fetchall()
                    schema = []
                    for (table_name,) in tables_result:
                        try:
                            columns_result = cursor.execute(f"DESCRIBE {table_name}").fetchall()
                            columns = []
                            for row in columns_result:
                                columns.append({
                                    'name': row[0],
                                    'type': row[1]
                                })
                            schema.append({
                                'name': table_name,
                                'columns': columns
                            })
                        except Exception as e2:
                            logger.warning(f"Could not describe table {table_name}: {str(e2)}")
                            continue
                    logger.debug(f"Schema fallback fetched for {len(schema)} tables")
                    return schema
                except Exception as e2:
                    logger.error(f"Could not fetch schema: {str(e2)}")
                    return []
    
    def get_table_columns(self, table_name: str) -> List[str]:
        logger.debug(f"Getting columns for table: {table_name}")
        with self.cursor() as cursor:
            try:
                result = cursor.execute(f"DESCRIBE {table_name}").fetchall()
                columns = [row[0] for row in result]
                logger.debug(f"Columns for {table_name}: {columns}")
                return columns
            except Exception as e:
                logger.error(f"Failed to get columns for table {table_name}: {str(e)}")
                raise Exception(f"Failed to get columns for table {table_name}: {str(e)}")
    
    def get_table_types(self, table_name: str) -> Dict[str, str]:
        logger.debug(f"Getting column types for table: {table_name}")
        with self.cursor() as cursor:
            try:
                result = cursor.execute(f"DESCRIBE {table_name}").fetchall()
                types = {row[0]: row[1] for row in result}
                logger.debug(f"Types for {table_name}: {types}")
                return types
            except Exception as e:
                logger.error(f"Failed to get types for table {table_name}: {str(e)}")
                raise Exception(f"Failed to get types for table {table_name}: {str(e)}")
    
    def close(self):
        logger.debug("Closing DuckDB connection")
        if self.connection:
            self.connection.close()

    @contextmanager
    def cursor(self):
        logger.debug("Creating DuckDB cursor")
        if not self.connection:
            logger.error("Connection not established")
            raise Exception("Connection not established")
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
            logger.debug("DuckDB cursor closed")

@dataclass
class DbConfig:
    id: str
    db_type: str
    configuration: Dict[str, Any]
    description: str
    schema: Optional[List[Dict[str, Any]]] = None
    query_runner: Optional[DuckDBQueryRunner] = None

def init_config(testing=False, test_db_type=None, test_db_config=None, test_db_configs=None) -> Dict[str, DbConfig]:
    logger.debug(f"Initializing config (testing={testing})")
    if not testing:
        parser = argparse.ArgumentParser(description='DuckDB MCP Server')
        parser.add_argument('--db-path', required=False, help='Path to DuckDB database file (optional, defaults to in-memory)')
        parser.add_argument('--db-configs', required=False, help='JSON string array containing multiple database configurations')
        args = parser.parse_args()
        db_configs_str = args.db_configs
        if not db_configs_str:
            db_configs_str = os.getenv("DB_CONFIGS", "")
        db_path = args.db_path
    else:
        db_configs_str = test_db_configs
        db_path = test_db_config.get('db_path') if test_db_config else None
        if not db_configs_str:
            db_configs_str = os.getenv("DB_CONFIGS", "")
        if not db_path:
            db_path = os.getenv("DB_PATH", "")
    if db_configs_str:
        try:
            db_configs_list = json.loads(db_configs_str) if isinstance(db_configs_str, str) else db_configs_str
            if not isinstance(db_configs_list, list) or len(db_configs_list) == 0:
                logger.error("DB_CONFIGS must be a non-empty JSON array")
                raise ValueError("DB_CONFIGS must be a non-empty JSON array")
            db_configs = {}
            for i, config in enumerate(db_configs_list):
                if not isinstance(config, dict) or "description" not in config:
                    logger.error("Each DB_CONFIG must contain description")
                    raise ValueError("Each DB_CONFIG must contain description")
                db_id = config.get("id", "")
                if not db_id:
                    desc_part = ''.join(c for c in config["description"] if c.isalnum())[:8].lower()
                    db_id = f"duckdb_{desc_part}_{i}"
                db_config = DbConfig(
                    db_type="duckdb",
                    configuration=config,
                    description=config["description"],
                    id=db_id
                )
                config_db_path = config.get("db_path", ":memory:")
                db_config.query_runner = DuckDBQueryRunner(db_path=config_db_path)
                db_configs[db_id] = db_config
                logger.debug(f"Initialized DuckDB connection for {db_id} at {config_db_path}")
            logger.info(f"Initialized {len(db_configs)} DuckDB connections")
            return db_configs
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing DB_CONFIGS: {str(e)}")
            print(f"Error parsing DB_CONFIGS: {str(e)}")
            raise
    if not db_path:
        db_path = os.getenv("DB_PATH", ":memory:")
    db_id = "duckdb_default"
    db_config_obj = DbConfig(
        db_type="duckdb",
        configuration={"db_path": db_path},
        description=f"DuckDB database ({db_path})",
        id=db_id
    )
    db_config_obj.query_runner = DuckDBQueryRunner(db_path=db_path)
    logger.debug(f"Initialized single DuckDB connection for {db_id} at {db_path}")
    db_configs = {db_id: db_config_obj}
    return db_configs

config_map: Dict[str, DbConfig] = {} 
_is_test = 'pytest' in sys.modules
if not _is_test:
    try:
        logger.debug("Starting global DuckDB config initialization")
        config_map = init_config()
    except Exception as e:
        logger.error(f"Error initializing DuckDB connections: {str(e)}")
        print(f"Error initializing DuckDB connections: {str(e)}")
        print("\nUsage:")
        print("1. For MCP CLI mode with single database:")
        print("   Set environment variable: DB_PATH (optional, defaults to in-memory)")
        print("   Or for multiple databases: DB_CONFIGS='[{\"description\":\"My DuckDB\",\"db_path\":\"/path/to/db.duckdb\"}]'")
        print("   Then run: mcp install mcp_server.py")
        print("   Or: mcp dev mcp_server.py")
        print("\n2. For direct execution with single database:")
        print("   python mcp_server.py --db-path <path_to_db>")
        print("   Example: python mcp_server.py --db-path /path/to/my_database.duckdb")
        print("\n3. For direct execution with multiple databases:")
        print("   python mcp_server.py --db-configs '[{\"description\":\"My DuckDB\",\"db_path\":\"/path/to/db.duckdb\"}]'")
        sys.exit(1)
    for db_config in config_map.values():
        try:
            logger.debug(f"Fetching schema for {db_config.description}")
            db_config.schema = db_config.query_runner.get_schema()
        except Exception as e:
            logger.warning(f"Could not fetch schema for {db_config.description}: {str(e)}")
            print(f"Warning: Could not fetch schema for {db_config.description}: {str(e)}")

@dataclass
class DbContext:
    db_configs: Dict[str, DbConfig]
    last_query: Optional[str] = None
    last_result: Optional[Dict[str, Any]] = None
    query_history: List[str] = None
    
    def __post_init__(self):
        logger.debug("Initializing DbContext")
        if self.query_history is None:
            self.query_history = []
    
    def get_default_query_runner(self) -> DuckDBQueryRunner:
        logger.debug("Getting default query runner")
        if not self.db_configs:
            logger.error("No database connections available")
            raise ValueError("No database connections available")
        first_db_id = next(iter(self.db_configs))
        return self.db_configs[first_db_id].query_runner

def _calculate_hash(content: str) -> str:
    logger.debug("Calculating MD5 hash")
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def _initialize_markdown_schema(runner: DuckDBQueryRunner):
    logger.debug("Initializing markdown_files schema")
    schema_sql = """
    CREATE TABLE IF NOT EXISTS markdown_files (
        id INTEGER PRIMARY KEY,
        file_path VARCHAR NOT NULL,
        file_name VARCHAR NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        file_size INTEGER NOT NULL,
        hash VARCHAR(32) NOT NULL,
        UNIQUE(file_path)
    )
    """
    runner.run_query(schema_sql)
    index_sql = """
    CREATE INDEX IF NOT EXISTS idx_markdown_files_path 
    ON markdown_files(file_path)
    """
    runner.run_query(index_sql)

@asynccontextmanager
async def db_lifespan(server: FastMCP) -> AsyncIterator[DbContext]:
    logger.debug("Starting db_lifespan context")
    db_context = DbContext(
        db_configs=config_map,
    )
    try:
        for db_config in db_context.db_configs.values():
            try:
                db_config.query_runner.test_connection()
                logger.info(f"Successfully connected to {db_config.description}")
            except Exception as e:
                logger.warning(f"Connection test failed for {db_config.description}: {str(e)}")
        yield db_context
    finally:
        logger.debug("Exiting db_lifespan context")


def register_database_tools(mcp: FastMCP):
    logger.debug("Registering database tools")

    return mcp

    @mcp.resource("resource://schema/{database_id}")
    def get_schema(database_id: Optional[str] = None) -> str:
        logger.debug(f"get_schema called with database_id={database_id}")
        try:
            schemas = []
            if database_id is not None and database_id != "all":
                if database_id not in config_map:
                    logger.error(f"Invalid database ID {database_id}")
                    return f"Error: Invalid database ID {database_id}"
                db_config = config_map[database_id]
                try:
                    schema = db_config.query_runner.get_schema()
                    schemas.append({
                        "id": database_id,
                        "description": db_config.description,
                        "db_type": db_config.db_type,
                        "schema": schema
                    })
                except Exception as e:
                    logger.warning(f"Could not get schema for {database_id}: {str(e)}")
                    schemas.append({
                        "id": database_id,
                        "description": db_config.description,
                        "db_type": db_config.db_type,
                        "error": str(e)
                    })
            else:
                for db_id, db_config in config_map.items():
                    try:
                        schema = db_config.query_runner.get_schema()
                        schemas.append({
                            "id": db_id,
                            "description": db_config.description,
                            "db_type": db_config.db_type,
                            "schema": schema
                        })
                    except Exception as e:
                        logger.warning(f"Could not get schema for {db_id}: {str(e)}")
                        schemas.append({
                            "id": db_id,
                            "description": db_config.description,
                            "db_type": db_config.db_type,
                            "error": str(e)
                        })
            return json.dumps(schemas)
        except Exception as e:
            logger.error(f"Error getting schemas: {str(e)}")
            return f"Error getting schemas: {str(e)}"

    @mcp.tool()
    def get_query_history(ctx: Context) -> str:
        logger.debug("get_query_history called")
        db_context = ctx.request_context.lifespan_context
        if not db_context.query_history:
            return "No query history available"
        result = "Query History:\n"
        for entry in db_context.query_history:
            if isinstance(entry, str):
                result += f"- {entry}\n"
            else:
                result += f"- {entry['query']} (Database: {entry['db_name']})\n"
        return result

    @mcp.tool()
    def list_databases(ctx: Context) -> str:
        logger.debug("list_databases called")
        db_context: DbContext = ctx.request_context.lifespan_context
        if not db_context.db_configs:
            return "No database connections available."
        db_list = []
        for db_id, db_config in db_context.db_configs.items():
            db_info = f"ID: {db_id} - {db_config.description} (Type: {db_config.db_type})"
            if db_config.schema:
                table_count = len(db_config.schema)
                db_info += f" - {table_count} tables"
            db_list.append(db_info)
        return "Available databases:\n" + "\n".join(db_list)

    @mcp.prompt()
    def select_database() -> str:
        logger.debug("select_database prompt called")
        return "I need to determine which database to use for your query. Please use the list_databases tool first, then tell me which database ID to use."

    def get_database_schema_summary(db_config: DbConfig) -> str:
        logger.debug(f"get_database_schema_summary called for {db_config.id}")
        if db_config.schema is None:
            return "Schema information not available"
        tables = db_config.schema
        if not tables:
            return "No tables found in schema"
        table_summaries = []
        for table in tables[:10]:
            table_name = table.get("name", "")
            if not table_name:
                continue
            columns = table.get("columns", [])
            column_names = [col.get("name", "") for col in columns[:5]]
            column_str = ", ".join(column_names)
            if len(columns) > 5:
                column_str += ", ..."
            table_summaries.append(f"- {table_name} ({column_str})")
        if len(tables) > 10:
            table_summaries.append(f"... and {len(tables) - 10} more tables")
        return "\n".join(table_summaries) if table_summaries else "No tables found in schema"

    @mcp.tool()
    def get_database_info(ctx: Context, db_id: Optional[str] = None) -> str:
        logger.debug(f"get_database_info called with db_id={db_id}")
        db_context: DbContext = ctx.request_context.lifespan_context
        if db_id is None:
            all_info = []
            for curr_db_id, db_config in db_context.db_configs.items():
                info = f"Database ID: {curr_db_id}\n"
                info += f"Description: {db_config.description}\n"
                info += f"Type: {db_config.db_type}\n"
                info += f"Schema Summary:\n{get_database_schema_summary(db_config)}"
                all_info.append(info)
            return "\n\n".join(all_info)
        if db_id not in db_context.db_configs:
            logger.error(f"Invalid database ID: {db_id}")
            return f"Invalid database ID: {db_id}"
        db_config = db_context.db_configs[db_id]
        info = f"Database ID: {db_id}\n"
        info += f"Description: {db_config.description}\n"
        info += f"Type: {db_config.db_type}\n"
        info += f"Schema Summary:\n{get_database_schema_summary(db_config)}"
        return info

    def _execute_and_get_results(query: str, ctx: Context, db_id: str) -> Dict[str, Any]:
        logger.debug(f"_execute_and_get_results called with db_id={db_id}, query={query}")
        db_context = ctx.request_context.lifespan_context
        if db_id not in db_context.db_configs:
            logger.error(f"Invalid database ID: {db_id}")
            raise ValueError(f"Invalid database ID: {db_id}")
        db_config = db_context.db_configs[db_id]
        query_runner = db_config.query_runner
        result = query_runner.run_query(query)
        db_context.last_query = query
        db_context.last_result = result
        db_context.query_history.append(f"[{db_id}] [{db_config.description}] {query}")
        columns = result.get('columns', [])
        column_names = [col.get('friendly_name', col.get('name', '')) for col in columns]
        rows = result.get('rows', [])
        row_count = len(rows)
        processed_rows = []
        for row_dict in rows:
            processed_row = [row_dict.get(col.get('name', '')) for col in columns]
            processed_rows.append(processed_row)
        logger.debug(f"Query executed, {row_count} rows processed")
        return {
            'column_names': column_names,
            'columns': columns,
            'rows': processed_rows,
            'raw_rows': rows,
            'row_count': row_count,
            'database': {
                'id': db_id,
                'description': db_config.description,
                'db_type': db_config.db_type
            }
        }

    @mcp.tool()
    def execute_query(query: str, ctx: Context, db_id: str) -> str:
        logger.debug(f"execute_query called with db_id={db_id}, query={query}")
        try:
            result = _execute_and_get_results(query, ctx, db_id)
            db_info = f"Database: {result['database']['description']} (Type: {result['database']['db_type']})"
            header = " | ".join(result['column_names'])
            separator = " | ".join(["---"] * len(result['column_names']))
            table_rows = []
            for row in result['rows'][:10]:
                table_rows.append(" | ".join(str(cell) for cell in row))
            result_table = f"Query executed on Database: {result['database']['description']}\n\n"
            result_table += f"{header}\n{separator}\n" + "\n".join(table_rows)
            if result['row_count'] > 10:
                result_table += f"\n\n... and {result['row_count'] - 10} more rows (total: {result['row_count']})"
            return f"{db_info}\n\n{result_table}"
        except ValueError as e:
            logger.error(f"Error executing query: {str(e)}")
            if "Invalid database ID" in str(e):
                return f"Error: {str(e)}"
            return f"Error executing query: {str(e)}"
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return f"Error executing query: {str(e)}"

    @mcp.tool()
    def execute_query_json(query: str, ctx: Context, db_id: str) -> str:
        logger.debug(f"execute_query_json called with db_id={db_id}, query={query}")
        try:
            result = _execute_and_get_results(query, ctx, db_id)
            output = {
                'database': result['database'],
                'columns': result['column_names'],
                'rows': result['raw_rows'],
                'row_count': result['row_count']
            }
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return f"Error executing query: {str(e)}"

    @mcp.tool()
    def get_table_columns(table_name: str, ctx: Context, db_id: str) -> str:
        logger.debug(f"get_table_columns called for table {table_name} in db_id={db_id}")
        try:
            db_context: DbContext = ctx.request_context.lifespan_context
            if db_id not in db_context.db_configs:
                logger.error(f"Invalid database ID: {db_id}")
                raise ValueError(f"Invalid database ID: {db_id}")
            db_config = db_context.db_configs[db_id]
            columns = db_config.query_runner.get_table_columns(table_name)
            return json.dumps({
                'database': {
                    'id': db_id,
                    'description': db_config.description,
                    'db_type': db_config.db_type
                },
                'table': table_name,
                'columns': columns
            })
        except Exception as e:
            logger.error(f"Error getting columns for table {table_name}: {str(e)}")
            return f"Error getting columns for table {table_name}: {str(e)}"

    @mcp.tool()
    def get_table_types(table_name: str, ctx: Context, db_id: str) -> str:
        logger.debug(f"get_table_types called for table {table_name} in db_id={db_id}")
        try:
            db_context: DbContext = ctx.request_context.lifespan_context
            if db_id not in db_context.db_configs:
                logger.error(f"Invalid database ID: {db_id}")
                raise ValueError(f"Invalid database ID: {db_id}")
            db_config = db_context.db_configs[db_id]
            types = db_config.query_runner.get_table_types(table_name)
            return json.dumps({
                'database': {
                    'id': db_id,
                    'description': db_config.description,
                    'db_type': db_config.db_type
                },
                'table': table_name,
                'types': types
            })
        except Exception as e:
            logger.error(f"Error getting types for table {table_name}: {str(e)}")
            return f"Error getting types for table {table_name}: {str(e)}"

    @mcp.tool()
    def describe_table(ctx: Context, table_name: str, db_id: str) -> str:
        logger.debug(f"describe_table called for table {table_name} in db_id={db_id}")
        try:
            db_context: DbContext = ctx.request_context.lifespan_context
            if db_id not in db_context.db_configs:
                logger.error(f"Invalid database ID {db_id}")
                return f"Error: Invalid database ID {db_id}"
            db_config = db_context.db_configs[db_id]
            columns = db_config.query_runner.get_table_columns(table_name)
            types = db_config.query_runner.get_table_types(table_name)
            description = f"Table: {table_name} in Database: {db_config.description} (ID: {db_id})\n\n"
            description += "Columns:\n"
            for column in columns:
                column_type = types.get(column, "unknown")
                description += f"- {column} ({column_type})\n"
            return description
        except Exception as e:
            logger.error(f"Error describing table {table_name}: {str(e)}")
            return f"Error describing table {table_name}: {str(e)}"

    @mcp.tool()
    def get_table_sample(
        ctx: Context, 
        table_name: str, 
        db_id: str, 
        limit: int = 10
        ) -> str:
        logger.debug(f"get_table_sample called for table {table_name} in db_id={db_id} with limit={limit}")
        try:
            db_context: DbContext = ctx.request_context.lifespan_context
            if db_id not in db_context.db_configs:
                logger.error(f"Invalid database ID {db_id}")
                return f"Error: Invalid database ID {db_id}"
            db_config = db_context.db_configs[db_id]
            query_runner = db_config.query_runner
            query = f"SELECT * FROM {table_name} LIMIT {min(limit, 100)}"
            result = query_runner.run_query(query)
            columns = result.get('columns', [])
            column_names = []
            for col in columns:
                if isinstance(col, dict):
                    column_names.append(col.get('friendly_name', col.get('name', '')))
                else:
                    column_names.append(col)
            header = " | ".join(column_names)
            separator = " | ".join(["---"] * len(column_names))
            rows = result.get('rows', [])
            table_rows = []
            for row in rows:
                if isinstance(row, dict):
                    row_values = [str(row.get(col, '')) for col in column_names]
                else:
                    row_values = [str(cell) for cell in row]
                table_rows.append(" | ".join(row_values))
            sample_data = f"Sample data from table '{table_name}' in Database: {db_config.description} (ID: {db_id})\n\n"
            sample_data += f"{header}\n{separator}\n" + "\n".join(table_rows)
            if not rows:
                sample_data += "\n\nNo data found in table."
            return sample_data
        except Exception as e:
            logger.error(f"Error getting sample data from table {table_name}: {str(e)}")
            return f"Error getting sample data from table {table_name}: {str(e)}"

    @mcp.tool()
    def find_table(
        table_name: str, 
        ctx: Context
        ) -> str:
        logger.debug(f"find_table called for table {table_name}")
        db_context: DbContext = ctx.request_context.lifespan_context
        found_in = []
        for db_id, db_config in db_context.db_configs.items():
            if not db_config.schema:
                continue
            for table in db_config.schema:
                if table.get("name") == table_name:
                    found_in.append({
                        "db_id": db_id,
                        "db_name": db_config.description,
                        "db_type": db_config.db_type
                    })
                    break
        if not found_in:
            logger.info(f"Table '{table_name}' was not found in any database schema.")
            return f"Table '{table_name}' was not found in any database schema."
        result = f"Table '{table_name}' was found in the following databases:\n"
        for db in found_in:
            result += f"- Database ID: {db['db_id']} - {db['db_name']} (Type: {db['db_type']})\n"
        return result

    @mcp.tool()
    def save_markdown_directory(
        ctx: Context, 
        directory_path: str, 
        db_id: str, 
        recursive: bool = True
        ) -> str:
        logger.debug(f"save_markdown_directory called for directory {directory_path} in db_id={db_id}, recursive={recursive}")
        try:
            db_context: DbContext = ctx.request_context.lifespan_context
            if db_id not in db_context.db_configs:
                logger.error(f"Invalid database ID {db_id}")
                return f"Error: Invalid database ID {db_id}"
            db_config = db_context.db_configs[db_id]
            runner = db_config.query_runner
            _initialize_markdown_schema(runner)
            directory_path = Path(directory_path).resolve()
            if not directory_path.exists():
                logger.error(f"Directory not found: {directory_path}")
                return f"Error: Directory not found: {directory_path}"
            if not directory_path.is_dir():
                logger.error(f"Path is not a directory: {directory_path}")
                return f"Error: Path is not a directory: {directory_path}"
            pattern = "**/*.md" if recursive else "*.md"
            markdown_files = list(directory_path.glob(pattern))
            if not markdown_files:
                logger.warning(f"No markdown files found in {directory_path}")
                return f"Warning: No markdown files found in {directory_path}"
            files_added = 0
            files_updated = 0
            files_skipped = 0
            errors = []
            for file_path in markdown_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    relative_path = str(file_path.relative_to(directory_path))
                    file_name = file_path.name
                    file_size = len(content.encode('utf-8'))
                    content_hash = _calculate_hash(content)
                    escaped_path = relative_path.replace("'", "''")
                    existing_result = runner.run_query(f"SELECT hash, updated_at FROM markdown_files WHERE file_path = '{escaped_path}'")
                    if existing_result['rows']:
                        existing_hash = existing_result['rows'][0]['hash']
                        if existing_hash == content_hash:
                            files_skipped += 1
                            continue
                        else:
                            escaped_content = content.replace("'", "''")
                            update_sql = f"""
                            UPDATE markdown_files 
                            SET content = '{escaped_content}',
                                file_size = {file_size},
                                hash = '{content_hash}',
                                updated_at = CURRENT_TIMESTAMP
                            WHERE file_path = '{escaped_path}'
                            """
                            runner.run_query(update_sql)
                            files_updated += 1
                    else:
                        escaped_name = file_name.replace("'", "''")
                        escaped_content = content.replace("'", "''")
                        insert_sql = f"""
                        INSERT INTO markdown_files (file_path, file_name, content, file_size, hash)
                        VALUES (
                            '{escaped_path}',
                            '{escaped_name}',
                            '{escaped_content}',
                            {file_size},
                            '{content_hash}'
                        )
                        """
                        runner.run_query(insert_sql)
                        files_added += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    errors.append(f"Error processing {file_path}: {str(e)}")
            result = {
                "status": "success" if not errors else "partial_success",
                "message": f"Processed {len(markdown_files)} markdown files",
                "files_processed": len(markdown_files),
                "files_added": files_added,
                "files_updated": files_updated,
                "files_skipped": files_skipped,
                "base_directory": str(directory_path),
                "database": db_config.description
            }
            if errors:
                result["errors"] = errors
            logger.info(f"Markdown directory save result: {result}")
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error saving markdown files: {str(e)}")
            return f"Error saving markdown files: {str(e)}"

    @mcp.tool()
    def extract_markdown_files(ctx: Context, 
                               output_directory: str, 
                               db_id: str, 
                               overwrite: bool = False
                               ) -> str:
        logger.debug(f"extract_markdown_files called for output_directory {output_directory} in db_id={db_id}, overwrite={overwrite}")
        try:
            db_context: DbContext = ctx.request_context.lifespan_context
            if db_id not in db_context.db_configs:
                logger.error(f"Invalid database ID {db_id}")
                return f"Error: Invalid database ID {db_id}"
            db_config = db_context.db_configs[db_id]
            runner = db_config.query_runner
            output_path = Path(output_directory).resolve()
            output_path.mkdir(parents=True, exist_ok=True)
            result = runner.run_query("SELECT * FROM markdown_files ORDER BY file_path")
            if not result['rows']:
                logger.warning("No markdown files found in database")
                return json.dumps({
                    "status": "warning",
                    "message": "No markdown files found in database",
                    "files_extracted": 0,
                    "files_skipped": 0
                }, indent=2)
            files_extracted = 0
            files_skipped = 0
            errors = []
            for row in result['rows']:
                try:
                    file_path = output_path / row['file_path']
                    if file_path.exists() and not overwrite:
                        files_skipped += 1
                        continue
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(row['content'])
                    written_hash = _calculate_hash(row['content'])
                    if written_hash != row['hash']:
                        logger.warning(f"Hash mismatch for {file_path}: expected {row['hash']}, got {written_hash}")
                        errors.append(f"Hash mismatch for {file_path}: expected {row['hash']}, got {written_hash}")
                    files_extracted += 1
                except Exception as e:
                    logger.error(f"Error extracting {row['file_path']}: {str(e)}")
                    errors.append(f"Error extracting {row['file_path']}: {str(e)}")
            result = {
                "status": "success" if not errors else "partial_success",
                "message": f"Extracted {files_extracted} markdown files",
                "files_extracted": files_extracted,
                "files_skipped": files_skipped,
                "output_directory": str(output_path),
                "database": db_config.description
            }
            if errors:
                result["errors"] = errors
            logger.info(f"Markdown extraction result: {result}")
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error extracting markdown files: {str(e)}")
            return f"Error extracting markdown files: {str(e)}"

    @mcp.tool()
    def list_markdown_files(ctx: Context, db_id: str) -> str:
        logger.debug(f"list_markdown_files called for db_id={db_id}")
        try:
            db_context: DbContext = ctx.request_context.lifespan_context
            if db_id not in db_context.db_configs:
                logger.error(f"Invalid database ID {db_id}")
                return f"Error: Invalid database ID {db_id}"
            db_config = db_context.db_configs[db_id]
            runner = db_config.query_runner
            result = runner.run_query("""
                SELECT file_path, file_name, file_size, created_at, updated_at, hash
                FROM markdown_files 
                ORDER BY file_path
            """)
            if not result['rows']:
                logger.info("No markdown files found in database")
                return "No markdown files found in database"
            files_info = []
            for row in result['rows']:
                files_info.append({
                    "file_path": row['file_path'],
                    "file_name": row['file_name'],
                    "file_size": row['file_size'],
                    "created_at": str(row['created_at']),
                    "updated_at": str(row['updated_at']),
                    "hash": row['hash']
                })
            logger.info(f"Listed {len(files_info)} markdown files")
            return json.dumps({
                "total_files": len(files_info),
                "database": db_config.description,
                "files": files_info
            }, indent=2)
        except Exception as e:
            logger.error(f"Error listing markdown files: {str(e)}")
            return f"Error listing markdown files: {str(e)}"

    @mcp.tool()
    def get_markdown_file_content(ctx: Context, file_path: str, db_id: str) -> str:
        logger.debug(f"get_markdown_file_content called for file_path={file_path} in db_id={db_id}")
        try:
            db_context: DbContext = ctx.request_context.lifespan_context
            if db_id not in db_context.db_configs:
                logger.error(f"Invalid database ID {db_id}")
                return f"Error: Invalid database ID {db_id}"
            db_config = db_context.db_configs[db_id]
            runner = db_config.query_runner
            escaped_path = file_path.replace("'", "''")
            result = runner.run_query(f"""
                SELECT * FROM markdown_files 
                WHERE file_path = '{escaped_path}'
            """)
            if not result['rows']:
                logger.warning(f"File not found: {file_path}")
                return f"Error: File not found: {file_path}"
            file_info = result['rows'][0]
            logger.info(f"Fetched markdown file content for {file_path}")
            return json.dumps({
                "file_path": file_info['file_path'],
                "file_name": file_info['file_name'],
                "content": file_info['content'],
                "file_size": file_info['file_size'],
                "created_at": str(file_info['created_at']),
                "updated_at": str(file_info['updated_at']),
                "hash": file_info['hash']
            }, indent=2)
        except Exception as e:
            logger.error(f"Error getting markdown file: {str(e)}")
            return f"Error getting markdown file: {str(e)}"

    @mcp.tool()
    def delete_markdown_file(ctx: Context, file_path: str, db_id: str) -> str:
        logger.debug(f"delete_markdown_file called for file_path={file_path} in db_id={db_id}")
        try:
            db_context: DbContext = ctx.request_context.lifespan_context
            if db_id not in db_context.db_configs:
                logger.error(f"Invalid database ID {db_id}")
                return f"Error: Invalid database ID {db_id}"
            db_config = db_context.db_configs[db_id]
            runner = db_config.query_runner
            escaped_path = file_path.replace("'", "''")
            check_result = runner.run_query(f"""
                SELECT COUNT(*) as count FROM markdown_files 
                WHERE file_path = '{escaped_path}'
            """)
            if check_result['rows'][0]['count'] == 0:
                logger.warning(f"File not found: {file_path}")
                return f"Error: File not found: {file_path}"
            runner.run_query(f"""
                DELETE FROM markdown_files 
                WHERE file_path = '{file_path.replace("'", "''")}'
            """)
            logger.info(f"Successfully deleted markdown file: {file_path}")
            return f"Successfully deleted markdown file: {file_path}"
        except Exception as e:
            logger.error(f"Error deleting markdown file: {str(e)}")
            return f"Error deleting markdown file: {str(e)}"

    @mcp.tool()
    def get_markdown_stats(ctx: Context, db_id: str) -> str:
        logger.debug(f"get_markdown_stats called for db_id={db_id}")
        try:
            db_context: DbContext = ctx.request_context.lifespan_context
            if db_id not in db_context.db_configs:
                logger.error(f"Invalid database ID {db_id}")
                return f"Error: Invalid database ID {db_id}"
            db_config = db_context.db_configs[db_id]
            runner = db_config.query_runner
            stats_result = runner.run_query("""
                SELECT 
                    COUNT(*) as total_files,
                    SUM(file_size) as total_size,
                    AVG(file_size) as avg_size,
                    MIN(created_at) as oldest_created,
                    MAX(updated_at) as newest_updated
                FROM markdown_files
            """)
            if not stats_result['rows']:
                logger.info("No markdown files found in database")
                return "No markdown files found in database"
            stats = stats_result['rows'][0]
            logger.info(f"Markdown stats: {stats}")
            return json.dumps({
                "database": db_config.description,
                "total_files": stats['total_files'],
                "total_size_bytes": stats['total_size'],
                "average_size_bytes": stats['avg_size'],
                "oldest_created": str(stats['oldest_created']) if stats['oldest_created'] else None,
                "newest_updated": str(stats['newest_updated']) if stats['newest_updated'] else None
            }, indent=2)
        except Exception as e:
            logger.error(f"Error getting markdown stats: {str(e)}")
            return f"Error getting markdown stats: {str(e)}"

    @mcp.prompt()
    def sql_query() -> str:
        logger.debug("sql_query prompt called")
        return "Please help me write a SQL query for the following question:\n\n"

    @mcp.prompt()
    def explain_query(query: str) -> str:
        logger.debug(f"explain_query prompt called for query: {query}")
        return f"Can you explain what the following SQL query does?\n\n{query}\n"

    @mcp.prompt()
    def optimize_query(query: str) -> str:
        logger.debug(f"optimize_query prompt called for query: {query}")
        return f"Can you optimize the following SQL query for better performance?\n\nsql\n{query}\n"

    return mcp
