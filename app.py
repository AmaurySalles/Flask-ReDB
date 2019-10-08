# Newbie tips on imports - https://www.youtube.com/watch?v=MZlKCdybZrA
# Newbie tips on Postgresql - http://www.postgresqltutorial.com/ 
# Newbie tips on SQLAlchemy - https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/
#                           - https://www.youtube.com/watch?v=YWFqtmGK0fk
#                           - https://stackoverflow.com/questions/2136739/error-handling-in-sqlalchemy
# Side note, Flask_SQLAlchemy is a level higher than SQLAlchemy




### IMPORTS

## Flask imports
# Documentation of Flask - http://flask.pocoo.org/
from flask import Flask
from flask import flash
from flask import jsonify
from flask import redirect
from flask import request
from flask import render_template
from flask import session as flask_session
from flask import url_for
from flask_session import Session as flask_Session


## SQLAlchemy imports
# Documentation of Flask_SQLAlchemy - http://flask-sqlalchemy.pocoo.org/2.3/
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError

from wtforms import validators
from wtforms import ValidationError



### SETUP:

## FLASK SERVER:

# Initialise app
app = Flask(__name__)

# Configure application
app.config.from_pyfile('config.cfg')

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Create flask_Session which allows different users to access app and have different views (e.g. projects listed under their name/session)
flask_Session(app)


## SQLALCHEMY DATABASE:

# Set up link to flask app
# Autoflush = False to stop Postgres / SQLAlchemy errors from crashing application (i.e. error is handled by the different routes)
db = SQLAlchemy(app, session_options={'autoflush': False})







### SERVER QUERIES


## RESOURCES USED:
#https://blog.whiteoctober.co.uk/2019/01/17/combining-multiple-forms-in-flask-wtforms-but-validating-independently/
#https://code.tutsplus.com/tutorials/intro-to-flask-adding-a-contact-page--net-28982



## IMPORTS FOR ROUTES 
# Import SQLAlchemy models
from models import Users, Projects, Plants, Partakers, Clients, Parties, Countries, Services, Roles, ClientsRoles, PartakersRoles, Technologies, Components, Types, Models, Suppliers, Configurations

# Import WTForms form classes from forms.py
from forms import LoginForm, RegisterForm, ProjectForm, PlantForm, TypeForm, PartyForm

# Helper.py contains functions which are called by the routes
from helpers import login_required, addNewProject, addNewPlant



## ADMIN (LOGIN, LOGOUT & REGISTER)
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    flask_session.clear()

    # Link to LoginForm (class) 
    form = LoginForm(request.form)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST" and form.validate():

        # Get data from form
        staffnum = form.staffnum.data
        password = form.password.data
        

        # Check user is already registered
        db_staff = Users.query.filter_by(staffnum=staffnum).first()

        # If no result, return to login page
        if db_staff == None:
            form.staffnum.errors.append('Incorrect staff number.')
            return render_template("login.html", form=form)  
        
        # If passwords do not match, return to login page
        else:
            if password != db_staff.passwordHash:
                form.password.errors.append('Incorrect password.')
                return render_template("login.html", form=form)
            else:
                # Enable user to log in (see login_requested function) & redirect
                flask_session['user_id'] = staffnum

                flash('Welcome to the Renewable Energy DataBase!', 'primary')
                
                return redirect('/')
        
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    flask_session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Link to RegisterForm (class) 
    form = RegisterForm(request.form)
    # User reached route via POST and has properly submitted form
    if request.method == "POST" and form.validate():

        # Get data from form
        name = form.name.data
        staffnum = form.staffnum.data
        password = form.password.data
        email = form.email.data

        # Check inputs are not already in database

        # Create new user
        new_user = Users(name=name,passwordHash=password, staffnum=staffnum, email=email)
        db.session.add(new_user)

        try:
            # Updating database
            db.session.commit()

            # Inform of successful operation
            flash('You have been registered!', 'success')
            

            # Enable user to log in using Flask session cookie 'user_id' (is used by all @loginRequired route)
            flask_session["user_id"] = staffnum

        # Checks for primary key, null and uniques - returns an integrity error if clash occurs
        except IntegrityError:
            # Rollback changes
            db.session.rollback()

            print(IntegrityError)
            
            # Inform of integrity error
            flash('Integrity Error! This user is already registered', 'danger')
            
            # Return to register page
            return render_template("register.html", form=form)

        flash('Welcome to the Renewable Energy DataBase (REDB)', 'primary')

        # Redirect user to home page
        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html", form=form)




## VIEWS (INDEX/HOME, OVERVIEW, UPDATING PROJECT, ADDING PROJECT)

# Index / Home / Main page.
# Displays user's projects (as PM or PP)
@app.route('/', methods=["GET", "POST"])
@login_required
def index():

    # TODO - Add capacity calculator for each tech with correct unit (MW vs GW)

    return render_template('home.html')

# Displays user's projects (as PM or PP)
@app.route('/allProjects', methods=["GET", "POST"])
@login_required
def allProjects():
    
    projects = db.session.query(Projects, Roles).outerjoin(Roles, Projects.role_id == Roles.id).all()
    print(projects)
    for project, roles in projects:
        print(project.code)

    return render_template('allprojects.html', projects=projects)


# Displays user's projects (as PM or PP)
@app.route('/myProjects', methods=["GET", "POST"])
@login_required
def myprojects():
    
    # Get user ID
    user = flask_session['user_id']

    # Find all projects in which user is PM
    projects_pm = Projects.query.filter_by(pm_id=user).all()
    projects_dpm = Projects.query.filter_by(dpm_id=user).all()
    projects_pp = Projects.query.filter_by(pp_id=user).all()

    if not projects_pm and not projects_pp:
        flash('You have no projects registered under your name.', 'danger')
        return redirect('./')
    else:
        return render_template('myprojects.html', projects_pm=projects_pm, projects_pp=projects_pp)


# Allows user to add new projects
@app.route('/addProject', methods=["GET", "POST"])
@login_required
def addProject():

    ## https://gist.github.com/doobeh/5d0f965502b86fee80fe
    ## https://stackoverflow.com/questions/29514798/filling-wtforms-formfield-fieldlist-with-data-results-in-html-in-fields



    # Link to ProjectForm (class) to display and retrieve data
    projectForm = ProjectForm(request.form)
    plantForm = PlantForm(request.form)
    clientForm = PartyForm(request.form)



    # Initialisation of select fields (plantForm types and suppliers select fields are initialised later on (_addPlant.js), depending on component selected)
    plantForm.country.choices = [(country.id, country.name) for country in Countries.query.all()]

    projectForm.plants.choices = [(plant.id, (plant.name + " --  " + plant.country.name + " --  " + str(plant.capacity_ac) + "MW")) for plant in Plants.query.order_by(desc(Plants.id)).all()]
    projectForm.client.choices = [(party.id, (party.short + " - " + party.name)) for party in Parties.query.order_by(desc(Parties.id)).all()]
    projectForm.client_role.choices = [(role.id, role.name) for role in ClientsRoles.query.all()]
    projectForm.pm.choices = [(user.staffnum, user.name) for user in Users.query.all()]
    projectForm.pp.choices = [(user.staffnum, user.name) for user in Users.query.all()]



    # If reached through submit & form is completed properly
    if request.method == "POST":

        ## PLANT FORM PROCESSING (MODAL):
        if "submit-plantForm" in request.form:
            
            plantForm = PlantForm(request.form)

            # Re-initialisation of select fields for validation purposes  
            # # Thanks to Raza Ashai for providing solution in youtube comment! - https://www.youtube.com/watch?v=I2dJuNwlIH0&t=170s
            plantForm.country.choices = [(country.id, country.name) for country in Countries.query.all()]

            for formTypes in plantForm.types:
                formTypes.type1.choices = [(types.id, types.name) for types in Types.query.all()]
                formTypes.type2.choices = [(types.id, types.name) for types in Types.query.all()]
                formTypes.supplier.choices = [(suppliers.id, suppliers.name) for suppliers in Suppliers.query.all()]

            # Attempt form validation
            if not plantForm.validate():
                flash(plantForm.errors)
                # Re-initialise other forms
                projectForm = ProjectForm()
                clientForm = PartyForm()
                return render_template('addProject.html', projectForm=projectForm, plantForm=plantForm, clientForm=clientForm)
            
            # Add new plant
            db_newPlant = addNewPlant(plantForm)

            # If result is successful
            try:
                # Check for project code
                db_newPlant.id
                
                # If no error 
                flash('Plant has been added to the database!', 'success')
                
                # Re-initialisation of forms
                plantForm = PlantForm()
                projectForm = ProjectForm()
                clientForm = PartyForm()

                # Re-initialise of select fields
                projectForm.plants.choices = [(plant.id, (plant.name + " --  " + plant.country.name + " --  " + str(plant.capacity_ac) + "MW")) for plant in Plants.query.order_by(desc(Plants.id)).all()]
                projectForm.pm.choices = [(user.staffnum, user.name) for user in Users.query.all()]
                projectForm.pp.choices = [(user.staffnum, user.name) for user in Users.query.all()]
                plantForm.country.choices = [(country.id, country.name) for country in Countries.query.all()]
                
                return render_template('addProject.html', projectForm=projectForm, plantForm=plantForm, clientForm=clientForm)

            except AttributeError:
                # Check whether db.commit() raised errors
                if db_newPlant == False:
                    flash('Please check for unique plant details')
                    # Re-initialisation of other forms
                    projectForm = ProjectForm()
                    clientForm = PartyForm()
                    return render_template('addProject.html', projectForm=projectForm, plantForm=plantForm, clientForm=clientForm)

                # Check whether backend checks are successful
                elif db_newPlant["errors"] != None:
                    flash('Please check plant details')
                    # Re-initialisation of other forms
                    projectForm = ProjectForm()
                    clientForm = PartyForm()
                    return render_template('addProject.html', projectForm=projectForm, plantForm=db_newPlant["errors"], clientForm=clientForm)
                
                else:
                    flash('An error has occured, please check plant details')
                    # Re-initialisation of other forms
                    projectForm = ProjectForm()
                    clientForm = PartyForm()
                    return render_template('addProject.html', projectForm=projectForm, plantForm=plantForm, clientForm=clientForm)

        ## PROJECT FORM PROCESSING:
        elif "submit-projectForm" in request.form: 

            # Re-initialisation of select fields for validation purposes
            projectForm.plants.choices = [(plant.id, (plant.name + " --  " + plant.country.name + " --  " + str(plant.capacity_ac) + "MW")) for plant in Plants.query.all()]
            projectForm.client.choices = [(party.id, (party.short + " - " + party.name)) for party in Parties.query.order_by(desc(Parties.id)).all()]
            projectForm.client_role.choices = [(role.id, role.name) for role in ClientsRoles.query.all()]
            projectForm.pm.choices = [(user.staffnum, user.name) for user in Users.query.all()]
            projectForm.pp.choices = [(user.staffnum, user.name) for user in Users.query.all()]

            if not projectForm.validate():
                flash(projectForm.errors)
                return render_template('addProject.html', projectForm=projectForm, plantForm=plantForm, clientForm=clientForm)
            
            # Add new project
            db_newProject = addNewProject(projectForm)

            # If result is successful
            try:
                # Check for project code
                db_newProject.code
                flash('Project has been added to the database!', 'success')
                return redirect("./")

            except AttributeError:
                # Check whether db.commit() raised errors
                if db_newProject == False:
                    flash('Please check for unique project details (code & name)', 'danger')
                    return render_template('addProject.html', projectForm=projectForm, plantForm=plantForm, clientForm=clientForm)

                # Check whether backend checks are successful
                elif db_newProject["errors"]:
                    flash('Please check project details', 'danger')
                    return render_template('addProject.html', projectForm=db_newProject["errors"], plantForm=plantForm, clientForm=clientForm)
                
                else:
                    flash('An error has occured, please check project details', 'danger')
                    return render_template('addProject.html', projectForm=projectForm, plantForm=plantForm, clientForm=clientForm)
            
    
    # User reached route via GET (as by clicking a link or via redirect) OR the form is has empty fields
    else:
        return render_template('addProject.html', projectForm=projectForm, plantForm=plantForm, clientForm=clientForm)

