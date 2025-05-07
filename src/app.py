import discord
from discord.ext import commands
import requests
import os
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from io import BytesIO
import json
from dotenv import load_dotenv

# We retrieve the bot token from the environment variables
load_dotenv()  # Loads environment variables from the .env file.
TOKEN = os.getenv("D_TOKEN")

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
)

# Dictionaries storing user preferences
user_lang = {}  # Key: user.id, value: "en" lub "pl"
user_currency = {}  # Key: user.id, value: f.ex. "USD", "PLN", etc.
user_favorites = {}
FAVORITES_FILE = "favorites.json"
message_fav_data = (
    {}
)  # Mapping: message.id -> dynamic favorite info (np. {"type": "price", "symbol": "BTC"})


# Translation function – the default language is English ('en')
def t(user_id, text):
    lang = user_lang.get(user_id, "en")
    return text.get(lang, text["en"])


# Bot initialization with the required intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Remove the default help command to avoid alias conflicts
bot.remove_command("help")


@bot.event
async def on_ready():
    global user_favorites
    user_favorites = load_favorites()
    print(f"Logged in as {bot.user}")


@bot.command(name="hello", aliases=["hej"])
async def hello(ctx):
    await ctx.send(t(ctx.author.id, {"en": "Hello!", "pl": "Cześć!"}))


@bot.command(name="lang", aliases=["jezyk"])
async def lang(ctx, kod: str = None):
    user_id = ctx.author.id
    if kod and kod.lower() in ("en", "pl"):
        user_lang[user_id] = kod.lower()
        msg = {
            "en": "✅ Language set to **English** 🇬🇧",
            "pl": "✅ Język ustawiony na **polski** 🇵🇱",
        }
        await ctx.send(msg[kod.lower()])
    else:
        await ctx.send(
            t(
                ctx.author.id,
                {
                    "en": "Please enter `!jezyk en/pl` or `!lang en/pl`.",
                    "pl": "Wpisz `!jezyk en/pl` albo `!lang en/pl`",
                },
            )
        )


@bot.command(name="price", aliases=["cena"])
async def price(ctx, symbol: str):
    user_id = ctx.author.id
    fiat_codes = {"USD", "EUR", "PLN", "GBP", "JPY", "CHF", "AUD", "CAD"}
    symbol_input = symbol.upper()

    # Handle fiat currency symbols with special logic
    if symbol_input in fiat_codes:
        # Get the target currency:
        # If the user set a currency (e.g., using !currency/!waluta) and it's different from the symbol,
        # use it; otherwise, default to PLN.
        target_fiat = user_currency.get(user_id, None)
        if not target_fiat or target_fiat.upper() == symbol_input:
            target_fiat = "PLN"
        else:
            target_fiat = target_fiat.upper()
        try:
            # Use the Frankfurter API to fetch the exchange rate from symbol_input (e.g., USD) to target_fiat (e.g., PLN).
            frankfurter_url = f"https://api.frankfurter.app/latest?from={symbol_input}&to={target_fiat}"
            res = requests.get(frankfurter_url).json()
            if "rates" not in res or target_fiat not in res["rates"]:
                await ctx.send(
                    t(
                        ctx.author.id,
                        {
                            "en": f"⚠️ An error occurred: {e}",
                            "pl": f"⚠️ Wystąpił błąd: {e}",
                        },
                    )
                )
                return
            rate = float(res["rates"][target_fiat])
            message_content = f"💱 1 {symbol_input} = {rate:.2f} {target_fiat}"
            msg = await ctx.send(message_content)
            await msg.add_reaction("❤️")
            # Save dynamic data — taking into account that this is a fiat currency conversion.
            message_fav_data[msg.id] = {
                "type": "price",
                "symbol": symbol_input,
                "currency": target_fiat,
                "fiat_conversion": True,
            }
            return
        except Exception as e:
            await ctx.send(
                t(
                    ctx.author.id,
                    {"en": f"⚠️ An error occurred: {e}", "pl": f"⚠️ Wystąpił błąd: {e}"},
                )
            )
            return

    # If the symbol is not a fiat currency, treat it as a cryptocurrency.
    currency = user_currency.get(user_id, "USD").upper()
    symbol_base = symbol_input
    symbol_with_usdt = symbol_base + "USDT"
    try:
        binance_url = (
            f"https://api.binance.com/api/v3/ticker/price?symbol={symbol_with_usdt}"
        )
        res = requests.get(binance_url).json()
        cena_usdt = float(res["price"])
        if currency in ["USD", "USDT"]:
            message_content = f"💰 Price of {symbol_base}: {cena_usdt:,.2f} {currency}"
        else:
            frankfurter_url = (
                f"https://api.frankfurter.app/latest?from=USD&to={currency}"
            )
            res2 = requests.get(frankfurter_url).json()
            if "rates" not in res2:
                kurs = 1.0
            else:
                kurs = float(res2["rates"].get(currency, 1.0))
            final_price = cena_usdt * kurs
            message_content = f"💰 Price of {symbol_base}: {final_price:,.2f} {currency} (conversion rate: {kurs:.4f})"
        msg = await ctx.send(message_content)
        await msg.add_reaction("❤️")
        message_fav_data[msg.id] = {
            "type": "price",
            "symbol": symbol_base,
            "currency": currency,
            "fiat_conversion": False,
        }
    except Exception as e:
        await ctx.send(
            t(user_id, {"en": f"⚠️ Error occurred: {e}", "pl": f"⚠️ Wystąpił błąd: {e}"})
        )


