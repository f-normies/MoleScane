## Установка:
1. Для начала лучше установить именно эти версии npm и node

    ```
    npm -v
    10.8.2
    ```

    ```
    node -v
    v20.18.0
    ```

2. Запустите файл `install_packages.py`

    Неустановленные пакеты будут в errors_requirements.txt, но с указанными выше версиями npm и node - ошибок не должно быть

3. Скачайте веса моделей

    ```
    wget https://share.xolostxutor.msk.ru/api/shares/gxMzkyN/files/298ee800-66eb-472c-985a-482d9887c591 -O yolonas-s.pth

    wget https://share.xolostxutor.msk.ru/api/shares/QxNTg1N/files/2495b663-1c11-4f4b-a318-eb07ca1989db -O yolonas-l.pth
    ```

4. Запуск для отладки на локальном сервере

    **Бэк**: ~/MoleScane$ uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

    **Фронт**: ~/MoleScane/frontend$ npm start
