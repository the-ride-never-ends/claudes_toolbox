I'll update the PRD to reflect the new architecture with state persistence.

## Product Requirement Document (PRD) - Revised v2

### Problem Statement
When code changes in a codebase, developers need to know which tests are affected by those changes. Currently, this requires manual inspection or running all tests, which is time-consuming and error-prone. We need an automated tool that can analyze code changes and generate a detailed report of which tests need to be updated.

### Goals
1. **Automatically identify code changes** that could affect test behavior
2. **Track changes over time** by maintaining state between runs
3. **Map code changes to their corresponding tests** accurately
4. **Generate detailed reports** showing what changed and which tests are affected
5. **Support unit test focus** while being extensible to other test types
6. **Provide actionable information** to help developers update tests efficiently

### Minimum Viable Product (MVP)

The MVP should:

1. **State Management**
   - Maintain persistent state between runs to track code evolution
   - Store baseline snapshots of code structure on first run
   - Compare current state against previous state to detect changes
   - Handle state corruption gracefully
   - Provide option to reset state and start fresh

2. **Change Detection**
   - Detect changes to functions, methods, and classes since last run
   - Identify changes to function signatures (parameters, return types)
   - Identify changes to function implementations
   - Track changes to class attributes and methods
   - Track changes to module-level constants and variables that tests might depend on
   - Detect newly added code elements
   - Detect removed code elements

3. **Test Mapping**
   - Identify which tests are related to changed code elements
   - Support unittest framework
   - Handle various test organization patterns (separate test files, test directories)
   - Map both direct imports and indirect dependencies

4. **Report Generation**
   - Generate a JSON report listing:
     - Each changed code element (function/class/method/etc.)
     - The type of change (signature change, implementation change, added, removed)
     - All tests that reference or test that code element
     - Metadata including timestamp, target path, and whether it's a first run
   - Structure the JSON for easy parsing and transformation
   - Report only changes since the last run (not cumulative)

5. **Scope**
   - Focus on Python codebases
   - Prioritize unit test identification
   - Analyze a single codebase directory with its associated tests
   - Support continuous monitoring through repeated runs

### Non-Functional Requirements
- Accuracy: Should have minimal false positives/negatives in test identification
- Reliability: Should handle state file corruption gracefully
- Performance: State storage should not significantly impact analysis time

### Stretch Goals
- Support for pytest framework
- Specific details about what changed (e.g., "parameter 'x' renamed to 'value'")
- Additional output formats (text, markdown) built from JSON
- Configuration file support for customizing behavior
- Integration with version control systems for more detailed change tracking

### Out of Scope for MVP
- Integration tests or end-to-end tests (future enhancement)
- Auto-updating tests (only reporting)
- Real-time monitoring of changes
- Cross-language support
- Distributed state management (multiple users/machines)

### Usage Model

The tool will be used as a command-line program:

```bash
# First run - establishes baseline
python test_change_detector.py --path /path/to/codebase

# Subsequent runs - reports changes since last run
python test_change_detector.py --path /path/to/codebase

# Reset state and start fresh
python test_change_detector.py --path /path/to/codebase --reset-state
```

The tool stores its state in a `.test_change_detector` directory within the target codebase, making it easy to exclude from version control if desired.

## Success Criteria
### 1. Change Detection Accuracy

The system must accurately identify code changes between runs with emphasis on minimizing false negatives.

$$P_{change} = \frac{TP_{change}}{TP_{change} + FP_{change}}$$

$$R_{change} = \frac{TP_{change}}{TP_{change} + FN_{change}}$$

$$F1_{change}^{weighted} = \frac{(1 + \beta^2) \cdot P_{change} \cdot R_{change}}{\beta^2 \cdot P_{change} + R_{change}}$$

Where:
- $TP_{change}$ = True Positives: Actual code changes since last run correctly identified
- $FP_{change}$ = False Positives: Non-changes incorrectly identified as changes
- $FN_{change}$ = False Negatives: Actual changes since last run that were missed
- $\beta = 2$ = Weight factor favoring recall (minimizing false negatives)
- $P_{change}$ = Precision of change detection (target: ≥ 0.85)
- $R_{change}$ = Recall of change detection (target: ≥ 0.99)
- $F1_{change}^{weighted}$ = Weighted F1 score for change detection (target: ≥ 0.95)

### 2. State Management Reliability

The system must reliably maintain state between runs.

$$R_{state} = \frac{N_{successful\_runs}}{N_{total\_runs}}$$

$$R_{recovery} = \frac{N_{recovered}}{N_{corruptions}}$$

Where:
- $N_{successful\_runs}$ = Number of runs that successfully read/write state
- $N_{total\_runs}$ = Total number of runs attempted
- $N_{recovered}$ = Number of times system recovered from corrupted state
- $N_{corruptions}$ = Number of times state corruption was encountered
- $R_{state}$ = State reliability rate (target: ≥ 0.999)
- $R_{recovery}$ = Recovery success rate (target: 1.0)