# Allows user to add new plant
@app.route('/addPlant', methods=["GET", "POST"])
@login_required
def addPlant():

    # Link between WTForms (PlantForm) and html (request.form) -- to display and retrieve data
    plantForm = PlantForm(request.form)
    partyForm = PartyForm(request.form)
    print(plantForm)

    # Initialisation of select fields (types and suppliers select fields are initialised later on (_addPlant.js), depending on component selected)
    plantForm.country.choices = [(country.id, country.name) for country in Countries.query.all()]
    for partaker in plantForm.partaker.entries:
        partaker.choices = [(party.id, party.name) for party in Parties.query.all()]
    for partaker_role in plantForm.partaker_role.entries:
        partaker_role.choices = [(role.id, role.name) for role in PartakersRoles.query.all()]

    # If reached through submit button
    if request.method == "POST":

        ## PLANT FORM PROCESSING:
        if "submit-plantForm" in request.form:
            
            plantForm = PlantForm(request.form)

            # Re-initialisation of select fields for validation purposes  
            # # Thanks to Raza Ashai for providing solution in youtube comment! - https://www.youtube.com/watch?v=I2dJuNwlIH0&t=170s
            plantForm.country.choices = [(country.id, country.name) for country in Countries.query.all()]

            for formTypes in plantForm.types:
                formTypes.type1.choices = [(types.id, types.name) for types in Types.query.all()]
                formTypes.type2.choices = [(types.id, types.name) for types in Types.query.all()]
                formTypes.supplier.choices = [(suppliers.id, suppliers.name) for suppliers in Suppliers.query.all()]

            # Attempt form validation
            if not plantForm.validate():

                flash(plantForm.errors)

                # Re-initialise other forms
                partyForm = PartyForm()
                return render_template('addProject.html', plantForm=plantForm, partyForm=partyForm)
            
            # Add new plant
            db_newPlant = addNewPlant(plantForm)

            # If result is successful
            try:
                # Check for project code
                db_newPlant.id
                
                # If no error 
                flash('Plant has been added to the database!', 'success')
                
                # Re-initialisation of all forms
                plantForm = PlantForm()
                partyForm = PartyForm()

                # Re-initialise of select fields
                plantForm.country.choices = [(country.id, country.name) for country in Countries.query.all()]
                
                return render_template('addProject.html', plantForm=plantForm, partyForm=partyForm)

            except AttributeError:
                # Check whether db.commit() raised errors
                if db_newPlant == False:
                    flash('Please check for unique plant details')
                    # Re-initialisation of other forms
                    projectForm = ProjectForm()
                    partyForm = PartyForm()
                    return render_template('addProject.html', plantForm=plantForm, partyForm=partyForm)

                # Check whether backend checks are successful
                elif db_newPlant["errors"] != None:
                    flash('Please check plant details')
                    # Re-initialisation of other forms
                    projectForm = ProjectForm()
                    partyForm = PartyForm()
                    return render_template('addProject.html', plantForm=db_newPlant["errors"], partyForm=partyForm)
                
                else:
                    flash('An error has occured, please check plant details')
                    # Re-initialisation of other forms
                    projectForm = ProjectForm()
                    partyForm = PartyForm()
                    return render_template('addProject.html', plantForm=plantForm, partyForm=partyForm)


        ## PARTY FORM PROCESSING
        elif "submit-partyForm" in request.form:
            flash('ADD PARTY', 'success')
            return render_template('addPlant.html', plantForm=plantForm, partyForm=partyForm)

    # User reached route via GET (as by clicking a link or via redirect) OR the form is has empty fields
    else:
        return render_template('addPlant.html', plantForm=plantForm, partyForm=partyForm)

# Allows user to add new projects
@app.route('/addParty', methods=["GET", "POST"])
@login_required
def addParty():

    # Link to AddProjectForm (class) to display and retrieve data
    clientForm = PartyForm(request.form)

    # Initialisation of select fields (plantForm types and suppliers select fields are initialised later on (_addPlant.js), depending on component selected)
    clients = ClientsRoles.query.all()
    clientForm.clientRole.choices = [(clientRole.id, clientRole.name) for clientRole in ClientsRoles.query.all()]

    # If reached through submit & form is completed properly
    if request.method == "POST":

        # Re-initialisation of select fields for validation purposes 
        #clientForm.clientRole.choices = [(clientRole.id, clientRole.name) for clientRole in ClientsRoles.query.all()]

        if not clientForm.validate():
            flash(clientForm.errors)
            return render_template('addClient.html', form=clientForm)
        
        ## FETCH DATA
        name = clientForm.name.data
        short = clientForm.short.data
        clientRole = clientForm.clientRole.data
        comment = clientForm.comment.data

        ## CHECK DATA
        form_errors = False

        # Check name for duplicates
        db_party = Parties.query.filter_by(name=name).first()
        if db_party != None:
            form_errors = True
            clientForm.name.errors.append('A party is already registered under that name. See party with ID ' + str(db_party.id))
        
        # Check short name for duplicates
        db_party = Parties.query.filter_by(short=short).first()
        if db_party != None:
            form_errors = True
            clientForm.short.errors.append('A party is already registered under that name. See ' + str(db_party.name))
            
        if form_errors == True:
            flash('Please check party does not already exist', 'danger')
            return render_template('addClient.html', form=clientForm)
    
        ## CREATE NEW CLIENT
        # Create new party
        db_newParty = Parties(
            name = name,
            short = short,
            comments=comment
        )
        db.session.add(db_newParty)

        # Commit session to database & check for integrity errors
        try:
            # Updating database
            db.session.commit()

        # Checks for primary key, null and uniques - returns an integrity error if clash occurs
        except IntegrityError:
            # Rollback changes
            db.session.rollback()
            flash('Please check party has not already been registered', 'danger')
            return render_template('addClient.html', form=clientForm)

        # Find client role
        db_clientrole = ClientsRoles.query.filter_by(id=clientRole).first()
        # Associate party to new client
        db_newClient = Clients(
            party_id = db_newParty.id,
            client_role_id = db_clientrole.id
        )
        db.session.add(db_newClient)

        # Commit session to database & check for integrity errors
        try:
            # Updating database
            db.session.commit()
            # Redirect user to home page
            flash('Client has been registered in database', 'success')
            return redirect('./')

        # Checks for primary key, null and uniques - returns an integrity error if clash occurs
        except IntegrityError:
            # Rollback changes
            db.session.rollback()
            flash('Please check client has not already been registered', 'danger')
            return render_template('addClient.html', form=clientForm)


    # User reached route via GET (as by clicking a link or via redirect) OR the form is has empty fields
    else:
        return render_template('addClient.html', form=clientForm)




