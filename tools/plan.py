"""Build the GitHub Actions matrix: one job per group of scenes. Usage: plan.py "<videos|all>" <scenes_per_job>"""
import ast, json, os, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def count(name):
    for f in (f'videos/{name}.py', 'lib/render2.py'):
        tree = ast.parse(open(os.path.join(root, f)).read())
        for n in tree.body:
            if isinstance(n, ast.Assign) and any(getattr(t, 'id', '') == 'SCENES' for t in n.targets) and isinstance(n.value, ast.List):
                return len(n.value.elts)
    raise SystemExit(f'SCENES not found for {name}')
arg = sys.argv[1].strip() if len(sys.argv) > 1 else 'all'
per = int(sys.argv[2]) if len(sys.argv) > 2 else 2
names = sorted(f[:-3] for f in os.listdir(os.path.join(root, 'videos')) if f.endswith('.py')) if arg in ('', 'all') else arg.split()
inc = []
for v in names:
    n = count(v)
    for s in range(0, n, per):
        inc.append({'video': v, 'scenes': ' '.join(map(str, range(s, min(n, s + per)))), 'part': f'{v}-{s:02d}'})
print('matrix=' + json.dumps({'include': inc}))
print('videos=' + ' '.join(names))
