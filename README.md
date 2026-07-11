# Aura Functional Interpreter

Aura is a robust, lightweight interpreter for a custom-designed functional programming language, built as part of the **CMPE 260 (Principles of Programming Languages)** curriculum at **Bogazici University**.

---

## Key Features

- **Multi-Paradigm Execution**: Native support for first-class functions, closures, and higher-order function patterns.
- **Advanced Data Types**: Full support for integers, booleans, strings, and dynamic lists.
- **Dual Scoping Engine**: Toggleable execution between lexical (static) and dynamic scoping via the `--scope` flag.
- **Hardened Runtime**: Comprehensive type checking, source coordinate error reporting, and recursion protection.
- **Pure Python Core**: Zero external dependencies for the runtime.

---

## Usage

```bash
python3 interpreter.py examples/recursion.txt --scope static
```

### Available Flags

| Flag | Description |
| :--- | :--- |
| `--scope static` | Use lexical (static) scoping (default) |
| `--scope dynamic` | Use dynamic scoping |

---

## Project Structure

```
├── interpreter.py        # Main interpreter entry point
├── examples/             # Sample programs demonstrating language features
│   ├── basics.txt
│   ├── closures.txt
│   ├── higher_order.txt
│   ├── recursion.txt
│   └── scope.txt
├── tests/                # Automated test suite with expected outputs
│   ├── test01_arithmetic.txt / .expected
│   ├── test02_comparison.txt / .expected
│   └── ...
├── run_tests.sh          # Shell script to run all tests
└── docs/                 # Design documentation
    ├── ast.pdf           # Abstract Syntax Tree diagrams
    ├── grammar.pdf       # EBNF grammar specification
    └── report.pdf        # Detailed design report
```

---

## Local Setup

### Prerequisites
- Python 3.8+

### Running
```bash
git clone https://github.com/yigitsarpavci/Aura-Functional-Interpreter.git
cd Aura-Functional-Interpreter
python3 interpreter.py examples/basics.txt
```

---

## Testing

Run the full test suite using the included shell script:

```bash
chmod +x run_tests.sh
./run_tests.sh
```

Each test case consists of a `.txt` input file and a corresponding `.expected` output file in the `tests/` directory. The script compares interpreter output against expected results.

---

## Documentation

Detailed design choices, grammar specifications (EBNF), and AST diagrams are available in the [docs/](docs/) directory.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