'''
# Allows user to update their projects
@app.route('/models', methods=["GET", "POST"])
@login_required
def models():

    # Link to AddProjectForm (class) to display and retrieve data
    form = Models(request.form)


    # If reached through submit & form is completed properly
    if request.method == "POST" and form.validate():

        # GET DATA FROM FORM
        
        # SANITY CHECKS:
       
        # CREATE NEW INSTANCE(S)
        model1 = Models(
            name='STP-72P Vfw',
            power='350W',
            energy='',                              
            char1='72 cells',                       # Manual select field for PV modules
            char2='bifacial',                       # Manual select field for PV modules
            comments='High PID, Common Hotspots',
            supplier='Suntech',                     # Ref to supplier table
            component='PV Module'                   # Ref to component table
            )
        
        # ADD NEW INSTANCE(S)
        db.session.add(model1)


        # CREATE RELATIONSHIPS
        # Find components & suppliers in database
        db_code = Projects.query.filter_by(code=code).first()
        
        # Add instance(s) to components
        db_code.component.append(model1)


        try:
            # Updating database
            db.session.commit()

            # Inform of successful operation
            flash('PV has been registered!', 'success')

        # Checks for primary key, null and uniques - returns an integrity error if clash occurs
        except IntegrityError:
            # Rollback changes
            db.session.rollback()
            
            # Inform of integrity error
            flash('Integrity Error! Cannot add this project.', 'danger')
            
            # Return to register page
            return render_template("addProject.html", form=form)

        # Redirect user to home page
        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect) OR the form is has empty fields
    else:
        return render_template('addProject.html', form=form)
'''

'''
@app.route('/suppliers', methods=["GET", "POST"])
@login_required
def suppliers():

    # Link to AddProjectForm (class) to display and retrieve data
    form = Models(request.form)


    # If reached through submit & form is completed properly
    if request.method == "POST" and form.validate():

        # GET DATA FROM FORM
        
        # SANITY CHECKS:
       
        # CREATE NEW INSTANCE(S)
        supplier1 = Suppliers(
            name='Suntech',                            
            comments='Bankrupt - bought by JA Solar in 2016',
            models='STP-72P-Vf, STP-72P-Vfw',       # Ref to model table
            component='PV ModuleS'                   # Ref to component table
            )
        
        # ADD NEW INSTANCE(S)
        db.session.add(supplier1)

        # CREATE RELATIONSHIPS
        # Find components & suppliers in database
        db_code = Projects.query.filter_by(code=code).first()
        
        # Add instance(s) to components
        db_code.component.append(supplier1)


        try:
            # Updating database
            db.session.commit()

            # Inform of successful operation
            flash('PV has been registered!', 'success')

        # Checks for primary key, null and uniques - returns an integrity error if clash occurs
        except IntegrityError:
            # Rollback changes
            db.session.rollback()
            
            # Inform of integrity error
            flash('Integrity Error! Cannot add this project.', 'danger')
            
            # Return to register page
            return render_template("addProject.html", form=form)

        # Redirect user to home page
        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect) OR the form is has empty fields
    else:
        return render_template('addProject.html', form=form)
'''


## HELPERS ROUTES

# Region dropdown menu filtering
@app.route('/add/<region>')
def region(region):

    # Search database for all countries in region
    countries = Countries.query.filter_by(region=region).all()

    # Create 'result array'
    countryArray = []

    # Create new country object for each result and append to 'result array' 
    for country in countries:
        countryObj = {}
        countryObj['id'] = country.id
        countryObj['name'] = country.name
        countryArray.append(countryObj)

    # Return json version of 'result array'
    return jsonify({'countries' : countryArray})


# Region dropdown menu filtering
@app.route('/FilterComponents/<tech>')
def filterComponents(tech):

    # Search database for requested technology
    technologies = Technologies.query.filter_by(short=tech).first()

    # Search database for all asociated components
    components = technologies.components.all()

    # Create JSON of components inside componentsArray
    componentsArray = []
    for component in components:
        componentObj = {}
        componentObj['id'] = component.id
        componentObj['name'] = component.name
        componentsArray.append(componentObj)

    # Return JSON of componentsArray
    return jsonify({'components' : componentsArray})



# Technologies - Components dropdown menu filtering
@app.route('/FilterTypes/<component>')
def filterTypes(component):

    response = {}

    # Search database for requested component
    components = Components.query.filter_by(name=component).first()
    componentObj = {}
    componentObj['id'] = components.id
    componentObj['name'] = components.name
    # Return obj of IDs and names
    response['component'] = componentObj

    # Search database for all asociated types
    component_types = Types.query.filter_by(component_id=components.id).all()
    typeArray = []
    for types in component_types:
        typeObj = {}
        typeObj['id'] = types.id
        typeObj['name'] = types.name
        typeArray.append(typeObj)
    # Return obj of IDs and names
    response['type'] = typeArray

    # Search database for all asociated suppliers 
    component_suppliers = components.suppliers
    supplierArray = []
    for suppliers in component_suppliers:
        supplierObj = {}
        supplierObj['id'] = suppliers.id
        supplierObj['name'] = suppliers.name
        supplierArray.append(supplierObj)
    # Return obj of IDs and names
    response['supplier'] = supplierArray


    # Return JSON of typesArray
    return jsonify(response)





## !DEVELOPMENT ONLY! ##
## HIDDEN ROUTES FOR RESETTING DATABASE

@app.route('/addTestData')
@login_required
def addTestData():

    test_Staff()

    test_Countries()
    test_Roles()
    test_ClientsRoles()
    test_PartakersRoles()
    test_Services()

    test_Technologies()
    test_Components()

    test_BOSTypes()
    test_PVTypes()
    test_CSPTypes()
    test_OtherTypes()

    test_PVModuleSuppliers()
    test_InverterSuppliers()
    test_TrackerSuppliers()
    test_OtherSuppliers()

    return redirect('/')


#  Route to add list of staff
@app.route('/test_Staff')
@login_required
def test_Staff():


    user = Users(staffnum="123456", name="John Doe", passwordHash="admin", email="John.Doe@email.com")
    db.session.add(user)

    user = Users(staffnum="123457", name="Paul Smith", passwordHash="admin", email="Paul.Smith@email.com")
    db.session.add(user)

    user = Users(staffnum="123458", name="Elsa Rice", passwordHash="admin", email="Elsa.Rice@email.com")
    db.session.add(user)
    
    user = Users(staffnum="123459", name="Freda Moss", passwordHash="admin", email="Freda.Moss@email.com")
    db.session.add(user)

    user = Users(staffnum="123460", name="Steven Pratt", passwordHash="admin", email="Steven.Pratt@email.com")
    db.session.add(user)



    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Staff members have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These staff members are already registered', 'danger')
        
        # Return to register page
        return render_template("home.html")

    
    
    return render_template('home.html')


