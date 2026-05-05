# Authors: Yiğit Sarp Avcı (2023400048) & Doğukan Sungu (2023400210)
import sys
import re
import argparse

# Increase recursion depth for deep recursive calls in the mini-language
sys.setrecursionlimit(5000)

"""
CMPE 260 - Principles of Programming Languages
Project 1: Mini Programming Language Interpreter

This interpreter implements a functional programming language with features including:
- Lexical and Dynamic Scoping (via --scope flag)
- First-class Functions and Closures
- Explicit Environment Management (Activation Records)
- Support for Integers, Booleans, Strings, and Lists
- Implicit Recursion for 'let' bound functions
"""

class Token:
    """Represents a single lexical unit in the source code."""
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}:{self.column})"

class Lexer:
    """Performs lexical analysis by converting source code into a stream of tokens."""
    TOKEN_SPEC = [
        ('COMMENT_START', r'\(\*'),            # Start of comment
        ('STRING',   r'"(?:\\.|[^"\\])*"'),   # String literals with escape support
        ('NUMBER',   r'\d+'),                 # Integer literals
        ('BOOL',     r'(?:true|false)\b'),    # Boolean literals (with word boundary)
        ('LET',      r'let\b'),               # Keywords
        ('WHILE',    r'while\b'),
        ('DO',       r'do\b'),
        ('PRINT',    r'print\b'),
        ('IF',       r'if\b'),
        ('THEN',     r'then\b'),
        ('ELSE',     r'else\b'),
        ('FUN',      r'fun\b'),
        ('END',      r'end\b'),
        ('AND',      r'and\b'),               # Logical keywords
        ('OR',       r'or\b'),
        ('NOT',      r'not\b'),
        ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'), # Identifiers
        ('ARROW',    r'->'),                  # Operators and punctuation (Longer first!)
        ('EQ',       r'=='),
        ('NEQ',      r'!='),
        ('LE',       r'<='),
        ('GE',       r'>='),
        ('ASSIGN',   r'='),
        ('PLUS',     r'\+'),
        ('MINUS',    r'-'),
        ('MUL',      r'\*'),
        ('DIV',      r'/'),
        ('LT',       r'<'),
        ('GT',       r'>'),
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('COMMA',    r','),
        ('SEMI',     r';'),
        ('NEWLINE',  r'\n'),                  # Whitespace tracking
        ('SKIP',     r'[ \t\r]+'),
        ('MISMATCH', r'.'),                   # Error handling
    ]

    def __init__(self, source):
        self.source = source
        self.regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in self.TOKEN_SPEC))

    def tokenize(self):
        """Generates a list of tokens from the source string."""
        tokens = []
        line_num = 1
        line_start = 0
        pos = 0
        while pos < len(self.source):
            mo = self.regex.match(self.source, pos)
            if not mo: break # Should not happen due to MISMATCH
            
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start + 1
            
            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                pos = mo.end()
            elif kind == 'SKIP':
                pos = mo.end()
                continue
            elif kind == 'COMMENT_START':
                # Manual nested comment handling
                depth = 1
                pos = mo.end()
                while depth > 0 and pos < len(self.source):
                    if self.source.startswith('(*', pos):
                        depth += 1
                        pos += 2
                    elif self.source.startswith('*)', pos):
                        depth -= 1
                        pos += 2
                    else:
                        if self.source[pos] == '\n':
                            line_num += 1
                            line_start = pos + 1
                        pos += 1
                if depth > 0:
                    print(f"Lexical error: Unclosed comment at line {line_num}", file=sys.stderr)
                    sys.exit(1)
                # After comment, continue the loop from new 'pos'
            elif kind == 'MISMATCH':
                # Report illegal characters immediately to stop lexical analysis
                print(f"Lexical error: Unexpected character '{value}' at {line_num}:{column}", file=sys.stderr)
                sys.exit(1)
            else:
                # Update line and column before creating the token
                val_text = mo.group(0)
                if kind == 'NUMBER': value = int(value)
                elif kind == 'BOOL': value = (value == 'true')
                elif kind == 'STRING': value = self.unescape_string(value[1:-1])
                tokens.append(Token(kind, value, line_num, column))
                
                # Count newlines in the matched text to keep line_num synchronized
                newlines_in_val = val_text.count('\n')
                if newlines_in_val > 0:
                    line_num += newlines_in_val
                    line_start = pos + val_text.rfind('\n') + 1
                
                pos = mo.end()
        return tokens

    def unescape_string(self, s):
        """Resolves escape sequences in string literals using a single-pass regex."""
        escapes = {'n': '\n', 't': '\t', '\\': '\\', '"': '"'}
        return re.sub(r'\\(.)', lambda m: escapes.get(m.group(1), m.group(0)), s)

