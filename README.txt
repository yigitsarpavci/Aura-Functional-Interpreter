Yiğit Sarp Avcı, 2023400048
Mehmet Doğukan Sungu, 2023400210

Aura Functional Interpreter
Built for CMPE 260 Project 1, Spring 2026 (Boğaziçi University).

----------------------------------------------------
How to Run the Interpreter
----------------------------------------------------
The interpreter is written in Python (compatible with Python 3.8+).

Run a program in the default (static/lexical scoping) mode:
    python interpreter.py <path_to_program_file>

Run a program with static scoping explicitly selected:
    python interpreter.py --scope static <path_to_program_file>

Run a program with dynamic scoping selected:
    python interpreter.py --scope dynamic <path_to_program_file>

----------------------------------------------------
How to Run the Test Suite
----------------------------------------------------
Under bash/Unix systems:
    chmod +x run_tests.sh
    ./run_tests.sh