#  Route to add list of countries, sub-regions and regions into 'Countries' table
@app.route('/test_Countries')
@login_required
def test_Countries():

    country0 = Countries(id='nul', name="All", sub_region="World Wide", region="World Wide")
    country1 = Countries(id="af", name="Afghanistan", sub_region="Southern Asia", region="MESA")
    country2 = Countries(id="al", name="Albania", sub_region="Eastern Europe", region="EUNA")
    country3 = Countries(id="dz", name="Algeria", sub_region="Northern Africa", region="EUNA")
    country4 = Countries(id="ao", name="Angola", sub_region="Middle Africa", region="EUNA")
    country5 = Countries(id="ar", name="Argentina", sub_region="South America", region="NASA")
    country6 = Countries(id="am", name="Armenia", sub_region="Middle East", region="MESA")
    country7 = Countries(id="aw", name="Aruba", sub_region="Caribbean", region="NASA")
    country8 = Countries(id="au", name="Australia", sub_region="Oceania", region="APNA")
    country9 = Countries(id="at", name="Austria", sub_region="Western Europe", region="EUNA")
    country10 = Countries(id="az", name="Azerbaijan", sub_region="Middle East", region="MESA")
    country11 = Countries(id="bs", name="Bahamas", sub_region="Caribbean", region="NASA")
    country12 = Countries(id="bh", name="Bahrain", sub_region="Middle East", region="MESA")
    country13 = Countries(id="bd", name="Bangladesh", sub_region="Southern Asia", region="MESA")
    country14 = Countries(id="bb", name="Barbados", sub_region="Caribbean", region="NASA")
    country15 = Countries(id="by", name="Belarus", sub_region="Eastern Europe", region="EUNA")
    country16 = Countries(id="be", name="Belgium", sub_region="Western Europe", region="EUNA")
    country17 = Countries(id="bz", name="Belize", sub_region="Central America", region="NASA")
    country18 = Countries(id="bj", name="Benin", sub_region="Western Africa", region="EUNA")
    country19 = Countries(id="bt", name="Bhutan", sub_region="Southern Asia", region="MESA")
    country20 = Countries(id="bo", name="Bolivia", sub_region="South America", region="NASA")
    country21 = Countries(id="ba", name="Bosnia", sub_region="Eastern Europe", region="EUNA")
    country22 = Countries(id="bw", name="Botswana", sub_region="Southern Africa", region="EUNA")
    country23 = Countries(id="br", name="Brazil", sub_region="South America", region="NASA")
    country24 = Countries(id="bn", name="Brunei", sub_region="South-Eastern Asia", region="APNA")
    country25 = Countries(id="bg", name="Bulgaria", sub_region="Eastern Europe", region="EUNA")
    country26 = Countries(id="bf", name="Burkina Faso", sub_region="Western Africa", region="EUNA")
    country27 = Countries(id="mm", name="Burma", sub_region="South-Eastern Asia", region="APNA")
    country28 = Countries(id="bi", name="Burundi", sub_region="Eastern Africa", region="EUNA")
    country29 = Countries(id="kh", name="Cambodia", sub_region="South-Eastern Asia", region="APNA")
    country30 = Countries(id="cm", name="Cameroon", sub_region="Middle Africa", region="EUNA")
    country31 = Countries(id="ca", name="Canada", sub_region="North America", region="NASA")
    country32 = Countries(id="cv", name="Cape Verde", sub_region="Western Africa", region="EUNA")
    country33 = Countries(id="cf", name="Central African Republic", sub_region="Middle Africa", region="EUNA")
    country34 = Countries(id="td", name="Chad", sub_region="Middle Africa", region="EUNA")
    country35 = Countries(id="ce", name="Channel Islands", sub_region="Western Europe", region="EUNA")
    country36 = Countries(id="cl", name="Chile", sub_region="South America", region="NASA")
    country37 = Countries(id="cn", name="China", sub_region="Eastern Asia", region="APNA")
    country38 = Countries(id="co", name="Colombia", sub_region="South America", region="NASA")
    country39 = Countries(id="km", name="Comoros", sub_region="Eastern Africa", region="EUNA")
    country40 = Countries(id="cg", name="Congo", sub_region="Middle Africa", region="EUNA")
    country41 = Countries(id="cd", name="DR Congo", sub_region="Middle Africa", region="EUNA")
    country42 = Countries(id="cr", name="Costa Rica", sub_region="Central America", region="NASA")
    country43 = Countries(id="ci", name="Côte d'Ivoire", sub_region="Western Africa", region="EUNA")
    country44 = Countries(id="hr", name="Croatia", sub_region="Eastern Europe", region="EUNA")
    country45 = Countries(id="cu", name="Cuba", sub_region="Caribbean", region="NASA")
    country46 = Countries(id="cy", name="Cyprus", sub_region="Middle East", region="MESA")
    country47 = Countries(id="cz", name="Czech Republic", sub_region="Eastern Europe", region="EUNA")
    country48 = Countries(id="dk", name="Denmark", sub_region="Western Europe", region="EUNA")
    country49 = Countries(id="dj", name="Djibouti", sub_region="Eastern Africa", region="EUNA")
    country50 = Countries(id="do", name="Dominican Republic", sub_region="Caribbean", region="NASA")
    country51 = Countries(id="ec", name="Ecuador", sub_region="South America", region="NASA")
    country52 = Countries(id="eg", name="Egypt", sub_region="Northern Africa", region="EUNA")
    country53 = Countries(id="sv", name="El Salvador", sub_region="Central America", region="NASA")
    country54 = Countries(id="gb", name="England", sub_region="Western Europe", region="EUNA")
    country55 = Countries(id="gq", name="Equatorial Guinea", sub_region="Middle Africa", region="EUNA")
    country56 = Countries(id="er", name="Eritrea", sub_region="Eastern Africa", region="EUNA")
    country57 = Countries(id="ee", name="Estonia", sub_region="Eastern Europe", region="EUNA")
    country58 = Countries(id="et", name="Ethiopia", sub_region="Eastern Africa", region="EUNA")
    country59 = Countries(id="eu", name="Fiji", sub_region="Oceania", region="APNA")
    country60 = Countries(id="fi", name="Finland", sub_region="Western Europe", region="EUNA")
    country61 = Countries(id="fr", name="France", sub_region="Western Europe", region="EUNA")
    country62 = Countries(id="gf", name="French Guiana", sub_region="South America", region="NASA")
    country63 = Countries(id="pf", name="French Polynesia", sub_region="Oceania", region="APNA")
    country64 = Countries(id="ga", name="Gabon", sub_region="Middle Africa", region="EUNA")
    country65 = Countries(id="gm", name="Gambia", sub_region="Western Africa", region="EUNA")
    country66 = Countries(id="ge", name="Georgia", sub_region="Middle East", region="MESA")
    country67 = Countries(id="de", name="Germany", sub_region="Western Europe", region="EUNA")
    country68 = Countries(id="gh", name="Ghana", sub_region="Western Africa", region="EUNA")
    country69 = Countries(id="gr", name="Greece", sub_region="Eastern Europe", region="EUNA")
    country70 = Countries(id="gd", name="Grenada", sub_region="Caribbean", region="NASA")
    country71 = Countries(id="gp", name="Guadeloupe", sub_region="Caribbean", region="NASA")
    country72 = Countries(id="gu", name="Guam", sub_region="Oceania", region="APNA")
    country73 = Countries(id="gt", name="Guatemala", sub_region="Central America", region="NASA")
    country74 = Countries(id="gw", name="Guinea-Bissau", sub_region="Western Africa", region="EUNA")
    country75 = Countries(id="gn", name="Guinea", sub_region="Western Africa", region="EUNA")
    country76 = Countries(id="gy", name="Guyana", sub_region="South America", region="NASA")
    country77 = Countries(id="ht", name="Haiti", sub_region="Caribbean", region="NASA")
    country78 = Countries(id="hn", name="Honduras", sub_region="Central America", region="NASA")
    country79 = Countries(id="hu", name="Hungary", sub_region="Eastern Europe", region="EUNA")
    country80 = Countries(id="is", name="Iceland", sub_region="Western Europe", region="EUNA")
    country81 = Countries(id="in", name="India", sub_region="Southern Asia", region="MESA")
    country82 = Countries(id="id", name="Indonesia", sub_region="South-Eastern Asia", region="APNA")
    country83 = Countries(id="ir", name="Iran", sub_region="Southern Asia", region="MESA")
    country84 = Countries(id="iq", name="Iraq", sub_region="Middle East", region="MESA")
    country85 = Countries(id="ie", name="Ireland ", sub_region="Western Europe", region="EUNA")
    country86 = Countries(id="il", name="Israel", sub_region="Middle East", region="MESA")
    country87 = Countries(id="it", name="Italy", sub_region="Western Europe", region="EUNA")
    country88 = Countries(id="jm", name="Jamaica", sub_region="Caribbean", region="NASA")
    country89 = Countries(id="jp", name="Japan", sub_region="Eastern Asia", region="APNA")
    country90 = Countries(id="jo", name="Jordan", sub_region="Middle East", region="MESA")
    country91 = Countries(id="kz", name="Kazakhstan", sub_region="Central Asia", region="EUNA")
    country92 = Countries(id="ke", name="Kenya", sub_region="Eastern Africa", region="EUNA")
    country93 = Countries(id="kw", name="Kuwait", sub_region="Middle East", region="MESA")
    country94 = Countries(id="kg", name="Kyrgyzstan", sub_region="Central Asia", region="EUNA")
    country95 = Countries(id="la", name="Laos", sub_region="South-Eastern Asia", region="APNA")
    country96 = Countries(id="lv", name="Latvia", sub_region="Eastern Europe", region="EUNA")
    country97 = Countries(id="lb", name="Lebanon", sub_region="Middle East", region="MESA")
    country98 = Countries(id="ls", name="Lesotho", sub_region="Southern Africa", region="EUNA")
    country99 = Countries(id="lr", name="Liberia", sub_region="Western Africa", region="EUNA")
    country100 = Countries(id="ly", name="Libya", sub_region="Northern Africa", region="EUNA")
    country101 = Countries(id="li", name="Liechtenstein", sub_region="Western Europe", region="EUNA")
    country102 = Countries(id="lt", name="Lithuania", sub_region="Eastern Europe", region="EUNA")
    country103 = Countries(id="lu", name="Luxembourg", sub_region="Western Europe", region="EUNA")
    country104 = Countries(id="mk", name="Macedonia", sub_region="Eastern Europe", region="EUNA")
    country105 = Countries(id="mg", name="Madagascar", sub_region="Eastern Africa", region="EUNA")
    country106 = Countries(id="mw", name="Malawi", sub_region="Eastern Africa", region="EUNA")
    country107 = Countries(id="my", name="Malaysia", sub_region="South-Eastern Asia", region="APNA")
    country108 = Countries(id="mv", name="Maldives", sub_region="Southern Asia", region="MESA")
    country109 = Countries(id="ml", name="Mali", sub_region="Western Africa", region="EUNA")
    country110 = Countries(id="mt", name="Malta", sub_region="Western Europe", region="EUNA")
    country111 = Countries(id="mq", name="Martinique", sub_region="Caribbean", region="NASA")
    country112 = Countries(id="mr", name="Mauritania", sub_region="Western Africa", region="EUNA")
    country113 = Countries(id="mu", name="Mauritius", sub_region="Eastern Africa", region="EUNA")
    country114 = Countries(id="yt", name="Mayotte", sub_region="Eastern Africa", region="EUNA")
    country115 = Countries(id="mx", name="Mexico", sub_region="Central America", region="NASA")
    country116 = Countries(id="fm", name="Micronesia", sub_region="Oceania", region="APNA")
    country117 = Countries(id="md", name="Moldova", sub_region="Eastern Europe", region="EUNA")
    country118 = Countries(id="mc", name="Monaco", sub_region="Western Europe", region="EUNA")
    country119 = Countries(id="mn", name="Mongolia", sub_region="Eastern Asia", region="APNA")
    country120 = Countries(id="me", name="Montenegro", sub_region="Eastern Europe", region="EUNA")
    country121 = Countries(id="ma", name="Morocco", sub_region="Northern Africa", region="EUNA")
    country122 = Countries(id="mz", name="Mozambique", sub_region="Eastern Africa", region="EUNA")
    country123 = Countries(id="na", name="Namibia", sub_region="Southern Africa", region="EUNA")
    country124 = Countries(id="np", name="Nepal", sub_region="Southern Asia", region="MESA")
    country125 = Countries(id="an", name="Netherlands Antilles", sub_region="Caribbean", region="NASA")
    country126 = Countries(id="nl", name="Netherlands", sub_region="Western Europe", region="EUNA")
    country127 = Countries(id="nc", name="New Caledonia", sub_region="Oceania", region="APNA")
    country128 = Countries(id="nz", name="New Zealand", sub_region="Oceania", region="APNA")
    country129 = Countries(id="ni", name="Nicaragua", sub_region="Central America", region="NASA")
    country130 = Countries(id="ne", name="Niger", sub_region="Western Africa", region="EUNA")
    country131 = Countries(id="ng", name="Nigeria", sub_region="Western Africa", region="EUNA")
    country132 = Countries(id="kp", name="North Korea", sub_region="Eastern Asia", region="APNA")
    country133 = Countries(id="nd", name="Northern Ireland", sub_region="Western Europe", region="EUNA")
    country134 = Countries(id="no", name="Norway", sub_region="Western Europe", region="EUNA")
    country135 = Countries(id="om", name="Oman", sub_region="Middle East", region="MESA")
    country136 = Countries(id="pk", name="Pakistan", sub_region="Southern Asia", region="MESA")
    country137 = Countries(id="ps", name="Palestine", sub_region="Middle East", region="MESA")
    country138 = Countries(id="pa", name="Panama", sub_region="Central America", region="NASA")
    country139 = Countries(id="pg", name="Papua New Guinea", sub_region="Oceania", region="APNA")
    country140 = Countries(id="py", name="Paraguay", sub_region="South America", region="NASA")
    country141 = Countries(id="pe", name="Peru", sub_region="South America", region="NASA")
    country142 = Countries(id="ph", name="Philippines", sub_region="South-Eastern Asia", region="APNA")
    country143 = Countries(id="pl", name="Poland", sub_region="Eastern Europe", region="EUNA")
    country144 = Countries(id="pt", name="Portugal", sub_region="Western Europe", region="EUNA")
    country145 = Countries(id="pr", name="Puerto Rico", sub_region="Caribbean", region="NASA")
    country146 = Countries(id="qa", name="Qatar", sub_region="Middle East", region="MESA")
    country147 = Countries(id="re", name="Réunion", sub_region="Eastern Africa", region="EUNA")
    country148 = Countries(id="ro", name="Romania", sub_region="Eastern Europe", region="EUNA")
    country149 = Countries(id="ru", name="Russia", sub_region="Eastern Europe", region="EUNA")
    country150 = Countries(id="rw", name="Rwanda", sub_region="Eastern Africa", region="EUNA")
    country151 = Countries(id="lc", name="Saint Lucia", sub_region="Caribbean", region="NASA")
    country152 = Countries(id="vc", name="Saint Vincent and the Grenadines", sub_region="Caribbean", region="NASA")
    country153 = Countries(id="ws", name="Samoa", sub_region="Oceania", region="APNA")
    country154 = Countries(id="st", name="Sao Tome and Principe", sub_region="Middle Africa", region="EUNA")
    country155 = Countries(id="sa", name="Saudi Arabia", sub_region="Middle East", region="MESA")
    country156 = Countries(id="sc", name="Scotland", sub_region="Western Europe", region="EUNA")
    country157 = Countries(id="sn", name="Senegal", sub_region="Western Africa", region="EUNA")
    country158 = Countries(id="cs", name="Serbia", sub_region="Eastern Europe", region="EUNA")
    country159 = Countries(id="sl", name="Sierra Leone", sub_region="Western Africa", region="EUNA")
    country160 = Countries(id="sg", name="Singapore", sub_region="South-Eastern Asia", region="APNA")
    country161 = Countries(id="sk", name="Slovakia", sub_region="Eastern Europe", region="EUNA")
    country162 = Countries(id="si", name="Slovenia", sub_region="Eastern Europe", region="EUNA")
    country163 = Countries(id="sb", name="Solomon Islands", sub_region="Oceania", region="APNA")
    country164 = Countries(id="so", name="Somalia", sub_region="Eastern Africa", region="EUNA")
    country165 = Countries(id="za", name="South Africa", sub_region="Southern Africa", region="EUNA")
    country166 = Countries(id="kr", name="South Korea", sub_region="Eastern Asia", region="APNA")
    country167 = Countries(id="es", name="Spain", sub_region="Western Europe", region="EUNA")
    country168 = Countries(id="lk", name="Sri Lanka", sub_region="Southern Asia", region="MESA")
    country169 = Countries(id="sd", name="Sudan", sub_region="Eastern Africa", region="EUNA")
    country170 = Countries(id="sr", name="Suriname", sub_region="South America", region="NASA")
    country171 = Countries(id="sz", name="Swaziland", sub_region="Southern Africa", region="EUNA")
    country172 = Countries(id="se", name="Sweden", sub_region="Western Europe", region="EUNA")
    country173 = Countries(id="ch", name="Switzerland", sub_region="Western Europe", region="EUNA")
    country174 = Countries(id="sy", name="Syria", sub_region="Middle East", region="MESA")
    country175 = Countries(id="tw", name="Taiwan", sub_region="Eastern Asia", region="APNA")
    country176 = Countries(id="tj", name="Tajikistan", sub_region="Central Asia", region="EUNA")
    country177 = Countries(id="tz", name="Tanzania", sub_region="Eastern Africa", region="EUNA")
    country178 = Countries(id="th", name="Thailand", sub_region="South-Eastern Asia", region="APNA")
    country179 = Countries(id="tl", name="Timor-Leste", sub_region="South-Eastern Asia", region="APNA")
    country180 = Countries(id="tg", name="Togo", sub_region="Western Africa", region="EUNA")
    country181 = Countries(id="to", name="Tonga", sub_region="Oceania", region="APNA")
    country182 = Countries(id="tt", name="Trinidad and Tobago", sub_region="Caribbean", region="NASA")
    country183 = Countries(id="tn", name="Tunisia", sub_region="Northern Africa", region="EUNA")
    country184 = Countries(id="tr", name="Turkey", sub_region="Middle East", region="MESA")
    country185 = Countries(id="tm", name="Turkmenistan", sub_region="Central Asia", region="EUNA")
    country186 = Countries(id="ug", name="Uganda", sub_region="Eastern Africa", region="EUNA")
    country187 = Countries(id="ua", name="Ukraine", sub_region="Eastern Europe", region="EUNA")
    country188 = Countries(id="ae", name="United Arab Emirates", sub_region="Middle East", region="MESA")
    country189 = Countries(id="us", name="United States", sub_region="North America", region="NASA")
    country190 = Countries(id="uy", name="Uruguay", sub_region="South America", region="NASA")
    country191 = Countries(id="vi", name="US Virgin Islands", sub_region="Caribbean", region="NASA")
    country192 = Countries(id="uz", name="Uzbekistan", sub_region="Central Asia", region="EUNA")
    country193 = Countries(id="va", name="Vanuatu", sub_region="Oceania", region="APNA")
    country194 = Countries(id="ve", name="Venezuela", sub_region="South America", region="NASA")
    country195 = Countries(id="vn", name="Vietnam", sub_region="South-Eastern Asia", region="APNA")
    country196 = Countries(id="wa", name="Wales", sub_region="Western Europe", region="EUNA")
    country197 = Countries(id="eh", name="Western Sahara", sub_region="Northern Africa", region="EUNA")
    country198 = Countries(id="ye", name="Yemen", sub_region="Middle East", region="MESA")
    country199 = Countries(id="zm", name="Zambia", sub_region="Eastern Africa", region="EUNA")
    country200 = Countries(id="zw", name="Zimbabwe", sub_region="Eastern Africa", region="EUNA")
    
    db.session.add(country0)
    db.session.add(country1)
    db.session.add(country2)
    db.session.add(country3)
    db.session.add(country4)
    db.session.add(country5)
    db.session.add(country6)
    db.session.add(country7)
    db.session.add(country8)
    db.session.add(country9)
    db.session.add(country10)
    db.session.add(country11)
    db.session.add(country12)
    db.session.add(country13)
    db.session.add(country14)
    db.session.add(country15)
    db.session.add(country16)
    db.session.add(country17)
    db.session.add(country18)
    db.session.add(country19)
    db.session.add(country20)
    db.session.add(country21)
    db.session.add(country22)
    db.session.add(country23)
    db.session.add(country24)
    db.session.add(country25)
    db.session.add(country26)
    db.session.add(country27)
    db.session.add(country28)
    db.session.add(country29)
    db.session.add(country30)
    db.session.add(country31)
    db.session.add(country32)
    db.session.add(country33)
    db.session.add(country34)
    db.session.add(country35)
    db.session.add(country36)
    db.session.add(country37)
    db.session.add(country38)
    db.session.add(country39)
    db.session.add(country40)
    db.session.add(country41)
    db.session.add(country42)
    db.session.add(country43)
    db.session.add(country44)
    db.session.add(country45)
    db.session.add(country46)
    db.session.add(country47)
    db.session.add(country48)
    db.session.add(country49)
    db.session.add(country50)
    db.session.add(country51)
    db.session.add(country52)
    db.session.add(country53)
    db.session.add(country54)
    db.session.add(country55)
    db.session.add(country56)
    db.session.add(country57)
    db.session.add(country58)
    db.session.add(country59)
    db.session.add(country60)
    db.session.add(country61)
    db.session.add(country62)
    db.session.add(country63)
    db.session.add(country64)
    db.session.add(country65)
    db.session.add(country66)
    db.session.add(country67)
    db.session.add(country68)
    db.session.add(country69)
    db.session.add(country70)
    db.session.add(country71)
    db.session.add(country72)
    db.session.add(country73)
    db.session.add(country74)
    db.session.add(country75)
    db.session.add(country76)
    db.session.add(country77)
    db.session.add(country78)
    db.session.add(country79)
    db.session.add(country80)
    db.session.add(country81)
    db.session.add(country82)
    db.session.add(country83)
    db.session.add(country84)
    db.session.add(country85)
    db.session.add(country86)
    db.session.add(country87)
    db.session.add(country88)
    db.session.add(country89)
    db.session.add(country90)
    db.session.add(country91)
    db.session.add(country92)
    db.session.add(country93)
    db.session.add(country94)
    db.session.add(country95)
    db.session.add(country96)
    db.session.add(country97)
    db.session.add(country98)
    db.session.add(country99)
    db.session.add(country100)
    db.session.add(country101)
    db.session.add(country102)
    db.session.add(country103)
    db.session.add(country104)
    db.session.add(country105)
    db.session.add(country106)
    db.session.add(country107)
    db.session.add(country108)
    db.session.add(country109)
    db.session.add(country110)
    db.session.add(country111)
    db.session.add(country112)
    db.session.add(country113)
    db.session.add(country114)
    db.session.add(country115)
    db.session.add(country116)
    db.session.add(country117)
    db.session.add(country118)
    db.session.add(country119)
    db.session.add(country120)
    db.session.add(country121)
    db.session.add(country122)
    db.session.add(country123)
    db.session.add(country124)
    db.session.add(country125)
    db.session.add(country126)
    db.session.add(country127)
    db.session.add(country128)
    db.session.add(country129)
    db.session.add(country130)
    db.session.add(country131)
    db.session.add(country132)
    db.session.add(country133)
    db.session.add(country134)
    db.session.add(country135)
    db.session.add(country136)
    db.session.add(country137)
    db.session.add(country138)
    db.session.add(country139)
    db.session.add(country140)
    db.session.add(country141)
    db.session.add(country142)
    db.session.add(country143)
    db.session.add(country144)
    db.session.add(country145)
    db.session.add(country146)
    db.session.add(country147)
    db.session.add(country148)
    db.session.add(country149)
    db.session.add(country150)
    db.session.add(country151)
    db.session.add(country152)
    db.session.add(country153)
    db.session.add(country154)
    db.session.add(country155)
    db.session.add(country156)
    db.session.add(country157)
    db.session.add(country158)
    db.session.add(country159)
    db.session.add(country160)
    db.session.add(country161)
    db.session.add(country162)
    db.session.add(country163)
    db.session.add(country164)
    db.session.add(country165)
    db.session.add(country166)
    db.session.add(country167)
    db.session.add(country168)
    db.session.add(country169)
    db.session.add(country170)
    db.session.add(country171)
    db.session.add(country172)
    db.session.add(country173)
    db.session.add(country174)
    db.session.add(country175)
    db.session.add(country176)
    db.session.add(country177)
    db.session.add(country178)
    db.session.add(country179)
    db.session.add(country180)
    db.session.add(country181)
    db.session.add(country182)
    db.session.add(country183)
    db.session.add(country184)
    db.session.add(country185)
    db.session.add(country186)
    db.session.add(country187)
    db.session.add(country188)
    db.session.add(country189)
    db.session.add(country190)
    db.session.add(country191)
    db.session.add(country192)
    db.session.add(country193)
    db.session.add(country194)
    db.session.add(country195)
    db.session.add(country196)
    db.session.add(country197)
    db.session.add(country198)
    db.session.add(country199)
    db.session.add(country200)

    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Countries have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These countries is already registered', 'danger')
        
        # Return to register page
        return render_template("home.html")
   
    return render_template('home.html')

