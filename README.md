# tube_upload_app
Dash app that walks through a directory of CSVs and locates missing info. Has the capability to upload to a database as well, but had to be taken out for NIH privacy reasons.

## Run Instructions
```shell
#clone
git clone https://github.com/grantmcc98/tube_upload_app.git

#cd into directory
cd trilution_webclient_integration

#make virtual environment
python -m venv .venv

#activate virtual environment
source .venv/Scripts/activate

#install libraries
pip install -r requirements.txt

#start app
py missing_tube_info_app.py
```
