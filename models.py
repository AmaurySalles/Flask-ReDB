# REDB tables - class construction:
# Each class represents a table in the database. The classes allow for simpler table queries (INSERT, SELECT, UPDATE, DELETE, etc.) using db.session


## INSTRUCTIONS
# To add (new) table in the database, create class below then enter following in python terminal window (once in app's folder path):
#   SET FLASK_APP = redb.py
#   python
#   >>> from redb import db
#   >>> db.create_all()
# If an error occurs and/or corrections are made, restart python interpreter (i.e. 'quit()' then 'python')
# If wanting to reset / correct table, ALTER TABLE; and make changes here accordingly.
# If wanting to reset table completely, save information, DROP TABLE; then re-add table using method above (then re-add information to the table)

# Removing many to many relationships
# https://stackoverflow.com/questions/26948397/how-to-delete-records-from-many-to-many-secondary-table-in-sqlalchemy


## IMPORT
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()



### TABLES

technology_component = db.Table('technology_component', 
    db.Column('technology', db.Integer, db.ForeignKey('technologies.id')),
    db.Column('component', db.Integer, db.ForeignKey('components.id'))
)

supplier_type = db.Table('supplier_type',
    db.Column('supplier', db.Integer, db.ForeignKey('suppliers.id')),
    db.Column('type', db.Integer, db.ForeignKey('types.id'))
)

supplier_component = db.Table('supplier_component',
    db.Column('supplier', db.Integer, db.ForeignKey('suppliers.id')),
    db.Column('component', db.Integer, db.ForeignKey('components.id'))
)

plant_partaker = db.Table('plant_partaker',
    db.Column('plant', db.Integer, db.ForeignKey('plants.id')),
    db.Column('partaker', db.Integer, db.ForeignKey('partakers.id'))
)

project_plant = db.Table('project_plant',
    db.Column('project', db.Integer, db.ForeignKey('projects.code')),
    db.Column('plant', db.Integer, db.ForeignKey('plants.id'))
)

plant_technology = db.Table('plant_technology',
    db.Column('plant', db.Integer, db.ForeignKey('plants.id')),
    db.Column('technology', db.Integer, db.ForeignKey('technologies.id'))
)



class Users(db.Model):

    # Table columns
    staffnum = db.Column('staffnum', db.Integer, primary_key=True)
    name = db.Column('name', db.String(30), nullable=False, unique=True)
    passwordHash = db.Column('password', db.String(100), nullable=False, unique=True)
    email = db.Column('email', db.String(50), nullable=False, unique=True)

    project_pm = db.relationship('Projects', backref='pm', primaryjoin='Users.staffnum==Projects.pm_id')
    project_dpm = db.relationship('Projects', backref='dpm', primaryjoin='Users.staffnum==Projects.dpm_id')
    project_pp = db.relationship('Projects', backref='pp', primaryjoin='Users.staffnum==Projects.pp_id')

    # Sets return data {User_# : staffnum}
    def __repr__(self):
        return '<User %r>' % self.staffnum


class Roles(db.Model):

    # Table columns    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    short = db.Column(db.String(10), unique=True, nullable=False)

    # Sets return data {Role_# : id}
    def __repr__(self):
        return '<Role %r>' % self.id


class Services(db.Model):

    # Table columns    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    short = db.Column(db.String(10), unique=True, nullable=False)

    # Sets return data {Service_# : id}
    def __repr__(self):
        return '<Service %r>' % self.id


class Parties(db.Model):

    # Table columns    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    short = db.Column(db.String(10), unique=True, nullable=False)
    comments = db.Column(db.String(1000))

    # Sets return data {Party_# : id}
    def __repr__(self):
        return '<Party %r>' % self.id


class PartakersRoles(db.Model):

    # Table columns    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    short = db.Column(db.String(10), unique=True, nullable=False)

    # Sets return data {PartakersRole_# : id}
    def __repr__(self):
        return '<PartakersRole %r>' % self.id



class ClientsRoles(db.Model):

    # Table columns    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    short = db.Column(db.String(10), unique=True, nullable=False)

    # Sets return data {ClientRole_# : id}
    def __repr__(self):
        return '<ClientRole %r>' % self.id



class Partakers(db.Model):

    # Table columns    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, nullable=False)

    # Relationships
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'))
    partaker_role_id = db.Column(db.Integer, db.ForeignKey('partakers_roles.id'))
  

    # Sets return data {Partaker_# : id}
    def __repr__(self):
        return '<Partaker %r>' % self.id




class Clients(db.Model):

    # Table columns    
    id = db.Column(db.Integer, primary_key=True)
    confidential = db.Column(db.Integer, nullable=False)

    # Relationships
    party_id = db.Column(db.Integer, db.ForeignKey('parties.id'))
    client_role_id = db.Column(db.Integer, db.ForeignKey('clients_roles.id'))

    # Sets return data {Client_# : id}
    def __repr__(self):
        return '<Client %r>' % self.id



