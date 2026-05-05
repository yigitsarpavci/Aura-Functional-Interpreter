# Aura Functional Interpreter

Aura is a robust, lightweight interpreter for a custom-designed functional programming language, built as part of the **CMPE 260 (Principles of Programming Languages)** curriculum at **Boğaziçi University**.

## 🚀 Key Features

- **Multi-Paradigm Execution**: Native support for first-class functions, closures, and higher-order function patterns.
- **Advanced Data Types**: Full support for **Integers**, **Booleans**, **Strings**, and dynamic **Lists**.
- **Dual Scoping Engine**: Toggleable execution between **Lexical (Static)** and **Dynamic** scoping via `--scope`.
- **Hardenened Runtime**: Comprehensive type checking, source coordinate error reporting, and recursion protection.
- **Pure Python Core**: Zero external dependencies for the runtime.

## ⚙️ Usage

```bash
python3 interpreter.py examples/recursion.txt --scope static
```

## 📂 Documentation

Detailed design choices, grammar specifications (EBNF), and AST diagrams are available in the [docs/](docs/) directory.
