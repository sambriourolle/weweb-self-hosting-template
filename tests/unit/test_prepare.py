import json, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
PREP=ROOT/'scripts/prepare.py'

def export(root, backend=True):
    if backend:
        files={
'package.json':'{}','src/integrations/index.ts':"import './weweb-storage/index.ts';",'src/integrations/aws-s3/aws-s3.drivers.ts':"bucket: visibility === 'private' ? runtimeConfig?.privateBucket : runtimeConfig?.publicBucket,\n            visibility,",'src/integrations/weweb-auth/better-auth.js':"sameSite: 'none',\n                  secure: true,\nuseSecureCookies: true,",'src/routes/workflows/workflows.controllers.js':"const query = c.req.query();\n    const body\nparameters: isGetOrDelete ? query : body,",'src/routes/workflows/workflows.routes.js':"""for (const workflow of workflows.filter(workflow => workflow.trigger === 'ww-api')) {
        app.on(
            workflow.meta?.method || 'POST',
            workflow.meta?.path || `/ww/workflows/${workflow.id}`,"""}
    else:
        files={'package.json':'{}','vite.config.js':"alias: {\n                '@': path.resolve(__dirname, './src'),",'src/extensions/integrations/demo/package.json':json.dumps({'name':'@weweb-internal/demo'})}
    for relative, body in files.items():
        p=root/relative; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(body)

class PrepareTests(unittest.TestCase):
    def run_prepare(self, front, back, out):
        return subprocess.run(['python3',str(PREP),'--frontend',str(front),'--backend',str(back),'--output',str(out)],text=True,capture_output=True)
    def test_prepares_copies_and_excludes_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); front=base/'front'; back=base/'back'; export(front,False); export(back); (front/'.env').write_text('secret')
            result=self.run_prepare(front,back,base/'out')
            self.assertEqual(result.returncode,0,result.stderr); self.assertFalse((base/'out/frontend/.env').exists())
            manifest=json.loads((base/'out/manifest.json').read_text()); self.assertIn('s3-endpoint',manifest['backend']); self.assertIn('frontend-extension-aliases',manifest['frontend'])
    def test_unknown_shape_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); front=base/'front'; back=base/'back'; export(front,False); export(back); (back/'src/integrations/index.ts').write_text('unknown')
            result=self.run_prepare(front,back,base/'out')
            self.assertEqual(result.returncode,2); self.assertIn('ERREUR DE COMPATIBILITÉ',result.stderr)
if __name__ == '__main__': unittest.main()
