# Accounting Tool

This tool will automate some of the monthly congregation accounting tasks
- Reads bankaccount report file (csv) and insert its data in jw org accounting page
- Downloads monthly report files and saves them at configured target location/file names


## Setup

Download tool.

Create virtual environment

```
apt install python3.11-venv
python3 -m venv ~/jw_autofill_venv
```

Activate virtual environment

```
source ~/jw_autofill_venv/bin/activate

pip3 install .
# pip3 install --editable .
```

Copy example.config.yml to config.yml and edit values according to your needs


## Usage

```
source ~/jw_autofill_venv/bin/activate
./run.sh --month=2023-06 --source=mt940.csv --account="Accounting sub-account name on jw org"
```

Follow the menu.
The tool will open a browser window and will navigate automatically.
You may login manually, the tool will wait at this step.

##### Note
To remove all temporary data / Cookies / ..., delete folder `tmp`. (This will require you to relogin on next run!)