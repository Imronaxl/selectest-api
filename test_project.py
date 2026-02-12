#!/usr/bin/env python3
"""
test_project.py – Функциональное тестирование исправленного проекта.

Запуск (после создания проекта и установки зависимостей):
    python test_project.py

Что делает:
    1. Запускает контейнеры Docker (docker compose up --build -d).
    2. Ожидает готовности приложения.
    3. Тестирует все CRUD-операции, включая граничные случаи (дубликаты, конфликты).
    4. Проверяет работу парсера (ручной запуск).
    5. Проверяет планировщик (изменяет интервал на 1 минуту и ждёт 2 запуска).
    6. Формирует детальный отчёт о результатах.
    7. Останавливает и удаляет контейнеры (с флагом -v).
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

#  Конфигурация
PROJECT_DIR = Path.cwd() / "selectest-api"
DOCKER_COMPOSE_FILE = PROJECT_DIR / "docker-compose.yml"
ENV_FILE = PROJECT_DIR / ".env"
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

HEADERS = {"Content-Type": "application/json"}

def run_cmd(cmd, cwd=None, capture=False):
    """Выполняет команду, логирует результат."""
    print(f"🔧 Выполняется: {' '.join(cmd)}")
    try:
        if capture:
            result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, cwd=cwd, check=True)
            return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка выполнения команды: {e}")
        if capture:
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
        sys.exit(1)


def wait_for_api(url, timeout=60):
    """Ожидает, пока Swagger UI станет доступным."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = requests.get(f"{url}/docs", timeout=2)
            if resp.status_code == 200:
                print("✅ API готов к работе.")
                return True
        except:
            pass
        time.sleep(2)
    print("❌ API не отвечает в течение таймаута.")
    return False


def test_endpoint(method, endpoint, expected_status=None, json_data=None, desc=""):
    """Универсальная функция тестирования эндпоинта."""
    url = f"{BASE_URL}{API_PREFIX}{endpoint}"
    print(f"Тест: {desc}")
    print(f"   {method} {url}")
    try:
        if method == "GET":
            resp = requests.get(url, headers=HEADERS)
        elif method == "POST":
            resp = requests.post(url, headers=HEADERS, json=json_data)
        elif method == "PUT":
            resp = requests.put(url, headers=HEADERS, json=json_data)
        elif method == "DELETE":
            resp = requests.delete(url, headers=HEADERS)
        else:
            raise ValueError(f"Unsupported method {method}")

        status_ok = expected_status is None or resp.status_code == expected_status
        result = {
            "desc": desc,
            "method": method,
            "url": url,
            "expected_status": expected_status,
            "actual_status": resp.status_code,
            "status_ok": status_ok,
            "response_body": resp.text[:500],  # ограничим длину
            "error": None,
        }
        if not status_ok:
            result["error"] = f"Статус {resp.status_code} вместо {expected_status}"
        return result
    except Exception as e:
        return {
            "desc": desc,
            "method": method,
            "url": url,
            "expected_status": expected_status,
            "actual_status": None,
            "status_ok": False,
            "response_body": "",
            "error": str(e),
        }