#  Route to add list of consultant roles
@app.route('/test_Roles')
@login_required
def test_Roles():

    role = Roles(name="Lenders Technical Advisors", short="lta")
    db.session.add(role)

    role = Roles(name="Independent Expert (w/o duty of care)", short="ie")
    db.session.add(role)

    role = Roles(name="Technical Advisor (w/ duty of care)", short="ta")
    db.session.add(role)

    role = Roles(name="Owner's Engineers", short="oe")
    db.session.add(role)
    

    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Consultant roles have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These roles are already registered', 'danger')
        
        # Return to register page
        return render_template("home.html")

    
    
    return render_template('home.html')


#  Route to add list of client roles
@app.route('/test_ClientsRoles')
@login_required
def test_ClientsRoles():

    clientRole = ClientsRoles(name="Lenders / Bank", short="bank")
    db.session.add(clientRole)

    clientRole = ClientsRoles(name="Developer", short="dev")
    db.session.add(clientRole)

    clientRole = ClientsRoles(name="Owner", short="owner")
    db.session.add(clientRole)

    clientRole = ClientsRoles(name="Governmental Body", short="gov")
    db.session.add(clientRole)

    clientRole = ClientsRoles(name="Asset Manager", short="asset")
    db.session.add(clientRole)

    clientRole = ClientsRoles(name="EPC Contractor", short="epc")
    db.session.add(clientRole)

    clientRole = ClientsRoles(name="O&M Contractor", short="om")
    db.session.add(clientRole)

    clientRole = ClientsRoles(name="Equipment Supplier", short="supplier")
    db.session.add(clientRole)
    
    clientRole = ClientsRoles(name="Investment Fund", short="fund")
    db.session.add(clientRole)
    

    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Client roles have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These roles are already registered', 'danger')
        
        # Return to register page
        return render_template("home.html")

    
    
    return render_template('home.html')


