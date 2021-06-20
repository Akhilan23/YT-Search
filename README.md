# simple-django-project
## Installation

### Prerequisites

#### 1. Install Python
Install ```python-3.7.2``` and ```python-pip```. Follow the steps from the below reference document based on your Operating System.
Reference: [https://docs.python-guide.org/starting/installation/](https://docs.python-guide.org/starting/installation/)

#### 2. Install MySQL
This project was built on ```mysql-5.7.26```. Follow the steps form the below reference document based on your Operating System.
Reference: [https://dev.mysql.com/doc/refman/5.5/en/](https://dev.mysql.com/doc/refman/5.5/en/)

#### 3. Setup virtual environment
```bash
# Create & activate virtual environment
python3 -m venv env

# Navigate to virtual environment
cd env

# Activate virtual environment
source bin/activate
```

#### 4. Clone git repository
```bash
git clone "https://github.com/Akhilan23/YT-Search.git"
```

#### 5. Install requirements
```bash
cd YT-Search/
python3 -m pip install -r requirements.txt
```

#### 6. Load schema into MySQL
```bash
# Open mysql bash in the same terminal
mysql -u<mysql-username> -p<mysql-password>

# Give the relative path of the file
mysql> source ytsearch.sql
mysql> exit;

```

#### 7. Edit project settings
```bash
# open settings file
# Edit Database configurations with your MySQL configurations.
# Search for DATABASES section.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ytsearch',
        'USER': '<mysql-username>',
        'PASSWORD': '<mysql-password>',
        'HOST': '<mysql-host>',
        'PORT': '<mysql-port>',
    }
}
# save the file

```
#### 8. Run the server
```bash
# Make migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Run the server
python3 manage.py runserver 0:8001

# your server is up on port 8001
```
Try opening [http://localhost:8001](http://localhost:8001) in the browser.

### 9. URLs
#### Browse by page: [http://localhost:8001/api/videos/page=0](http://localhost:8001/api/videos/page=0)
#### Browse by search: [http://localhost:8001/api/videos/page=0&query=cristiano](http://localhost:8001/api/videos/page=0&query=cristiano)
