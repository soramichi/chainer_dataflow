#!/usr/bin/env python

import sys
import ast
import functools

source = ""
assignments_forward = {}
assignments_backward = {}

class FunctionVisitor(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        if node.name == "forward_gpu":
            trace_assignments(node, assignments_forward)
        if node.name == "backward_gpu":
            trace_assignments(node, assignments_backward)

def get_names(assign, ans):
    if isinstance(assign, ast.Name):
        ans += [assign.id]
    elif isinstance(assign, ast.Tuple):
        for e in assign.elts:
            get_names(e, ans)
    #else:
    #    print(ast.dump(assign))

def trace_assignments(node, assignments):
    if isinstance(node, ast.Assign):
        targets = node.targets[0]
        names = []
        get_names(targets, names)

        for n in names:
            if n not in assignments:
                assignments[n] = []
            assignments[n] += [[node.lineno, ast.dump(node.value)]]

    for child in ast.iter_child_nodes(node):
        trace_assignments(child, assignments)

def main():
    if len(sys.argv) < 2:
        print("{0} filename".format(argv[0]))
        sys.exit()

    filename = sys.argv[1]
    
    with open(filename, 'r') as f:
        source = f.read()
        
    tree = ast.parse(source, filename)
    FunctionVisitor().visit(tree)

    if len(assignments_forward) == 0:
        print("forward seems to have no assignments.")
    if len(assignments_backward) == 0:
        print("backward seems to have no assignments.")

    for k in assignments_forward:
        if k in assignments_backward:
            body_forward = functools.reduce(lambda a,b: a + [b[1]], assignments_forward[k], [])
            body_backward = functools.reduce(lambda a,b: a + [b[1]], assignments_backward[k], [])
            if body_forward != body_backward:
                print("different data flow! (", k, ")")
                print("forward: ")
                for a in assignments_forward[k]:
                    print(source.split('\n')[a[0]-1].strip())
                print("backward: ")
                for a in assignments_backward[k]:
                    print(source.split('\n')[a[0]-1].strip())
                print("--------------------------------------------------")

if __name__ == '__main__':
    main()
