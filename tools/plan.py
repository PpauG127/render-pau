"""Build the GitHub Actions matrix: one job per group of scenes. Usage: plan.py "<videos|all>" <scenes_per_job>"""
import ast, json, os, sys
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def count(name):
    try:
        import runpy
        ns = runpy.run_path(os.path.join(root, f'videos/{name}.py'), run_name='plan')
        if 'SCENES' in ns:
            return len(ns['SCENES']), ns.get('PER_JOB')
    except Exception:
        pass
    for f in (f'videos/{name}.py', 'lib/render2.py'):
        tree = ast.parse(open(os.path.join(root, f)).read())
        for n in tree.body:
            if isinstance(n, ast.Assign) and any(getattr(t, 'id', '') == 'SCENES' for t in n.targets) and isinstance(n.value, ast.List):
                return len(n.value.elts), None
    raise SystemExit(f'SCENES not found for {name}')
arg = sys.argv[1].strip() if len(sys.argv) > 1 else 'all'
per = int(sys.argv[2]) if len(sys.argv) > 2 else 2
names = sorted(f[:-3] for f in os.listdir(os.path.join(root, 'videos')) if f.endswith('.py')) if arg in ('', 'all') else arg.split()
inc = []
for v in names:
    n, pj = count(v)
    step = pj or per
    for s in range(0, n, step):
        inc.append({'video': v, 'scenes': ' '.join(map(str, range(s, min(n, s + step)))), 'part': f'{v}-{s:03d}'})
print('matrix=' + json.dumps({'include': inc}))
print('videos=' + ' '.join(names))
