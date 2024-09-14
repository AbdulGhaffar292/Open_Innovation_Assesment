import unittest
from unittest.mock import patch, MagicMock
from main import set_undetected_chrome_browser_options, create_chrome_web_driver, scrape_products_page, scrape_product_details, save_to_csv

class TestWebScrapingFunctions(unittest.TestCase):

    @patch('main.uc.ChromeOptions')
    def test_set_undetected_chrome_browser_options(self, MockChromeOptions):
        mock_options = MockChromeOptions.return_value
        options = set_undetected_chrome_browser_options()
        
        self.assertIsInstance(options, MagicMock)
        mock_options.add_argument.assert_any_call("--no-sandbox")
        mock_options.add_argument.assert_any_call('--profile-directory=Default')
        self.assertFalse(options.headless)  # or True, depending on the expected behavior

    @patch('main.uc.Chrome')
    @patch('main.set_undetected_chrome_browser_options')
    def test_create_chrome_web_driver(self, MockSetOptions, MockChrome):
        mock_options = MockSetOptions.return_value
        mock_driver = MockChrome.return_value
        user_agent = "Mozilla/5.0"
        proxy = "http://proxy:port"
        
        driver = create_chrome_web_driver(user_agent, proxy)
        
        MockSetOptions.assert_called_once()
        MockChrome.assert_called_once_with(options=mock_options)
        mock_options.add_argument.assert_any_call(f"user-agent={user_agent}")
        mock_options.add_argument.assert_any_call(f'--proxy-server={proxy}')
        self.assertEqual(driver, mock_driver)

    @patch('main.create_chrome_web_driver')
    @patch('main.time.sleep', return_value=None)  # Mock sleep to avoid waiting
    def test_scrape_products_page(self, MockSleep, MockCreateWebDriver):
        mock_driver = MagicMock()
        mock_driver.find_elements.return_value = [
            MagicMock(get_attribute=MagicMock(return_value='http://example.com/product1')),
            MagicMock(get_attribute=MagicMock(return_value='http://example.com/product2'))
        ]
        MockCreateWebDriver.return_value = mock_driver

        product_links = []
        scrape_products_page(mock_driver, product_links)
        
        self.assertEqual(len(product_links), 2)
        self.assertIn('http://example.com/product1', product_links)
        self.assertIn('http://example.com/product2', product_links)

    @patch('main.create_chrome_web_driver')
    @patch('main.time.sleep', return_value=None)  # Mock sleep to avoid waiting
    def test_scrape_product_details(self, MockSleep, MockCreateWebDriver):
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = [
            MagicMock(text='Product Name'),
            MagicMock(text='10'),
            MagicMock(text='5'),
            MagicMock(text='20'),
            MagicMock(text='15'),
        ]
        MockCreateWebDriver.return_value = mock_driver

        product_url = 'http://example.com/product1'
        details = scrape_product_details(mock_driver, product_url)

        expected_details = {
            'product name': 'Product Name',
            'Bid price': '10',
            'Buy Offer': '5',
            'Ask price': '20',
            'Sale Offer': '15',
            'product url': product_url
        }
        self.assertEqual(details, expected_details)

    @patch('main.pd.DataFrame.to_csv')
    def test_save_to_csv(self, MockToCsv):
        data = [{'product name': 'Product1', 'Bid price': '10'}]
        save_to_csv(data)
        
        MockToCsv.assert_called_once_with('Stream_Community_Data.csv', index=False)
        self.assertEqual(MockToCsv.call_args[0][0], 'Stream_Community_Data.csv')

if __name__ == '__main__':
    unittest.main()
