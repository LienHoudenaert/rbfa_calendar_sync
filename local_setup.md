# RBFA Calendar Sync

Python web application for synchronizing RBFA calendar data.

This guide explains how to set up the project on **Windows** using **pyenv-win**, a Python virtual environment, and VS Code.

## Prerequisites

* Windows 10 or Windows 11
* Visual Studio Code
* Git
* PowerShell
* pyenv-win

---

# 1. Install Git

If Git is not already installed, download and install Git for Windows:

https://git-scm.com/download/win

After installation, restart VS Code.

Verify the installation:

```powershell
git --version
```

You should see something similar to:

```text
git version 2.x.x
```

---

# 2. Install pyenv-win

This project uses **pyenv-win** to manage Python versions on Windows.

Official project:

https://github.com/pyenv-win/pyenv-win

The official pyenv-win documentation provides several installation methods. The PowerShell installer is the easiest method.

Open PowerShell and run:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

## PowerShell execution policy error

If you see:

```text
running scripts is disabled on this system
```

you can allow scripts for your current Windows user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Confirm with:

```text
Y
```

Then close and reopen PowerShell.

Alternatively, you can temporarily allow scripts only for the current PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run the pyenv-win installer again.

> **Note:** The `Process` option only applies to the current PowerShell window.

---

# 3. Verify pyenv-win

Close and reopen PowerShell or the VS Code terminal.

Run:

```powershell
pyenv --version
```

You should see the installed pyenv-win version.

You can also check the available Python versions:

```powershell
pyenv install -l
```

These are the standard validation steps recommended by pyenv-win.

---

# 4. Install Python

Choose the Python version required by the project.

For example:

```powershell
pyenv install 3.14
```

Check installed versions:

```powershell
pyenv versions
```

Set Python 3.14 as your global Python version:

```powershell
pyenv global 3.14
```

Verify:

```powershell
python --version
```

You should see something similar to:

```text
Python 3.14.x
```

Also verify which Python executable is being used:

```powershell
python -c "import sys; print(sys.executable)"
```

pyenv-win uses shims to select the Python version configured by `global`, `local`, or `shell`.

---

# 5. Clone the project

Choose a directory for your projects:

```powershell
cd C:\Users\<username>\Documents\vscode_code
```

Clone the repository:

```powershell
git clone https://github.com/LienHoudenaert/rbfa_calendar_sync.git
```

Enter the project:

```powershell
cd rbfa_calendar_sync
```

Open it in VS Code:

```powershell
code .
```

---

# 6. Set the Python version for this project

Inside the project directory, run:

```powershell
pyenv local 3.14
```

This creates a `.python-version` file.

The project will now use Python 3.14 whenever you work inside this directory.

Verify:

```powershell
pyenv version
```

And:

```powershell
python --version
```

`pyenv local` is different from a virtual environment: pyenv selects the Python version, while the virtual environment isolates the project's installed packages.

---

# 7. Create the virtual environment

From the project directory:

```powershell
python -m venv .venv
```

This creates a `.venv` directory:

```text
rbfa_calendar_sync/
│
├── .venv/
├── app.py
├── requirements.txt
├── .python-version
└── ...
```

The `.venv` directory should normally **not** be committed to Git.

Make sure `.gitignore` contains:

```text
.venv/
```

---

# 8. Activate the virtual environment

In PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Your terminal should now show:

```text
(.venv) PS C:\Users\<username>\Documents\vscode_code\rbfa_calendar_sync>
```

The `(.venv)` indicates that the virtual environment is active.

---

# 9. Upgrade pip

With the virtual environment activated:

```powershell
python -m pip install --upgrade pip
```

---

# 10. Install project dependencies

If the project contains a `requirements.txt` file:

```powershell
python -m pip install -r requirements.txt
```

This installs the Python packages required by the application.

---

# 11. Select the virtual environment in VS Code

In VS Code:

1. Press `Ctrl + Shift + P`
2. Search for:

```text
Python: Select Interpreter
```

3. Select the interpreter inside:

```text
.venv\Scripts\python.exe
```

VS Code should then use the project's virtual environment for Python files, debugging, and the integrated terminal.

---

# 12. Run the application

Make sure the virtual environment is active:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then run:

```powershell
python app.py
```

If this is a web application, the terminal should display the local address where the application is running, for example:

```text
http://127.0.0.1:5000
```

Open that address in your browser.

---

# 13. Daily development workflow

When starting work on the project:

```powershell
cd C:\Users\<username>\Documents\vscode_code\rbfa_calendar_sync
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the application:

```powershell
python app.py
```

When finished:

```powershell
deactivate
```

---

# 14. Useful pyenv commands

List installed Python versions:

```powershell
pyenv versions
```

List available Python versions:

```powershell
pyenv install -l
```

Install a Python version:

```powershell
pyenv install 3.14
```

Set the global Python version:

```powershell
pyenv global 3.14
```

Set the Python version for the current project:

```powershell
pyenv local 3.14
```

Show the currently selected Python version:

```powershell
pyenv version
```

Show which Python executable is being used:

```powershell
pyenv which python
```

Remove a Python version:

```powershell
pyenv uninstall 3.14
```

After changing or modifying Python installations, pyenv-win provides:

```powershell
pyenv rehash
```

These commands are part of the pyenv-win command set.

---

# 15. Useful Git commands

Check the current repository status:

```powershell
git status
```

Pull the latest changes:

```powershell
git pull
```

Stage changes:

```powershell
git add .
```

Commit changes:

```powershell
git commit -m "Describe your changes"
```

Push changes to GitHub:

```powershell
git push
```

---

# Troubleshooting

## `python` is not recognized

Check pyenv:

```powershell
pyenv --version
```

Then:

```powershell
pyenv versions
```

Make sure a Python version has been installed:

```powershell
pyenv install 3.14
```

Then:

```powershell
pyenv global 3.14
```

Restart VS Code if necessary.

pyenv-win also recommends restarting the terminal/IDE after installation.

---

## `pyenv` is not recognized

Check that these directories are in your user `PATH`:

```text
C:\Users\<username>\.pyenv\pyenv-win\bin
C:\Users\<username>\.pyenv\pyenv-win\shims
```

These are the paths documented by pyenv-win for accessing the `pyenv` command.

Restart VS Code after changing environment variables.

---

## PowerShell says scripts are disabled

Run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Then restart PowerShell.

For a temporary solution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

---

## `.venv` activation is blocked

Try:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## Python is opening the Microsoft Store

Windows can have App Execution Aliases enabled for Python.

Go to:

```text
Settings
→ Apps
→ Advanced app settings
→ App execution aliases
```

Disable the Python aliases if they interfere with pyenv-win.

This is also noted in the pyenv-win documentation.

---

# Project setup summary

The complete setup is:

```powershell
# Install/check pyenv-win
pyenv --version

# Install Python
pyenv install 3.14

# Clone project
cd C:\Users\<username>\Documents\vscode_code
git clone https://github.com/LienHoudenaert/rbfa_calendar_sync.git

# Enter project
cd rbfa_calendar_sync

# Select Python version for this project
pyenv local 3.14

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
python -m pip install -r requirements.txt

# Run application
python app.py
```

## Architecture

The development environment has three layers:

```text
pyenv-win
    │
    └── Selects Python version (e.g. Python 3.14)
             │
             ▼
        .venv
             │
             └── Isolates project dependencies
                      │
                      ▼
                  app.py
                      │
                      └── Runs the web application
```

This means **pyenv-win manages Python versions**, while **`.venv` manages the packages for this particular project**.