#  Route to add list of client roles
@app.route('/test_PartakersRoles')
@login_required
def test_PartakersRoles():

    partakerRoles = PartakersRoles(name="Developer", short="dev")
    db.session.add(partakerRoles)

    partakerRoles = PartakersRoles(name="EPC Contractor", short="epc")
    db.session.add(partakerRoles)

    partakerRoles = PartakersRoles(name="O&M Contractor", short="om")
    db.session.add(partakerRoles)

    partakerRoles = PartakersRoles(name="Offtaker", short="offtaker")
    db.session.add(partakerRoles)

    partakerRoles = PartakersRoles(name="Owner", short="owner")
    db.session.add(partakerRoles)

    partakerRoles = PartakersRoles(name="Asset Manager", short="asset")
    db.session.add(partakerRoles)
    

    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Partakers roles have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These roles are already registered', 'danger')
        
        # Return to register page
        return render_template("home.html")

    
    
    return render_template('home.html')


#  Route to add list of consultant roles
@app.route('/test_Services')
@login_required
def test_Services():

    service = Services(name="Feasibility Study", short="fs")
    db.session.add(service)

    service = Services(name="Fatal Flaw", short="ff")
    db.session.add(service)

    service = Services(name="Due Diligence", short="dd")
    db.session.add(service)

    service = Services(name="Construction Monitoring", short="cm")
    db.session.add(service)

    service = Services(name="Operation Monitoring", short="om")
    db.session.add(service)

    service = Services(name="Buyer Due Diligence", short="bdd")
    db.session.add(service)

    service = Services(name="Vendor Due Diligence", short="vdd")
    db.session.add(service)
    
    service = Services(name="Governmental Advisory", short="gov")
    db.session.add(service)

    service = Services(name="Bankability Study", short="bs")
    db.session.add(service)

    service = Services(name="Dispute Resolution", short="dr")
    db.session.add(service)

    service = Services(name="Energy Yield Assessment", short="eya")
    db.session.add(service)

    service = Services(name="Site Visit", short="sv")
    db.session.add(service)

    service = Services(name="Factory Visit", short="fv")
    db.session.add(service)

    service = Services(name="Other", short="oth")
    db.session.add(service)

    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Consultant roles have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These roles are already registered', 'danger')
        
        # Return to register page
        return render_template("home.html")

    
    
    return render_template('home.html')


#  Route to add list of technologies
@app.route('/test_Technologies')
@login_required
def test_Technologies():

    tech = Technologies(name='Photovoltaics (PV)', short='pv')
    db.session.add(tech)

    tech = Technologies(name='Concentrated Solar Thermal (CSP)', short='csp')
    db.session.add(tech)

    tech = Technologies(name='Onshore Wind', short='windon')
    db.session.add(tech)

    tech = Technologies(name='Offshore Wind', short='windoff')
    db.session.add(tech)

    tech = Technologies(name='Wave', short='wave')
    db.session.add(tech)

    tech = Technologies(name='Tidal', short='tidal')
    db.session.add(tech)

    tech = Technologies(name='Storage', short='storage')
    db.session.add(tech)

    tech = Technologies(name='Balance of Systems', short='bos')
    db.session.add(tech)
        

    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Technologies have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These technologies are already registered in the database', 'danger')
        
        # Return to register page
        return render_template("home.html")

    
    
    return render_template('home.html')


