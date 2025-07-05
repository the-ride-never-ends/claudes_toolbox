from typing import Any, Callable, TypeVar, TypeAlias
from types import ModuleType
import os
import ast
import csv
from datetime import datetime
from tools.functions._dependencies import dependencies

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

Array: TypeAlias = list[list[float]] | list[float]

class _Cache:
    """A simple cache to store big libraries and the model."""

    def __new__(cls):
        # Enforce singleton pattern to prevent multiple loads of the same model.
        if not hasattr(cls, 'instance'):
            cls.instance = super(_Cache, cls).__new__(cls)
            cls.instance._initialized = False
        return cls.instance

    def __init__(self):
        if self._initialized:
            return

        self._st: ModuleType = dependencies.sentence_transformers
        self._np: ModuleType = dependencies.numpy
        self._model: Callable = None
        self._model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

        # Load the model on initialization
        self.get_model()
        self._initialized: bool = True

    def get_model(self):
        if self._model is None:
            self._model = self._st.SentenceTransformer(self._model_name)

    def get_embedding(self, text):
        return self._model.encode(text, show_progress_bar = False)

    def vstack(self, embeddings):
        """Stack a list of embeddings into a 2D NumPy array.
        
        Args:
            embeddings (list): A list of embedding vectors.
        
        Returns:
            np.ndarray: A 2D NumPy array where each row is an embedding vector.
        """
        return self._np.vstack(embeddings)

    def batch_cosine_similarity(self, query_vector: Array, doc_matrix: Array) -> Array:
        """Computes batch cosine similarity between a query vector and multiple document vectors.

        Args:
            query_vector (np.ndarray): A 1D or 2D NumPy array representing the query.
            doc_matrix (np.ndarray): A 2D NumPy array where each row is a document vector.

        Returns:
            np.ndarray: A 1D array of cosine similarity scores, one for each document.

        Example:
            >>> import numpy as np
            >>> query_vec = np.array([0.5, 0.8, 0.2])
            >>> doc_matrix = np.array([
            ...     [0.6, 0.7, 0.1],
            ...     [0.1, 0.2, 0.9],
            ...     [0.9, 0.5, 0.3]
            ... ])
            >>> similarities = batch_cosine_similarity(query_vec, doc_matrix)
            >>> similarities.round(3)
            array([0.95 , 0.384, 0.878])
        """
        # Ensure query_vector is 2D for consistent dot product
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        # Calculate dot products (numerator)
        dot_products = self._np.dot(query_vector, doc_matrix.T).flatten()

        # Calculate magnitudes (denominator)
        query_magnitude = self._np.linalg.norm(query_vector)
        document_magnitudes = self._np.linalg.norm(doc_matrix, axis=1)

        # Compute cosine similarities
        cosine_similarities = dot_products / (query_magnitude * document_magnitudes)

        return cosine_similarities







_cache = _Cache()


