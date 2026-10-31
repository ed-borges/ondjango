"""Static config tests: they do not launch Docker or assess sandbox security."""
import importlib.util
import io
import os
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'infra/judge0/manage_config.py'
spec = importlib.util.spec_from_file_location('judge0_manage_config', SCRIPT)
config_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_tool)


class Judge0ConfigTests(SimpleTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.config = Path(self.temp.name) / 'judge0.conf'
        self.patch = patch.object(config_tool, 'CONFIG', self.config)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def invoke(self, action):
        out, err = io.StringIO(), io.StringIO()
        with patch('sys.argv', ['manage_config.py', action]), redirect_stdout(out), redirect_stderr(err):
            status = config_tool.main()
        return status, out.getvalue(), err.getvalue()

    def test_create_is_private_unique_and_not_overwritten(self):
        status, output, error = self.invoke('create')
        self.assertEqual(status, 0, error)
        content = self.config.read_text()
        values = config_tool.validate(content)
        self.assertEqual(self.config.stat().st_mode & 0o777, 0o600)
        self.assertNotIn(values['AUTHN_TOKEN'], output + error)
        self.assertEqual(len({values[key] for key in config_tool.SECRET_KEYS}), 4)
        self.assertEqual(self.invoke('check')[0], 0)
        self.assertEqual(self.invoke('create')[0], 1)
        self.assertEqual(self.config.read_text(), content)

    def test_check_rejects_unsafe_settings_and_insecure_permissions(self):
        self.invoke('create')
        content = self.config.read_text()
        self.config.write_text(content.replace('ALLOW_ENABLE_NETWORK=false', 'ALLOW_ENABLE_NETWORK=true'))
        self.assertEqual(self.invoke('check')[0], 1)
        self.config.write_text(content)
        os.chmod(self.config, 0o644)
        self.assertEqual(self.invoke('check')[0], 1)

    def test_example_and_compose_bind_to_loopback(self):
        example = config_tool.TEMPLATE.read_text()
        self.assertIn('ALLOW_ENABLE_NETWORK=false', example)
        self.assertIn('ENABLE_ADDITIONAL_FILES=false', example)
        self.assertIn('ENABLE_CALLBACKS=false', example)
        compose = (ROOT / 'infra/judge0/docker-compose.yml').read_text()
        self.assertIn('127.0.0.1:2358:2358', compose)
        self.assertNotIn('/var/run/docker.sock', compose)
        self.assertEqual(compose.count('privileged: true'), 2)
