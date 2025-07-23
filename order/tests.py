from audioop import reverse
from django.test import TestCase, Client
# Create your tests here.
# class TestPage(TestCase):

#    def setUp(self):
#        self.client = Client()

#    def test_index_page(self):
#        url = reverse('home')
#        response = self.client.get(url)
#     #    print(response.status_code)
#     #    print('salom')
#        self.assertEqual(response.status_code, 404)

    #    self.assertEqual(response.status_code, 200)
    #    self.assertTemplateUsed(response, 'index.html')
    #    self.assertContains(response, 'Company Name XYZ')