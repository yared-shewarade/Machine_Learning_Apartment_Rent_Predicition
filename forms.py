from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, RadioField

class UserInput(FlaskForm):
    street = StringField("street")
    city = StringField("city")
    state = StringField("state")
    bed = IntegerField("number of bed(s)")
    bath = IntegerField("number of bath(s)")
    sf = IntegerField("square feet")
    free_rent = IntegerField("month(s) of free rent")
    washer_dryer_0 = SelectField("Do you have a washer & dryer in unit", choices=[(1, "Yes"), (0, "no")])
    washer_dryer_1 = SelectField("Do you have a washer & dryer but not in unit", choices=[(1, "Yes"), (0, "no")])
    washer_dryer_2 = SelectField("There is no washer & dryer", choices=[(1, "Yes"), (0, "no")])
    walk_in_closet = SelectField("walk-in closet?", choices=[(1, "Yes"), (0, "no")])
    hardwood_vinyl_floor = SelectField("hardwood/vinyl floor?", choices=[(1, "Yes"), (0, "no")])
    submit = SubmitField()
