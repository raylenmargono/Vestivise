from django.test import TestCase

# Create your tests here.
class QuovoTest(TestCase):

    def test_token_is_valid(self):
        false_response_date = "2016-03-31T18:45:09Z"
        correct_response_date = "2216-03-31T18:45:09Z"
        