#!/usr/bin/env python3
"""
Test script for the DuckDB database server functionality.
This script tests the core DuckDB operations to ensure everything works correctly.
"""

import sys
import os
import json
import traceback

# Add the current directory to Python path so we can import the database module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import DuckDBQueryRunner, DbConfig, init_config
    print("✓ Successfully imported database module")
except ImportError as e:
    print(f"✗ Failed to import database module: {e}")
    sys.exit(1)

def test_duckdb_query_runner():
    """Test the DuckDBQueryRunner class"""
    print("\n=== Testing DuckDBQueryRunner ===")
    
    try:
        # Test 1: Create in-memory database
        print("Test 1: Creating in-memory DuckDB connection...")
        runner = DuckDBQueryRunner()
        print("✓ Successfully created DuckDBQueryRunner")
        
        # Test 2: Test connection
        print("Test 2: Testing database connection...")
        runner.test_connection()
        print("✓ Database connection test passed")
        
        # Test 3: Create a test table and insert data
        print("Test 3: Creating test table and inserting data...")
        runner.run_query("CREATE TABLE test_users (id INTEGER, name VARCHAR, age INTEGER)")
        runner.run_query("INSERT INTO test_users VALUES (1, 'Alice', 30), (2, 'Bob', 25), (3, 'Charlie', 35)")
        print("✓ Successfully created table and inserted data")
        
        # Test 4: Query data
        print("Test 4: Querying data...")
        result = runner.run_query("SELECT * FROM test_users ORDER BY age")
        print(f"✓ Query returned {result['row_count']} rows")
        print(f"  Columns: {[col['name'] for col in result['columns']]}")
        print(f"  Sample row: {result['rows'][0] if result['rows'] else 'No data'}")
        
        # Test 5: Get schema
        print("Test 5: Getting database schema...")
        schema = runner.get_schema()
        print(f"✓ Schema contains {len(schema)} tables")
        if schema:
            print(f"  First table: {schema[0]['name']} with {len(schema[0]['columns'])} columns")
        
        # Test 6: Get table columns
        print("Test 6: Getting table columns...")
        columns = runner.get_table_columns("test_users")
        print(f"✓ Table 'test_users' has columns: {columns}")
        
        # Test 7: Get table types
        print("Test 7: Getting table column types...")
        types = runner.get_table_types("test_users")
        print(f"✓ Column types: {types}")
        
        # Test 8: Close connection
        print("Test 8: Closing connection...")
        runner.close()
        print("✓ Connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ DuckDBQueryRunner test failed: {e}")
        traceback.print_exc()
        return False

def test_config_initialization():
    """Test the configuration initialization"""
    print("\n=== Testing Configuration Initialization ===")
    
    try:
        # Test 1: Initialize with default settings (testing mode)
        print("Test 1: Initialize default configuration...")
        config_map = init_config(testing=True)
        print(f"✓ Initialized {len(config_map)} database configurations")
        
        # Test 2: Check configuration structure
        print("Test 2: Checking configuration structure...")
        for db_id, db_config in config_map.items():
            print(f"  Database ID: {db_id}")
            print(f"  Description: {db_config.description}")
            print(f"  Type: {db_config.db_type}")
            print(f"  Has query runner: {db_config.query_runner is not None}")
            
            # Test the query runner
            if db_config.query_runner:
                db_config.query_runner.test_connection()
                print(f"  ✓ Connection test passed for {db_id}")
        
        # Test 3: Initialize with multiple database configs
        print("Test 3: Initialize with multiple database configs...")
        test_configs = [
            {"description": "Test Database 1", "db_path": ":memory:"},
            {"description": "Test Database 2", "db_path": ":memory:", "id": "test_db_2"}
        ]
        
        multi_config_map = init_config(
            testing=True,
            test_db_configs=json.dumps(test_configs)
        )
        print(f"✓ Initialized {len(multi_config_map)} database configurations")
        
        for db_id, db_config in multi_config_map.items():
            print(f"  Database ID: {db_id} - {db_config.description}")
            db_config.query_runner.test_connection()
            print(f"  ✓ Connection test passed for {db_id}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration initialization test failed: {e}")
        traceback.print_exc()
        return False

def test_database_operations():
    """Test end-to-end database operations"""
    print("\n=== Testing Database Operations ===")
    
    try:
        # Initialize configuration
        config_map = init_config(testing=True)
        db_id = next(iter(config_map))
        db_config = config_map[db_id]
        runner = db_config.query_runner
        
        print(f"Using database: {db_config.description}")
        
        # Create sample data
        print("Creating sample data...")
        runner.run_query("""
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                department VARCHAR(50),
                salary DECIMAL(10,2),
                hire_date DATE
            )
        """)
        
        runner.run_query("""
            INSERT INTO employees VALUES
            (1, 'John Doe', 'Engineering', 75000.00, '2020-01-15'),
            (2, 'Jane Smith', 'Marketing', 65000.00, '2019-03-20'),
            (3, 'Mike Johnson', 'Engineering', 80000.00, '2021-06-10'),
            (4, 'Sarah Wilson', 'HR', 55000.00, '2018-11-05'),
            (5, 'Tom Brown', 'Marketing', 70000.00, '2020-09-12')
        """)
        
        print("✓ Sample data created")
        
        # Test various queries
        test_queries = [
            ("Count employees", "SELECT COUNT(*) as total_employees FROM employees"),
            ("Average salary", "SELECT AVG(salary) as avg_salary FROM employees"),
            ("Employees by department", "SELECT department, COUNT(*) as count FROM employees GROUP BY department"),
            ("High earners", "SELECT name, salary FROM employees WHERE salary > 70000 ORDER BY salary DESC"),
        ]
        
        for description, query in test_queries:
            print(f"\nTesting: {description}")
            print(f"Query: {query}")
            result = runner.run_query(query)
            print(f"✓ Result: {result['row_count']} rows returned")
            if result['rows']:
                print(f"  Sample result: {result['rows'][0]}")
        
        # Test schema operations
        print("\nTesting schema operations...")
        schema = runner.get_schema()
        print(f"✓ Found {len(schema)} tables in schema")
        
        for table in schema:
            table_name = table['name']
            columns = runner.get_table_columns(table_name)
            types = runner.get_table_types(table_name)
            print(f"  Table: {table_name}")
            print(f"    Columns: {columns}")
            print(f"    Types: {list(types.values())}")
        
        return True
        
    except Exception as e:
        print(f"✗ Database operations test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("DuckDB Database Server Test Suite")
    print("=" * 50)
    
    tests = [
        ("DuckDBQueryRunner", test_duckdb_query_runner),
        ("Configuration Initialization", test_config_initialization),
        ("Database Operations", test_database_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning test: {test_name}")
        print("-" * 30)
        
        if test_func():
            print(f"✓ {test_name} PASSED")
            passed += 1
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DuckDB integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
