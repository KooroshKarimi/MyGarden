import unittest
from app import app

class GardenRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_no_admin(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MyGarden', response.data)
        self.assertNotIn(b'ADMIN MODE', response.data)

    def test_index_admin(self):
        response = self.app.get('/?admin=true')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ADMIN MODE', response.data)
        # Prüfen, ob der Stift-Button gerendert wird (indirekt über das SVG oder den Button-Tag)
        self.assertIn(b'Bild \xc3\xa4ndern', response.data) # "Bild ändern" title

if __name__ == '__main__':
    unittest.main()
