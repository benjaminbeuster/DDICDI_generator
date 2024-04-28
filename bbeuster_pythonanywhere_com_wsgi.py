import sys

# Path to the virtual environment site-packages
path_to_virtualenv = "/home/BBeuster/.virtualenvs/myvirtualenv/lib/python3.9/site-packages"
sys.path.append(path_to_virtualenv)

# Add your project directory to the sys.path
project_home = '/home/BBeuster/mysite'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Import dash app but need to call the server "application" for WSGI to work
from app import server as application  # noqa