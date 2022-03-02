# tube_upload_app
Dash app that walks through a directory of CSVs and locates missing info. Has the capability to upload to a datbase as well, but had to be taken out for NIH privacy reasons

## Run Instructions
```shell
#clone
git clone https://github.com/grantmcc98/trilution_webclient_integration.git

#cd into directory
cd trilution_webclient_integration

#make virtual environment
python -m venv .venv

#activate virtual environment
source .venv/Scripts/activate

#install libraries
pip install -r requirements.txt

#start app
set FLASK_APP=main.py
flask run
```
