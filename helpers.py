### IMPORTS

# Import Flask enging from app.py
from app import app

# Import SQLAlchemy engine from app.py
from app import db

# Flask imports
from flask import redirect
from flask import session as flask_session





### FUNCTIONS


## ADMIN FUNCTIONS

# Specific import
from functools import wraps

# Login check - @login_required in app.py
def login_required(f):
    # Decorate routes to require login.
    # http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if flask_session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function





## ROUTE HELPER FUNCTIONS


# Import SQLAlchemy models
from models import Users, Projects, Plants, Partakers, Clients, Parties, Countries, Roles, ClientsRoles, PartakersRoles, Technologies, Components, Types, Models, Suppliers, Configurations


# Add a Project to the database
def addNewProject(form):
    # FETCH DATA
        # Get data from form
        code = form.code.data
        name = form.name.data
        plants = form.plants.data
        pm = form.pm.data
        pp = form.pp.data
        site = form.site.data
        role = form.role.data
        dict_services = {
            "fs" : form.fs.data, 
            "ff" : form.ff.data, 
            "eya" : form.eya.data, 
            "dd" : form.dd.data,  
            "cm" : form.cm.data,  
            "om" : form.om.data, 
            "bdd" : form.bdd.data, 
            "vdd" : form.vdd.data, 
            "gov" : form.gov.data, 
            "bs" : form.bs.data, 
            "oth" : form.oth.data
        }

        other = form.other.data
        #description = form.description.data


    # CHECK DATA
        # Perform sanity checks:
        form_errors = False

        # Verify name is not already in use in database:
        db_project = Projects.query.filter_by(name=name).first()
        if db_project!= None:
            form_errors = True
            form.name.errors.append('Project already registered under that name. See project code ' + str(db_project.code))

        # Verify code is not already in use in database:
        db_project = Projects.query.filter_by(code=code).first()
        if not db_project==None:
            form_errors = True
            form.code.errors.append('Project already registered under that code. See project name ' + str(db_project.name))

        # Verify PM and PP are still staffmembers
        db_pm = Users.query.filter_by(staffnum=pm).first()
        db_pp = Users.query.filter_by(staffnum=pp).first()
        if db_pm == None or db_pp == None:
            form_errors = True
            form.pm.errors.append('Project Manager and Project Principal should be current staffmembers')

        # Verify PM and PP are not the same person
        if pm == pp:
            form_errors = True
            form.pm.errors.append('Project Manager and Project Principal should not be the same person.')
            form.pp.errors.append(' ')
            
        # Verify at least one service has been selected        
        if all(boolean == False for key, boolean in dict_services.items()):
            form_errors = True
            for key, boolean in dict_services.items():
                if key == 'eya':
                    form.eya.errors.append('Please select at least one service.')
                else:
                    form[key].errors.append('')

        elif dict_services['oth'] == True and other == '':
            form_errors = True
            form.other.errors.append('Please specify which other service was provided.')
            form.oth.errors.append('')


        # If errors have been found, return form for completion
        if form_errors == True:
            result = { "errors" : form }
            return result


    # CREATE NEW PROJECT IN DATABASE
        # Fetch role from db
        db_role = Roles.query.filter_by(short=role).first()

        # Create new project
        db_project = Projects(
            code=code, 
            name=name, 
            role_id=db_role.id,
            services=dict_services,
            #description=description,
            link=site,
            pm_id=db_pm.staffnum,
            pp_id=db_pp.staffnum
            #client_id=db_client.id
            ) 
        
        db.session.add(db_project)
        
        for plant in plants:
            # Find plant in database
            db_plant = Plants.query.filter_by(id=plant).first()
            # Add project - plants relationship
            db_project.plants.append(db_plant)

        # Commit session to database & check for integrity errors
        try:
            # Updating database
            db.session.commit()
            # Redirect user to home page
            return db_project

        # Checks for primary key, null and uniques - returns an integrity error if clash occurs
        except IntegrityError:
            # Rollback changes
            db.session.rollback()
            result = False
            return result
        

