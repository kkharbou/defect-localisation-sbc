# Contributing

Contributions are welcome, and they are greatly appreciated! You can contribute in many ways:

## Types of Contributions

### Report Bugs

Add a bug to the project's backlog or report bugs by sending me an email : khadija.kharbouch@suez.com

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs or Implement Features

Look through the backlog for bugs and user stories. It is open to whoever wants to
fix or implement them.

### Write Documentation

Python defect_localisation_sbc could always use more documentation, whether as part of the
Python defect_localisation_sbc docs or in docstrings.

### Submit Feedback

The best way to send feedback is to file an issue in the backlog.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.

## Get Started!

Ready to contribute? Here's how to set up defect_localisation_sbc for local development.

1. Clone the repo locally :

    ```
    $ git clone https://gitlab.com/Khadija Kharbouch/defect_localisation_sbc.git
    ```

2. Install your local copy into a virtualenv. Assuming you have pew installed,
this is how you set up your fork for local development :

    ```
    $ pew new aquadvanced_env
    $ cd defect_localisation_sbc/
    ```

3. Install package dependencies :

    This can be achieved either by using the Makefile :
    ```
    $ make init
    ```

    Or with :
    ```
    $ pip install --editable .
	$ pip install --upgrade -r requirements/main.txt  -r requirements/dev.txt
    ```

4. Create a branch for local development :

    ```
    $ git checkout -b name-of-your-bugfix-or-feature
    ```
    Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests :

    ```
    $ flake8 defect_localisation_sbc tests
    $ pytest
    ```

6. Commit your changes and push your branch to the repo :

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the Azure DevOps website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the README.md.
3. The pull request should work for Python 3.6, 3.7 and 3.8. Make sure that the tests pass for all supported Python versions.

## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.md).

1. Update version :

    ```
    $ bump2version patch # possible: major / minor / patch
    $ git push
    $ git push --tags
    ```

2. Build and upload on the feed :

    Using Makefile :

    ```
    $ make dist
    $ twine upload -r defect_localisation_sbc dist/*
    ```

    Or manualy :

    ```
    $ rm -rf build/ dist/ .eggs/
    $ python setup.py sdist bdist_wheel
    $ twine upload -r MyRepo dist/*
    ```

