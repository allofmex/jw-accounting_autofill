# Accounting Tool

This tool will automate some of the monthly congregation accounting tasks
- Reads bankaccount report file (csv) and inserts data on jw org accounting page
- Downloads monthly report files and saves them at configured target location/file names
- Prepares email templates for transfer approval and montly report
- tracks total project donation amount

The Tool will simply operate and read your local browser instance to navigate jw org website, same as user
would do it. (Via Selenium/Python. No hidden/private APIs are used).


## Setup (Linux)

Install Python if not present already.

Download tool.

```
git clone github.com/allofmex/jw-accounting_autofill
cd jw-accounting_autofill
```

Create virtual python environment

```
apt install python3-venv python3-pip
python3 -m venv ~/jw_autofill_venv
```

Activate virtual environment

```
source ~/jw_autofill_venv/bin/activate

pip3 install .

## If you plan to contribute to this tool, you may use instead:
# pip3 install --editable .
## For priate gitlab repository create access token in group or repository with scope "read_repository" and at least role Reporter (guest will not work)
```

Copy example.config.yml to config.yml and edit values according to your needs

```
cp example.config.yml config.yml
nano config.yml
```


## Setup (Windows)

##### Install dependencies
(You may use [UniGetUI](https://github.com/marticliment/UniGetUI))

- [GIT](https://marticliment.com/unigetui/share?name=Git&id=Microsoft.Git&sourceName=winget&managerName=WinGet)
- [Python 3](https://marticliment.com/unigetui/share?name=Python&id=python&sourceName=community&managerName=Chocolatey)

##### Create virtual python environment
Open PowersShell in accounting-tool folder (shift + right click in explorer window)

```
python -m venv $ENV:TEMP\jw_accounting_autofill_venv
& "$ENV:TEMP\jw_accounting_autofill_venv\Scripts\Activate.ps1"
# confirm script warning with 'm' if needed
```

##### Install python dependencies

```
python -m pip install .
```


## Usage (Linux)

Activate virtual python environment and start tool

```
source ~/jw_autofill_venv/bin/activate
./run.sh --month=2023-06 --source=mt940.csv --account="Accounting sub-account name on jw org" --project="jw org project label"
```

Follow the menu.
The tool will open a browser window and will navigate automatically.
You may login manually, the tool will wait at this step.


## Usage (Windows)

```
& "$ENV:TEMP\jw_accounting_autofill_venv\Scripts\Activate.ps1"
.\run.bat --month=2023-06 --source=mt940.csv --account="Accounting sub-account name on jw org" --project="jw org project label"
```


##### Note

If you experience failures in script, try again. It may have been a timeout issue.
Also make sure you closed all browser windows that were opened previously by this tool.

To remove all temporary data / Cookies / ..., use tools "Clear cache..." option or delete folder `tmp`.
(This will require you to relogin on next run!)
