import ast
import subprocess
import tempfile

class LoopAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0

    def visit_For(self, node, depth=1):
        if depth > self.max_depth:
            self.max_depth = depth
        # Check inside the loop body for nested loops
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                self.visit(child, depth=depth+1)
        self.generic_visit(node)

    def visit_While(self, node, depth=1):
        if depth > self.max_depth:
            self.max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                self.visit(child, depth=depth+1)
        self.generic_visit(node)

def analyze_code(code):
    results = []

    # AST check (syntax errors)
    try:
        tree = ast.parse(code)
        results.append("✅ No syntax errors found.")
    except SyntaxError as e:
        results.append(f"❌ Syntax Error: {e}")
        return results

    # Time Complexity Estimation using AST
    loop_analyzer = LoopAnalyzer()
    loop_analyzer.visit(tree)
    depth = loop_analyzer.max_depth

    if depth == 0:
        results.append("⚡ Estimated Time Complexity: O(1) - No loops detected.")
    elif depth == 1:
        results.append("⚡ Estimated Time Complexity: O(n) - Single loop detected.")
    else:
        results.append(f"⚡ Estimated Time Complexity: O(n^{depth}) - Nested loops detected (depth={depth}).")

    # Detect recursive functions
    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    recursive_found = False
    for func_name in function_names:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # For functions defined normally, id attribute is on node.func.id
                if isinstance(node.func, ast.Name) and node.func.id == func_name:
                    recursive_found = True
                    break
                # For method calls (e.g. self.func()), attribute attr is used
                if isinstance(node.func, ast.Attribute) and node.func.attr == func_name:
                    recursive_found = True
                    break
        if recursive_found:
            break

    if recursive_found:
        results.append("⚠️ Warning: Recursive function detected. Be careful of potential high complexity.")

    # Pylint analysis
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        file_name = f.name

    pylint_output = subprocess.getoutput(f"pylint {file_name} --disable=all --enable=E,W,C,R")

    results.append("🔍 Code Quality Report:")
    results.append(pylint_output)

    return results
