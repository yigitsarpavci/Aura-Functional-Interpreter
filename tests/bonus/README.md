# Released Bonus Tests

These tests cover the auto-graded bonus features (B1--B4) from the project
specification. Bonus tests are **optional**: failing them does not affect
your D3 score on the core interpreter. They contribute only to the bonus
points described in the spec, with per-feature caps:

| Feature | Cap |
|---------|-----|
| B1 strings | 5 |
| B2 while | 5 |
| B3 lists | 5 |
| B4 dual scoping | 10 |

The total bonus is capped at **20 points**.

## Filename convention

The autograder routes tests to features by filename prefix and (for B4)
suffix:

```
b1_*.txt           B1 strings
b2_*.txt           B2 while
b3_*.txt           B3 lists
b4_*_static.txt    B4 -- run with --scope static
b4_*_dynamic.txt   B4 -- run with --scope dynamic
```

For B4, paired `_static` / `_dynamic` files contain the **same source code**
but expect different output depending on the scoping rule. The autograder
invokes your interpreter twice with the corresponding `--scope` flag.

## Running the released bonus tests locally

```bash
# Run a single bonus test
python interpreter.py tests/released/bonus/b1_concat.txt

# Run a B4 test with the appropriate scoping flag
python interpreter.py --scope static  tests/released/bonus/b4_basic_static.txt
python interpreter.py --scope dynamic tests/released/bonus/b4_basic_dynamic.txt
```

Compare against the corresponding `.expected` file:

```bash
diff <(python interpreter.py tests/released/bonus/b1_concat.txt) \
     tests/released/bonus/b1_concat.expected
```

## Reminders

- Implementing any bonus feature requires using the **Bonus Standard Syntax**
  in the project description (string literals with `\n \t \\ \"`,
  `while ... do ... end`, `[a, b]` and `lst[i]`, `length(...)` /
  `append(...)` as reserved keywords, `--scope static|dynamic` for B4).
- The keywords `while`, `do`, `length`, and `append` are reserved in *all*
  programs (regardless of which bonus features you implement) so that the
  language remains stable.
- Unreleased bonus tests follow the same filename convention and are used
  during grading only.
