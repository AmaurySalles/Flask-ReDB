## IMPORT


# You always put the ForeignKey in the table which contains only one of those many items

## ONE parent TO MANY children relationships:
class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    children = db.relationship("Child", backref="parent")

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))



## MANY parents TO ONE child relationships:
class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'))
    

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parents = db.relationship("Parents", backref="child")






## ONE TO ONE relationships:
class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'))
    child = db.relationship("Child", backref=db.backref("parent", uselist=False))

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent = db.relationship("Parent", back_populates="child", uselist=False)




## MANY TO MANY relationships:
parent_child = db.Table('parent_child', 
    db.Column('parent_id', db.Integer, db.ForeignKey('parent.id')),
    db.Column('child_id', db.Integer, db.ForeignKey('child.id'))
)

class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    children = db.relationship("Child", secondary=parent_child, backref='parents')

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)






# Create users:
new_user = Users(user_id=6, name='Carlos Reyes',password='12345', staffnum='36548', email='carlos.reyes@mottmac.com')
db.session.add(new_user)
db.session.commit()

# Count users:
user_count = Users.query().count()
print(user_count)

# Retrieve all users (response is an array / list)
all_users = Users.query().all()
for user in all_users:
    print(f'{user.name}, with staff number {user.staffnum} and email {user.email} is registered in database')

# Retrieve certain users (response is an array / list)
all_users = Users.query.filter_by().all()