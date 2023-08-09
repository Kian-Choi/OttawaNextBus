import unittest
from unittest.mock import patch, Mock
import json
from model import fetch_oc_route_summary_for_stop_feed, Route, fetch_next_trips_all_routes, Trip


class TestModelFunctions(unittest.TestCase):

    @patch('model.requests.get')
    def test_fetch_oc_route_summary_for_stop_feed(self, mock_get):
        # Load the sample JSON data
        with open('data/sample/all_route_info.json', 'r') as file:
            sample_data = json.load(file)

        # Mock the API call
        mock_response = Mock()
        mock_response.text = json.dumps(sample_data)
        mock_get.return_value = mock_response

        # Call the function
        stop_no = '3047'
        result = fetch_oc_route_summary_for_stop_feed(stop_no)

        # Expected routes
        expected_routes = [
            Route('75', "Tunney's Pasture & Gatineau & N Rideau"),
            Route('75', 'Barrhaven Centre'),
            Route('80', 'Barrhaven Centre'),
            Route('80', "Tunney's Pasture"),
            Route('99', 'Barrhaven Centre'),
            Route('99', 'Greenboro & Hurdman'),
            Route('170', 'Fallowfield & CFIA'),
            Route('170', 'Barrhaven Centre'),
            Route('171', 'Fallowfield'),
            Route('171', 'Barrhaven Centre'),
            Route('173', 'Barrhaven Centre'),
            Route('173', 'Fallowfield & Bayshore'),
            Route('175', 'Golflinks'),
            Route('175', 'Barrhaven Centre'),
            Route('176', 'Manotick'),
            Route('176', 'Barrhaven Centre'),
            Route('305', 'Carlingwood'),
            Route('305', 'North Gower / Manotick')
        ]

        # Validate the results
        self.assertEqual(result, expected_routes)

    @patch('model.requests.get')
    def test_fetch_next_trips_all_routes(self, mock_get):
        # Mocking the method to return the provided JSON content
        with open('data/sample/next_trips_all_routes_sample.json', 'r') as file:
            sample_data = json.load(file)

        # Mock the API call
        mock_response = Mock()
        mock_response.text = json.dumps(sample_data)
        mock_get.return_value = mock_response
        # Calling the function
        stop_no = '3047'
        result = fetch_next_trips_all_routes(stop_no)

        # Sample expected result (you should fill this with what you expect the function to return)
        expected_trips = [
            Trip("75", "Tunney's Pasture", "23", "-75.73182180653448", "45.241415106731914"),
            Trip("75", "Tunney's Pasture", "37", "", ""),
            Trip("75", "Tunney's Pasture", "52", "", ""),
            Trip("75", "Cambrian", "1", "", ""),
            Trip("75", "Cambrian", "17", "-75.77130150072503", "45.358177705244586"),
            Trip("75", "Cambrian", "30", "", ""),
            Trip("80", "Barrhaven Centre", "16", "-75.70750357887961", "45.294374292547054"),
            Trip("80", "Barrhaven Centre", "36", "", ""),
            Trip("80", "Barrhaven Centre", "67", "", ""),
            Trip("80", "Tunney's Pasture", "22", "-75.70750357887961", "45.294374292547054"),
            Trip("80", "Tunney's Pasture", "51", "", ""),
            Trip("80", "Tunney's Pasture", "82", "", ""),
            Trip("99", "Barrhaven Centre", "15", "", ""),
            Trip("99", "Barrhaven Centre", "44", "", ""),
            Trip("99", "Barrhaven Centre", "75", "", ""),
            Trip("99", "Greenboro", "23", "", ""),
            Trip("99", "Greenboro", "52", "", ""),
            Trip("99", "Greenboro", "84", "", ""),
            Trip("170", "Fallowfield", "13", "-75.74161333333333", "45.26718666666667"),
            Trip("170", "Fallowfield", "42", "", ""),
            Trip("170", "Barrhaven Centre", "26", "-75.7566909790039", "45.28738021850586"),
            Trip("170", "Barrhaven Centre", "53", "", ""),
            Trip("170", "Barrhaven Centre", "83", "", ""),
            Trip("171", "Fallowfield", "47", "", ""),
            Trip("171", "Fallowfield", "77", "", ""),
            Trip("171", "Barrhaven Centre", "32", "", ""),
            Trip("173", "Barrhaven Centre", "11", "-75.75819480582459", "45.28028514287243"),
            Trip("173", "Barrhaven Centre", "34", "", ""),
            Trip("173", "Barrhaven Centre", "64", "", ""),
            Trip("173", "Fallowfield", "19", "-75.75819480582459", "45.28028514287243"),
            Trip("173", "Bayshore", "48", "", ""),
            Trip("173", "Fallowfield", "78", "", ""),
            Trip("175", "Golflinks", "53", "", ""),
            Trip("175", "Barrhaven Centre", "68", "", "")
        ]

        # Asserting the expected results against the actual results
        self.assertEqual(result, expected_trips)


if __name__ == '__main__':
    unittest.main()
