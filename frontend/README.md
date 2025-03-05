# Football Analyzer

Profesjonalne narzędzie do analizy meczów piłkarskich pod kątem zakładów bukmacherskich z wykorzystaniem zaawansowanych statystyk, modeli predykcyjnych oraz AI zintegrowanego z DeepSeek API.

## Funkcjonalności

- Automatyczne pobieranie i aktualizowanie danych o meczach piłkarskich
- Zaawansowane analizy statystyczne (xG, xA, PPDA, Model Poissona, Ranking Elo)
- Prognozowanie wyników z wykorzystaniem modeli ML i AI
- Analiza kursów bukmacherskich i identyfikacja value betów
- Wykrywanie trendów i anomalii w statystykach i kursach
- Generowanie raportów przedmeczowych przez AI
- Interaktywny dashboard z wykresami i tabelami
- Możliwość zadawania pytań do AI

## Architektura

- **Backend**: Python (FastAPI)
- **Frontend**: React.js
- **Baza danych**: SQLite (możliwość rozszerzenia do PostgreSQL)
- **AI**: Integracja z DeepSeek API
- **Konteneryzacja**: Docker

## Wymagania

- Docker i Docker Compose
- Klucz API do Football API (football-data.org)
- Klucz API do DeepSeek

## Instalacja

1. Sklonuj repozytorium:
   ```
   git clone https://github.com/twoje-konto/football-analyzer.git
   cd football-analyzer
   ```

2. Utwórz plik `.env` w katalogu `backend/` na podstawie pliku `.env.example`:
   ```
   cp backend/.env.example backend/.env
   ```

3. Edytuj plik `.env` i wprowadź swoje klucze API:
   ```
   FOOTBALL_API_KEY=your_football_api_key
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ```

4. Uruchom aplikację za pomocą Docker Compose:
   ```
   cd docker
   docker-compose up -d
   ```

5. Aplikacja będzie dostępna pod adresem http://localhost w przeglądarce.

## Rozwój lokalny

### Backend

1. Przejdź do katalogu backend:
   ```
   cd backend
   ```

2. Utwórz i aktywuj wirtualne środowisko:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Zainstaluj zależności:
   ```
   pip install -r requirements.txt
   ```

4. Uruchom serwer:
   ```
   uvicorn main:app --reload
   ```

5. Backend będzie dostępny pod adresem http://localhost:8000

### Frontend

1. Przejdź do katalogu frontend:
   ```
   cd frontend
   ```

2. Zainstaluj zależności:
   ```
   npm install
   ```

3. Uruchom serwer deweloperski:
   ```
   npm start
   ```

4. Frontend będzie dostępny pod adresem http://localhost:3000

## Dokumentacja API

Po uruchomieniu aplikacji, automatycznie generowana dokumentacja API jest dostępna pod adresem:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Źródła danych

Aplikacja wykorzystuje dane z następujących źródeł:
- Football-Data.co.uk (historyczne wyniki, statystyki)
- Football-Data.org API (wyniki, tabele, terminarze)
- WhoScored/FBref/SofaScore (zaawansowane statystyki)
- The Odds API (kursy bukmacherskie)

## Struktura projektu

```
football-analyzer/
├── backend/               # Kod backendu (FastAPI)
│   ├── app/               # Główny kod aplikacji
│   │   ├── api/           # Endpointy API
│   │   ├── core/          # Podstawowe funkcjonalności, konfiguracja
│   │   ├── db/            # Definicje bazy danych
│   │   ├── models/        # Modele danych
│   │   ├── services/      # Usługi/Serwisy
│   │   └── utils/         # Funkcje pomocnicze
│   ├── tests/             # Testy 
│   ├── .env               # Zmienne środowiskowe
│   └── main.py            # Punkt wejścia aplikacji
│
├── frontend/              # Kod frontendu (React)
│   ├── public/            # Pliki statyczne
│   ├── src/               # Kod źródłowy React
│   │   ├── components/    # Komponenty UI
│   │   ├── pages/         # Strony
│   │   ├── services/      # Serwisy do komunikacji z API
│   │   └── utils/         # Funkcje pomocnicze
│   └── package.json       # Konfiguracja npm
│
├── docker/                # Pliki Docker 
│   ├── docker-compose.yml # Konfiguracja docker-compose
│   ├── Dockerfile.backend # Dockerfile dla backendu
│   ├── Dockerfile.frontend # Dockerfile dla frontendu
│   └── nginx.conf         # Konfiguracja nginx
│
└── README.md              # Dokumentacja
```

## Licencja

Ten projekt jest prywatny i przeznaczony do użytku osobistego.

## Autor

Twoje imię i nazwisko