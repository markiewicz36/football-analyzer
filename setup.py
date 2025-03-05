#!/usr/bin/env python3
"""
Skrypt do konfiguracji i uruchomienia aplikacji Football Analyzer.
Umożliwia łatwe uruchomienie zarówno backendu, frontendu jak i całego stosu za pomocą Dockera.
"""

import os
import sys
import subprocess
import shutil
import argparse
import platform
import webbrowser
import time
from pathlib import Path
import json


# Kolory dla lepszej czytelności w terminalu
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Określenie ścieżek projektu
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DOCKER_DIR = PROJECT_ROOT / "docker"
ENV_FILE = BACKEND_DIR / ".env"
ENV_EXAMPLE_FILE = BACKEND_DIR / ".env.example"


def print_header(text):
    """Wyświetla nagłówek sekcji w konsoli."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}\n")


def print_step(text):
    """Wyświetla krok w konsoli."""
    print(f"{Colors.CYAN}> {text}{Colors.ENDC}")


def print_success(text):
    """Wyświetla informację o sukcesie w konsoli."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_warning(text):
    """Wyświetla ostrzeżenie w konsoli."""
    print(f"{Colors.WARNING}! {text}{Colors.ENDC}")


def print_error(text):
    """Wyświetla błąd w konsoli."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def run_command(command, cwd=None, env=None, shell=False):
    """Uruchamia komendę w podproceskie i zwraca kod wyjścia."""
    try:
        # W systemie Windows używamy shell=True dla lepszej kompatybilności
        if platform.system() == "Windows":
            shell = True

        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'  # Zastępuj znaki, których nie można zdekodować
        )

        # Wyświetl output w czasie rzeczywistym
        for line in process.stdout:
            print(line, end='')

        # Poczekaj na zakończenie procesu
        process.wait()

        if process.returncode != 0:
            stderr = process.stderr.read()
            print_error(f"Komenda zakończyła się błędem (kod: {process.returncode}):")
            print(stderr)

        return process.returncode
    except Exception as e:
        print_error(f"Błąd podczas uruchamiania komendy: {e}")
        return 1


def check_docker():
    """Sprawdza czy Docker jest zainstalowany i uruchomiony."""
    print_step("Sprawdzanie czy Docker jest zainstalowany...")

    docker_cmd = "docker --version"
    returncode = run_command(docker_cmd.split(), shell=(platform.system() == "Windows"))

    if returncode != 0:
        print_error("Docker nie jest zainstalowany lub nie jest dostępny w PATH.")
        print_warning("Zainstaluj Docker ze strony: https://docs.docker.com/get-docker/")
        return False

    print_success("Docker jest zainstalowany.")

    # Sprawdź czy Docker działa
    print_step("Sprawdzanie czy Docker działa...")
    docker_run_cmd = "docker info"
    returncode = run_command(docker_run_cmd.split(), shell=(platform.system() == "Windows"))

    if returncode != 0:
        print_error("Docker jest zainstalowany, ale nie działa.")
        print_warning("Uruchom Docker Desktop lub serwis dockerd i spróbuj ponownie.")
        return False

    print_success("Docker działa poprawnie.")
    return True


def check_docker_compose():
    """Sprawdza czy Docker Compose jest zainstalowany."""
    print_step("Sprawdzanie czy Docker Compose jest zainstalowany...")

    # Najpierw sprawdź czy mamy nowszą wersję (docker compose)
    docker_compose_cmd = "docker compose version"
    returncode = run_command(docker_compose_cmd.split(), shell=(platform.system() == "Windows"))

    if returncode == 0:
        print_success("Docker Compose (nowa wersja) jest zainstalowany.")
        return "docker compose"

    # Jeśli nie, sprawdź starszą wersję (docker-compose)
    docker_compose_cmd = "docker-compose --version"
    returncode = run_command(docker_compose_cmd.split(), shell=(platform.system() == "Windows"))

    if returncode == 0:
        print_success("Docker Compose (starsza wersja) jest zainstalowany.")
        return "docker-compose"

    print_error("Docker Compose nie jest zainstalowany lub nie jest dostępny w PATH.")
    print_warning("Zainstaluj Docker Compose: https://docs.docker.com/compose/install/")
    return None


def check_env_file():
    """Sprawdza czy plik .env istnieje i zawiera wymagane zmienne."""
    print_step("Sprawdzanie pliku .env...")

    if not ENV_FILE.exists():
        print_warning(f"Plik {ENV_FILE} nie istnieje. Tworzenie na podstawie .env.example...")

        if not ENV_EXAMPLE_FILE.exists():
            print_error(f"Plik {ENV_EXAMPLE_FILE} nie istnieje. Tworzenie pustego pliku .env...")
            with open(ENV_FILE, 'w', encoding='utf-8') as f:
                f.write("# Football Analyzer environment variables\n\n")
                f.write("# API Keys\n")
                f.write("FOOTBALL_API_KEY=b93f3651b608893ee85e3748a8f6faf9\n")
                f.write("DEEPSEEK_API_KEY=sk-57ea962dbd774eaea8f624605a2c7117\n\n")
                f.write("# Database Configuration\n")
                f.write("DATABASE_URL=sqlite:///./football_analyzer.db\n\n")
                f.write("# Backend Server\n")
                f.write("HOST=0.0.0.0\n")
                f.write("PORT=8000\n")
                f.write("# Football API\n")
                f.write("FOOTBALL_API_BASE_URL=https://v3.football.api-sports.io\n")
                f.write(
                    "FOOTBALL_API_HEADERS={\"x-rapidapi-key\": \"${FOOTBALL_API_KEY}\", \"x-rapidapi-host\": \"v3.football.api-sports.io\"}\n\n")
                f.write("# DeepSeek AI API\n")
                f.write("DEEPSEEK_API_BASE_URL=https://api.deepseek.com\n")
        else:
            shutil.copy(ENV_EXAMPLE_FILE, ENV_FILE)
            print_success(f"Skopiowano {ENV_EXAMPLE_FILE} do {ENV_FILE}")

    # Sprawdź czy zawiera wymagane zmienne
    with open(ENV_FILE, 'r', encoding='utf-8', errors='replace') as f:
        env_content = f.read()

    missing_keys = []
    for key in ["FOOTBALL_API_KEY", "DEEPSEEK_API_KEY"]:
        if f"{key}=" in env_content and not f"{key}=your" in env_content.lower():
            # Klucz ma wartość inną niż przykładową
            continue
        else:
            missing_keys.append(key)

    if missing_keys:
        print_warning(f"W pliku .env brakuje wartości dla kluczy: {', '.join(missing_keys)}")

        update_env = input("\nCzy chcesz teraz podać wartości dla brakujących kluczy? (t/n): ").lower()
        if update_env.startswith('t'):
            with open(ENV_FILE, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            updated_lines = []
            for line in lines:
                updated = False
                for key in missing_keys:
                    if line.startswith(f"{key}="):
                        value = input(f"Podaj wartość dla {key}: ")
                        updated_lines.append(f"{key}={value}\n")
                        updated = True
                        break

                if not updated:
                    updated_lines.append(line)

            with open(ENV_FILE, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)

            print_success("Zaktualizowano plik .env")
        else:
            print_warning("Pamiętaj, aby zaktualizować plik .env przed uruchomieniem aplikacji.")
    else:
        print_success("Plik .env zawiera wszystkie wymagane klucze.")

    return True


def setup_backend_dev():
    """Konfiguruje środowisko deweloperskie dla backendu."""
    print_step("Konfigurowanie środowiska deweloperskiego dla backendu...")

    if not BACKEND_DIR.exists():
        print_error(f"Katalog {BACKEND_DIR} nie istnieje.")
        return False

    # Sprawdź czy venv istnieje, jeśli nie, stwórz go
    venv_dir = BACKEND_DIR / "venv"
    if not venv_dir.exists():
        print_step("Tworzenie wirtualnego środowiska Python...")

        venv_cmd = [sys.executable, "-m", "venv", str(venv_dir)]
        returncode = run_command(venv_cmd)

        if returncode != 0:
            print_error("Nie udało się utworzyć wirtualnego środowiska.")
            return False

        print_success("Utworzono wirtualne środowisko.")

    # Aktywuj venv i zainstaluj zależności
    print_step("Instalowanie zależności...")

    # Określ ścieżkę do aktywacji venv w zależności od systemu
    if platform.system() == "Windows":
        activate_script = venv_dir / "Scripts" / "activate.bat"
        pip_path = venv_dir / "Scripts" / "pip"
    else:
        activate_script = venv_dir / "bin" / "activate"
        pip_path = venv_dir / "bin" / "pip"

    # Zainstaluj zależności
    if platform.system() == "Windows":
        # W Windows musimy aktywować środowisko w ten sposób
        install_cmd = f"cmd /c {activate_script} && pip install -r requirements.txt"
        returncode = run_command(install_cmd, cwd=BACKEND_DIR, shell=True)
    else:
        # W Linux/Mac możemy użyć bezpośrednio pip z venv
        install_cmd = [str(pip_path), "install", "-r", "requirements.txt"]
        returncode = run_command(install_cmd, cwd=BACKEND_DIR)

    if returncode != 0:
        print_error("Nie udało się zainstalować zależności.")
        return False

    print_success("Zainstalowano zależności.")
    return True


def setup_frontend_dev():
    """Konfiguruje środowisko deweloperskie dla frontendu."""
    print_step("Konfigurowanie środowiska deweloperskiego dla frontendu...")

    if not FRONTEND_DIR.exists():
        print_error(f"Katalog {FRONTEND_DIR} nie istnieje.")
        return False

    # Sprawdź czy node_modules istnieje, jeśli nie, zainstaluj zależności
    node_modules_dir = FRONTEND_DIR / "node_modules"
    if not node_modules_dir.exists():
        print_step("Instalowanie zależności npm...")

        npm_cmd = "npm install"
        returncode = run_command(npm_cmd.split(), cwd=FRONTEND_DIR, shell=(platform.system() == "Windows"))

        if returncode != 0:
            print_error("Nie udało się zainstalować zależności npm.")
            print_warning("Upewnij się, że masz zainstalowany Node.js i npm.")
            return False

        print_success("Zainstalowano zależności npm.")
    else:
        print_success("Zależności npm są już zainstalowane.")

    return True


def run_backend_dev():
    """Uruchamia backend w trybie deweloperskim."""
    print_step("Uruchamianie backendu w trybie deweloperskim...")

    # Określ ścieżkę do aktywacji venv i uvicorn w zależności od systemu
    if platform.system() == "Windows":
        activate_script = BACKEND_DIR / "venv" / "Scripts" / "activate.bat"
        run_cmd = f"cmd /c {activate_script} && uvicorn main:app --reload"
    else:
        uvicorn_path = BACKEND_DIR / "venv" / "bin" / "uvicorn"
        run_cmd = f"{uvicorn_path} main:app --reload"

    print_warning("Backend zostanie uruchomiony w trybie deweloperskim. Naciśnij Ctrl+C, aby zatrzymać.")
    print_success("Backend będzie dostępny pod adresem: http://localhost:8000")

    returncode = run_command(run_cmd, cwd=BACKEND_DIR, shell=(platform.system() == "Windows"))

    if returncode != 0:
        print_error("Backend zakończył działanie z błędem.")
        return False

    return True


def run_frontend_dev():
    """Uruchamia frontend w trybie deweloperskim."""
    print_step("Uruchamianie frontendu w trybie deweloperskim...")

    npm_cmd = "npm start"

    print_warning("Frontend zostanie uruchomiony w trybie deweloperskim. Naciśnij Ctrl+C, aby zatrzymać.")
    print_success("Frontend będzie dostępny pod adresem: http://localhost:3000")

    # Uruchom npm start
    returncode = run_command(npm_cmd.split(), cwd=FRONTEND_DIR, shell=(platform.system() == "Windows"))

    if returncode != 0:
        print_error("Frontend zakończył działanie z błędem.")
        return False

    return True


def run_docker():
    """Uruchamia aplikację z użyciem Docker Compose."""
    print_step("Uruchamianie aplikacji z użyciem Docker...")

    # Sprawdź czy docker-compose.yml istnieje
    docker_compose_file = DOCKER_DIR / "docker-compose.yml"
    if not docker_compose_file.exists():
        print_error(f"Plik {docker_compose_file} nie istnieje.")
        return False

    # Sprawdź, czy requirements.txt istnieje
    requirements_file = BACKEND_DIR / "requirements.txt"
    if not requirements_file.exists():
        print_warning(f"Plik {requirements_file} nie istnieje, tworzę go...")
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write("fastapi==0.104.1\n")
            f.write("uvicorn==0.23.2\n")
            f.write("python-dotenv==1.0.0\n")
            f.write("httpx==0.25.0\n")
            f.write("SQLAlchemy==2.0.23\n")
            f.write("pydantic==2.4.2\n")
            f.write("pandas==2.1.1\n")
            f.write("numpy==1.26.0\n")
            f.write("scikit-learn==1.3.2\n")
            f.write("matplotlib==3.8.0\n")
            f.write("seaborn==0.13.0\n")
            f.write("beautifulsoup4==4.12.2\n")
            f.write("aiohttp==3.8.6\n")
            f.write("aiofiles==23.2.1\n")
            f.write("jinja2==3.1.2\n")
            f.write("pytest==7.4.3\n")
            f.write("celery==5.3.4\n")
            f.write("pymongo==4.5.0\n")
            f.write("requests==2.31.0\n")
            f.write("python-multipart==0.0.6\n")
            f.write("SQLAlchemy-Utils==0.41.1\n")
    else:
        # Sprawdź kodowanie pliku requirements.txt
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # Jeśli doszliśmy tutaj, kodowanie jest prawidłowe
        except UnicodeDecodeError:
            print_warning(f"Plik {requirements_file} ma nieprawidłowe kodowanie, naprawiam...")
            try:
                # Spróbuj odczytać z różnymi kodowaniami
                encodings = ['latin1', 'cp1252', 'ascii']
                content = None
                for encoding in encodings:
                    try:
                        with open(requirements_file, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue

                if content:
                    # Zapisz plik z poprawnym kodowaniem UTF-8
                    with open(requirements_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    # Jeśli się nie udało, utwórz nowy plik
                    with open(requirements_file, 'w', encoding='utf-8') as f:
                        f.write("fastapi==0.104.1\n")
                        f.write("uvicorn==0.23.2\n")
                        f.write("python-dotenv==1.0.0\n")
                        f.write("httpx==0.25.0\n")
                        f.write("SQLAlchemy==2.0.23\n")
                        f.write("pydantic==2.4.2\n")
                        f.write("pandas==2.1.1\n")
                        f.write("numpy==1.26.0\n")
                        f.write("scikit-learn==1.3.2\n")
                        f.write("matplotlib==3.8.0\n")
                        f.write("seaborn==0.13.0\n")
                        f.write("beautifulsoup4==4.12.2\n")
                        f.write("aiohttp==3.8.6\n")
                        f.write("aiofiles==23.2.1\n")
                        f.write("jinja2==3.1.2\n")
                        f.write("pytest==7.4.3\n")
                        f.write("celery==5.3.4\n")
                        f.write("pymongo==4.5.0\n")
                        f.write("requests==2.31.0\n")
                        f.write("python-multipart==0.0.6\n")
                        f.write("SQLAlchemy-Utils==0.41.1\n")
            except Exception as e:
                print_error(f"Nie udało się naprawić pliku requirements.txt: {str(e)}")
                return False

    # Sprawdź czy main.py istnieje
    main_file = BACKEND_DIR / "main.py"
    if not main_file.exists():
        print_warning(f"Plik {main_file} nie istnieje, przeszukuję katalog backend...")
        # Spróbujmy znaleźć plik main.py w podkatalogach backend
        found_main = None
        for path in BACKEND_DIR.glob("**/main.py"):
            found_main = path
            break

        if found_main:
            print_warning(f"Znaleziono plik main.py w lokalizacji {found_main}, kopiuję do {main_file}")
            # Utwórz kopię pliku main.py w głównym katalogu backendu
            shutil.copy(found_main, main_file)
        else:
            print_warning(f"Nie znaleziono pliku main.py, tworzę minimalny plik...")
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write('import uvicorn\n')
                f.write('from fastapi import FastAPI\n\n')
                f.write('app = FastAPI(title="Football Analyzer")\n\n')
                f.write('@app.get("/")\n')
                f.write('async def root():\n')
                f.write('    return {"message": "Football Analyzer API is running"}\n\n')
                f.write('if __name__ == "__main__":\n')
                f.write('    uvicorn.run("main:app", host="0.0.0.0", port=8000)\n')

    # Sprawdź czy struktura katalogów backendu jest poprawna
    app_dir = BACKEND_DIR / "app"
    if not app_dir.exists():
        print_warning(f"Katalog {app_dir} nie istnieje, tworzę go...")
        app_dir.mkdir(exist_ok=True)

        # Utwórz plik __init__.py w katalogu app
        init_file = app_dir / "__init__.py"
        if not init_file.exists():
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('# Football Analyzer App\n')

    # Wybierz odpowiednią komendę na podstawie sprawdzenia
    docker_compose_cmd = check_docker_compose()
    if not docker_compose_cmd:
        return False

    # Przejdź do katalogu projektu przed uruchomieniem docker-compose
    os.chdir(PROJECT_ROOT)

    # Uruchom docker-compose up
    print_step("Uruchamianie kontenerów Docker...")

    if docker_compose_cmd == "docker compose":
        up_cmd = f"docker compose -f {docker_compose_file} up -d --build"
    else:
        up_cmd = f"docker-compose -f {docker_compose_file} up -d --build"

    if platform.system() == "Windows":
        returncode = run_command(up_cmd, shell=True)
    else:
        returncode = run_command(up_cmd.split())

    if returncode != 0:
        print_error("Nie udało się uruchomić kontenerów Docker.")
        return False

    print_success("Kontenery Docker zostały uruchomione pomyślnie.")
    print_success("Aplikacja będzie dostępna pod adresem: http://localhost")

    # Otwórz przeglądarkę z aplikacją po krótkim czasie oczekiwania
    print_step("Otwieranie aplikacji w przeglądarce za 5 sekund...")
    time.sleep(5)
    webbrowser.open("http://localhost")

    return True


def stop_docker():
    """Zatrzymuje kontenery uruchomione przez Docker Compose."""
    print_step("Zatrzymywanie kontenerów Docker...")

    # Wybierz odpowiednią komendę na podstawie sprawdzenia
    docker_compose_cmd = check_docker_compose()
    if not docker_compose_cmd:
        return False

    # Zatrzymaj kontenery
    docker_compose_file = DOCKER_DIR / "docker-compose.yml"

    if docker_compose_cmd == "docker compose":
        down_cmd = f"docker compose -f {docker_compose_file} down"
    else:
        down_cmd = f"docker-compose -f {docker_compose_file} down"

    if platform.system() == "Windows":
        returncode = run_command(down_cmd, shell=True)
    else:
        returncode = run_command(down_cmd.split())

    if returncode != 0:
        print_error("Nie udało się zatrzymać kontenerów Docker.")
        return False

    print_success("Kontenery Docker zostały zatrzymane pomyślnie.")
    return True


def main():
    """Główna funkcja programu."""
    parser = argparse.ArgumentParser(description="Skrypt do konfiguracji i uruchamiania aplikacji Football Analyzer")

    # Dodaj argumenty
    subparsers = parser.add_subparsers(dest="command", help="Komenda do wykonania")

    # Komenda setup
    setup_parser = subparsers.add_parser("setup", help="Konfiguruje środowisko")
    setup_parser.add_argument("--backend", action="store_true", help="Konfiguruje tylko backend")
    setup_parser.add_argument("--frontend", action="store_true", help="Konfiguruje tylko frontend")

    # Komenda run
    run_parser = subparsers.add_parser("run", help="Uruchamia aplikację")
    run_parser.add_argument("--backend", action="store_true", help="Uruchamia tylko backend")
    run_parser.add_argument("--frontend", action="store_true", help="Uruchamia tylko frontend")
    run_parser.add_argument("--docker", action="store_true", help="Uruchamia w Dockerze")

    # Komenda stop
    stop_parser = subparsers.add_parser("stop", help="Zatrzymuje aplikację")
    stop_parser.add_argument("--docker", action="store_true", help="Zatrzymuje kontenery Docker")

    # Parsuj argumenty
    args = parser.parse_args()

    # Banner
    print(f"""
{Colors.BLUE}{Colors.BOLD}
  █████▒ ▒█████   ▒█████  ▄▄▄█████▓ ▄▄▄▄    ▄▄▄       ██▓     ██▓    
