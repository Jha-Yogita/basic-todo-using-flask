# Flask Notes

## How to run server
python app.py

## Install packages
python -m pip install flask

## Doubts
virtualenv creates a copy of python instance we have so there is no mismatch of version.
isolation of env
to enter env

.\env\Scripts\activate.ps1

Set-ExecutionPolicy unrestricted- in administrator powershell


in static directory -as it is we can serve our files
we can directly acces at /static/file_name

templates folder-for html and all

orm we using here is SQLAlchemy

U can visit flash-sqlalchemy documentation

in console write 
first write $env:FLASK_APP="app.py"
then flask shell
in which write 
from app import db
db.create_all()
in your instance folder todo.db will be create as u create the todo model

in SQLlite viewer website u can go and check what is in your todo.db folder

using loop.index for incremental sno