# Решение команды Мисисково
## Кейс - Вопросно-ответная система по технической документации RuStore

Наше решение заключается в создании автоматически обновляемой вопросно-ответной системы, которая поможет пользователям и разработчикам разобраться в особенностях технической документации RuStore.

### Общий подход к решению:
- Парсинг полной документации с сайта https://www.rustore.ru/help/
- Обработка сложных случаев и разделение текста на фрагменты
- Получение контекстных фрагментов с помощью модели E5 и алгоритма rank-bm25
- Переранжирование кандидатов с помощью модели colbert-xm
- Передача контекстных фрагментов в Mistral-instructv0.2 и GigaChatPro
- Выдача ответа пользователю

### Структура файлов:
1. `indexes` - содержит индексы для векторной базы данных для быстрого поиска по ним (файлы обновляются сами при вызове скрипта)
2. `parser` - парсер документации, jsons полученные при парсинге, обрабатываются и сохраняются в pikle для модели
3. `update_docs` - обработка, разрезание по фрагментам и формирование индексов векторной базы данных
4. `utils` - содержит вспомогательные классы для retriever, LLM, reranking, создания промпта
5. `main.py` - создание главной страницы и вывода фронта с помощью фреймворка streamlit (страница чата)
6. `update_documents.py` - вторая страница streamlit для обновления данных
7. `side.py` - запуск всего приложения

### Запуск приложения:
```bash
git clone https://github.com/polinaMinina/rustore_docs.git
cd rustore_docs
python -m venv <venv name>
pip install -r requirements.txt
streamlit run side.py
```

### Особенности системы:
 - Применение Sota-моделей для получения эмбеддингов
 - Быстрый инференс и высокая точность ответов
 - Система не требует дообучения громоздких моделей, что делает ее удобной для инференса и легко масштабируемой для решения похожих задач.