class Countries(db.Model):

    # Table columns
    id = db.Column('id', db.String(3), primary_key=True)
    name = db.Column('name', db.String(50), nullable=False, unique=True)
    sub_region = db.Column('sub_region', db.String(30), nullable=False)
    region = db.Column('region', db.String(10), nullable=False)
    
    #Relationships
    plants = db.relationship('Plants', backref='country')
    
    # Sets return data {Country_# : id}
    def __repr__(self):
        return '<Country %r>' % self.id




class Technologies(db.Model):

    # Table columns
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(50), nullable=False, unique=True)
    short = db.Column('short', db.String(10), nullable=False, unique=True)
    comments = db.Column('comments', db.String(1000))

    # Relationships
    components = db.relationship("Components", secondary=technology_component, backref='technology')
    
        
    # Format return data
    def __repr__(self):
        return '<Technology %r>' % self.name



class Components(db.Model):

    # Table columns
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(30), nullable=False, unique=True)
    short = db.Column('short', db.String(15), nullable=False, unique=True)
    comments = db.Column('comments', db.String(1000))

    # Relationships
    tech_id = db.Column(db.Integer, db.ForeignKey('technologies.id'))
    types = db.relationship("Types", backref="component")
    suppliers = db.relationship("Suppliers", secondary=supplier_component, backref='components')
    models = db.relationship("Models", backref="component")

    # Format return data
    def __repr__(self):
        return '<Component %r>' % self.name



class Types(db.Model):

    # Table columns
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(50), nullable=False, unique=True)
    short = db.Column('short', db.String(20), nullable=False, unique=True)
    
    # Relationships
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'))
    #models = db.relationship("Models", backref="type")
    
    # Format return data
    def __repr__(self):
        return '<Type %r>' % self.name



class Suppliers(db.Model):

    # Table columns
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(50), nullable=False, unique=True)
    short = db.Column('short', db.String(10), nullable=False, unique=True)
    comments = db.Column('comments', db.String(1000))

    # Relationships
    types = db.relationship("Types", secondary=supplier_type, backref='suppliers')
    models = db.relationship("Models", backref="supplier")
        
    # Formats return data
    def __repr__(self):
        return '<Supplier %r>' % self.name



class Models(db.Model):

    # Table columns
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(30), nullable=False, unique=True)
    power = db.Column('power', db.Integer)
    energy = db.Column('energy', db.Integer)
    char1 = db.Column('char1', db.String(30))
    char2 = db.Column('char2', db.String(30))
    comments = db.Column('comments', db.String(1000))

    # Relationships
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    type1_id = db.Column(db.Integer, db.ForeignKey('types.id'))
    type2_id = db.Column(db.Integer, db.ForeignKey('types.id'))
        
    # Formats return data
    def __repr__(self):
        return '<Model %r>' % self.name



class Configurations(db.Model):

    # Table columns
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column('status', db.String(20), default='active')
    quantity = db.Column('quantity', db.Integer)
    comments = db.Column('comments', db.String(1000))

    # Relationships
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'))
    component_id = db.Column(db.Integer, db.ForeignKey('components.id'))
    type1_id = db.Column(db.Integer, db.ForeignKey('types.id'))
    type2_id = db.Column(db.Integer, db.ForeignKey('types.id'))
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))

    # Formats return data
    def __repr__(self):
        return '<Configurations %r>' % self.id





class Plants(db.Model):
    
    # Table columns
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(30), nullable=False)
    capacity_ac = db.Column(db.Integer)
    capacity_dc = db.Column(db.Integer)
    latitude = db.Column(db.Integer)
    longitude = db.Column(db.Integer)
    status = db.Column(db.String(20))
    comments = db.Column(db.String(1000), nullable=True)

    # Relationships
    country_id = db.Column(db.String, db.ForeignKey('countries.id'))
    technologies = db.relationship("Technologies", secondary=plant_technology, backref='plants')
    configurations = db.relationship("Configurations", backref="plant")
    partakers = db.relationship("Partakers", secondary=plant_partaker, backref='plants')   
    
    # Sets return data {Plant_# : name}
    def __repr__(self):
        return '<Plant %r>' % self.name



class Projects(db.Model):

    # Table columns    
    code = db.Column(db.Integer, primary_key=True)
    name = db.Column("Name", db.String(50), nullable=False)
    description = db.Column('Description', db.String(10000))
    link = db.Column('Sharepoint Site', db.String(200))
    
    services = db.Column('Services', db.JSON, nullable=False)

    # Relationships
    plants = db.relationship("Plants", secondary=project_plant, backref='projects')
    role_id= db.Column(db.Integer, db.ForeignKey('roles.id'))
    pm_id = db.Column(db.Integer, db.ForeignKey('users.staffnum'))
    dpm_id = db.Column(db.Integer, db.ForeignKey('users.staffnum'))
    pp_id = db.Column(db.Integer, db.ForeignKey('users.staffnum'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))   

    # Sets return data {Project_# : code}
    def __repr__(self):
        return '<Project %r>' % self.code


