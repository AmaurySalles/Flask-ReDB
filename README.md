# STAGE_00 -> Setting up flask, and figuring out how to integrate postgres, SQLAlchemy, WTForms, Bootstrap.
    ## Sorry, lost track of the number of sources used
    # TODO - Find relevant sources to system configuration deployed.
# STAGE_01 -> Testing Semantics UI but bakc-tracked and stayed with Bootstrap

# STAGE_02 -> Building technologies & components (database tables & relationships + python / SQLAlchemy classes)

# STAGE_03 -> Building wtform, janja & javascript to add any number of technologies & components to forms & web.
# STAGE___ -> Build wtform and database mechanism to add multiple countries or components to a project
    ## https://gist.github.com/doobeh/5d0f965502b86fee80fe
    ## https://stackoverflow.com/questions/30121763/how-to-use-a-wtforms-fieldlist-of-formfields

# STAGE_04 -> Re-design of database to accommodate for projects->plants->configs + implementation of all techs up to stage_03
# STAGE_05 -> Create additonal views & searches (test Semantics UI again?)
# STAGE_05 -> Implement portfolios & create update page (reverse of STAGE_03 - show fields info but editable)
    ## https://stackoverflow.com/questions/29514798/filling-wtforms-formfield-fieldlist-with-data-results-in-html-in-fields
# STAGE_06 -> Build permissions levels and @permissionRequired route
# STAGE_07 -> Build security (flask tokens)



# Renewable Energy Database

This database uses:
- PostgreSQL as database
- SQLAlchemy to connect to it
- Python to run queries
- Flask to run web server
- JSON to communicate with web server
- HTML/CSS/Bootstrap to display web page
- Jinja as templating engine (e.g. template inputs & macros)
- JavaScript for web interactions (e.g. non-submit buttons, search bar mid-result filter display, dynamic dropdowns, etc.)
- WTForms to validate form inputs

Note: This app does not use flask_wtf but imports from WTForms directly (due to recent incompatible patches), therefore some of the methods might differ. 



# Application Components:

1. app.py       - Main python file which sets up and runs Flask application. Includes main server routes
2. forms.py     - Secondary python file which sets up WTForms classes (forms)
3. helpers.py   - Secondary python file which includes helpers python functions (which can can called from any route)
4. models.py    - Secondary python file which sets up SQLAlchemy classes (models)
5. test.py      - Secondary python file which includes sever routes to include test data 




# First runs:
1. Run requirement.txt to make sure that all necessary Python packages (Flask and SQLAlchemy) are installed:
    (i.e. 'pip3 install -r requirements.txt')

2. Set the environment variable FLASK_APP to be application.py. 
    On a Mac or on Linux, the command to do this is 'export FLASK_APP=application.py'. 
    On Windows, the command is 'set FLASK_APP=application.py'. 
3. For admin purposes, you can set the environment variable 'FLASK_DEBUG=1', which will activate Flask’s debugger and will automatically reload your web application whenever you save a change to a file.

4. Set the environment variable 'DATABASE_URL' to be the URI of your database, which you should be able to see from the credentials page on Heroku.

5. Start the flask app with 'flask run'  
    If you navigate to the URL provided by flask, you should see the web app




# General Setup of Database:
    Refer to database relation diagrams in helpers/dbschema





# Newbie tips on (integration of) Flask, SQLAlchemy, WTForms, AJAX, etc.
    
    # W3Schools is your friend (HTML, JS, SQL, Bootstrap, Python, JQuery, XML)
    https://www.w3schools.com/

    # PrettyPrinted is also your friend (Flask app tutorials)
    https://prettyprinted.com/





# Jinja documentation & other resources
    
    # Jinja documentation
    http://jinja.pocoo.org/docs/2.10/templates/



# SQLAlchemy documentation & other resources

    # Integration with flask_bootstrap - Not currently in use!
    https://pythonhosted.org/Flask-Bootstrap/basic-usage.html
    
    # List of SQLAlchemy errors
    https://docs.sqlalchemy.org/en/latest/core/exceptions.html

    

# WTForms documentation & other resources
    # Note: This app does not use flask_wtf but imports from WTForms directly (due to recent incompatible patches), therefore some of the methods might differ

    # WTForms Documentation
    https://wtforms.readthedocs.io/en/stable/index.html - 

    # Practical integration of WTForms in Flask app
    http://flask.pocoo.org/docs/1.0/patterns/wtforms/#forms-in-templates - 

    # Submit an entire add project form, while the details of the technology or suppliers changes according to selected field of technology
    https://blog.whiteoctober.co.uk/2019/01/17/combining-multiple-forms-in-flask-wtforms-but-validating-independently/

    # Add personalised validators, and have the form check all errors at once. - Note: Could not manage to make it work.
    https://medium.com/@doobeh/posting-a-wtform-via-ajax-with-flask-b977782edeee 


    # Resources to produce more complex forms (dynamic select fields, multiple forms) & related routes for post processing
    
    # WTForms fields documentation 
    http://wtforms.simplecodes.com/docs/0.6/fields.html

    # Dynamic flask form (Javascript / jQuery) example 
    https://github.com/sebkouba/dynamic-flask-form 
    https://gist.github.com/kageurufu/6813878 

    # Add multiple forms to a page
    https://gist.github.com/doobeh/5d0f965502b86fee80fe
    https://stackoverflow.com/questions/30121763/how-to-use-a-wtforms-fieldlist-of-formfields

    # Validating multiple forms, or individual
    https://dev.to/sampart/combining-multiple-forms-in-flask-wtforms-but-validating-independently-cbm 

    # Re-display data for submition errors (to not have to refill whole form) or to edit / update information
    https://stackoverflow.com/questions/29514798/filling-wtforms-formfield-fieldlist-with-data-results-in-html-in-fields
