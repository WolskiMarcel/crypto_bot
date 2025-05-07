import unittest
from unittest.mock import patch, Mock
from src.app import price, user_currency, message_fav_data


# Fake classes for simulating Discord context
class FakeAuthor:
    def __init__(self, id):
        self.id = id


# Class simulating a message returned by ctx.send.
class FakeMessage:
    def __init__(self, content):
        self.content = content
        self.id = 9999
        self.reactions = []

    async def add_reaction(self, reaction):
        self.reactions.append(reaction)


# Class simulating the context (ctx) of a Discord command.
class FakeContext:
    def __init__(self, author_id):
        self.author = FakeAuthor(author_id)
        self.sent_messages = []  # Stores sent messages (texts)

    async def send(self, message):
        msg = FakeMessage(message)
        self.sent_messages.append(message)
        return msg


class TestPriceCommand(unittest.IsolatedAsyncioTestCase):
    @patch("src.app.requests.get")
    async def test_price_command_fiat(self, mock_get):
        """
        Tests the !price command in the fiat currency branch.
        If the user does not have a preferred currency (target) set, it will default to PLN.

        Scenario:
        - Call the !price command with the argument "usd" (this is a fiat currency).
        - Due to the lack of a set currency, the target will be set to "PLN".
        - Patch requests.get to return a sample response from the Frankfurter API:
            { "rates": {"PLN": 4.0} }
        - Expect that the resulting message will contain the text "💱 1 USD = 4.00 PLN".
        - Check if the global dictionary message_fav_data has been updated
            with the appropriate keys, including the fixed message ID (9999).
        """
        # Reset global settings to ensure the test is repeatable.
        user_currency.pop(10, None)
        message_fav_data.clear()

        # Prepare a simulated API response.
        fake_response = {"rates": {"PLN": 4.0}}
        mock_response = Mock()
        mock_response.json.return_value = fake_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Create a simulated context: user with id=10.
        ctx = FakeContext(author_id=10)

        # Call the price command with the argument "usd".
        await price(ctx, "usd")

        # Expected message – since the user does not have a set currency, the target will be "PLN".
        expected_message = "💱 1 USD = 4.00 PLN"
        self.assertTrue(ctx.sent_messages, "Nie wysłano żadnej wiadomości!")
        self.assertIn(expected_message, ctx.sent_messages[0])

        # Check if the global dictionary message_fav_data has been updated.
        self.assertIn(9999, message_fav_data)
        fav_entry = message_fav_data[9999]
        self.assertEqual(fav_entry["type"], "price")
        self.assertEqual(fav_entry["symbol"], "USD")
        self.assertEqual(fav_entry["currency"], "PLN")
        self.assertEqual(fav_entry["fiat_conversion"], True)


if __name__ == "__main__":
    unittest.main()
