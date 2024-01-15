# ![Talos-Logo](arc/web/static/images/taloslogoreadme.png) TalosBDD Automation Framework

> A framework developed and supported by the ***Testing Automation CoE - Automation Toolkit***

**TalosBDD** is a [Python](https://devdocs.io/python~3.6/) test automation framework based on the BDD development
methodology. Uses a Gherkin language layer for automated test case development. It allows the automation of functional
tests web, mobile, API, FTP, among others, in a simple, fast and easy maintenance way.

**You can find more information and documentation in the Sharepoint space of
the [Automation Toolkit](https://santandernet.sharepoint.com/sites/Talos-Ecosystem/SitePages/es/Home.aspx)**

----

## Table of Contents

1. [About TalosBDD](#about-talosbdd)
2. [Requirements](#requirements)
3. [How to download TalosBDD](#how-to-download-talos-bdd)
    - [Download mode](#download-sources)
4. [Folders and Files Structure](#folders-and-files-structure)
5. [How to install](#how-to-install)
6. [How to run the framework](#how-to-run-the-framework)
7. [Initial Considerations](#initial-considerations)

----

## About TalosBDD

TalosBDD is based on open technologies to offer the necessary functionalities to automate your tests. Among these
technologies are:

- [Behave](https://behave.readthedocs.io/en/latest/)
- [Selenium](https://www.seleniumhq.org/docs/)
- [Appium](http://appium.io/docs/en/about-appium/intro/)
- [Request](https://requests.readthedocs.io/en/master/)
- [Records](https://pypi.org/project/records/)
- [Pillow](https://pillow.readthedocs.io/en/stable/)
- [Pytest](https://docs.pytest.org/en/stable/contents.html)

**TalosBDD** is an all-terrain Framework:

- **Multi-platform**
    - Allows execution in Windows, Linux and Mac environments
- **Multi-functional**
    - It allows automating functional tests Web, Mobile, microservices, FTP, Database, etc.
- **Multi-device**
    - Allows execution in all browsers, headless, Android and iOS mobile devices, virtualization, local devices and in
      the cloud
- **Multi-environments**
    - Allows easy data management between business environments

----

## Requirements

- [Python 3.10](https://www.python.org/downloads/release/python-3100/) or higher 64 bits ([Python 3.11](https://www.python.org/downloads/release/python-3110/) recommended).
- **Pip**: Python usually comes with Pip, but if this is not the case, you will need the PIP dependency manager version 20.0.0 or higher. 
- Pip configuration for **Nexus** connection.
- **Java 1.8** or higher (Optional: If you want to run the Talos Connector integrated in TalosBDD).
- Browsers (The type of browser is optional, but the one to be used must be installed).
- [PyCharm](https://www.jetbrains.com/es-es/pycharm/) (Optional: highly recommended IDE).

----

## How to download TalosBDD

**TalosBDD** is managed by the Automation Toolkit team, so its use is upon request to the CoE Automation Testing.

### Download sources

- [Corporate Github.](https://github.alm.europe.cloudcenter.corp/sgt-talos/python-talos-talos-bdd/releases)
- [Github Enterprise.](https://github.com/santander-group-solution-testautomation/talos-bdd/releases)
- [Talos Automation Framework Teams.](https://santandernet.sharepoint.com/sites/TALOSAutomationFramework/Shared%20Documents/Forms/AllItems.aspx?csf=1&web=1&e=dMo4zz&cid=ddbeb564%2D52df%2D4e20%2Db3a2%2D6aa41db8afca&RootFolder=%2Fsites%2FTALOSAutomationFramework%2FShared%20Documents%2FGeneral%2FTALOS%20BDD&FolderCTID=0x012000E3B38C1F0EA7D74389308499CBC02E81)
- Contact the Automation Toolkit Team - CoE Automation Testing, and you will be given a copy of the compressed file with the Framework.
----

## Folders and Files Structure

The TalosBDD folder structure is composed of several folders and files. The most important is the 'arc' folder where the core of the framework is located.

You can find more information about the folder and file structure on [this page.](https://santandernet.sharepoint.com/sites/Talos-Ecosystem/SitePages/TalosBDD/User%20Guide/Using%20TalosBDD/Folders%20and%20Files%20Structure.aspx)

## How to install

**Step 1:** If you have downloaded TalosBDD as a zip file. Unzip it wherever you want.

**Step 2:** Go into the Framework folder, you should see all the Framework files like 'arc', 'test' or 'settings' folder.

**Step 3:** Open a console or terminal or command line.

**Step 4:** Creation of the virtual environment (Optional but recommended)

Windows: Type in the command line the following command:
~~~
# Basic virtual environment creation command
python -m venv venv
# Command to choose with which version of python the virtual environment is going to be created
virtualenv -p 'C:/Path/To/Python/Python311/python.exe' venv
~~~

Linux: Type in the terminal the following command:
~~~
# Basic virtual environment creation commands
python3 -m pip install --upgrade pip
virtualenv -p /path/to/Python/python3 venv
~~~

After the above commands the 'venv' folder will have been created.

**Step 5:** Activate virtual environment with the following command:

**Windows:**
~~~
venv\Scripts\activate
~~~

**Linux:**
~~~
source venv/bin/activate
~~~
You should be able to see '(venv)' at the beginning of the prompt. This indicates that the virtual environment has been activated successfully.

**Step 6:** Install TalosBDD dependencies.
~~~
pip install -r requirements.txt
~~~
If installing the dependencies gives you any errors related to the proxy or SSL, you must either install the dependencies through a proxy or configure Pip so that the dependency repository is the Nexus of your organization.

----

## How to run the framework

To run TalosBDD you have to run the file talos_run.py.

For that you can execute the following command (you must have the virtual environment activated):
~~~
python talos_run.py
~~~
Check out more TalosBDD execution options on [this page](https://santandernet.sharepoint.com/sites/Talos-Ecosystem/SitePages/TalosBDD/User%20Guide/Execution/Run%20TalosBDD.aspx).


## Initial Considerations

1. When you run TalosBDD for the first time, you may get an error due to a version conflict between the driver and the browser installed on your computer. To fix this you can update the driver manually or use the built-in driver updater in TalosBDD.

To activate the automatic updater of TalosBDD you must go to the settings/settings.py file and look for the variable 'PYTALOS_GENERAL'

In this variable you will find many general TalosBDD settings but the one you need to enable is the 'update_driver' setting by setting the value 'enabled_update' to True.
~~~
PYTALOS_GENERAL = {
    'update_driver': { 
            'enabled_update': True, # Set to True to enable automatic driver updater
            'enable_proxy': False,
            'proxy': PROXY
        }
}
~~~

2. It is possible that you will also get an error that you must fill in some mandatory configuration fields related to the project information.

To fix this you should fill in the following variables in the settings/settings.py file as reliably as possible:
~~~
# PROJECT INFO IS REQUIRED. PLEASE COMPLETE THESE FIELDS WITH THE PROJECT INFORMATION
PROJECT_INFO = {
    'application': '',  # application being tested
    'business_area': '',  # application business area
    'entity': '',  # your department
    'user_code': ''  # your LDAP-ID
}
~~~

3. If in any previous step you have crashed, got an error or have any questions, please feel free to write to the [TalosBDD support channel](https://teams.microsoft.com/l/channel/19%3a81ededf4d389425f92d3ff4bcf49f7b5%40thread.skype/Talos%2520BDD?groupId=66e4a0f7-e684-4a3a-b47e-e583edfe295b&tenantId=35595a02-4d6d-44ac-99e1-f9ab4cd872db) about the problem or question you have.