### 3. Test Mapping Accuracy

The system must correctly map changed code elements to their corresponding tests, prioritizing minimal false negatives.

$$P_{map} = \frac{TP_{map}}{TP_{map} + FP_{map}}$$

$$R_{map} = \frac{TP_{map}}{TP_{map} + FN_{map}}$$

$$F1_{map}^{weighted} = \frac{(1 + \beta^2) \cdot P_{map} \cdot R_{map}}{\beta^2 \cdot P_{map} + R_{map}}$$

Where:
- $TP_{map}$ = True Positives: Tests correctly identified as needing updates
- $FP_{map}$ = False Positives: Tests incorrectly flagged as needing updates
- $FN_{map}$ = False Negatives: Tests that need updates but weren't flagged
- $\beta = 2$ = Weight factor favoring recall
- $P_{map}$ = Precision of test mapping (target: ≥ 0.80)
- $R_{map}$ = Recall of test mapping (target: ≥ 0.98)
- $F1_{map}^{weighted}$ = Weighted F1 score for test mapping (target: ≥ 0.92)

### 4. Report Completeness

The generated report must contain all required information fields.

$$C_{report} = \frac{\sum_{i=1}^{N} \sum_{j=1}^{M} I_{ij}}{N \cdot M}$$

$$C_{metadata} = \frac{\sum_{k=1}^{K} M_k}{K}$$

Where:
- $N$ = Number of detected changes
- $M$ = Number of required fields per change (element_type, element_name, file_path, change_type, affected_tests)
- $I_{ij}$ = Indicator function: 1 if field $j$ is present for change $i$, 0 otherwise
- $K$ = Number of required metadata fields (first_run, run_timestamp, target_path)
- $M_k$ = Indicator: 1 if metadata field $k$ is present, 0 otherwise
- $C_{report}$ = Change completeness score (target: 1.0)
- $C_{metadata}$ = Metadata completeness score (target: 1.0)

### 5. Code Coverage

The system should handle various Python code constructs.

$$Coverage_{constructs} = \frac{\sum_{c \in C} w_c \cdot I_c}{\sum_{c \in C} w_c}$$

Where:
- $C$ = Set of Python constructs: {function_def, async_function_def, method_def, classmethod_def, staticmethod_def, property_def, class_def, module_var, module_const}
- $I_c$ = Indicator: 1 if construct $c$ is handled, 0 otherwise
- $w_c$ = Weight for construct $c$:
  - $w_{function\_def} = 1.0$ (regular functions)
  - $w_{async\_function\_def} = 0.8$ (async functions)
  - $w_{method\_def} = 1.0$ (instance methods)
  - $w_{classmethod\_def} = 0.9$ (class methods)
  - $w_{staticmethod\_def} = 0.9$ (static methods)
  - $w_{property\_def} = 0.8$ (properties)
  - $w_{class\_def} = 1.0$ (class definitions)
  - $w_{module\_var} = 0.7$ (module-level variables)
  - $w_{module\_const} = 0.8$ (module-level constants)
- $Coverage_{constructs}$ = Weighted coverage score (target: ≥ 0.95)

### 6. JSON Validity

All generated reports must conform to JSON specification and schema.

$$V_{json} = V_{syntax} \cdot V_{schema}$$

$$V_{syntax} = \frac{N_{parseable}}{N_{total}}$$

$$V_{schema} = \frac{\sum_{i=1}^{N_{parseable}} S_i}{N_{parseable}}$$

Where:
- $N_{parseable}$ = Number of reports that can be parsed by a standard JSON parser
- $N_{total}$ = Total number of reports generated
- $S_i$ = Schema validation indicator: 1 if report $i$ conforms to predefined schema, 0 otherwise
- $V_{syntax}$ = Syntactic validity rate (target: 1.0)
- $V_{schema}$ = Schema conformance rate (target: 1.0)
- $V_{json}$ = Overall JSON validity (target: 1.0)

The JSON schema must include:
- Root object with keys: "changes", "metadata"
- Each change object must have: "element_type", "element_name", "file_path", "change_type", "affected_tests"
- Metadata must have: "first_run" (boolean), "run_timestamp" (ISO 8601 string), "target_path" (string)
- All strings must be properly escaped
- No trailing commas, proper nesting, valid Unicode

### 7. Temporal Consistency

The system must correctly track changes only since the last run.

$$T_{consistency} = \frac{N_{correct\_deltas}}{N_{total\_runs} - 1}$$

Where:
- $N_{correct\_deltas}$ = Number of runs where reported changes accurately reflect only changes since the previous run
- $N_{total\_runs}$ = Total number of runs (excluding first run)
- $T_{consistency}$ = Temporal consistency rate (target: 1.0)
