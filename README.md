## Installation and Setup
1. Create a virtual environment and activate it:
   ```bash
    pipenv shell
   ```
2. Install project dependencies:
   ```bash
    pipenv install
    #or
    pipenv install -r requirements.txt
    ```
3. Apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
