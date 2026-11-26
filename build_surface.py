"""Assemble the public Pages artifact from validated elemental surface files."""
import hashlib
import json
import math
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(path, data):
    record = data['record']
    key = record['id']
    symbol, = record['materials']
    phase = data['material_id']
    require(re.fullmatch(r'[A-Z][a-z]?', symbol) and re.fullmatch(r'mp-\d+', phase)
            and path.stem == f'{symbol}_{phase}', 'invalid element or phase filename')
    require(re.fullmatch(r'[a-z0-9-]+', key) and record['kind'] == 'surface'
            and record.get('material_id', phase) == phase, 'invalid surface identity')
    for field in ('title','property','property_label','quality','quality_label','comparison_group','unit'):
        require(isinstance(record[field], str) and record[field], field)
    require(isinstance(record['conditions'], dict) and record['provenance']['model']
            and isinstance(record['provenance']['modal'], str), 'missing calculation provenance')
    facets = set()
    for row in record['surfaces']:
        facet = row['facet']
        require(isinstance(facet, str) and facet not in facets and math.isfinite(row['gamma_J_m2'])
                and row['gamma_J_m2'] >= 0, 'invalid facet or surface energy')
        facets.add(facet)
        geom = row['geometry']
        require(len(geom['symbols']) == len(geom['positions']) == row['atoms'] > 0
                and set(geom['symbols']) == {symbol} and len(geom['cell']) == 3
                and all(len(v) == 3 and all(map(math.isfinite, v)) for v in geom['cell'] + geom['positions'])
                and re.fullmatch(r'[a-f0-9]{64}', row['structure_sha256']), 'invalid slab geometry or provenance')
    require(facets, 'missing facet results')
    for mesh in [record['shape'], *record.get('wulff_comparison', {}).values()]:
        require(mesh['vertices'] and mesh['faces'] and mesh['area_fractions'], 'empty Wulff mesh')
        for face in mesh['faces']:
            require(len(face['indices']) >= 3 and all(isinstance(i,int) and 0 <= i < len(mesh['vertices'])
                    for i in face['indices']), 'invalid Wulff face')


def build(out):
    out.mkdir(parents=True, exist_ok=True)
    phases = out / '01_surface'
    phases.mkdir(exist_ok=True)
    db = json.loads((ROOT / 'catalog.json').read_text())
    records = {r['id']: r for r in db['records']}
    # Preserve catalog order while letting the phase uploads own their model data.
    for key, r in records.items():
        if r['kind'] == 'surface' and re.fullmatch(r'[A-Z][a-z]?', r['materials'][0]):
            records[key] = {'id':key}
            db['model_comparison']['surfaces'].pop(key, None)
    stubs = {}
    phase_ids = set()
    for path in sorted((ROOT / '01_surface').glob('*.json')):
        try:
            data = json.loads(path.read_text())
            validate(path, data)
            raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
            require(not any(x in raw for x in (b'"/home/',b'"/data3/',b'checkpoint_path',b'slurm_job_id')), 'private metadata')
            r = data['record']
            key, phase = r['id'], data['material_id']
            require(key not in stubs and phase not in phase_ids and not records.get(key, {}).get('kind'), 'duplicate record or phase')
            phase_ids.add(phase)
            name = f'{path.stem}.{hashlib.sha256(raw).hexdigest()[:16]}.json'
            (phases / name).write_bytes(raw)
            records[key] = r
            stub = {k:r[k] for k in ('id','kind','materials','title','quality','quality_label','property','property_label','comparison_group','unit','value')}
            stub['surfaces'] = [{k:f[k] for k in ('facet','gamma_J_m2')} for f in r['surfaces']]
            if 'paired_face' in r:
                stub['paired_face'] = r['paired_face']
            stubs[key] = dict(stub, material_id=phase, surface_file='01_surface/' + name)
            if 'nano' in data:
                db['model_comparison']['surfaces'][key] = data['nano']
            db['surface_model_failures'].pop(phase, None)
            if 'failures' in data:
                db['surface_model_failures'][phase] = data['failures']
        except (TypeError, KeyError, ValueError) as err:
            raise ValueError(f'{path.name}: {err}') from err
    require(all('kind' in r for r in records.values()), 'missing phase file for a registered record')
    db['records'] = list(records.values())
    write_json(out / 'catalog.json', db)
    db['records'] = [stubs.get(r['id'], r) for r in db['records']]
    payload = json.dumps(db, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    (out / 'site-data.js').write_text('const SITE_DB=' + payload + ';\n')

    for path in ROOT.glob('*.html'):
        if path.name == 'index.html':
            html = path.read_text()
            if 'const DB=SITE_DB;' not in html:
                html, changes = re.subn(r'^const DB=\{.*\};$', 'const DB=SITE_DB;', html, flags=re.M)
                require(changes == 1, 'missing catalog binding in index.html')
                html = html.replace('</main><script>', '</main><script src="site-data.js"></script><script>')
            require('src="site-data.js"' in html and 'fetch(record.surface_file)' in html, 'missing phase loader')
            (out / path.name).write_text(html)
        else:
            shutil.copyfile(path, out / path.name)
    shutil.copyfile(ROOT / '.nojekyll', out / '.nojekyll')


if __name__ == '__main__':
    build(Path(sys.argv[1]))