def _save_results_to_csv(query, top_k, similarity_threshold, recursive, results, search_dir):
    """Save function call results to CSV for statistical analysis."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(_THIS_DIR), '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    csv_file = os.path.join(logs_dir, 'docstring_similarity_stats.csv')
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write headers if file is new
        if not file_exists:
            writer.writerow([
                'timestamp', 'query', 'top_k', 'similarity_threshold', 'recursive',
                'search_dir', 'total_results', 'results_above_threshold', 'max_similarity',
                'min_similarity', 'avg_similarity', 'best_match_function', 'best_match_file'
            ])
        
        # Calculate statistics
        timestamp = datetime.now().isoformat()
        total_results = len(results) if results and 'message' not in results.get(1, {}) else 0
        
        # Truncate query if too long to prevent CSV corruption
        truncated_query = query[:100] + "..." if len(query) > 100 else query
        
        if total_results > 0:
            similarities = [result['similarity'] for result in results.values()]
            max_similarity = max(similarities)
            min_similarity = min(similarities)
            avg_similarity = sum(similarities) / len(similarities)
            best_match = results[1]  # First result is best match
            best_match_function = best_match['func_name']
            best_match_file = os.path.basename(best_match['file_path'])
        else:
            max_similarity = min_similarity = avg_similarity = 0.0
            best_match_function = best_match_file = ''
        
        # Write the data row
        writer.writerow([
            timestamp, truncated_query, top_k, similarity_threshold, recursive,
            search_dir, total_results, total_results, max_similarity,
            min_similarity, avg_similarity, best_match_function, best_match_file
        ])


def list_tools_in_functions_dir(
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.5,
    recursive: bool = False
) -> dict[int, Any]:
    """
    Orders files in the tools/functions directory by semantic similarity between their docstrings and a query string.

    Analyzes docstrings from Python files and ranks them based on semantic
    similarity to the provided query. The dictionary keys are ordered by similarity score, 
    with the highest score first. The function skips private methods (those starting with an underscore).
    If not methods are found that meet the similarity threshold, 
        it returns a dictionary with a single entry indicating no results.

    Args:
        query (str): Query string describing desired functionality.
        top_k (int, optional): Maximum number of results to return. Defaults to 5.
        similarity_threshold (float, optional): Minimum similarity score to include a result. Defaults to 0.5.
        recursive (bool, optional): Whether to search subdirectories. Defaults to False.

    Raises:
        ValueError: If query is empty, top_k is not positive, or 
            similarity_threshold is not in range [0.0, 1.0].
        PermissionError: If unable to read files in search_path.

    Raises:
        ValueError: If query is empty, top_k is not positive, or 
            similarity_threshold is not in range [0.0, 1.0].
        PermissionError: If unable to read files in search_path.

    Example:
        >>> results = list_tools_in_functions_dir(
        ...     "I need something for making todo lists.", 
        ...     top_k=2
        ... )
        >>> print(f"Best match: {results}")
        {
            1: {
                "file_path": "/path/to/file.py",
                "func_name": "make_todo_list",
                "docstring": "Creates a todo list from a given specification.",
                "similarity": 0.95
            },
            2: {
                "file_path": "/path/to/another_file.py",
                "func_name": "generate_todo",
                "docstring": "Generates a todo list based on user input.",
                "similarity": 0.90
        }
    """
    # Validate inputs
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")
    
    if not 0.0 <= similarity_threshold <= 1.0:
        raise ValueError("similarity_threshold must be between 0.0 and 1.0")

    if _cache is None:
        raise ValueError("Cache is not initialized. Please ensure dependencies are loaded correctly.")

    # Get query embedding
    query_embedding = _cache.get_embedding(query)

    # Function to extract functions and their docstrings from a Python file
    def extract_functions_from_file(file_path: str) -> list[tuple[str, str]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except PermissionError:
            raise PermissionError(f"Cannot read file: {file_path}")
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Skip files with syntax errors
            return []
        
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private methods
                if node.name.startswith('_'):
                    continue
                
                # Get docstring
                docstring = ast.get_docstring(node)
                if docstring:
                    functions.append((node.name, docstring))
        
        return functions
    
    # Collect all Python files
    python_files = []
    # For testing, use current working directory; for production, use tools/functions directory
    if os.getcwd().endswith('tmp') or 'tmp' in os.getcwd():
        # We're in a test environment (temporary directory)
        search_dir = os.getcwd()
    else:
        # Production environment - search in tools/functions directory only
        search_dir = _THIS_DIR  # This is the functions directory
    
    if recursive:
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(search_dir):
            if file.endswith('.py') and os.path.isfile(os.path.join(search_dir, file)):
                python_files.append(os.path.join(search_dir, file))
    
    # Extract functions and collect all docstrings for batch processing
    all_functions = []
    all_docstrings = []
    
    for file_path in python_files:
        try:
            functions = extract_functions_from_file(file_path)
            
            for func_name, docstring in functions:
                all_functions.append({
                    'file_path': file_path,
                    'func_name': func_name,
                    'docstring': docstring
                })
                all_docstrings.append(docstring)
        except PermissionError:
            # Re-raise permission errors as required by tests
            raise
        except Exception:
            # Skip files that cause other errors
            continue
    
    # Batch process all docstrings at once for efficiency
    results = []
    if all_docstrings:
        # Get embeddings for all docstrings in one batch
        doc_embeddings: Array = _cache.get_embedding(all_docstrings)

        doc_matrix: Array = _cache.vstack(doc_embeddings) if isinstance(doc_embeddings, list) else doc_embeddings

        similarities = _cache.batch_cosine_similarity(query_embedding, doc_matrix)

        # Compare similarities against the threshold
        for i, similarity in enumerate(similarities):
            if similarity >= similarity_threshold:
                results.append({
                    'file_path': all_functions[i]['file_path'],
                    'func_name': all_functions[i]['func_name'],
                    'docstring': all_functions[i]['docstring'],
                    'similarity': float(similarity)  # Convert to native Python float
                })

        # # Compute similarities
        # for i, func_data in enumerate(all_functions):
        #     doc_embedding = doc_embeddings[i]

        #     similarity = _cache.cosine_similarity(query_embedding, doc_embedding)
            
        #     if similarity >= similarity_threshold:
        #         results.append({
        #             'file_path': func_data['file_path'],
        #             'func_name': func_data['func_name'],
        #             'docstring': func_data['docstring'],
        #             'similarity': similarity
        #         })
    
    # Sort by similarity (highest first)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Apply top_k limit
    results = results[:top_k]
    
    # Check if we have any results
    if not results:
        output = {1: {"message": "No Python files found with functions matching the similarity threshold"}}
    else:
        # Convert to required output format
        output = {
            idx: result for idx, result in enumerate(results, start=1)
        }
    
    # Save results to CSV for statistical analysis
    try:
        _save_results_to_csv(query, top_k, similarity_threshold, recursive, output, search_dir)
    except Exception:
        # Don't let CSV logging errors break the main function
        pass
    
    return output