# j_project_api

## 🔸Automated testing framework developed for the J.* project, a B2C web application that serves as a dynamic platform for creative professionals

🔸 Includes:

- sets of both positive and negative tests to validate API functionality across core features (e.g.user registration, authorization, password recovery, and account deletion)
- a suite of basic fixtures to streamline the setup of preconditions and teardown of postconditions
- helper classes featuring methods for specialized tasks, like accessing and parsing email-received information for test use, or executing complex multi-step processes needed in tests

▶️ To run the framework:
- clone it from the current repository to your local machine
- install all necessary packages and modules by running `pip install -r requirements.txt` in PyCharm's Terminal
- (!) an .env file with access credentials is required to run tests

▶️ To run tests for API:
- (for all tests) execute `pytest ./api/tests` in PyCharm's Terminal
- (for specific test): run pytest `./api/[name_of_specific_test_file].py`
- (for all tests with specific mark): `pytest -m [title_of_specific_mark]`

_*J. project: a B2C web application designed for creative professionals as a platform to showcase, discover, sell, and purchase creative work. Serves a diverse community of designers, artists, photographers, and other creatives, facilitating portfolio display, inspiration sourcing, and connection with potential clients and recruiters. Key features currently include portfolio creation tools, social networking elements, and an advanced search function for exploring new artists and designs_ 

_**Published with the consent of the project team and all confidential data removed_
