import pickle
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextAreaField, \
	RadioField, IntegerField
from wtforms.validators import DataRequired, NumberRange

with open("category-number.txt", "rb") as f:
	categoryNumber = pickle.load(f)
districtPair = [(v, k)for k, v in categoryNumber["district"].items()]
townPair = [(v, k)for k, v in categoryNumber["town"].items()]
floorTypePair = [(v, k)for k, v in categoryNumber["floorType"].items()]
# sort by name
districtPair = sorted(districtPair, key=lambda d: d[1], reverse=False)
district_all = [(-1, 'All')]
district_all.extend(districtPair)


class LoginForm(FlaskForm):
	login_email = StringField(
		'Email',
		validators=[DataRequired()],
		render_kw={"class": "form-control", "placeholder": 'Enter your email'}
		)
	login_password = PasswordField(
		'Password',
		validators=[DataRequired()],
		render_kw={"class": "form-control", "placeholder": 'Enter your password'})

	# submit = SubmitField('Sign In')


class AgentLoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
	register_username = StringField(
		'Username',
		validators=[DataRequired(message="username is required")],
		render_kw={"class": "form-control", "placeholder": 'Set your username'})
	email = StringField(
		'Email',
		validators=[DataRequired(message="email is required")],
		render_kw={"class": "form-control", "placeholder": 'Enter your email'})
	register_password = PasswordField(
		'Password',
		validators=[DataRequired(message="password is required")],
		render_kw={"class": "form-control", "placeholder": 'Set your password'})
	password2 = PasswordField(
		'Confirm Password',
		validators=[DataRequired(message="password is required")],
		render_kw={"class": "form-control", "placeholder": 'Repeat your password'})
	# submit = SubmitField('Register')


class CalculationForm(FlaskForm):
	room_numbers = []
	floor_numbers = []
	year_numbers = []
	years = range(1950, 2022)
	for i in range(0, 100):
		room_numbers.append((i, '{}'.format(i)))
		floor_numbers.append((i+1, '{}'.format(i+1)))

	for i in reversed(years):
		year_numbers.append((i, '{}'.format(i)))

	square = IntegerField('Square', validators=[
	                      DataRequired("Please fill this information!")])
	livingRoom = SelectField(
		label='Living Room',
		validate_choice=False,
		choices=room_numbers[1:],
		coerce=int)
	drawingRoom = SelectField(
		label='Drawing Room',
		validate_choice=False,
		choices=room_numbers,
		coerce=int)
	kitchen = SelectField(
		label='Kitchen',
		validate_choice=False,
		choices=room_numbers,
		coerce=int)
	bathRoom = SelectField(
		label='Bath Room',
		validate_choice=False,
		choices=room_numbers,
		coerce=int)
	buildingType = SelectField(
		label='Building Type',
		validators=[DataRequired()],
		choices=[(1, 'tower'), (2, 'bungalow'),
		          (3, 'combination of plate and tower'), (4, 'plate')],
		default=1,
		coerce=int)
	constructionTime = SelectField(
		label='Construction Time',
		validators=[DataRequired()],
		choices=year_numbers,
		coerce=int)
	renovationCondition = SelectField(
		label='Renovation Condition',
		validators=[DataRequired()],
		choices=[(1, 'other'), (2, 'rough'), (3, 'simplicity'), (4, 'hardcover')],
		coerce=int)
	buildingStructure = SelectField(
		label='Building Structure',
		validators=[DataRequired()],
		choices=[(1, 'unknow'), (2, 'mixed'), (3, 'brick and wood'), (4,
		          'brick and concrete'), (5, 'steel'), (6, 'steel-concrete composite')],
		coerce=int)
	elevator = SelectField(
		label='Elevator',
		validate_choice=False,
		choices=[(1, 'Yes'), (0, 'No')],
		default=1,
		coerce=int)
	fiveYearsProperty = SelectField(
		label='Five-Year-Property',
		validate_choice=False,
		choices=[(1, 'Yes'), (0, 'No')],
		default=1,
		coerce=int)
	subway = SelectField(
		label='Subway',
		# validators=[DataRequired()],
		choices=[(1, 'Yes'), (0, 'No')],
		default=1,
		coerce=int)
	district = SelectField(
		label='District',
		validate_choice=False,
		choices=districtPair,
		coerce=int,
		default=0,
		id="district")
	town = SelectField(
		label='Town',
		validate_choice=False,
		validators=[DataRequired()],
		id="town")
	business = SelectField(
		label='Business',
		validate_choice=False,
		validators=[DataRequired()],
		id="business")
	floorType = SelectField(
		label='Floor Type',
		validate_choice=False,
		choices=floorTypePair,
		default=0,
		coerce=int)
	floorHeight = SelectField(
		label='Floor Height',
		validators=[DataRequired()],
		choices=floor_numbers,
		coerce=int)
	submit = SubmitField('Calculate', id="calculate")


class FilterForm(FlaskForm):
	size = RadioField(
		label='Size',
		choices=[(None, 'All'), ((0, 49), '<50'), ((50, 100), '50-100'), ((101, 150), '101-150'), ((151, 200), '151-200'), ((201, 999999999999), '>200')])

	price = RadioField(
		label='Price',
		choices=[(None, 'All'), ((0, 199), '<2M'), ((200, 250), '2M-2.5M'), ((251, 300), '2.51M-3M'), ((301, 400), '3.01M-4M'), ((401, 999999999999), '>4M')])

	room = RadioField(
		label='Room',
		choices=[(None, 'All'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7')])

	district = SelectField(
		label='District',
		validate_choice=False,
		choices=district_all,
		coerce=int,
		default=-1,
		id="district")


class SearchForm(FlaskForm):
	query = StringField()

	search = SubmitField()


class RecommendationForm(FlaskForm):
	options = SelectField(
		label='More options',
		validate_choice=False,
		choices=[(0, 'Default'), (1, 'Less Price'), (2, 'Less Size'), (3, 'More Size'), (4, 'Less Room'), (5, 'More Room'), (6, 'Lower Floor'), (7, 'Higher Floor')],
		coerce = int,
		id = "options")

	# lessPrice = SubmitField('Less price')
	# lessSize = SubmitField('Less size')
	# moreSize = SubmitField('More size')
	# lessRoom = SubmitField('Less room')
	# moreRoom = SubmitField('More room')
	# lowerFloor = SubmitField('Lower floor')
	# higherFloor = SubmitField('Higher floor')



	# submit = SubmitField(choices = [(1, 'Dublin'), (2, 'Belfast'), (3, 'Cork'), (4, 'Derry'), (5, 'Limerick'),
	# 		   (6, 'Galway'), (7, 'Craigavon')])
