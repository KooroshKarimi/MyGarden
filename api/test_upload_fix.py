import unittest
import shutil
import tempfile
import sys
import os
from pathlib import Path
from io import BytesIO
from unittest.mock import patch

# Ensure we can import server.py from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import server

class TestUploadFix(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.content_root = Path(self.test_dir) / "content"
        self.content_root.mkdir()
        
        # Patch CONTENT_ROOT in server module
        self.patcher = patch('server.CONTENT_ROOT', self.content_root)
        self.mock_content_root = self.patcher.start()
        
        # Patch _trigger_rebuild to avoid running scripts
        self.rebuild_patcher = patch('server._trigger_rebuild')
        self.mock_rebuild = self.rebuild_patcher.start()

        self.app = server.app.test_client()

    def tearDown(self):
        self.patcher.stop()
        self.rebuild_patcher.stop()
        shutil.rmtree(self.test_dir)

    def test_upload_creates_directory(self):
        # Path to a page in a subdirectory that does not exist yet
        rel_path = "new_folder/index.md"
        
        # Simulate image data
        data = {
            'page_path': rel_path,
            'image_name': 'test_image.jpg',
            'image': (BytesIO(b"fake image data"), 'test_image.jpg')
        }
        
        response = self.app.post('/api/content/image', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200, f"Upload failed: {response.json if response.is_json else response.data}")
        
        # Check if directory and file were created
        expected_dir = self.content_root / "new_folder"
        expected_file = expected_dir / "test_image.jpg"
        
        self.assertTrue(expected_dir.exists(), "Directory was not created")
        self.assertTrue(expected_file.exists(), "Image file was not created")

if __name__ == '__main__':
    unittest.main()
