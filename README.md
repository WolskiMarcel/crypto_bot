# 🚀 *CRC CryptoBot*

Kurs z ramach programu *Corporate Readiness Certificate* od *ING HUBS POLAND* - *Kod na produkcji - od pisania
do wdrożenia oprogramowania*.

CRC-Crypto Bot to bot Discord napisany w Pythonie, który integruje się 
z [Binance API](https://binance-docs.github.io/apidocs/spot/en/) 
oraz [Frankfurter API](https://www.frankfurter.app/docs), 
oferując szereg komend przydatnych w codziennych finansach. Dodatkowo bot umożliwia dodawanie ulubionych wpisów i 
obsługuje dwujęzyczność!

## 📖 Spis Treści
- [🚀 CRC CryptoBot](#-crc-cryptobot)
- [🔗 Funkcje](#-funkcje)
- [🔧 Wymagania](#-wymagania)
- [⚙️ Instalacja i uruchomienie](#-instalacja-i-uruchomienie)
- [🧪 Testy](#-testy)
- [🐳 Docker](#-docker)
- [🔄⚙ CI/CD Pipelines](#-cicd-pipelines)
- [🛠 Kontrybucje](#-kontrybucje)
- [📜 Licencja](#-licencja)

## ![Funkcje](https://img.shields.io/badge/Features-Available-brightgreen?style=flat-square) Funkcje 🔗


- **Generowanie wykresów:**  
  **Opis:** Komenda `!wykres` pozwala na generowanie wykresów na podstawie wybranych symboli kryptowalut (np. BTC, ETH) oraz określonych przedziałów czasowych.  
  **Przykład użycia:**  
  - `!wykres BTC 1d` – generuje wykres dzienny dla Bitcoina.  
  **Technologia:** Wykresy tworzone są przy użyciu biblioteki matplotlib na podstawie danych pobieranych z Binance API.


- **Wyświetlanie cen:**  
  **Opis:** Komenda `!price` wyświetla aktualną cenę wybranej kryptowaluty w określonej walucie.  
  **Przykład użycia:**  
  - `!price ETH USD` – pokazuje aktualną cenę Ethereum w dolarach amerykańskich.  
  **Technologia:** Aktualne dane są pobierane bezpośrednio z Binance API.


- **Obsługa ulubionych:**  
  **Opis:** Użytkownik może dodać wpis do ulubionych reagując reakcją ❤️. Ulubione wpisy są zapisywane i później wyświetlane za pomocą komendy `!ulubione`.


- **Zmiana języka:**  
  **Opis:** Komenda `!lang` lub `!jezyk` pozwala na ustawienie preferowanego języka (np. `!lang pl` dla polskiego lub `!lang en` dla angielskiego).  
  **Cel:** Ułatwienie korzystania z bota użytkownikom z różnych regionów.


- **Konfiguracja waluty:**  
  **Opis:** Komenda `!waluta` umożliwia ustawienie preferowanej waluty, w której bot przedstawia ceny kryptowalut, co jest szczególnie przydatne przy międzynarodowym użyciu.

## ![Wymagania](https://img.shields.io/badge/Requirements-Python%203.13-important?style=flat-square) Wymagania 🔧

- Python 3.13 lub nowszy
- [discord.py](https://pypi.org/project/discord.py/)
- [requests](https://pypi.org/project/requests/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- Narzędzia do testów: pytest, black

## ![Instalacja i uruchamianie](https://img.shields.io/badge/Setup-Installation-red?style=flat-square) Instalacja i Uruchomienie ⚙️

1. **Klonowanie repozytorium**

   ```bash
   git clone https://github.com/WolskiMarcel/crypto_bot.git
   cd crypto_bot
   ```

2. **Utworzenie i aktywacja wirtualnego środowiska**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Na Windows: venv\Scripts\activate
   ```

3. **Instalacja zależności**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Konfiguracja zmiennych środowiskowych**

   **Token bota:**

   Upewnij się, że Twój token bota jest przechowywany w bezpieczny sposób (najlepiej jako zmienna środowiskowa lub umieszczony w pliku konfiguracyjnym, którego nie commitujesz do repozytorium).

   Na przykład, możesz utworzyć plik `.env` (jeśli używasz narzędzia do ładowania zmiennych, np. python-dotenv) lub ustawić zmienne ręcznie:

   ```bash
   export BOT_TOKEN="twoj_token"
   ```

5. **Uruchomienie bota**

   ```bash
   python src/app.py
   ```

## ![Tests](https://img.shields.io/badge/Tests-Passed-green?style=flat-square) Testy 🧪

Testy w CRC CryptoBocie mają na celu weryfikację, że kluczowe funkcje aplikacji działają poprawnie oraz że wprowadzone
zmiany nie powodują regresji. W projekcie stosujemy podejście testów jednostkowych oraz integracyjnych przy użyciu 
frameworków unittest, pytest, modułu unittest oraz unittest.mock.

Testy jednostkowe są definiowane w plikach rozpoczynających się od test_ (lub w katalogu tests/). Każdy plik zawiera 
zestaw testów, gdzie przy użyciu klas dziedziczących po unittest.TestCase definiujemy metody testowe.

Testy integracyjne sprawdzają współdziałanie różnych modułów aplikacji. Na przykład:

- **Połączenie z API:** 
czy funkcje komunikujące się z Binance API właściwie przetwarzają dane i reagują na błędy.
-  **Całościowe działanie komend:** 
uruchomienie sekwencji funkcji, które razem odpowiadają za 
wykonanie komendy bota, na przykład `!price` czy `!ulubione`.

Oprócz testów funkcjonalnych, w pipeline znajduje się również krok sprawdzający styl kodu za pomocą narzędzia Black. 
Dzięki temu mamy pewność, że kod jest spójny i czytelny, co ułatwia współpracę i utrzymanie projektu.

### Jak uruchamiać testy?

- **W PyCharmie:**  
  Wystarczy kliknąć na ikonę run/test przy pliku lub metodzie testowej, albo użyć opcji "Run All Tests" z panelu testów.

- **Z linii poleceń:**  
  Wejdź do katalogu głównego projektu i użyj:
  ```bash
  python -m unittest discover

## ![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker) Docker 🐳

Aplikację można zbudować i uruchomić w kontenerze Docker. Przykładowy plik `Dockerfile`:

```dockerfile
FROM python:3.9-slim
LABEL authors="marcello"

WORKDIR /src
COPY requirements.txt requirements.txt

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Create a user without administrative privileges and set the appropriate permissions for the /src directory
RUN useradd -m appuser && chown -R appuser:appuser /src

COPY . .
RUN rm Dockerfile

USER appuser
EXPOSE 32025

CMD [ "python", "app.py" ]
#CMD ["tail", "-f", "/dev/null"]
```

### Budowanie i uruchomienie kontenera

1. **Budowanie obrazu**

   ```bash
   docker build -t NAME:latest -f src/Dockerfile src/
   ```
    `-f src/Dockerfile` – wskazuje lokalizację pliku Dockerfile.

    `src/` – ustawia kontekst budowania (katalog, z którego kopiowane są pliki do obrazu).


2. **Uruchomienie kontenera**

   Upewnij się, że zmienne środowiskowe są ustawione, np.:

   ```bash
   docker run -e D_TOKEN="twoj_token" -p 32025:32025 NAME:latest
   ```

    `-e D_TOKEN="twoj_token"` – przekazuje zmienną środowiskową z tokenem bota.

    `-p 32025:32025` – przekierowuje porty, umożliwiając dostęp do aplikacji.

    `NAME:latest` – określa obraz, z którego kontener ma zostać uruchomiony.


## ![CI/CD](https://img.shields.io/badge/CI/CD-Automated-aquamarine) CI/CD – Azure Pipelines 🔄


CI/CD (Continuous Integration / Continuous Deployment) pozwala na automatyzację procesu budowania, 
testowania i wdrażania aplikacji, dzięki czemu zmiany w kodzie mogą być szybko i niezawodnie integrowane oraz 
dostarczane do środowiska produkcyjnego.

Ze względu na ograniczoną równoległość na hostowanych agentach Azure DevOps, zdecydowano o ręcznym wdrożeniu 
self-hosted agenta na maszynie wirtualnej (VM) w Azure. Aby zapewnić jego automatyczne działanie po restarcie maszyny, 
skonfigurowano usługę systemową (systemctl). Dzięki temu agent startuje samoistnie przy każdym uruchomieniu VM, 
umożliwiając stabilne i niezależne wykonywanie pipeline’ów CI/CD bez konieczności ręcznego uruchamiania procesu.

Utworzenie pliku usługi systemowej:
```bash
  sudo vim /etc/systemd/system/azure-agent.service
```
Dodajemy następującą konfigurację:
```yaml
[Unit]
Description=Azure DevOps Self-hosted Agent
After=network.target

[Service]
User=azureuser  # Użytkownik na VM, który uruchamia agenta
WorkingDirectory=/home/azureuser/myagent  # Ścieżka do katalogu agenta
ExecStart=/home/azureuser/myagent/run.sh
Restart=always
KillSignal=SIGINT

[Install]
WantedBy=multi-user.target
```
Należy załadować nową usługę i ją uruchomić.

```bash
    sudo systemctl daemon-reload
    sudo systemctl start azure-agent
    sudo systemctl status azure-agent
```
Aby agent automatyczne uruchamiał się po restarcie VM:

```bash
    sudo systemctl enable azure-agent
```

Przykładowy pipeline Azure definiuje etapy:
- **Tests:** Tworzenie wirtualnego środowiska, instalacja zależności, uruchomienie testów i sprawdzenie kodu przy użyciu Black.
- **Docker:** Budowanie i wypychanie obrazu Dockera.
- **GithubSync:** Synchronizacja repozytorium.

Fragment pipeline YAML (zobacz pełny kod w repozytorium):

```yaml
# [Przykładowa konfiguracja pipeline]
trigger:
  branches:
    include:
      - main
  
# Parametry, zmienne oraz etapy pipeline są zdefiniowane poniżej
# [Pełna konfiguracja pipeline w pliku azure-pipelines.yml]
```

## ![Contributing](https://img.shields.io/badge/Contributing-Welcome-brown) Konstrybucje 🛠

Jeśli chcesz przyczynić się do rozwoju projektu, proszę otwórz pull request lub zgłoś issue w repozytorium GitHub.

## ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square) License 📜

Projekt jest udostępniany na warunkach MIT License.

Co to oznacza?

- Możesz swobodnie używać, modyfikować i dystrybuować kod.

- Wymagana jest informacja o autorach projektu.

- Nie ponosimy odpowiedzialności za ewentualne szkody wynikające z użycia oprogramowania.

---

Dzięki tym instrukcjom będziesz mógł lokalnie rozwijać, testować i wdrażać crypto-bot'a w środowisku Docker, a także 
zautomatyzować procesy CI/CD przy użyciu Azure Pipelines.
```