## DOCUMENTATION 
# Documentation of WTForms - https://wtforms.readthedocs.io/en/stable/index.html
# PrettyPrinted tutorial on FormFields https://www.youtube.com/watch?v=ymW_HTzVdjc

# TIPS:
# https://stackoverflow.com/questions/18290142/multiple-forms-in-a-single-page-using-flask-and-wtforms


## WTForms imports
#from flask_wtf import FlaskForm as Form - does not completely work, due to compatibility following latest patch
#from flask_wtf import FlaskForm
from wtforms import Form
from wtforms import StringField
from wtforms import IntegerField
from wtforms import DecimalField
from wtforms import TextAreaField
from wtforms import PasswordField
from wtforms import RadioField
from wtforms import SelectField
from wtforms import SelectMultipleField
from wtforms import BooleanField
from wtforms import DateField
from wtforms import FieldList
from wtforms import FormField
from wtforms import validators



### FORM CLASSES
## Used to generate forms on web and validate for inputs


## ADMINISTRATIVE FORMS:

class LoginForm(Form):
    staffnum = IntegerField('Staff Number', [validators.InputRequired(message='Staff number required.')])
    password = PasswordField('Password', [validators.InputRequired(message='Password required.')])


class RegisterForm(Form):
    name = StringField('Name', [validators.InputRequired('Staff name required (max. 30 char)'), validators.Length(min=1, max=30)])
    staffnum = IntegerField('Staff Number', [validators.InputRequired(message='Staff number required.')])
    password = PasswordField('Password', [validators.InputRequired(), validators.Length(min=1, max=100)])
    confirm = PasswordField('Confirm Password', [validators.InputRequired(), validators.EqualTo('password', message='Passwords do not match.')])
    email = StringField('E-mail address', [validators.InputRequired(message="Email (@mottmac.com) required."), validators.Length(min=1, max=50)])


## REGISTER PROJECT FORMS:

class PartyForm(Form):
    name = StringField('Name', [validators.InputRequired('Entity full name required (max. 50 char)'), validators.Length(min=1, max=50)])
    short = StringField('Abbreviation', [validators.InputRequired('Abbreviation or short name required (max. 20 char)'), validators.Length(min=1, max=20)])
    comments = TextAreaField('Comments', [validators.Optional(), validators.Length(min=0, max=1000)])




class TypeForm(Form):

    # Component field (hidden as automatically filled)
    component = StringField()

    # Following select fields get their 'choices' inputs from @app.route('/addPlant') which will fetch inputs from database

    # (Optional) Types fields (type2 is needed only in case of pvModule / pvCells comp1onents)
    type1 = SelectField('Type', choices=[], coerce=int, validators=[validators.Optional()])
    type2 = SelectField('Cell Type', choices=[], coerce=int, validators=[validators.Optional()])
    
    # (Optional) Fields to be used to add component supplier already registered in database
    supplier = SelectField('Supplier', choices=[], coerce=int, validators=[validators.Optional()])
    
    # (Optional) Fields to be used to add component model already registered in database
    model = StringField('Model', validators=[validators.Length(min=0, max=50)])
    
    # (Optional) number of equipment 
    quantity = IntegerField('Quantity', validators=[validators.optional()])



class PlantForm(Form):
    
    ## PROJECT INFO
    # Following select fields (except status) get their 'choices' inputs from @app.route('/addPlant') which will fetch inputs from database
    name = StringField('Plant name', [validators.DataRequired(), validators.Length(min=1, max=50)])
    country = SelectField('', choices=[])
    capacity_ac = DecimalField('', [validators.optional()])
    capacity_dc = DecimalField('', [validators.optional()])
    longitude = DecimalField('', [validators.optional()])
    latitude = DecimalField('', [validators.optional()])

    status = RadioField('Status', default='fs', choices=[('fs', 'Conception / Feasibility Study'), ('fc', "Reaching Financial Close"), ('con', "Construction"), ('ops', "Operation"), ('ext', "Life Extention"), ('dec', "Decommissioning")])
    fc = DateField('Financial Close', [validators.Optional()])
    cod = DateField('COD', [validators.Optional()])
    ppa = DateField('PPA End Date', [validators.Optional()])

    partaker = FieldList(SelectField('Name', choices=[], coerce=int), min_entries=1, max_entries=10)
    partaker_role = FieldList(SelectField('Role', choices=[], coerce=int), min_entries=1, max_entries=10)

    comments = TextAreaField('Comments', [validators.Length(min=0, max=10000)])
    
    # Checkboxes of each technology
    pv = BooleanField('Photovoltaics (PV)')
    csp = BooleanField('Concentrated Solar Thermal (CSP)')
    windon = BooleanField('Onshore Wind')
    windoff = BooleanField('Offshore Wind')
    wave = BooleanField('Wave')
    tidal = BooleanField('Tidal')
    storage = BooleanField('Energy Storage')

    # Types (Multiple forms)
    types = FieldList(FormField(TypeForm), min_entries=1, max_entries=10)


class ProjectForm(Form):
    
    ## PROJECT INFO
    code = IntegerField('Project code', [validators.InputRequired(message="Please fill in PMD project code.")])
    name = StringField('Project name', [validators.InputRequired(message="Please fill in PMD projec name"), validators.Length(min=1, max=50)])
    
    # PLANTS
    # Following select fields get their 'choices' inputs from @app.route('/addProject') which will fetch inputs from database
    plants = SelectMultipleField('Plant(s)', choices=[], coerce=int)

    # CLIENTS
    client = SelectMultipleField('Name', choices=[], coerce=int)
    client_role = SelectField('Client Role', choices=[], coerce=int)
    confidential = BooleanField('Confidential', [validators.Optional()])

    ## MANAGEMENT
    pm = SelectField('Project Manager', choices=[], coerce=int)
    pp = SelectField('Project Principal', choices=[], coerce=int)
    site = StringField('Project Site', [validators.Length(min=0, max=200), validators.optional()])

    ## ROLE 
    role = RadioField('Role', default='ie', choices=[('ie', 'Independent Engineer'), ('lta', "Lender's Technical Advisors"), ('oe', "Owner's Engineers")])
    
    ## SERVICES
    fs = BooleanField("Feasibility Study", [validators.optional()])
    ff = BooleanField("Fatal Flaw", [validators.optional()])
    eya = BooleanField("Energy Yield Assessment", [validators.optional()])
    dd = BooleanField("Due Diligence", [validators.optional()])
    cm = BooleanField("Construction Monitoring", [validators.optional()])
    om = BooleanField("Operation Monitoring", [validators.optional()])
    bdd = BooleanField("Buyer's Due Diligence", [validators.optional()])
    vdd = BooleanField("Vendor's Due Diligence", [validators.optional()])
    gov = BooleanField("Governmental Study", [validators.optional()])
    bs = BooleanField("Bankability Study", [validators.optional()])
    oth = BooleanField("Other", [validators.optional()])
    other = StringField("Other", [validators.optional()])

    ## STAKEHOLDERS
    #client = SelectField('Client', choices=[])
    #confidential = BooleanField("Confidential Client", [validators.optional()])


    ## DESCRIPTION
    description = TextAreaField('Project Description', [validators.Length(min=0, max=10000), validators.optional()])