# --- AST Node Definitions ---

class ASTNode:
    def __init__(self, line=0, col=0):
        self.line = line
        self.col = col

class Literal(ASTNode):
    def __init__(self, value, line=0, col=0):
        super().__init__(line, col)
        self.value = value

class Var(ASTNode):
    def __init__(self, name, line=0, col=0):
        super().__init__(line, col)
        self.name = name

class BinOp(ASTNode):
    def __init__(self, op, left, right, line=0, col=0):
        super().__init__(line, col)
        self.op = op
        self.left = left
        self.right = right

class UnaryOp(ASTNode):
    def __init__(self, op, expr, line=0, col=0):
        super().__init__(line, col)
        self.op = op
        self.expr = expr

class IfExpr(ASTNode):
    def __init__(self, cond, then_branch, else_branch, line=0, col=0):
        super().__init__(line, col)
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch

class FunExpr(ASTNode):
    def __init__(self, params, body, line=0, col=0):
        super().__init__(line, col)
        self.params = params
        self.body = body

class CallExpr(ASTNode):
    def __init__(self, func, args, line=0, col=0):
        super().__init__(line, col)
        self.func = func
        self.args = args

class LetStmt(ASTNode):
    def __init__(self, name, expr, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.expr = expr

class AssignStmt(ASTNode):
    def __init__(self, name, expr, line=0, col=0):
        super().__init__(line, col)
        self.name = name
        self.expr = expr

class PrintStmt(ASTNode):
    def __init__(self, expr, line=0, col=0):
        super().__init__(line, col)
        self.expr = expr

class WhileStmt(ASTNode):
    def __init__(self, cond, body, line=0, col=0):
        super().__init__(line, col)
        self.cond = cond
        self.body = body

class ListExpr(ASTNode):
    def __init__(self, elements, line=0, col=0):
        super().__init__(line, col)
        self.elements = elements

class IndexExpr(ASTNode):
    def __init__(self, list_expr, index_expr, line=0, col=0):
        super().__init__(line, col)
        self.list_expr = list_expr
        self.index_expr = index_expr

class Block(ASTNode):
    def __init__(self, statements, last_expr=None, line=0, col=0):
        super().__init__(line, col)
        self.statements = statements
        self.last_expr = last_expr

class Parser:
    """Recursive descent parser to convert tokens into an Abstract Syntax Tree (AST)."""
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        if self.pos + offset >= len(self.tokens): return None
        return self.tokens[self.pos + offset]

    def consume(self, expected_type=None):
        token = self.peek()
        if not token:
            print("Syntax error: Unexpected end of input", file=sys.stderr)
            sys.exit(1)
        if expected_type and token.type != expected_type:
            print(f"Syntax error at {token.line}:{token.column}: Expected {expected_type}, got {token.type} ({token.value})", file=sys.stderr)
            sys.exit(1)
        self.pos += 1
        return token

    def match(self, *types):
        token = self.peek()
        if token and token.type in types:
            return self.consume()
        return None

    def parse_program(self):
        ast = self.parse_block()
        if self.peek():
            token = self.peek()
            print(f"Parser error: Unexpected tokens at end of file at {token.line}:{token.column}", file=sys.stderr)
            sys.exit(1)
        return ast

    def parse_block(self):
        """Parses a sequence of statements and an optional final expression."""
        stmts = []
        last_expr = None
        while self.peek() and self.peek().type not in ('END', 'ELSE'):
            # If the next construct is a statement ending with ';', it's a stmt
            # If it's the last thing in the block and has no ';', it's an expr
            expr = self.parse_expr()
            if self.match('SEMI'):
                if isinstance(expr, (LetStmt, PrintStmt, WhileStmt, AssignStmt)):
                    stmts.append(expr)
                else:
                    # Expr as stmt
                    stmts.append(expr)
            else:
                last_expr = expr
                break
        return Block(stmts, last_expr)

    # --- Expression Precedence Levels (Low to High) ---

    def parse_expr(self):
        return self.parse_assignment()

    def parse_assignment(self):
        """Lowest precedence: variable assignment."""
        if self.peek() and self.peek().type == 'ID' and self.peek(1) and self.peek(1).type == 'ASSIGN':
            tok = self.consume('ID')
            name = tok.value
            self.consume('ASSIGN')
            expr = self.parse_assignment() # Right-associative
            return AssignStmt(name, expr, tok.line, tok.column)
        
        # Check for standalone let/print/while which are statements
        let_tok = self.match('LET')
        if let_tok:
            name_tok = self.consume('ID')
            name = name_tok.value
            self.consume('ASSIGN')
            expr = self.parse_expr()
            return LetStmt(name, expr, let_tok.line, let_tok.column)
        
        print_tok = self.match('PRINT')
        if print_tok:
            self.consume('LPAREN')
            expr = self.parse_expr()
            self.consume('RPAREN')
            return PrintStmt(expr, print_tok.line, print_tok.column)
        
        while_tok = self.match('WHILE')
        if while_tok:
            cond = self.parse_expr()
            self.consume('DO')
            body = self.parse_block()
            self.consume('END')
            return WhileStmt(cond, body, while_tok.line, while_tok.column)

        return self.parse_logic_or()

    def parse_logic_or(self):
        left = self.parse_logic_and()
        while True:
            tok = self.match('OR')
            if not tok: break
            right = self.parse_logic_and()
            left = BinOp('or', left, right, tok.line, tok.column)
        return left

    def parse_logic_and(self):
        left = self.parse_comparison()
        while True:
            tok = self.match('AND')
            if not tok: break
            right = self.parse_comparison()
            left = BinOp('and', left, right, tok.line, tok.column)
        return left

    def parse_comparison(self):
        left = self.parse_arithmetic()
        op_tok = self.match('EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE')
        if op_tok:
            right = self.parse_arithmetic()
            return BinOp(op_tok.value, left, right, op_tok.line, op_tok.column)
        return left

    def parse_arithmetic(self):
        left = self.parse_term()
        while True:
            op_tok = self.match('PLUS', 'MINUS')
            if not op_tok: break
            right = self.parse_term()
            left = BinOp(op_tok.value, left, right, op_tok.line, op_tok.column)
        return left

    def parse_term(self):
        left = self.parse_unary()
        while True:
            op_tok = self.match('MUL', 'DIV')
            if not op_tok: break
            right = self.parse_unary()
            left = BinOp(op_tok.value, left, right, op_tok.line, op_tok.column)
        return left

    def parse_unary(self):
        op_tok = self.match('NOT', 'MINUS')
        if op_tok:
            expr = self.parse_unary()
            return UnaryOp(op_tok.value, expr, op_tok.line, op_tok.column)
        return self.parse_call_index()

    def parse_call_index(self):
        """Handles function calls and list indexing (high precedence)."""
        expr = self.parse_primary()
        while True:
            call_tok = self.match('LPAREN')
            if call_tok:
                args = []
                if not self.peek() or self.peek().type != 'RPAREN':
                    args.append(self.parse_expr())
                    while self.match('COMMA'):
                        if self.peek() and self.peek().type == 'RPAREN': break # Trailing comma
                        args.append(self.parse_expr())
                self.consume('RPAREN')
                expr = CallExpr(expr, args, call_tok.line, call_tok.column)
            else:
                idx_tok = self.match('LBRACKET')
                if idx_tok:
                    index = self.parse_expr()
                    self.consume('RBRACKET')
                    expr = IndexExpr(expr, index, idx_tok.line, idx_tok.column)
                else:
                    break
        return expr

    def parse_primary(self):
        """Highest precedence: Literals, IDs, and grouped expressions."""
        if self.match('LPAREN'):
            expr = self.parse_expr()
            self.consume('RPAREN')
            return expr
        
        tok = self.match('NUMBER', 'BOOL', 'STRING')
        if tok: return Literal(tok.value, tok.line, tok.column)
        
        lb_tok = self.match('LBRACKET')
        if lb_tok:
            elements = []
            if self.peek() and self.peek().type != 'RBRACKET':
                elements.append(self.parse_expr())
                while self.match('COMMA'):
                    if self.peek() and self.peek().type == 'RBRACKET': break # Trailing comma
                    elements.append(self.parse_expr())
            self.consume('RBRACKET')
            return ListExpr(elements, lb_tok.line, lb_tok.column)

        if_tok = self.match('IF')
        if if_tok:
            cond = self.parse_expr()
            self.consume('THEN')
            then_branch = self.parse_block()
            self.consume('ELSE')
            else_branch = self.parse_block()
            self.consume('END')
            return IfExpr(cond, then_branch, else_branch, if_tok.line, if_tok.column)

        fun_tok = self.match('FUN')
        if fun_tok:
            self.consume('LPAREN')
            params = []
            if self.peek() and self.peek().type == 'ID':
                params.append(self.consume('ID').value)
                while self.match('COMMA'):
                    if self.peek() and self.peek().type == 'RPAREN': break # Trailing comma
                    params.append(self.consume('ID').value)
            self.consume('RPAREN')
            self.consume('ARROW')
            body = self.parse_block()
            self.consume('END')
            return FunExpr(params, body, fun_tok.line, fun_tok.column)
        
        tok = self.consume('ID')
        return Var(tok.value, tok.line, tok.column)

# --- Runtime Classes ---

class Closure:
    """Represents a function along with its defining environment (lexical scope)."""
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env # Capture definition-time environment

class Environment:
    """Manages variable bindings in a linked-frame structure (Activation Records)."""
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent

    def extend(self, name, value):
        """Adds a new binding to the current frame."""
        self.bindings[name] = value

    def lookup(self, name, node=None):
        """Recursively looks up a variable name in the current and parent frames."""
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name, node)
        loc = f" at {node.line}:{node.col}" if node else ""
        print(f"Runtime error{loc}: Unbound variable '{name}'", file=sys.stderr)
        sys.exit(1)

    def update(self, name, value, node=None):
        """Updates an existing binding in the nearest frame where it's defined."""
        if name in self.bindings:
            self.bindings[name] = value
        elif self.parent:
            self.parent.update(name, value, node)
        else:
            loc = f" at {node.line}:{node.col}" if node else ""
            print(f"Runtime error{loc}: Cannot assign to unbound variable '{name}'", file=sys.stderr)
            sys.exit(1)

