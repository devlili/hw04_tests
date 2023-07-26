[![Python](https://img.shields.io/badge/-Python_3.9-464646??style=flat-square&logo=Python)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/-Django_2.2.16-464646??style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Unittest](https://img.shields.io/badge/-Unittest-464646??style=flat-square&logo=Unittest)](https://docs.python.org/3/library/unittest.html)
[![Pytest](https://img.shields.io/badge/Pytest-464646??style=flat-square&logo=Pytest)](https://docs.pytest.org/en/)

# Покрытие тестами проекта «Yatube»
## Описание
Yatube - это социальная сеть с авторизацией, персональными лентами, комментариями и подписками на авторов статей.
### Реализовано (https://github.com/devlili/hw04_tests/tree/master/yatube/posts/tests)
- тестирование моделей приложения posts в Yatube;
- проверка доступности страниц и названия шаблонов приложения Posts проекта Yatube, проверка учитывает права доступа;
- проверка корректности использования html-шаблонов во view-функциях;
- проверка соответствия ожиданиям словаря context, передаваемого в шаблон при вызове;
- проверка на корректное отображение поста на главной странице сайта, на странице выбранной группы и в профайле пользователя при создании поста и указании группы, а также проверка, что пост не попал в группу, для которой не был предназначен;
- проверка создания новой записи в базе данных при отправке валидной формы со страницы создания поста, а при отправке валидной формы со страницы редактирования поста изменение поста с post_id в базе данных.

## Как запустить проект:
* Клонировать репозиторий и перейти в него в командной строке: 
  ```
  git clone https://github.com/devlili/hw04_tests.git
  cd hw04_tests
  ```
* Cоздать и активировать виртуальное окружение:
  * Windows
     ```
     python -m venv venv
     source venv/Scripts/activate
     ```
  * Linux
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```
* Установить зависимости из файла requirements.txt:
    ```
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```
* Выполнить миграции:
    ```
    python manage.py migrate
    ```
* Запустить проект:
    ```
    python manage.py runserver
    ```

## Автор
Лилия Альмухаметова
