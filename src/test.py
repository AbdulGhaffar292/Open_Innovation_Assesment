import unittest
from unittest.mock import patch, MagicMock
from main import create_driver, scrape_products_on_page, scrape_product_details

class TestScraperFunctions(unittest.TestCase):

    @patch('your_script.webdriver.Chrome')
    @patch('your_script.ChromeDriverManager')
    def test_create_driver(self, MockChromeDriverManager, MockChrome):
        # Arrange
        MockChromeDriverManager.return_value.install.return_value = '/path/to/chromedriver'
        mock_options = MagicMock()
        MockChrome.return_value = MagicMock()
        
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        proxy = "http://proxy:port"
        
        # Act
        # driver = create_driver(user_agent, proxy)
        driver = create_driver(user_agent)
        
        # Assert
        MockChrome.assert_called_once_with(service=MockChromeDriverManager.return_value.install.return_value, options=mock_options)
        mock_options.add_argument.assert_any_call(f"user-agent={user_agent}")
        # mock_options.add_argument.assert_any_call(f'--proxy-server={proxy}')

    @patch('your_script.driver')
    def test_scrape_products_on_page(self, mock_driver):
        # Arrange
        mock_driver.find_elements.return_value = [MagicMock(get_attribute=MagicMock(return_value='http://example.com/product1')),
                                                MagicMock(get_attribute=MagicMock(return_value='http://example.com/product2'))]
        global product_links
        product_links = []
        
        # Act
        scrape_products_on_page()
        
        # Assert
        self.assertEqual(len(product_links), 2)
        self.assertIn('http://example.com/product1', product_links)
        self.assertIn('http://example.com/product2', product_links)

    @patch('your_script.driver')
    def test_scrape_product_details(self, mock_driver):
        # Arrange
        mock_driver.get = MagicMock()
        mock_driver.find_element.side_effect = [
            MagicMock(text='Test Product'),
            MagicMock(text='10'),
            MagicMock(text='5'),
            MagicMock(text='20'),
            MagicMock(text='15')
        ]
        
        product_url = 'http://example.com/product'
        
        # Act
        details = scrape_product_details(product_url)
        
        # Assert
        self.assertIsNotNone(details)
        self.assertEqual(details['product name'], 'Test Product')
        self.assertEqual(details['Bid price'], '10')
        self.assertEqual(details['Buy Offer'], '5')
        self.assertEqual(details['Ask price'], '20')
        self.assertEqual(details['Sale Offer'], '15')
        self.assertEqual(details['product url'], product_url)

if __name__ == '__main__':
    unittest.main()