@bot.command(name="currencies", aliases=["waluta"])
async def currencies(ctx, kod: str = None):
    user_id = ctx.author.id

    # If a currency code is provided to set
    if kod:
        kod = kod.upper()
        try:
            response = requests.get("https://api.frankfurter.app/currencies")
            response.raise_for_status()
            currencies = response.json()

            # Add USDT manually because it is not available in the API.
            if "USDT" not in currencies:
                currencies["USDT"] = "Tether (US Dollar Pegged)"

            if kod in currencies:
                user_currency[user_id] = kod
                await ctx.send(
                    f"✅ {t(user_id, {'en': 'Currency set to', 'pl': 'Ustawiono walutę na'})} **{kod} – {currencies[kod]}**"
                )
            else:
                await ctx.send(
                    f"❌ {t(user_id, {'en': 'Unknown currency code.', 'pl': 'Nieznany kod waluty.'})}"
                )
        except Exception as e:
            await ctx.send(
                f"⚠️ {t(user_id, {'en': 'Error setting currency.', 'pl': 'Błąd podczas ustawiania waluty.'})}\n{str(e)}"
            )
    else:
        # Get the currently set currency (default is USD).
        current = user_currency.get(user_id, "USD")
        display_current = current  # This will be displayed to the user
        # If the user has set USDT, we will use "USD" as the API baseI
        base_for_api = "USD" if current == "USDT" else current
        try:
            response = requests.get(
                f"https://api.frankfurter.app/latest?from={base_for_api}&to=EUR,GBP,PLN,USD"
            )
            response.raise_for_status()
            data = response.json()
            rates = data.get("rates", {})
            currency_list = "\n".join(
                [f"• `{code}`: {rate}" for code, rate in rates.items()]
            )

            # Fetch the full list of currencies from the API.
            response_currencies = requests.get("https://api.frankfurter.app/currencies")
            response_currencies.raise_for_status()
            currencies = response_currencies.json()
            # Add USDT manually as it is not available in the API.
            if "USDT" not in currencies:
                currencies["USDT"] = "Tether (US Dollar Pegged)"

            await ctx.send(
                f"🌍 {t(user_id, {'en': 'Your current currency:', 'pl': 'Twoja aktualna waluta:'})} **{display_current} – {currencies.get(display_current, '')}**\n\n"
                f"{t(user_id, {'en': 'Available currencies:', 'pl': 'Dostępne waluty:'})}\n"
                f"{currency_list}"
            )
        except Exception as e:
            await ctx.send(
                f"⚠️ {t(user_id, {'en': 'Error fetching currencies.', 'pl': 'Błąd pobierania walut.'})}\n{str(e)}"
            )


