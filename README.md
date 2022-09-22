# PortfolioProject #

#### This project was designed to implement a portfolio of my projects. Users can create accounts, add comments on code, create issues, and download projects using an API. ####

<br>
<hr>

### Installing the Appropriate Libraries ###
* To install the appropriate libraries, use Python's package manager. Use this command at the root directory of the project:
    ```
    pip install -r requirements.txt
    ```


<hr>

### Required Project Files ###

* ***Important Note: Any file or database that contains sensitive information should be stored in a safe location.***
* Since this project runs on the Flask web framework, there are some required files in order to get it running.
* Here is a list:
    
    * **.env**
        
        * This file is needed to set the environment correctly. It is a key-value pair setup, so it should follow this format:


        ```
        INSTANCE_MODE = <'development' | 'production'>
        DEV_DATABASE_PATH = <SQLite3 Database Path> (NOTE: This is for a DEV environment.)
        PROD_DATABASE_PATH = <SQLite3 Database Path> (NOTE: This is for a PRODUCTION environment.)
        SECRET_KEY_PATH = <secret_key path>
        EMAIL_USERNAME = <email username>
        EMAIL_PASSWORD_PATH = <email_password path>
        ```   
    
    * **portfolio_key.txt**

        * This file stores the AES key needed to encrypt data. This file should be stored in a safe location for production and should only be given read access to the user running this program.

        * To generate this, simply use Python's urandom module from os to create a key.

    * **email_password.txt**

        * This file stores the password to the email used to send notifications for the contact form to.

        * Note: This file has been excluded from the repository as it has sensitive information.