#  Route to add list of components
@app.route('/test_Components')
@login_required
def test_Components():

    # Query database for tech objects
    pv = Technologies.query.filter_by(short='pv').first()
    csp = Technologies.query.filter_by(short='csp').first()
    windon = Technologies.query.filter_by(short='windon').first()
    windoff = Technologies.query.filter_by(short='windoff').first()
    wave = Technologies.query.filter_by(short='wave').first()
    tidal = Technologies.query.filter_by(short='tidal').first()
    bos = Technologies.query.filter_by(short='bos').first()
    storage = Technologies.query.filter_by(short='storage').first()

    # Solar PV
    component = Components(name="PV Module", short="pvModule")
    component.technology.append(pv)
    db.session.add(component)

    component = Components(name="PV Cell", short="pvCell")
    component.technology.append(pv)
    db.session.add(component)

    component = Components(name="Mounting Structure", short="tracker")
    component.technology.append(pv)
    db.session.add(component)

    
    
    # Solar CSP
    component = Components(name="Reflector", short="reflector")
    component.technology.append(csp)
    db.session.add(component)

    component = Components(name="Heating Thermal Fluid", short="htf")
    component.technology.append(csp)
    db.session.add(component)

    component = Components(name="Turbine (Steam)", short="steamTurbine")
    component.technology.append(csp)
    db.session.add(component)

    component = Components(name="Generator (Steam)", short="steamGen")
    component.technology.append(csp)
    db.session.add(component)


    # Wind
    component = Components(name="Turbine (Wind)", short="windTurbine")
    component.technology.append(windon)
    component.technology.append(windoff)
    db.session.add(component)
    

    # Wave
    component = Components(name="Generator (Wave)", short="waveGen")
    component.technology.append(wave)
    db.session.add(component)

    # Tidal
    component = Components(name="Generator (Tidal)", short="tidalGen")
    component.technology.append(tidal)
    db.session.add(component)


    # BOS
    
    component = Components(name="Inverter", short="inverter")
    component.technology.append(bos)
    db.session.add(component)
    
    component = Components(name="Transformer", short="transformer")
    component.technology.append(bos)
    db.session.add(component)

    component = Components(name="Delivery Station", short="substation")
    component.technology.append(bos)
    db.session.add(component)

    component = Components(name="Junction Box", short="junctionbox")
    component.technology.append(bos)
    db.session.add(component)

    component = Components(name="AC Cables", short="cables_ac")
    component.technology.append(bos)
    db.session.add(component)

    component = Components(name="DC Cables", short="cables_dc")
    component.technology.append(bos)
    db.session.add(component)

    component = Components(name="Foundations", short="foundation")
    component.technology.append(windon)
    component.technology.append(windoff)
    db.session.add(component)
    
    component = Components(name="Anchors", short="anchors")
    component.technology.append(windoff)
    component.technology.append(wave)
    component.technology.append(tidal)
    db.session.add(component)


    # Storage    
    component = Components(name="Battery Storage", short="baterryStorage")
    component.technology.append(storage)
    db.session.add(component)
    
    component = Components(name="Thermal Storage", short="thermoStorage")
    component.technology.append(storage)
    db.session.add(component)
    
    component = Components(name="Hydro Storage", short="hydroStorage")
    component.technology.append(storage)
    db.session.add(component)

    component = Components(name="Hydrogen Storage", short="h2Storage")
    component.technology.append(storage)
    db.session.add(component)   
       
    
    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Components have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These Components is already registered', 'danger')
        
        # Return to register page
        return render_template("home.html")
   
    return render_template('home.html')


# TYPES
#  Route to add test BOS types 
@app.route('/test_BOSTypes')
@login_required
def test_BOSTypes():

    # Query database for component objects
    inverter = Components.query.filter_by(short='inverter').first()
    transformer = Components.query.filter_by(short='transformer').first()


    # INVERTER TYPES
    type = Types(name="Central Inverters", short='central', component_id=inverter.id)
    db.session.add(type)

    type = Types(name="String Inverters", short='string', component_id=inverter.id)
    db.session.add(type)

    type = Types(name="Micro Inverters", short='micro', component_id=inverter.id)
    db.session.add(type)

    type = Types(name="Other Inverter Type", short='othInverter', component_id=inverter.id)
    db.session.add(type)


    # TRANSFORMER TYPES
    type = Types(name="Low Voltage", short='lv', component_id=transformer.id)
    db.session.add(type)

    type = Types(name="Medium Voltage", short='mv', component_id=transformer.id)
    db.session.add(type)

    type = Types(name="High Voltage", short='hv', component_id=transformer.id)
    db.session.add(type)

    type = Types(name="Other Transformer Type", short='othTransformer', component_id=transformer.id)
    db.session.add(type)
      
    
    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Types have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These Types are already registered!', 'danger')
        
        # Return to register page
        return render_template("home.html")
   
    return render_template('home.html')

#  Route to add test PV types
@app.route('/test_PVTypes')
@login_required
def test_PVTypes():
    
    pvModule = Components.query.filter_by(short='pvModule').first()
    pvCell = Components.query.filter_by(short='pvCell').first()
    tracker = Components.query.filter_by(short='tracker').first()

    # PV CELL TYPES
    type = Types(name="Poly c-Si", short='polySi', component_id=pvCell.id)
    db.session.add(type)

    type = Types(name="Mono c-Si", short='monoSi', component_id=pvCell.id)
    db.session.add(type)

    type = Types(name="Amorphous c-Si", short='amorphSi', component_id=pvCell.id)
    db.session.add(type)

    type = Types(name="Thin Film (CdTe)", short='cdte', component_id=pvCell.id)
    db.session.add(type)

    type = Types(name="Thin Film (CIGs)", short='cigs', component_id=pvCell.id)
    db.session.add(type)

    type = Types(name="Other Cell Type", short='othCell', component_id=pvCell.id)
    db.session.add(type)


    # PV MODULE TYPES
    type = Types(name="Conventional", short='monoFacial', component_id=pvModule.id)
    db.session.add(type)

    type = Types(name="Bi-facial", short='biFacial', component_id=pvModule.id)
    db.session.add(type)

    type = Types(name="Half-cell", short='half', component_id=pvModule.id)
    db.session.add(type)

    type = Types(name="Concentrated", short='concentrated', component_id=pvModule.id)
    db.session.add(type)

    type = Types(name="Other Module Type", short='othModule', component_id=pvModule.id)
    db.session.add(type)
    

    # MOUNTING STRUCTURE TYPES
    type = Types(name="Fixed Structures", short='fixed', component_id=tracker.id)
    db.session.add(type)

    type = Types(name="Variable Fixed Structures", short='varfixed', component_id=tracker.id)
    db.session.add(type)

    type = Types(name="Single Axis Tracker", short='singleaxis', component_id=tracker.id)
    db.session.add(type)

    type = Types(name="Dual Axis Trakcer", short='dualaxis', component_id=tracker.id)
    db.session.add(type)

    type = Types(name="Floating Structures", short='floating', component_id=tracker.id)
    db.session.add(type)

    type = Types(name="Rooftop Structures", short='rooftop', component_id=tracker.id)
    db.session.add(type)

    type = Types(name="Carport Structures", short='carport', component_id=tracker.id)
    db.session.add(type)

    type = Types(name="Other Structure Type", short='othTracker', component_id=tracker.id)
    db.session.add(type)

    

    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('PV Component types have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! Cannot add component types!', 'danger')
        
        # Return to register page
        return render_template("home.html")

    # Redirect user to home page
    return render_template('home.html')

# Route to add test CSP types
@app.route('/test_CSPTypes')
@login_required
def test_CSPTypes():

    # CSP COMPONENTS
    reflector = Components.query.filter_by(short='reflector').first()
    htf = Components.query.filter_by(short='htf').first()
    steamTurbine = Components.query.filter_by(short='steamTurbine').first()
    steamGen = Components.query.filter_by(short='steamGen').first()


    # REFLECTOR TYPES
    type = Types(name='Tower', short='tower', component_id=reflector.id)
    db.session.add(type)

    type = Types(name='Parabolic Trough', short='trough', component_id=reflector.id)
    db.session.add(type)

    type = Types(name='Parabolic Dish', short='dish', component_id=reflector.id)
    db.session.add(type)

    type = Types(name='Linear Fresnel', short='fresnel', component_id=reflector.id)
    db.session.add(type)

    type = Types(name='Other Reflector Type', short='othReflector', component_id=reflector.id)
    db.session.add(type)


    # HTF TYPES
    type = Types(name='Molten Salt', short='salt', component_id=htf.id)
    db.session.add(type)

    type = Types(name='Saturated Steam', short='steam', component_id=htf.id)
    db.session.add(type)

    type = Types(name='Synthetic Oil', short='oil', component_id=htf.id)
    db.session.add(type)


    # STEAM TURBINES TYPES
    type = Types(name='Steam Turbine Type 1', short='steamTurbine1', component_id=steamTurbine.id)
    db.session.add(type)

    type = Types(name='Steam Turbine Type 2', short='steamTurbine2', component_id=steamTurbine.id)
    db.session.add(type)
    

    # STEAM GENERATOR TYPES
    type = Types(name='Steam Generator Type 1', short='steamGen1', component_id=steamGen.id)
    db.session.add(type)

    type = Types(name='Steam Generator Type 2', short='steamGen2', component_id=steamGen.id)
    db.session.add(type)


    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('CSP Component types have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! Cannot add CSP component types!', 'danger')
        
        # Return to register page
        return render_template("home.html")

    # Redirect user to home page
    return render_template('home.html')

