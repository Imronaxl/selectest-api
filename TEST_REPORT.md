📋 ОТЧЁТ ПО ФУНКЦИОНАЛЬНОМУ ТЕСТИРОВАНИЮ

✅ Успешно: 10
❌ Ошибки:   0

✅ Тест #1: Ручной запуск парсинга
   Метод: POST http://localhost:8000/api/v1/parse/
   Ожидаемый статус: 200, Фактический: 200
   Ответ: {"created":0}...

✅ Тест #2: Создание вакансии
   Метод: POST http://localhost:8000/api/v1/vacancies/
   Ожидаемый статус: 201, Фактический: 201
   Ответ: {"title":"Python Developer","timetable_mode_name":"Full-time","tag_name":"Backend","city_name":"Moscow","published_at":"2026-02-12T10:00:00Z","is_remote_available":true,"is_hot":false,"external_id":10...

✅ Тест #3: Создание дубликата (409 Conflict)
   Метод: POST http://localhost:8000/api/v1/vacancies/
   Ожидаемый статус: 409, Фактический: 409
   Ответ: {"detail":"Vacancy with external_id already exists"}...

✅ Тест #4: Получение списка вакансий
   Метод: GET http://localhost:8000/api/v1/vacancies/
   Ожидаемый статус: 200, Фактический: 200
   Ответ: [{"title":"Python Developer","timetable_mode_name":"Full-time","tag_name":"Backend","city_name":"Moscow","published_at":"2026-02-12T10:00:00Z","is_remote_available":true,"is_hot":false,"external_id":1...

✅ Тест #5: Получение вакансии по ID
   Метод: GET http://localhost:8000/api/v1/vacancies/26
   Ожидаемый статус: 200, Фактический: 200
   Ответ: {"title":"Python Developer","timetable_mode_name":"Full-time","tag_name":"Backend","city_name":"Moscow","published_at":"2026-02-12T10:00:00Z","is_remote_available":true,"is_hot":false,"external_id":10...

✅ Тест #6: Обновление вакансии
   Метод: PUT http://localhost:8000/api/v1/vacancies/26
   Ожидаемый статус: 200, Фактический: 200
   Ответ: {"title":"Senior Python Developer","timetable_mode_name":"Full-time","tag_name":"Backend","city_name":"Saint Petersburg","published_at":"2026-02-12T12:00:00Z","is_remote_available":true,"is_hot":true,...

✅ Тест #7: Создание второй вакансии
   Метод: POST http://localhost:8000/api/v1/vacancies/
   Ожидаемый статус: 201, Фактический: 201
   Ответ: {"title":"Go Developer","timetable_mode_name":"Full-time","tag_name":"Backend","city_name":"Moscow","published_at":"2026-02-12T11:00:00Z","is_remote_available":false,"is_hot":false,"external_id":1002,...

✅ Тест #8: Обновление с конфликтом external_id (409)
   Метод: PUT http://localhost:8000/api/v1/vacancies/26
   Ожидаемый статус: 409, Фактический: 409
   Ответ: {"detail":"External ID already in use by another vacancy"}...

✅ Тест #9: Удаление вакансии
   Метод: DELETE http://localhost:8000/api/v1/vacancies/27
   Ожидаемый статус: 204, Фактический: 204

✅ Тест #10: Планировщик запускается каждую минуту
   Метод: LOG 
   Ожидаемый статус: >=2 запусков за 70с, Фактический: 3 запусков
   Ответ: re "default"
2026-02-12 08:39:48,742 | INFO | apscheduler.scheduler | Scheduler started
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
...

🎯 ВСЕ ИСПРАВЛЕННЫЕ БАГИ ПРОВЕРЕНЫ И РАБОТАЮТ КОРРЕКТНО.
