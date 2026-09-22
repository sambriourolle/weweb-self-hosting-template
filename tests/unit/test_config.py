import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
class ConfigurationTests(unittest.TestCase):
 def test_compose_defaults_to_loopback_and_persistent_volumes(self):
  text=(ROOT/'compose.yaml').read_text()
  self.assertIn('${BIND_ADDRESS:-127.0.0.1}:${HTTP_PORT:-8080}:8080', text)
  self.assertIn('postgres-data:', text); self.assertIn('minio-data:', text)
 def test_example_has_no_real_default_secret(self):
  text=(ROOT/'.env.example').read_text()
  self.assertIn('CHANGE_ME',text); self.assertNotIn('samnotes',text.lower())
if __name__=='__main__': unittest.main()