▓██   ▒ ▒██▒  ██▒▒██▒  ██▒▓  ██▒ ▓▒▓█████▄ ▒████▄    ▓██▒    ▓██▒    
▒████ ░ ▒██░  ██▒▒██░  ██▒▒ ▓██░ ▒░▒██▒ ▄██▒██  ▀█▄  ▒██░    ▒██░    
░▓█▒  ░ ▒██   ██░▒██   ██░░ ▓██▓ ░ ▒██░█▀  ░██▄▄▄▄██ ▒██░    ▒██░    
░▒█░    ░ ████▓▒░░ ████▓▒░  ▒██▒ ░ ░▓█  ▀█▓ ▓█   ▓██▒░██████▒░██████▒
 ▒ ░    ░ ▒░▒░▒░ ░ ▒░▒░▒░   ▒ ░░   ░▒▓███▀▒ ▒▒   ▓▒█░░ ▒░▓  ░░ ▒░▓  ░
 ░        ░ ▒ ▒░   ░ ▒ ▒░     ░    ▒░▒   ░   ▒   ▒▒ ░░ ░ ▒  ░░ ░ ▒  ░
 ░ ░    ░ ░ ░ ▒  ░ ░ ░ ▒    ░       ░    ░   ░   ▒     ░ ░     ░ ░   
          ░ ░      ░ ░              ░            ░  ░    ░  ░    ░  ░
                                         ░                           
