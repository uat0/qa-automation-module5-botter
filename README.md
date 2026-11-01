# Автоматизация тестирования DemoQA

Практическая работа по модулю 5. Боттер Вадим Валерьевич, ПКТб-23-1.

Объект: [Practice Form](https://demoqa.com/automation-practice-form) из модуля 4 и [Book Store API](https://demoqa.com/swagger/).

Проект содержит 42 Unit-проверки, 7 API-проверок, 17 UI-проверок и 2 BDD-сценария. Unit-тесты проверяют собственные эталонные валидаторы из `app/`, а не исходный код DemoQA. Покрытие `app/` не означает покрытие кода сайта.

## Запуск

Требуется Python 3.12, Git, Java 21 и Node.js 22 для генератора Allure 2.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --index-url https://pypi-mirror.gitverse.ru/simple/ -r requirements.txt
python -m playwright install chromium firefox
npm install --global allure-commandline@2.46.1
python scripts/run_suite.py --run run01
python scripts/run_suite.py --run run02
python scripts/run_suite.py --run firefox01 --browser firefox
allure open results/allure-report
```

На Linux/macOS: `source .venv/bin/activate`; для браузеров CI используйте `python -m playwright install --with-deps chromium`.

Каждому запуску нужен новый идентификатор `--run`: результаты прошлых запусков сохраняются. Генератор автоматически переносит `history/` предыдущего Allure-отчёта. Без установленного Allure сохраняются исходные результаты; после установки можно выполнить `allure generate results/run01/allure-results --clean -o results/allure-report`.

Выборочные проверки:

```bash
python -m pytest tests/unit --cov=app --cov-branch --cov-report=html
python -m pytest tests/api -v
python -m pytest tests/ui --browser chromium -v
python -m behave -f pretty
```

## Структура

```text
app/                 Эталонные валидаторы требований
tests/unit/          Unit-тесты и граничные значения
tests/api/           Реальные HTTP-запросы, изолированный тестовый пользователь
tests/ui/            UI-регрессия, внешние CSV-данные
pages/               Page Object Model и все локаторы
features/            Gherkin на русском языке и шаги Behave
data/                Внешние данные DDT
config/              Конфигурации зеркал PyPI и Docker Hub
scripts/             Запуск и сбор метрик
docs/                Трассировка, дефекты, результаты
.github/workflows/   GitHub Actions
```

## Известные дефекты

Четыре проверки отмечены `xfail(strict=True, raises=AssertionError)` и выполняются при каждом прогоне:

- BUG-03 из модуля 4: корректный email с зоной `.online` отклоняется.
- BUG-01 из модуля 4: кнопка Close не закрывает окно результата.
- API-BUG-01: два набора неверных данных `/Account/v1/Login` возвращают HTTP 200 с пустым телом.

`XFAIL` означает подтверждённое несоответствие ожидаемому контракту, а не успешную проверку продукта. Если дефект исчезнет, строгий `XPASS` сделает сборку красной и потребует пересмотра отметки. Ошибки инфраструктуры не маскируются через `xfail`: перехватывается только AssertionError. Скриншоты UI-ошибок и подтверждённых известных дефектов прикладываются к Allure.

API-тест регистрации создаёт уникального учебного пользователя и удаляет его в `finally`. Пароли и токены вырезаются из HTTP-вложений. Повторные попытки HTTP-запросов и тестов автоматически не выполняются. В UI блокируются только запросы к сторонним рекламным доменам; HTML формы и логика валидации не изменяются.

## CI и отчёты

[GitHub Actions](https://github.com/uat0/qa-automation-module5-botter/actions) запускает полный набор при `push`, `pull_request` и вручную в двух независимых заданиях Chromium и Firefox на Ubuntu. Код выхода pytest/Behave сохраняется. Даже при ошибке загружается артефакт `module5-results-BROWSER-N`: JUnit XML, JSON, HTML, логи, покрытие, Allure results и готовый Allure report. История каждого браузера переносится между CI-запусками через отдельный GitHub Actions cache.

При скачивании артефакта откройте Allure командой `allure open results/allure-report` либо запустите `python -m http.server 8000 --directory results/allure-report` и перейдите на http://localhost:8000. Прямое открытие `index.html` через `file://` может ограничивать загрузку JSON.

## Зеркала

Зависимости установлены через PyPI-зеркало GitVerse. В CI оно задано переменной `PIP_INDEX_URL`. Файл `config/pip.ini` позволяет настроить то же зеркало для отдельного окружения. Настройки ОС пользователя автоматически не меняются.

`config/daemon.json` содержит шаблон зеркала Docker Hub `https://dh-mirror.gitverse.ru`. При использовании Docker его нужно объединить с существующими настройками Docker Engine. Selenoid — опциональная часть задания; здесь кросс-браузерность проверяется непосредственно Playwright в Chromium и Firefox. Подключение Playwright по CDP к обычному WebDriver-порту Selenoid некорректно; для Selenoid нужен Selenium Remote WebDriver.

## Метрики

`python scripts/collect_metrics.py` строит `results/metrics.json` из фактических файлов запусков. Pass Rate = passed / total, где XFAIL включён в знаменатель и показан отдельно. Flaky Rate считается по изменению статуса одного и того же pytest nodeid в повторных прогонах одинакового браузера; другой браузер не смешивается с этим расчётом. Короткая серия не доказывает отсутствие нестабильности в дальнейшем. ROI рассчитывается как модель при явно заданных предположениях о ручном времени и трудозатратах.

Трассировка: [docs/traceability.md](docs/traceability.md). Результаты и ограничения: [docs/results.md](docs/results.md).
