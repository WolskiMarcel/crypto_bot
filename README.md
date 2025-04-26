
# CRC-CryptoBot

CRC-Crypto Bot to bot Discord napisany w Pythonie, który integruje się z API Binance i Frankfurter oferując szereg komend pomocnych w codziennych finansach. Dodatkowo z opcjami dodawania do ulubionych i to w dwóch językach.

## Funkcje

- **Generowanie wykresów:**  
  Komenda `!wykres` umożliwia generowanie wykresów na podstawie wybranych symboli (np. BTC, ETH) i okresów.
  
- **Wyświetlanie cen:**  
  Komenda `!price` pokazuje aktualną cenę kryptowaluty w wybranej walucie.
  
- **Obsługa ulubionych:**  
  Dodaj ulubione wpisy za pomocą reakcji ❤️ – ulubione są zapisywane i później wyświetlane przez komendę `!ulubione`.

- **Zmiana języka:**  
  Komenda `!lang` lub `!jezyk` pozwala ustawiać preferowany język (np. `!lang pl`).

- **Konfiguracja walut:**  
  Komenda `!waluta` umożliwia ustawienie preferowanej waluty.

## Wymagania

- Python 3.8 lub nowszy
- [discord.py](https://pypi.org/project/discord.py/)
- [requests](https://pypi.org/project/requests/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- Inne narzędzia do testów: pytest

## Instalacja i Uruchomienie

1. **Klonowanie repozytorium**

   ```bash
   git clone https://github.com/WolskiMarcel/crypto_bot.git
   cd crc-crypto_bot
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
   export NASA_API_KEY="twoj_klucz_api"
   ```

5. **Uruchomienie bota**

   ```bash
   python src/app.py
   ```

## Testy

Testy jednostkowe zostały napisane przy użyciu modułu unittest oraz unittest.mock.

### Jak uruchamiać testy?

- **W PyCharmie:**  
  Wystarczy kliknąć na ikonę run/test przy pliku lub metodzie testowej, albo użyć opcji "Run All Tests" z panelu testów.

- **Z linii poleceń:**  
  Wejdź do katalogu głównego projektu i użyj:
  ```bash
  python -m unittest discover

## Docker

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

2. **Uruchomienie kontenera**

   Upewnij się, że zmienne środowiskowe są ustawione, np.:

   ```bash
   docker run -e D_TOKEN="twoj_token" -p 32025:32025 NAME:latest
   ```

## Wdrożenie w Kubernetes z Helm

Bot działa jako klient (inicjuje połączenia wychodzące), więc do wdrożenia wystarczy Deployment. Jeśli chcesz wymusić uruchomienie na konkretnym nodzie (np. `minipc1`), możesz użyć `nodeSelector` w manifeście Deployment.

Przykładowy fragment `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crc-bot
  labels:
    app: crc-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: crc-bot
  template:
    metadata:
      labels:
        app: crc-bot
    spec:
      containers:
        - name: crc-bot
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          env:
            - name: BOT_TOKEN
              value: "{{ .Values.env.BOT_TOKEN }}"
            - name: NASA_API_KEY
              value: "{{ .Values.env.NASA_API_KEY }}"
          ports:
            - containerPort: {{ .Values.service.port }}
```

## CI/CD – Azure Pipelines

Przykładowy pipeline Azure definiuje etapy:
- **Tests:** Tworzenie wirtualnego środowiska, instalacja zależności, uruchomienie testów i sprawdzenie kodu przy użyciu Black.
- **Docker:** Budowanie i wypychanie obrazu Dockera.
- **microk8s:** Wdrożenie Helm na klastrze.
- **GithubSync:** Synchronizacja repozytorium.

Fragment pipeline YAML (zobacz pełny kod w repozytorium):

```yaml
# [Przykładowa konfiguracja pipeline]
trigger:
  branches:
    include:
      - '*'
  
# Parametry, zmienne oraz etapy pipeline są zdefiniowane poniżej
# [Pełna konfiguracja pipeline w pliku azure-pipelines.yml]
```

## Kontrybucje

Jeśli chcesz przyczynić się do rozwoju projektu, proszę otwórz pull request lub zgłoś issue w repozytorium GitHub.


---

Dzięki tym instrukcjom będziesz mógł lokalnie rozwijać, testować i wdrażać CRC-NasaBot zarówno w środowisku Docker, jak i Kubernetes, a także zautomatyzować procesy CI/CD przy użyciu Azure Pipelines.
```