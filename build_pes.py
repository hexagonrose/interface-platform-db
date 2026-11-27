"""Validate rigid builder-slab scans and emit a versioned PES file per interface."""
import hashlib
import json
import math


def check(ok, message):
    if not ok:
        raise ValueError(message)


def assemble(root, out, records):
    html = (root/'pes.html').read_text()
    source = next(line for line in html.splitlines() if line.startswith('const datasets='))
    geometry = json.loads(source[len('const datasets='):-1])
    groups = {}
    for path in sorted((root/'02_interface_pes').glob('*.json')):
        try:
            s = json.loads(path.read_text())
            key = s['id']
            r, view = records[key], geometry[key]
            prov, cond = r['provenance'], r['conditions']
            check(cond.get('builder') and s['source_sha256'] == prov['structure_sha256']
                  and s['checkpoint_sha256'] == prov['checkpoint_sha256'], 'structure or checkpoint mismatch')
            check(s['model']=='SevenNet-Omni(MPA)' and s.get('twist_deg',0)==s.get('tilt_deg',0)==0
                  and s.get('method','rigid')=='rigid', 'unsupported scan protocol')
            area, dz, gap = s['area_A2'], s['dz_A'], s['gap_A']
            check(abs(area-cond['area_A2'])<1e-5 and gap>0 and abs(gap-dz-cond['relaxed_interlayer_spacing_A'])<1e-4, 'incorrect cell area or gap')
            axis, energies, gamma = s['axes'], s['energies_eV'], s['gamma_J_m2']
            n = len(axis)-1
            check(n>=2 and all(abs(x-i/n)<1e-9 for i,x in enumerate(axis)), 'expected a uniform periodic grid')
            check(all(len(g)==n+1 and all(len(row)==n+1 for row in g) for g in (gamma,energies)), 'grid size mismatch')
            e0 = cond['interface_energy_eV']
            g0 = sum(view['surface_refs'])-r['value']
            check(abs(s['origin_control_eV']-e0)<.02, 'relaxed origin energy mismatch')
            if dz == 0:
                check(abs(energies[0][0]-e0)<.02, 'baseline grid origin mismatch')
            for j,row in enumerate(gamma):
                for i,value in enumerate(row):
                    expected = g0 + (energies[j][i]-e0)*16.02176634/area
                    check(math.isfinite(expected) and abs(expected-value)<1e-5, 'absolute energy reference mismatch')
                check(abs(row[0]-row[-1])<.001 and all(abs(a-b)<.001 for a,b in zip(gamma[0],gamma[-1])), 'periodic edge mismatch')
            layers = groups.setdefault(key, [])
            check(all(round(x['gap'],3)!=round(gap,3) for x in layers), 'duplicate gap for the same structure and model')
            j,i = min(((j,i) for j in range(n) for i in range(n)),key=lambda ji:gamma[ji[0]][ji[1]])
            layers.append(dict(gap=gap,dz=dz,gamma=gamma,minimum=[i,j]))
        except (ValueError, TypeError, KeyError, IndexError) as err:
            raise ValueError(f'{path.name}: {err}') from err

    folder = out/'02_interface_pes'
    folder.mkdir(exist_ok=True)
    manifest = {}
    for key, layers in groups.items():
        if not any(x['dz']==0 for x in layers):
            # The legacy grid is centred on its sampled minimum. Restore the raw registry.
            v = geometry[key]
            grid = v['gamma']
            n = len(grid)-1
            a,b = v['minimum_registry']
            raw = [[v['gamma_min']+grid[(j-b+n//2)%n][(i-a+n//2)%n] for i in range(n+1)] for j in range(n+1)]
            layers.append(dict(gap=records[key]['conditions']['relaxed_interlayer_spacing_A'],dz=0,gamma=raw,minimum=[a,b]))
        layers.sort(key=lambda x:x['gap'])
        raw = json.dumps(layers,separators=(',',':'),allow_nan=False).encode()
        name = f'{key}.{hashlib.sha256(raw).hexdigest()[:16]}.json'
        (folder/name).write_bytes(raw)
        manifest[key]='02_interface_pes/'+name
    return manifest, groups