# Add a Plant to the database
def addNewPlant(form):   
    # FETCH DATA FROM FORM

        latitude = form.latitude.data
        longitude = form.longitude.data

        status = form.status.data

        comments = form.comments.data

        techs = {
            ("pv", form.pv.data),
            ("csp", form.csp.data),
            ("windon", form.windon.data),
            ("windoff", form.windoff.data),
            ("wave", form.wave.data),
            ("tidal", form.tidal.data),
            ("storage", form.storage.data),
        }

        type_forms = form.types.entries


    # CHECK DATA 
        form_errors = False

        name_check = Plants.query.filter_by(name=form.name.data).all()
        if name_check:
            form_errors = True
            form.name.errors = {'Please enter a unique plant name'}

        db_country = Countries.query.filter_by(id=form.country.data).first()

        # Check at least one of the capacities was added
        if form.capacity_ac.data == None and form.capacity_dc.data == None:
            form_errors = True
            # For some reason, decimalField's error is a tuple instead of a list..
            form.capacity_ac.errors = {'Please enter the plant capacity (can be estimated then corrected once known)'}
            form.capacity_dc.errors = {''}

        # If both are added, check DC is greater than AC
        elif form.capacity_ac.data !=None and form.capacity_dc.data != None and form.capacity_ac.data > form.capacity_dc.data:
            form_errors = True
            form.capacity_ac.errors = {'Please ensure AC capacity is equal or lower to DC capacity'}
            form.capacity_dc.errors = {''}

        # Check at tech has been selected & find tech ID
        selected_a_technology = False
        techs_selected = {}
        for tech, boolean in techs:
            if boolean == True:
                    technology = Technologies.query.filter_by(short=tech).first()
                    if technology != None:
                        selected_a_technology = True
                        techs_selected[tech] = technology
        if selected_a_technology == False:
            form_errors = True
            form.csp.errors = {'Please select a technology'}

        # If errors have been found, return form errors
        if form_errors == True:
            result = { "errors" : form }
            return result


    # CREATE PLANT IN DATABASE                
        # Create new plant
        db_plant = Plants(
            name=form.name.data,
            country_id=db_country.id,
            capacity_ac=form.capacity_ac.data,
            capacity_dc=form.capacity_dc.data,
            latitude=latitude,
            longitude=longitude,
            status=status,
            comments=comments,
        )

        for technology in techs_selected:
            print(techs_selected[technology])
            db_plant.technologies.append(techs_selected[technology])


        # Add plant to database
        db.session.add(db_plant)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            result = FALSE
            return result



    # CREATE PLANT COMPONENT CONFIGURATION (if filled in)
        # Creates and attachs all components and their respective types to the plant
        for entry in type_forms[1:]:
            
            # Skips template - entry.data['component'] is set automatically when cloning template type form, along with any component          # Should be able to remove due to type_forms[1:]
            if entry.data['component'] == None or entry.data['component'] == '':
                continue

            # Quantity
            if entry.data['quantity'] != None:
                quantity = entry.data['quantity']
                db_configuration = Configurations(plant_id=db_plant.id, quantity = quantity)
            else:
                db_configuration = Configurations(plant_id=db_plant.id)
                

            # Add component configuration to database
            db.session.add(db_configuration)


            # Component:
            db_configuration.component_id = entry.data['component']

            # Type1:
            db_configuration.type1_id = entry.data['type1']

            # Type2:
            if entry.data['type2'] != None:
                db_configuration.type2_id = entry.data['type2']

            # Supplier
            db_configuration.supplier_id = entry.data['supplier']

            # Model
            model = entry.data['model']
            print(model)
            if model != "":
                db_model = Models(
                    name=entry.data['model'],
                    component_id=entry.data['component'],
                    supplier_id=entry.data['supplier'],
                    type1_id=entry.data['type1'])
                if entry.data['type2'] != None:
                    db_model.type2_id = entry.data['type2']
                
                db.session.add(db_model)   

                db_configuration.model_id=db_model.id
            
            db.session.commit()


        result = db_plant
        return result



    