class Evaluator:
    """Walks the AST and executes the program logic."""
    def __init__(self, scope_mode='static'):
        self.scope_mode = scope_mode

    def eval(self, node, env):
        """Recursively evaluates an AST node within a given environment."""
        if isinstance(node, Literal):
            return node.value
        elif isinstance(node, Var):
            return env.lookup(node.name, node)
        elif isinstance(node, UnaryOp):
            val = self.eval(node.expr, env)
            if node.op == 'not':
                if not isinstance(val, bool): self.error("Type error: 'not' expects a boolean", node)
                return not val
            if node.op == '-':
                if type(val) is not int: self.error("Type error: unary '-' expects an integer", node)
                return -val
        elif isinstance(node, BinOp):
            # Short-circuiting for logical operators
            left = self.eval(node.left, env)
            if node.op == 'and':
                if not isinstance(left, bool): self.error("Type error: 'and' expects booleans", node)
                if not left: return False
                right = self.eval(node.right, env)
                if not isinstance(right, bool): self.error("Type error: 'and' expects booleans", node)
                return right
            if node.op == 'or':
                if not isinstance(left, bool): self.error("Type error: 'or' expects booleans", node)
                if left: return True
                right = self.eval(node.right, env)
                if not isinstance(right, bool): self.error("Type error: 'or' expects booleans", node)
                return right
            
            # Non-short-circuiting operators
            right = self.eval(node.right, env)
            if node.op == '+':
                if type(left) is int and type(right) is int: return left + right
                if isinstance(left, str) and isinstance(right, str): return left + right
                self.error(f"Type error: '+' expects two integers or two strings, got {type(left).__name__} and {type(right).__name__}", node)
            elif node.op == '-':
                if not (type(left) is int and type(right) is int): 
                    self.error(f"Type error: '-' expects integers, got {type(left).__name__} and {type(right).__name__}", node)
                return left - right
            elif node.op == '*':
                if not (type(left) is int and type(right) is int): 
                    self.error(f"Type error: '*' expects integers, got {type(left).__name__} and {type(right).__name__}", node)
                return left * right
            elif node.op == '/':
                if not (type(left) is int and type(right) is int): 
                    self.error(f"Type error: '/' expects integers, got {type(left).__name__} and {type(right).__name__}", node)
                if right == 0: self.error("Runtime error: division by zero", node)
                # Perform integer division with truncation towards zero (C-style)
                if (left < 0) ^ (right < 0): # Different signs
                    return -(-left // right)
                else:
                    return left // right
            elif node.op == '==': return left == right
            elif node.op == '!=': return left != right
            elif node.op == '<':
                if not (type(left) in (int, str)) or type(left) is not type(right):
                    self.error(f"Type error: '<' expects matching integers or strings, got {type(left).__name__} and {type(right).__name__}", node)
                return left < right
            elif node.op == '>':
                if not (type(left) in (int, str)) or type(left) is not type(right):
                    self.error(f"Type error: '>' expects matching integers or strings, got {type(left).__name__} and {type(right).__name__}", node)
                return left > right
            elif node.op == '<=':
                if not (type(left) in (int, str)) or type(left) is not type(right):
                    self.error(f"Type error: '<=' expects matching integers or strings, got {type(left).__name__} and {type(right).__name__}", node)
                return left <= right
            elif node.op == '>=':
                if not (type(left) in (int, str)) or type(left) is not type(right):
                    self.error(f"Type error: '>=' expects matching integers or strings, got {type(left).__name__} and {type(right).__name__}", node)
                return left >= right
        elif isinstance(node, IfExpr):
            cond = self.eval(node.cond, env)
            if not isinstance(cond, bool): self.error("Type error: 'if' condition must be a boolean", node)
            return self.eval(node.then_branch if cond else node.else_branch, env)
        elif isinstance(node, FunExpr):
            return Closure(node.params, node.body, env)
        elif isinstance(node, CallExpr):
            func = self.eval(node.func, env)
            # Handle built-in methods
            if func == '__built_in_length__':
                if len(node.args) != 1: self.error("length() expects 1 argument", node)
                val = self.eval(node.args[0], env)
                if not (isinstance(val, (str, list))): self.error("length() expects a string or list", node)
                return len(val)
            if func == '__built_in_append__':
                if len(node.args) != 2: self.error("append() expects 2 arguments", node)
                lst = self.eval(node.args[0], env)
                val = self.eval(node.args[1], env)
                if not isinstance(lst, list): self.error("append() expects a list as first argument", node)
                lst.append(val)
                return lst

            if not isinstance(func, Closure):
                self.error(f"Runtime error: Expression is not a function", node)
            if len(node.args) != len(func.params):
                self.error(f"Runtime error: Expected {len(func.params)} arguments, got {len(node.args)}", node)
            
            args_vals = [self.eval(arg, env) for arg in node.args]
            
            # Create a new environment frame for the function call
            if self.scope_mode == 'static':
                new_env = Environment(func.env) # Lexical Scoping: use definition-time parent
            else:
                new_env = Environment(env)      # Dynamic Scoping: use call-time parent
            
            for param, val in zip(func.params, args_vals):
                new_env.extend(param, val)
            return self.eval(func.body, new_env)
        elif isinstance(node, LetStmt):
            if isinstance(node.expr, FunExpr):
                # Support for recursion: allow function to see itself by pre-extending env
                env.extend(node.name, None)
                val = self.eval(node.expr, env)
                env.update(node.name, val, node)
            else:
                val = self.eval(node.expr, env)
                env.extend(node.name, val)
            return None
        elif isinstance(node, AssignStmt):
            val = self.eval(node.expr, env)
            env.update(node.name, val, node)
            return val
        elif isinstance(node, PrintStmt):
            val = self.eval(node.expr, env)
            print(self.format_val(val))
            return None
        elif isinstance(node, WhileStmt):
            while True:
                cond = self.eval(node.cond, env)
                if not isinstance(cond, bool): self.error("Type error: 'while' condition must be a boolean", node)
                if not cond: break
                self.eval(node.body, env)
            return None
        elif isinstance(node, ListExpr):
            return [self.eval(e, env) for e in node.elements]
        elif isinstance(node, IndexExpr):
            lst = self.eval(node.list_expr, env)
            idx = self.eval(node.index_expr, env)
            if not isinstance(lst, list): self.error("Indexing expects a list", node)
            if type(idx) is not int: self.error("List index must be an integer", node)
            if idx < 0 or idx >= len(lst): self.error("Runtime error: Index out of range", node)
            return lst[idx]
        elif isinstance(node, Block):
            res = None
            for stmt in node.statements:
                res = self.eval(stmt, env)
            if node.last_expr:
                res = self.eval(node.last_expr, env)
            return res

    def error(self, msg, node=None):
        """Unified error reporting to stderr with non-zero exit and location info."""
        loc = f" at {node.line}:{node.col}" if node else ""
        print(f"{msg}{loc}", file=sys.stderr)
        sys.exit(1)

    def format_val(self, val, visited=None):
        """Formats internal Python values back into the mini-language representation with circular detection."""
        if visited is None: visited = set()
        
        if isinstance(val, bool): return 'true' if val else 'false'
        if isinstance(val, list):
            if id(val) in visited: return '[...]'
            visited.add(id(val))
            items = []
            for item in val:
                if isinstance(item, str): 
                    # Correctly escape quotes inside list strings
                    escaped = item.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
                    items.append(f'"{escaped}"')
                else: items.append(self.format_val(item, visited))
            visited.remove(id(val))
            return '[' + ', '.join(items) + ']'
        if isinstance(val, Closure): return '<function>'
        return str(val)

def main():
    """CLI entry point for the interpreter."""
    arg_parser = argparse.ArgumentParser(description="Mini Language Interpreter")
    arg_parser.add_argument('file', help="The source code file to execute")
    arg_parser.add_argument('--scope', choices=['static', 'dynamic'], default='static', help="Scoping mode (default: static)")
    args = arg_parser.parse_args()

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: file {args.file} not found", file=sys.stderr)
        sys.exit(1)

    # Execution Pipeline: Lex -> Parse -> Eval
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse_program()
    
    evaluator = Evaluator(scope_mode=args.scope)
    global_env = Environment() # The top-level activation record
    global_env.extend('length', '__built_in_length__')
    global_env.extend('append', '__built_in_append__')
    evaluator.eval(ast, global_env)

if __name__ == '__main__':
    main()