def parse_chart_args(args):
    """
    Parses the arguments of the 'chart' command and returns a dictionary with the set parameters. Default values below.
    Allowed argument sets:
      1 argument: only symbol
      2 arguments: symbol and (days or target, depending on the argument format)
      3 arguments: symbol, target, days
      4 arguments: symbol, target, days, interval
      5 arguments: symbol, target, days, interval, color
    """
    # Default values:
    params = {
        "symbol": "BTC",
        "target": "USDT",
        "days": 30,
        "interval": "1d",
        "kolor": "royalblue",
    }

    if len(args) == 1:
        params["symbol"] = args[0].upper()
    elif len(args) == 2:
        params["symbol"] = args[0].upper()
        if args[1].endswith("d"):
            params["days"] = int(args[1].replace("d", ""))
        else:
            params["target"] = args[1].upper()
    elif len(args) == 3:
        params["symbol"] = args[0].upper()
        params["target"] = args[1].upper()
        params["days"] = int(args[2].replace("d", ""))
    elif len(args) == 4:
        params["symbol"] = args[0].upper()
        params["target"] = args[1].upper()
        params["days"] = int(args[2].replace("d", ""))
        params["interval"] = args[3]
    elif len(args) == 5:
        params["symbol"] = args[0].upper()
        params["target"] = args[1].upper()
        params["days"] = int(args[2].replace("d", ""))
        params["interval"] = args[3]
        params["kolor"] = args[4].lower()

    return params


def get_fiat_data(symbol, target, days):
    """
    Fetches historical exchange rate data for fiat pairs using the Frankfurter API.

    Returns:
      - a list of dates (as datetime objects)
      - a list of exchange rates
      - the chart title
      - the Y-axis label
    """
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=days)
    url = f"https://api.frankfurter.app/{start_date}..{end_date}?from={symbol}&to={target}"

    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    if "rates" not in data or not data["rates"]:
        raise Exception("No data available for that period.")

    dates = sorted(data["rates"].keys())
    prices = [data["rates"][d][target] for d in dates]
    dates_dt = [datetime.strptime(d, "%Y-%m-%d") for d in dates]

    title = f"{symbol}/{target} – {days} days"
    ylabel = f"Exchange Rate ({target})"
    return dates_dt, prices, title, ylabel


def get_crypto_data(symbol, target, days, interval):
    """
    Fetches candlestick (klines) data for cryptocurrency pairs from Binance and performs any necessary currency conversion.

    Determines the expected data limit based on the interval and the number of days.
    Returns:
      - a list of dates (as datetime objects)
      - a list of converted closing prices
      - the chart title
      - the Y-axis label
    """
    # Determining the candlestick data limit
    if "h" in interval:
        try:
            hours_per_day = 24 // int(interval.replace("h", ""))
        except Exception:
            hours_per_day = 24
        max_limit = min(days * hours_per_day, 1000)
    else:
        max_limit = min(days, 1000)

    conversion_rate = 1.0
    # Attempt to fetch data for a direct pair, e.g., BTCPLN
    pair = f"{symbol}{target}"
    url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval={interval}&limit={max_limit}"
    try:
        res = requests.get(url)
        res.raise_for_status()
        klines = res.json()
        if not klines:
            raise Exception("Brak danych dla pary")
        use_fallback = False
    except Exception:
        use_fallback = True

    if use_fallback:
        # If the direct pair doesn't work, use a pair with USDT and convert the rate to the target (e.g., PLN)
        pair = f"{symbol}USDT"
        url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval={interval}&limit={max_limit}"
        res = requests.get(url)
        res.raise_for_status()
        klines = res.json()
        if target not in ["USD", "USDT"]:
            rate_url = f"https://api.frankfurter.app/latest?from=USD&to={target}"
            r = requests.get(rate_url).json()
            if "rates" in r:
                conversion_rate = float(r["rates"].get(target, 1.0))

    timestamps = [datetime.fromtimestamp(k[0] / 1000) for k in klines]
    prices_raw = [float(k[4]) for k in klines]
    prices = [p * conversion_rate for p in prices_raw]
    title = f"{symbol}/{target} – {days} periods ({interval})"
    ylabel = f"Price ({target})"
    return timestamps, prices, title, ylabel


