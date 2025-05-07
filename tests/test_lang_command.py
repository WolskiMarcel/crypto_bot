import unittest
from src.app import lang, user_lang, t


# Fake classes for simulating Discord context
class FakeAuthor:
    def __init__(self, id):
        self.id = id


class FakeContext:
    def __init__(self, author_id):
        self.author = FakeAuthor(author_id)
        self.sent_messages = []

    async def send(self, message):
        self.sent_messages.append(message)


class TestLangCommand(unittest.IsolatedAsyncioTestCase):

    async def test_lang_no_argument(self):
        """
        Test that checks calling the !lang command without an argument.
        We expect a message to be sent informing the user that a language code must be provided.
        """
        ctx = FakeContext(author_id=1)
        # Make sure that no language is set for the given user (or it defaults to "en")
        user_lang.pop(ctx.author.id, None)
        # Call the command without an argument
        await lang(ctx)
        # Expected message – the t() function will return the version for the default "en"
        expected = t(
            ctx.author.id,
            {
                "en": "Please enter `!jezyk en/pl` or `!lang en/pl`.",
                "pl": "Wpisz `!jezyk en/pl` albo `!lang en/pl`",
            },
        )
        self.assertIn(expected, ctx.sent_messages)

    async def test_lang_set_to_pl(self):
        """
        Test that checks if calling the !lang command with the "pl" argument sets the language to Polish
        and sends the appropriate message.
        """
        ctx = FakeContext(author_id=2)
        user_lang.pop(ctx.author.id, None)  # Remove any previous settings
        # Call the command with the "pl" argument
        await lang(ctx, "pl")
        expected = "✅ Język ustawiony na **polski** 🇵🇱"
        self.assertIn(expected, ctx.sent_messages)
        self.assertEqual(user_lang[ctx.author.id], "pl")


if __name__ == "__main__":
    unittest.main()
