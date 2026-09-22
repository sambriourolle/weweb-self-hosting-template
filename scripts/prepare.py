#!/usr/bin/env python3
"""Fail-closed preparation of known-compatible WeWeb exports.

This script copies an export; it never edits the user's source directory.  Its
patches are intentionally narrow and signature checked because WeWeb exports
are not a stable self-hosting API.
"""
from __future__ import annotations
import argparse, json, re, shutil, sys
from pathlib import Path

SKIP_NAMES = {'.git', 'node_modules', '.DS_Store', 'dist', 'dist-ssr', '.cache'}
SKIP_ENV = re.compile(r'^\.env(?:\..*)?$')

class PreparationError(RuntimeError): pass

def copy_export(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise PreparationError(f"Export absent ou non lisible : {source}")
    if destination.exists(): shutil.rmtree(destination)
    def ignore(directory, names):
        return [name for name in names if name in SKIP_NAMES or SKIP_ENV.match(name)]
    shutil.copytree(source, destination, ignore=ignore)

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    data = path.read_text()
    count = data.count(old)
    if count != 1:
        raise PreparationError(f"Patch {label}: signature attendue une fois dans {path.relative_to(path.parents[2])}, trouvée {count} fois.")
    path.write_text(data.replace(old, new, 1))

def patch_backend(root: Path) -> list[str]:
    required = ['package.json', 'src/integrations/index.ts', 'src/integrations/aws-s3/aws-s3.drivers.ts',
                'src/integrations/weweb-auth/better-auth.js', 'src/routes/workflows/workflows.routes.js',
                'src/routes/workflows/workflows.controllers.js']
    missing = [x for x in required if not (root/x).is_file()]
    if missing: raise PreparationError('Export backend non compatible; fichiers absents : ' + ', '.join(missing))
    changes=[]
    p=root/'src/integrations/index.ts'
    replace_once(p, "import './weweb-storage/index.ts';", "import './weweb-storage/index.ts';\nimport './aws-s3/index.ts';", 'aws-s3-registration'); changes.append('aws-s3-registration')
    p=root/'src/integrations/aws-s3/aws-s3.drivers.ts'
    replace_once(p, "bucket: visibility === 'private' ? runtimeConfig?.privateBucket : runtimeConfig?.publicBucket,\n            visibility,", "bucket: visibility === 'private' ? runtimeConfig?.privateBucket : runtimeConfig?.publicBucket,\n            endpoint: process.env.AWS_S3_ENDPOINT || undefined,\n            forcePathStyle: Boolean(process.env.AWS_S3_ENDPOINT),\n            visibility,", 's3-endpoint'); changes.append('s3-endpoint')
    p=root/'src/integrations/weweb-auth/better-auth.js'
    replace_once(p, "sameSite: 'none',\n                  secure: true,", "sameSite: process.env.LOCAL_HTTP === 'true' ? 'lax' : 'none',\n                  secure: process.env.LOCAL_HTTP !== 'true',", 'local-http-cookies')
    replace_once(p, "useSecureCookies: true,", "useSecureCookies: process.env.LOCAL_HTTP !== 'true',", 'local-http-secure-cookie'); changes.append('local-http-cookies')
    p=root/'src/routes/workflows/workflows.controllers.js'
    replace_once(p, "const query = c.req.query();\n    const body", "const query = c.req.query();\n    const pathParams = c.req.param();\n    const body", 'path-parameters-context')
    replace_once(p, "parameters: isGetOrDelete ? query : body,", "parameters: { ...pathParams, ...(isGetOrDelete ? query : body) },", 'path-parameters-merge'); changes.append('path-parameters')
    p=root/'src/routes/workflows/workflows.routes.js'
    old="""for (const workflow of workflows.filter(workflow => workflow.trigger === 'ww-api')) {
        app.on(
            workflow.meta?.method || 'POST',
            workflow.meta?.path || `/ww/workflows/${workflow.id}`,"""
    new="""for (const workflow of workflows.filter(workflow => workflow.trigger === 'ww-api')) {
        const exportedPath = workflow.meta?.path || `/ww/workflows/${workflow.id}`;
        const localPath = exportedPath.replace(/^\\/api(?=\\/)/, '').replace(/\\{([^}]+)\\}/g, ':$1');
        app.on(
            workflow.meta?.method || 'POST',
            localPath,"""
    replace_once(p, old, new, 'api-route-normalization'); changes.append('api-route-normalization')
    return changes

def patch_frontend(root: Path) -> list[str]:
    for name in ('package.json','vite.config.js'):
        if not (root/name).is_file(): raise PreparationError(f'Export frontend non compatible; {name} absent.')
    packages=[]
    for package in (root/'src/extensions').glob('*/*/package.json'):
        meta=json.loads(package.read_text())
        name=meta.get('name','')
        if name.startswith('@weweb-internal/'):
            packages.append((name, './' + str(package.parent.relative_to(root)).replace('\\','/')))
    if not packages: raise PreparationError("Export frontend non compatible : aucun paquet @weweb-internal d'extension trouvé.")
    vite=root/'vite.config.js'; data=vite.read_text()
    marker="alias: {\n                '@': path.resolve(__dirname, './src'),"
    if marker not in data: raise PreparationError("Patch frontend-aliases : bloc d'alias Vite inconnu.")
    aliases=''.join(f"\n                {json.dumps(name)}: path.resolve(__dirname, {json.dumps(path)})," for name,path in sorted(packages))
    vite.write_text(data.replace(marker, marker+aliases, 1))
    # The tested standalone export references non-exported package subpaths
    # named /config. Rewrite only those imports to the ww-config.js shipped
    # beside each extension; aliases above still serve normal package imports.
    bases = root/'src/pinia/componentBases.js'
    changes = ['frontend-extension-aliases']
    if bases.is_file():
        source = bases.read_text()
        def config_path(match):
            package = '@weweb-internal/ext-' + match.group(1) + '-' + match.group(2)
            for name, path in packages:
                if name == package:
                    return "'../" + path.removeprefix('./src/') + "/ww-config.js'"
            raise PreparationError(f"Patch frontend-config-imports : extension absente pour {package}.")
        patched, count = re.subn(r"'@weweb-internal/ext-(element|section)-([0-9a-f-]+)/config'", config_path, source)
        if count:
            bases.write_text(patched); changes.append('frontend-config-imports')
    return changes

def main() -> int:
    parser=argparse.ArgumentParser(description='Prépare des copies build de deux exports WeWeb connus.')
    parser.add_argument('--frontend', type=Path, required=True); parser.add_argument('--backend', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    try:
        front=args.output/'frontend'; back=args.output/'backend'
        copy_export(args.frontend, front); copy_export(args.backend, back)
        manifest={'frontend': patch_frontend(front), 'backend': patch_backend(back)}
        (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
        print(json.dumps(manifest, sort_keys=True))
        return 0
    except PreparationError as exc:
        print(f'ERREUR DE COMPATIBILITÉ: {exc}', file=sys.stderr); return 2
if __name__ == '__main__': raise SystemExit(main())