def create_chart(dates_dt, prices, title, ylabel, kolor):
    """
    Creates a chart using the matplotlib library and saves it to a BytesIO object.

    Returns a buffer object, ready to be sent via Discord.
    """
    plt.figure(figsize=(14, 7))
    plt.rcParams.update({"font.size": 12})
    plt.plot(dates_dt, prices, color=kolor, linewidth=2)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.title(title, fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf


@bot.command(name="chart", aliases=["wykres"])
async def wykres(ctx, *args):
    user_id = ctx.author.id
    try:
        # Parsing the command arguments
        params = parse_chart_args(args)

        # If the user hasn't specified a currency (only the symbol or symbol and days were provided),
        # overwrite the default target ("USDT") with the currency set by the user.
        if len(args) == 1 or (len(args) == 2 and args[1].endswith("d")):
            default_currency = user_currency.get(user_id, "USD").upper()
            params["target"] = default_currency

        symbol = params["symbol"]
        target = params["target"]
        days = params["days"]
        interval = params["interval"]
        kolor = params["kolor"]

        # List of fiat currencies – can be extended as needed
        fiat_codes = {"USD", "EUR", "PLN", "GBP", "JPY", "CHF", "AUD", "CAD"}

        if symbol in fiat_codes and target in fiat_codes:
            dates_dt, prices, title, ylabel = get_fiat_data(symbol, target, days)
        else:
            dates_dt, prices, title, ylabel = get_crypto_data(
                symbol, target, days, interval
            )

        # Generating the chart
        buf = create_chart(dates_dt, prices, title, ylabel, kolor)
        await ctx.send(file=discord.File(buf, filename="wykres.png"))
    except Exception as e:
        await ctx.send(
            t(
                user_id,
                {
                    "en": f"⚠️ Error generating chart: {e}",
                    "pl": f"⚠️ Błąd generowania wykresu: {e}",
                },
            )
        )


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return  # Ignoring bots

    if str(reaction.emoji) == "❤️":
        message = reaction.message

        if message.author == bot.user:
            user_id = user.id

            # If the message has dynamic content, gather that data;
            # otherwise, fetch the static content.
            if message.id in message_fav_data:
                fav_item = message_fav_data[message.id]
            else:
                fav_item = {
                    "type": "static",
                    "content": (
                        message.content
                        if message.content
                        else (
                            message.embeds[0].description
                            if message.embeds
                            else "Attachment"
                        )
                    ),
                }

            favs = user_favorites.get(user_id, [])
            if fav_item not in favs:
                favs.append(fav_item)
                user_favorites[user_id] = favs
                save_favorites()
                await message.channel.send(
                    f"💾 {user.mention}, added to your favorites!"
                )


@bot.command(name="favorite", aliases=["ulubione", "fav"])
async def show_favorites(ctx):
    user_id = ctx.author.id
    favs = user_favorites.get(user_id, [])
    if not favs:
        await ctx.send(
            t(
                user_id,
                {
                    "en": "You don't have any favorites yet. ❤️",
                    "pl": "Nie masz jeszcze żadnych ulubionych. ❤️",
                },
            )
        )
    else:
        display_lines = []
        # Displaying the last 5 favorites
        for fav in favs[-5:]:
            if isinstance(fav, dict) and fav.get("type") == "price":
                # Dla dynamicznych wpisów liczymy aktualną cenę
                updated_msg = get_dynamic_price(fav, user_id)
                display_lines.append(f"🔸 {updated_msg}")
            elif isinstance(fav, dict) and fav.get("type") == "static":
                display_lines.append(f"🔸 {fav.get('content')}")
            else:
                display_lines.append(f"🔸 {fav}")
        response = "\n\n".join(display_lines)
        await ctx.send(
            t(
                user_id,
                {
                    "en": f"📌 Your recent favorites:\n{response}",
                    "pl": f"📌 Twoje ostatnie ulubione:\n{response}",
                },
            )
        )


def save_favorites():
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(user_favorites, f, ensure_ascii=False, indent=2)


def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
            except json.JSONDecodeError:
                print("Error decoding favorites.json")
    return {}


def get_dynamic_price(fav, user_id):
    """
     Updates the dynamic entry of favorites.
    For 'price' entries with the key "fiat_conversion": True, treat it as a fiat currency exchange rate,
    calling the Frankfurter API to fetch the current rate (e.g., 1 USD = X PLN).
    Otherwise, assume it's a cryptocurrency and fetch the price from Binance.
    """
    base_symbol = fav.get("symbol")
    # Use the saved currency or the one set by the user
    stored_currency = fav.get("currency")
    currency = (
        stored_currency if stored_currency else user_currency.get(user_id, "USD")
    ).upper()

    if fav.get("fiat_conversion"):
        # Special path for fiat currency conversion (e.g., !price usd/!cena usd)
        try:
            frankfurter_url = (
                f"https://api.frankfurter.app/latest?from={base_symbol}&to={currency}"
            )
            res = requests.get(frankfurter_url).json()
            if "rates" not in res or currency not in res["rates"]:
                return f"⚠️ Error updating conversion for {base_symbol}: missing rate"
            rate = float(res["rates"][currency])
            return f"💱 1 {base_symbol} = {rate:.2f} {currency}"
        except Exception as e:
            return f"⚠️ Error updating conversion for {base_symbol}: {e}"
    else:
        # Assume the entry is for cryptocurrency – fetch the price from Binance
        symbol_with_usdt = base_symbol + "USDT"
        try:
            binance_url = (
                f"https://api.binance.com/api/v3/ticker/price?symbol={symbol_with_usdt}"
            )
            res = requests.get(binance_url).json()
            price_usdt = float(res["price"])
            if currency in ["USD", "USDT"]:
                return f"💰 Price of {base_symbol}: {price_usdt:,.2f} {currency}"
            else:
                frankfurter_url = (
                    f"https://api.frankfurter.app/latest?from=USD&to={currency}"
                )
                res2 = requests.get(frankfurter_url).json()
                rate = float(res2["rates"].get(currency, 1.0))
                final_price = price_usdt * rate
                return f"💰 Price of {base_symbol}: {final_price:,.2f} {currency} (conversion rate: {rate:.4f})"
        except Exception as e:
            return f"⚠️ Error updating price for {base_symbol}: {e}"


@bot.command(name="remove-favorite", aliases=["usun_ulubione", "rmfav", "usunfav"])
async def remove_favorite(ctx, index: int):
    user_id = ctx.author.id
    favs = user_favorites.get(user_id, [])
    if not favs:
        await ctx.send(
            t(
                user_id,
                {
                    "en": "❌ You have no favorites",
                    "pl": "❌ Nie masz żadnych ulubionych.",
                },
            )
        )
        return

    # Assume the user provides the index starting from 1
    if index < 1 or index > len(favs):
        await ctx.send(
            t(
                user_id,
                {
                    "en": f"❌ Please provide a valid number. You have {len(favs)} favorite items.",
                    "pl": f"❌ Podaj poprawny numer. Masz {len(favs)} ulubionych elementów.",
                },
            )
        )
        return

    removed_fav = favs.pop(index - 1)
    save_favorites()  # Save the update to the file
    await ctx.send(
        t(
            user_id,
            {
                "en": f"✅ Removed from favorites: {removed_fav}",
                "pl": f"✅ Usunięto z ulubionych: {removed_fav}",
            },
        )
    )


@bot.command(name="help", aliases=["pomoc"])
async def help_command(ctx):
    user_id = ctx.author.id

    help_text_pl = (
        "**📜 Pomoc - Lista dostępnych komend i funkcji:**\n\n"
        "**Podstawowe komendy:**\n"
        "**👋 !hej / !hello**\n"
        '  - Pozdrawia użytkownika. Przykład: `!hello` lub `!hej` zwraca "Hello!" lub "Cześć!".\n\n'
        "**🇵🇱🇬🇧 !jezyk / !lang [en/pl]**\n"
        "  - Ustawia język bota. Przykład: `!jezyk pl` ustawi język polski.\n\n"
        "**💲 !price / !cena [symbol]**\n"
        "  - Wyświetla aktualną cenę kryptowaluty w ustawionej walucie. Przykład: `!price BTC`.\n\n"
        "**💱 !waluta / !currencies [kod waluty]**\n"
        "  - Ustawia Twoją preferowaną walutę lub wyświetla listę dostępnych walut. Przykład: `!waluta USD` ustawi walutę na USD.\n\n"
        "**📈 !wykres / !chart [symbol] [target] [dni] [interwał opcjonalnie] [kolor opcjonalnie]**\n"
        "  - Generuje wykres dla wybranego symbolu.\n"
        "    - **Przykłady:**\n"
        "      - `!wykres BTC 30d` → wykres BTC/USDT z 30 dniowym okresem (domyślne ustawienia target, interwału i koloru)\n"
        "      - `!wykres ETH USDT 7d 4h` → wykres ETH/USDT z 7 dniowym okresem i interwałem 4-godzinnym\n"
        "      - `!wykres USD PLN 90d` → wykres USD/PLN z 90 dniowym okresem\n\n"
        "**⭐ Ulubione i zarządzanie:**\n"
        "• **❤️ (reakcja)**\n"
        "  - Aby dodać wiadomość (np. wynik ceny lub wykres) do ulubionych, wystarczy zareagować emoji ❤️.\n\n"
        "• **!ulubione / !fav**\n"
        "  - Wyświetla listę Twoich ostatnich ulubionych wpisów.\n\n"
        "• **!usun_ulubione [numer] / !remove-favorite [numer] / !rmfav [numer]**\n"
        "  - Usuwa wybrany wpis ulubionych. Numeracja zaczyna się od 1. Przykład: `!usunfav 2` usunie drugi wpis.\n\n"
        "**Dodatkowe informacje:**\n"
        "• Dynamiczne wpisy (np. ceny) są aktualizowane na bieżąco, co oznacza, że Twoje ulubione mogą zawsze prezentować aktualne dane.\n"
        "• Bot korzysta z API Binance i Frankfurter, aby pobierać kursy walut oraz generować wykresy.\n\n"
        "**Przykłady użycia:**\n"
        "• `!hej`\n"
        "• `!jezyk en`\n"
        "• `!cena USD`\n"
        "• `!cena BTC`\n"
        "• `!waluta EUR`\n"
        "• `!wykres BTC 30d`\n"
        "• `!wykres BTC usd 30d 1h purple`\n\n"
        "Aby dodać wpis do ulubionych, zareaguj emoji ❤️ na wiadomość bota (np. cenę lub wykres)."
    )

    help_text_en = (
        "**📜 Help - List of available commands and features:**\n\n"
        "**Basic commands:**\n"
        "**👋 !hello / !hej**\n"
        '  - Greets the user. Example: `!hello` or `!hej` returns "Hello!" or "Cześć!".\n\n'
        "**🇵🇱🇬🇧 !lang / !jezyk [en/pl]**\n"
        "  - Sets the bot's language. Example: `!jezyk en` sets the language to English.\n\n"
        "**💲 !price / !cena [symbol]**\n"
        "  - Displays the current price of a cryptocurrency in your selected currency. Example: `!price BTC`.\n\n"
        "**💱 !currencies / !waluta [currency code]**\n"
        "  - Sets your preferred currency or displays the list of available currencies. For example, `!waluta USD` sets your currency to USD.\n\n"
        "**📈 !chart / !wykres [symbol] [target] [days] [interval optional] [color optional]**\n"
        "  - Generates a chart for the selected symbol.\n"
        "    - **Examples:**\n"
        "      - `!chart BTC 30d` → chart for BTC/USDT over 30 days (default target, interval, and color applied)\n"
        "      - `!chart ETH USDT 7d 4h` → chart for ETH/USDT over 7 days with a 4-hour interval\n"
        "      - `!chart USD PLN 90d` → chart for USD/PLN over 90 days\n\n"
        "**⭐ Favorites and management:**\n"
        "• **❤️ (reaction)**\n"
        "  - To add a bot's message (e.g., a price result or chart) to your favorites, simply react with ❤️.\n\n"
        "• **!fav / !ulubione**\n"
        "  - Displays a list of your recent favorite entries.\n\n"
        "• **!remove-favorite [number] / !usun_ulubione [number] / !rmfav [number]**\n"
        "  - Removes the selected favorite entry. Indexing starts at 1. Example: `!rmfav 2` removes the second entry.\n\n"
        "**Additional information:**\n"
        "• Dynamic entries (like prices) update in real-time, ensuring that your favorites display the most current data.\n"
        "• The bot integrates with Binance and Frankfurter APIs to retrieve currency data and generate charts.\n\n"
        "**Usage examples:**\n"
        "• `!hello`\n"
        "• `!lang en`\n"
        "• `!price USD`\n"
        "• `!price BTC`\n"
        "• `!currencies EUR`\n"
        "• `!chart BTC 30d`\n"
        "• `!chart BTC usd 30d 1h purple`\n\n"
        "To add an entry to your favorites, simply react with ❤️ to the bot's message (such as a price result or chart)."
    )

    # Send the appropriate version of the message based on the user's set language:
    await ctx.send(t(user_id, {"en": help_text_en, "pl": help_text_pl}))


@bot.event
async def on_command_error(ctx, error):
    user_id = ctx.author.id
    if isinstance(error, commands.CommandNotFound):
        # Handling an unknown command
        await ctx.send(
            t(
                user_id,
                {
                    "en": f"⚠️ Unknown command: `{ctx.message.content}`. Use `!help` or `!pomoc` to see the list of available commands.",
                    "pl": f"⚠️ Nieznana komenda: `{ctx.message.content}`. Użyj `!pomoc` lub `!help`, aby zobaczyć listę dostępnych komend.",
                },
            )
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        # Handling missing required arguments
        await ctx.send(
            t(
                user_id,
                {
                    "en": f"⚠️ Missing required arguments in command `{ctx.command}`. Check the correct usage with `!help`.",
                    "pl": f"⚠️ Brakuje wymaganych argumentów w komendzie `{ctx.command}`. Sprawdź poprawne użycie za pomocą `!pomoc`.",
                },
            )
        )
    elif isinstance(error, commands.BadArgument):
        # Handling an invalid argument
        await ctx.send(
            t(
                user_id,
                {
                    "en": f"⚠️ Invalid argument in command `{ctx.command}`. Check the correct usage with `!help`.",
                    "pl": f"⚠️ Błędny argument w komendzie `{ctx.command}`. Sprawdź poprawne użycie za pomocą `!pomoc`.",
                },
            )
        )
    else:
        # General errors
        await ctx.send(
            t(
                user_id,
                {
                    "en": f"⚠️ An error occurred: {error}",
                    "pl": f"⚠️ Wystąpił błąd: {error}",
                },
            )
        )


if __name__ == "__main__":
    logging.info("Bot starting...")
    logging.info(TOKEN)
    bot.run(TOKEN)