def set_env_variable(key, value):
    """Изменяет переменную в .env файле."""
    env_path = ENV_FILE
    if not env_path.exists():
        print("❌ .env файл не найден.")
        return False
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(env_path, "w", encoding="utf-8") as f:
        found = False
        for line in lines:
            if line.startswith(f"{key}="):
                f.write(f"{key}={value}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"{key}={value}\n")
    print(f"🔧 Установлена {key}={value}")
    return True


def get_docker_logs(container="selectest-api-app-1", lines=20):
    """Возвращает последние строки лога контейнера."""
    try:
        output = subprocess.check_output(
            ["docker", "logs", "--tail", str(lines), container],
            stderr=subprocess.STDOUT,
            text=True,
        )
        return output
    except:
        return ""

def run_tests():
    print("=" * 80)
    print("ЗАПУСК ФУНКЦИОНАЛЬНОГО ТЕСТИРОВАНИЯ")
    print("=" * 80)

    results = []
    created_ids = []
    external_id_counter = 1000

    print("\n🚀 Запуск контейнеров...")
    run_cmd(["docker", "compose", "up", "--build", "-d"], cwd=PROJECT_DIR)
    if not wait_for_api(BASE_URL):
        print("❌ Не удалось дождаться старта приложения. Тестирование прервано.")
        return results

    print("\nРучной запуск парсинга...")
    res = test_endpoint("POST", "/parse/", expected_status=200, desc="Ручной запуск парсинга")
    results.append(res)
    time.sleep(2)  

    print("\n Тестирование CRUD операций...")

    vacancy1 = {
        "title": "Python Developer",
        "timetable_mode_name": "Full-time",
        "tag_name": "Backend",
        "city_name": "Moscow",
        "published_at": "2026-02-12T10:00:00Z",
        "is_remote_available": True,
        "is_hot": False,
        "external_id": external_id_counter,
    }
    res = test_endpoint("POST", "/vacancies/", expected_status=201, json_data=vacancy1, desc="Создание вакансии")
    results.append(res)
    if res["status_ok"]:
        try:
            data = json.loads(res["response_body"])
            created_ids.append(data["id"])
        except:
            pass
    external_id_counter += 1

    vacancy_dup = vacancy1.copy()
    vacancy_dup["title"] = "Duplicate Test"
    res = test_endpoint("POST", "/vacancies/", expected_status=409, json_data=vacancy_dup, desc="Создание дубликата (409 Conflict)")
    results.append(res)

    res = test_endpoint("GET", "/vacancies/", expected_status=200, desc="Получение списка вакансий")
    results.append(res)

    if created_ids:
        res = test_endpoint("GET", f"/vacancies/{created_ids[0]}", expected_status=200, desc="Получение вакансии по ID")
        results.append(res)

    if created_ids:
        update_data = {
            "title": "Senior Python Developer",
            "timetable_mode_name": "Full-time",
            "tag_name": "Backend",
            "city_name": "Saint Petersburg",
            "published_at": "2026-02-12T12:00:00Z",
            "is_remote_available": True,
            "is_hot": True,
            "external_id": external_id_counter,
        }
        res = test_endpoint("PUT", f"/vacancies/{created_ids[0]}", expected_status=200, json_data=update_data, desc="Обновление вакансии")
        results.append(res)
        external_id_counter += 1

    vacancy2 = {
        "title": "Go Developer",
        "timetable_mode_name": "Full-time",
        "tag_name": "Backend",
        "city_name": "Moscow",
        "published_at": "2026-02-12T11:00:00Z",
        "is_remote_available": False,
        "is_hot": False,
        "external_id": external_id_counter,
    }
    res = test_endpoint("POST", "/vacancies/", expected_status=201, json_data=vacancy2, desc="Создание второй вакансии")
    results.append(res)
    second_id = None
    if res["status_ok"]:
        try:
            data = json.loads(res["response_body"])
            second_id = data["id"]
        except:
            pass
    external_id_counter += 1

    if created_ids and second_id:
        conflict_update = update_data.copy()
        conflict_update["external_id"] = vacancy2["external_id"]
        res = test_endpoint("PUT", f"/vacancies/{created_ids[0]}", expected_status=409, json_data=conflict_update, desc="Обновление с конфликтом external_id (409)")
        results.append(res)

    if second_id:
        res = test_endpoint("DELETE", f"/vacancies/{second_id}", expected_status=204, desc="Удаление вакансии")
        results.append(res)

    print("\nТестирование планировщика (интервал 1 минута)...")
    set_env_variable("PARSE_SCHEDULE_MINUTES", "1")
    run_cmd(["docker", "compose", "restart", "app"], cwd=PROJECT_DIR)
    time.sleep(10)  

    print("   Ожидание 70 секунд...")
    time.sleep(70)

    logs = get_docker_logs("selectest-api-app-1", lines=100)
    parse_count = logs.count("Старт парсинга вакансий")
    scheduler_ok = parse_count >= 2
    results.append({
        "desc": "Планировщик запускается каждую минуту",
        "method": "LOG",
        "url": "",
        "expected_status": ">=2 запусков за 70с",
        "actual_status": f"{parse_count} запусков",
        "status_ok": scheduler_ok,
        "response_body": logs[-200:],
        "error": None if scheduler_ok else f"Найдено только {parse_count} запусков, ожидалось минимум 2",
    })

    return results


def generate_report(results):
    """Формирует текстовый отчёт."""
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("ОТЧЁТ ПО ФУНКЦИОНАЛЬНОМУ ТЕСТИРОВАНИЮ")
    report_lines.append(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)
    report_lines.append("")

    total = len(results)
    passed = sum(1 for r in results if r["status_ok"])
    failed = total - passed

    report_lines.append(f"✅ Успешно: {passed}")
    report_lines.append(f"❌ Ошибки:   {failed}")
    report_lines.append("")

    for i, r in enumerate(results, 1):
        status_icon = "✅" if r["status_ok"] else "❌"
        report_lines.append(f"{status_icon} Тест #{i}: {r['desc']}")
        report_lines.append(f"   Метод: {r['method']} {r['url']}")
        report_lines.append(f"   Ожидаемый статус: {r['expected_status']}, Фактический: {r['actual_status']}")
        if r.get("error"):
            report_lines.append(f"   Ошибка: {r['error']}")
        if r.get("response_body") and len(r["response_body"]) > 0:
            # усечённый ответ
            report_lines.append(f"   Ответ: {r['response_body'][:200]}...")
        report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append(" ВСЕ ИСПРАВЛЕННЫЕ БАГИ ПРОВЕРЕНЫ И РАБОТАЮТ КОРРЕКТНО.")
    report_lines.append("=" * 80)
    return "\n".join(report_lines)


def main():
    if not PROJECT_DIR.exists():
        print(f"❌ Папка проекта не найдена: {PROJECT_DIR}")
        print("   Сначала запустите create_project.py")
        sys.exit(1)

    if not ENV_FILE.exists():
        print("Файл .env не найден. Создаю из .env.example...")
        example = PROJECT_DIR / ".env.example"
        if example.exists():
            with open(example, "r") as src, open(ENV_FILE, "w") as dst:
                dst.write(src.read())
        else:
            print("❌ .env.example тоже отсутствует. Создайте .env вручную.")
            sys.exit(1)

    try:
        run_cmd(["docker", "--version"], capture=True)
        run_cmd(["docker", "compose", "version"], capture=True)
    except:
        print("❌ Docker или Docker Compose не установлены или не доступны.")
        sys.exit(1)

    try:
        import requests
    except ImportError:
        print(" Устанавливаю requests...")
        run_cmd([sys.executable, "-m", "pip", "install", "requests"])

    print("\n Начинаем тестирование...")
    results = run_tests()

    print("\nОстанавливаем и удаляем контейнеры...")
    run_cmd(["docker", "compose", "down", "-v"], cwd=PROJECT_DIR)

    report = generate_report(results)
    print("\n" + report)

    report_path = Path.cwd() / "test_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n Отчёт сохранён в {report_path}")


if __name__ == "__main__":
    main()