#  Route to add test other types
@app.route('/test_OtherTypes')
@login_required
def test_OtherTypes():

    # Query database for component objects
    windTurbine = Components.query.filter_by(short='windTurbine').first()
    waveGen = Components.query.filter_by(short='waveGen').first()
    tidalGen = Components.query.filter_by(short='tidalGen').first()

    # WIND TURBINES TYPES
    type = Types(name='Direct Current', short='dcturbine', component_id=windTurbine.id)
    db.session.add(type)

    type = Types(name='AC Synchronous Generator', short='synchro', component_id=windTurbine.id)
    db.session.add(type)

    type = Types(name='AC Asynchronous Generator', short='asynchro', component_id=windTurbine.id)
    db.session.add(type)
    

    # WAVE GENERATOR TYPES
    type = Types(name='Attenuator', short='attenuator', component_id=waveGen.id)
    db.session.add(type)

    type = Types(name='Oscillating Water Column', short='column', component_id=waveGen.id)
    db.session.add(type)

    type = Types(name='Oscillating Wave Surge Converter', short='surgeconverter', component_id=waveGen.id)
    db.session.add(type)

    type = Types(name='Overtopping / Terminator', short='overtopterminator', component_id=waveGen.id)
    db.session.add(type)

    type = Types(name='Point Absorber', short='absorber', component_id=waveGen.id)
    db.session.add(type)

    type = Types(name='Rotating Mass', short='rotatingmass', component_id=waveGen.id)
    db.session.add(type)

    type = Types(name='Submerged Pressure Differential', short='pressuredif', component_id=waveGen.id)
    db.session.add(type)

    type = Types(name='Other Wave Generator', short='othWaveGen', component_id=waveGen.id)
    db.session.add(type)


    # TIDAL GENERATOR TYPES
    type = Types(name='	Archimedes Screw', short='screw', component_id=tidalGen.id)
    db.session.add(type)

    type = Types(name='Enclosed tips (Venturi)', short='venturi', component_id=tidalGen.id)
    db.session.add(type)

    type = Types(name='Horizontal Axis Turbine', short='horizontalturbine', component_id=tidalGen.id)
    db.session.add(type)

    type = Types(name='Oscillating Hydrofoil', short='hydrofoil', component_id=tidalGen.id)
    db.session.add(type)

    type = Types(name='Tidal Kite', short='kite', component_id=tidalGen.id)
    db.session.add(type)

    type = Types(name='Vertical Axis Turbine', short='verticalturbine', component_id=tidalGen.id)
    db.session.add(type)

    type = Types(name='Other Tidal Generator', short='othTidalGen', component_id=tidalGen.id)
    db.session.add(type)

    
    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('CSP Component types have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! Cannot add CSP component types!', 'danger')
        
        # Return to register page
        return render_template("home.html")

    # Redirect user to home page
    return render_template('home.html')


# SUPPLIERS
#  Route to add test PV module suppliers
@app.route('/test_PVModuleSuppliers')
@login_required
def test_PVModuleSuppliers():

    # Query database for component objects
    pvModule = Components.query.filter_by(short='pvModule').first()
    pvCell = Components.query.filter_by(short='pvCell').first()


    # MODULE SUPPLIERS
    suppliers = Suppliers(name='BYD', short='byd')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Canadian Solar', short='canadian')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='First Solar', short='first')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Hanwha Q Cell', short='hanwha')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Jinko Solar', short='jinko')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='REC Solar', short='rec')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Risen', short='risen')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Sunergy', short='sunergy')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='SunPower', short='sunpower')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)
    
    suppliers = Suppliers(name='SunTech', short='suntech')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Talesun', short='talesun')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Trina Solar', short='trina')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Yingli', short='yingli')
    suppliers.components.append(pvModule)
    suppliers.components.append(pvCell)
    db.session.add(suppliers)
    
    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('PV Module Suppliers have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These suppliers are already registered!', 'danger')
        
        # Return to register page
        return render_template("home.html")
   
    return render_template('home.html')


#  Route to add test inverter suppliers
@app.route('/test_InverterSuppliers')
@login_required
def test_InverterSuppliers():

    # Query database for component objects
    inverter = Components.query.filter_by(short='inverter').first()


    # INVERTER SUPPLIERS
    suppliers = Suppliers(name='ABB', short='abb')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Conergy', short='conergy')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Fimer', short='fimer')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Gamesa', short='gamesa')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='General Electric', short='ge')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='GPTech', short='gptech')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Huawei', short='huawei')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Ingeteam', short='ingeteam')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='KACO', short='kaco')
    suppliers.components.append(inverter)
    db.session.add(suppliers)
    
    suppliers = Suppliers(name='Power Electronics', short='pe')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Power One', short='powerone')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Satcon', short='satcon')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Schneider Electri', short='schneider')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Siemens', short='siemens')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Sungrow', short='sungrow')
    suppliers.components.append(inverter)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Toshiba & Mitsubishi Electric Corporations (TMEIC)', short='tmeic')
    suppliers.components.append(inverter)
    db.session.add(suppliers)
    
    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Inverter Suppliers have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These suppliers are already registered!', 'danger')
        
        # Return to register page
        return render_template("home.html")
   
    return render_template('home.html')

#  Route to add test tracker suppliers
@app.route('/test_TrackerSuppliers')
@login_required
def test_TrackerSuppliers():

    # Query database for component objects
    tracker = Components.query.filter_by(short='tracker').first()


    # TRACKER SUPPLIERS
    suppliers = Suppliers(name='NexTracker', short='nextracker')
    suppliers.components.append(tracker)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Convert', short='convert')
    suppliers.components.append(tracker)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Heliostat', short='heliostat')
    suppliers.components.append(tracker)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Ideematec Deutschland', short='ideematec')
    suppliers.components.append(tracker)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Soltec', short='soltec')
    suppliers.components.append(tracker)
    db.session.add(suppliers)

    
    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Tracker Suppliers have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These suppliers are already registered!', 'danger')
        
        # Return to register page
        return render_template("home.html")
   
    return render_template('home.html')

#  Route to add test other suppliers
@app.route('/test_OtherSuppliers')
@login_required
def test_OtherSuppliers():

    # http://www.emec.org.uk/marine-energy/wave-developers/
    # http://www.emec.org.uk/marine-energy/tidal-developers/

    # Query database for component objects
    windTurbine = Components.query.filter_by(short='windTurbine').first()
    waveGen = Components.query.filter_by(short='waveGen').first()
    tidaleGen = Components.query.filter_by(short='tidalGen').first()

    # WIND TURBINE SUPPLIERS
    supplier = Suppliers.query.filter_by(short='gamesa').first()
    supplier.components.append(windTurbine)


    supplier = Suppliers.query.filter_by(short='ge').first()
    supplier.components.append(windTurbine)


    suppliers = Suppliers(name='Nordex', short='nordex')
    suppliers.components.append(windTurbine)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Acciona Energia', short='acciona')
    suppliers.components.append(windTurbine)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Mistubishi Power Systems', short='mistubishi')
    suppliers.components.append(windTurbine)
    db.session.add(suppliers)


    # WAVE GENERATOR SUPPLIERS
    suppliers = Suppliers(name='ATA Engineering', short='ata')
    suppliers.components.append(waveGen)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Eco Wave Power', short='ecowave')
    suppliers.components.append(waveGen)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Laminaria', short='laminaria')
    suppliers.components.append(waveGen)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Martifer Energia', short='martifer')
    suppliers.components.append(waveGen)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Aquanet Power', short='aquanet')
    suppliers.components.append(waveGen)
    db.session.add(suppliers)


    # TIDAL GENERATOR SUPPLIERS
    suppliers = Suppliers(name='OpenHydro', short='openhydro')
    suppliers.components.append(tidaleGen)
    db.session.add(suppliers)

    suppliers = Suppliers(name='SeaPower Gen', short='seapower')
    suppliers.components.append(tidaleGen)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Minesto', short='minesto')
    suppliers.components.append(tidaleGen)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Kawasaki Heavy Industries', short='kawasaki')
    suppliers.components.append(tidaleGen)
    db.session.add(suppliers)

    suppliers = Suppliers(name='Nautricity ', short='nautricity')
    suppliers.components.append(tidaleGen)
    db.session.add(suppliers)

    
    try:
        # Updating database
        db.session.commit()

        # Inform of successful operation
        flash('Other Suppliers have been registered!', 'success')

    # Checks for primary key, null and uniques - returns an integrity error if clash occurs
    except IntegrityError:
        # Rollback changes
        db.session.rollback()
        
        # Inform of integrity error
        flash('Integrity Error! These suppliers are already registered!', 'danger')
        
        # Return to register page
        return render_template("home.html")
   
    return render_template('home.html')
 



## RUN PROGRAM (WITH DEBUG MODE)
if __name__ == '__main__':
    app.run()



## TIPS:

# Create users:
#new_user = Users(user_id=6, name='Carlos Reyes',password='12345', staffnum='36548', email='carlos.reyes@mottmac.com')
#db_session.add(new_user)
#db_session.commit()

# Retrieve users:
#q_count = db_session.query(Users).count()
#print(q_count)
#q_user = db_session.query(Users).all()
#for user in q_user:
    #print(f'{user.name}, with staff number {user.staffnum} and email {user.email} is registered in database')

'''
    All = Technologies.query.filter_by(short='all').first()
    pv = Technologies.query.filter_by(short='pv').first()
    csp = Technologies.query.filter_by(short='csp').first()
    
    # Link to correct technology
    All.techs.append(All)
    type2.tech_ref.append(All)
    type3.tech_ref.append(All)
    type4.tech_ref.append(All)
    type5.tech_ref.append(All)
    type6.tech_ref.append(All)
    type7.tech_ref.append(All)
    type8.tech_ref.append(All)
    type9.tech_ref.append(pv)
    type10.tech_ref.append(pv)
    type11.tech_ref.append(pv)
    type12.tech_ref.append(pv)
    type13.tech_ref.append(pv)
    type14.tech_ref.append(pv)
    type15.tech_ref.append(pv)
    type16.tech_ref.append(pv)
    type17.tech_ref.append(pv)
    type18.tech_ref.append(pv)
    type19.tech_ref.append(pv)
    type20.tech_ref.append(pv)
    type21.tech_ref.append(pv)
    type22.tech_ref.append(pv)
    type23.tech_ref.append(pv)
    type24.tech_ref.append(pv)
    type25.tech_ref.append(pv)
    type26.tech_ref.append(pv)
    type27.tech_ref.append(csp)
    type28.tech_ref.append(csp)
    type29.tech_ref.append(csp)
    type30.tech_ref.append(csp)
    type31.tech_ref.append(csp)
    type32.tech_ref.append(csp)
    type33.tech_ref.append(csp)
    type34.tech_ref.append(csp)
    type35.tech_ref.append(csp)
    type36.tech_ref.append(csp)
    type37.tech_ref.append(csp)
    '''