░██▄▄▄▄██ ▓██▒  ▐▌██▒░██▄▄▄▄██ ▒██░    ░ ▐██▓░  ▄▀▒   ░▒▓█  ▄ ▒██▀▀█▄  
  ▓█   ▓██▒▒██░   ▓██░ ▓█   ▓██▒░██████▒░ ██▒▓░▒███████▒░▒████▒░██▓ ▒██▒
  ▒▒   ▓▒█░░ ▒░   ▒ ▒  ▒▒   ▓▒█░░ ▒░▓  ░ ██▒▒▒ ░▒▒ ▓░▒░▒░░ ▒░ ░░ ▒▓ ░▒▓░
   ▒   ▒▒ ░░ ░░   ░ ▒░  ▒   ▒▒ ░░ ░ ▒  ▓██ ░▒░ ░░▒ ▒ ░ ▒ ░ ░  ░  ░▒ ░ ▒░
   ░   ▒      ░   ░ ░   ░   ▒     ░ ░  ▒ ▒ ░░  ░ ░ ░ ░ ░   ░     ░░   ░ 
       ░  ░         ░       ░  ░    ░  ░ ░       ░ ░       ░  ░   ░     
                                       ░ ░     ░                       
{Colors.ENDC}
""")

    # Jeśli nie podano komendy, wyświetl menu
    if not args.command:
        print("Wybierz opcję:")
        print(f"  {Colors.CYAN}1.{Colors.ENDC} Konfiguracja środowiska")
        print(f"  {Colors.CYAN}2.{Colors.ENDC} Uruchom aplikację w Dockerze")
        print(f"  {Colors.CYAN}3.{Colors.ENDC} Uruchom backend (tryb dev)")
        print(f"  {Colors.CYAN}4.{Colors.ENDC} Uruchom frontend (tryb dev)")
        print(f"  {Colors.CYAN}5.{Colors.ENDC} Zatrzymaj kontenery Docker")
        print(f"  {Colors.CYAN}0.{Colors.ENDC} Wyjście")

        choice = input("\nTwój wybór: ")

        if choice == "1":
            args.command = "setup"
            args.backend = False
            args.frontend = False
        elif choice == "2":
            args.command = "run"
            args.docker = True
            args.backend = False
            args.frontend = False
        elif choice == "3":
            args.command = "run"
            args.backend = True
            args.frontend = False
            args.docker = False
        elif choice == "4":
            args.command = "run"
            args.frontend = True
            args.backend = False
            args.docker = False
        elif choice == "5":
            args.command = "stop"
            args.docker = True
        elif choice == "0":
            print("Do widzenia!")
            sys.exit(0)
        else:
            print_error("Nieprawidłowy wybór.")
            sys.exit(1)
    elif args.command == "setup" and not hasattr(args, "backend"):
        args.backend = False
        args.frontend = False
    elif args.command == "run" and not hasattr(args, "backend"):
        args.backend = False
        args.frontend = False
        args.docker = False

    # Wykonaj odpowiednią komendę
    if args.command == "setup":
        print_header("Konfiguracja środowiska")

        # Jeśli nie podano konkretnych flag, skonfiguruj wszystko
        if not (args.backend or args.frontend):
            args.backend = True
            args.frontend = True

        # Zawsze sprawdź plik .env
        check_env_file()

        if args.backend:
            setup_backend_dev()

        if args.frontend:
            setup_frontend_dev()

        print_success("Konfiguracja zakończona.")

    elif args.command == "run":
        print_header("Uruchamianie aplikacji")

        # Jeśli nie podano konkretnych flag, uruchom w Dockerze
        if not (args.backend or args.frontend or args.docker):
            args.docker = True

        if args.docker:
            # Sprawdź czy Docker jest zainstalowany i działa
            if not check_docker():
                sys.exit(1)

            # Sprawdź czy plik .env jest poprawny
            check_env_file()

            # Uruchom w Dockerze
            run_docker()
        else:
            if args.backend:
                # Sprawdź czy plik .env jest poprawny
                check_env_file()
                run_backend_dev()

            if args.frontend:
                run_frontend_dev()

    elif args.command == "stop":
        print_header("Zatrzymywanie aplikacji")

        if args.docker or not any(vars(args).values()):
            # Sprawdź czy Docker jest zainstalowany i działa
            if not check_docker():
                sys.exit(1)

            # Zatrzymaj kontenery Docker
            stop_docker()
        else:
            print_warning("Nie podano, co zatrzymać. Użyj --docker, aby zatrzymać kontenery Docker.")

    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika.")
        sys.exit(0)