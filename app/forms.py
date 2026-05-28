from app import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, DecimalField, DateField, TextAreaField, SelectField, SearchField
from wtforms.validators import InputRequired, Length, ValidationError, Email, DataRequired, Optional, EqualTo
from app.models import User
from flask_login import current_user




class RegistrationForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=6, max=20)], render_kw={"placeholder": "Username"})
    
    password = PasswordField(
        validators=[InputRequired(), 
                    Length(min=6, max=20)],
                    render_kw={"placeholder": "Password"})
    
    confirm_password = PasswordField(validators=[
                                     InputRequired(),
                                     EqualTo('password', message='Passwords must match')],
                                     render_kw={'placeholder': 'Confirm Password'})
    
    email = StringField(validators=[InputRequired(), Length(
        min=6, max=50)], render_kw={"placeholder": "Email"})

    submit = SubmitField("Register")


    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()

        if existing_username:
            raise ValidationError(
                "That username is being used. Try another."
            )
        
    def validate_email(self, email):
        existing_email = User.query.filter_by(email=email.data).first()

        if existing_email:
            raise ValidationError(
                "That email is being used. Try another."
            )
           




class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
      
    submit = SubmitField("Login")


   

class EntryForm(FlaskForm):
    stock_sym = StringField(validators=[InputRequired()],
                                render_kw={"placeholder": "Enter symbol Name",})
    
    entry_date = DateField(validators=[DataRequired()], format="%Y-%m-%d")

    exit_date = DateField(validators=[Optional()], format="%Y-%m-%d")
    
    price_entry = DecimalField(validators=[DataRequired()],
                            render_kw={"placeholder": "Enter entry price",
                                        "step": "0.01",
                                        "min": "0"})
    
    price_exit = DecimalField(validators=[Optional()],
                              render_kw={"placeholder": "Enter exit price",
                                         "step": "0.01",
                                         "min": "0"})
    
    
    status = SelectField("Status", choices=[("",'Select status '),
                                              ('long', 'Long'), 
                                              ('short', 'Short')],
                                              validators=[DataRequired(message="Please select a status")])
    
    qty = DecimalField(validators=[DataRequired()],
                          render_kw={"placeholder": "Enter quanity amount",
                                     "step": "1",
                                     "min": "0"})
    
    
    entry_journal = TextAreaField("Notes", validators=[Optional()],
                        render_kw={"placeholder": "Add any notes about this trade..."})
    
    
    
    submit = SubmitField("Add Trade")



class PassWordResetRequestForm(FlaskForm):
    email = EmailField(validators=[DataRequired(), Email()], 
                        render_kw={"placeholder": "Enter your email"})

    submit = SubmitField("Click here for the password reset link")


class PassWordResetForm(FlaskForm):
    new_password = PasswordField(validators=[InputRequired(), Length(
        min=6, max=20)], render_kw={"placeholder": "Enter your new password"})
    
    submit = SubmitField("Enter")

    user = None

    def validate_new_password(self, new_password):
        if self.user:
            if bcrypt.check_password_hash(self.user.password, new_password.data):
                raise ValidationError(
                "New password cannot be the same as the old password, try again."
            )



class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField(validators=[DataRequired()],
                        render_kw={"placeholder": "Enter your old password"})
    
    new_password = PasswordField(validators=[InputRequired(), Length(
        min=6, max=20)], render_kw={"placeholder": "Enter your new password"})
    
    submit = SubmitField("Update")

    def validate_old_password(self, old_password):
        if not bcrypt.check_password_hash(current_user.password, old_password.data):
                raise ValidationError(
                    "Old password is incorrect"
                )
        
    def validate_new_password(self, new_password):
        if bcrypt.check_password_hash(current_user.password, new_password.data):
            raise ValidationError (
                "New password cannot be the same as the old password, try again"
            )
        

class UpdateUserNameForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=6, max=20)], render_kw={"placeholder": "Username"})
    
    submit = SubmitField("Update")

    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()

        if existing_username:
            raise ValidationError(
                "Username is already taken, try again"
            )


class DeleteAccountForm(FlaskForm):
    password = PasswordField(validators=[DataRequired()], 
                                         render_kw={"placeholder": "Enter password"})
    
    submit = SubmitField("Enter")
    

    def validate_password(self, password):
        if not bcrypt.check_password_hash(current_user.password, password.data):
            raise ValidationError(
            "Incorrect password. Please enter your password to confirm account deletion.")


class SearchForm(FlaskForm):
    search = SearchField(validators=[DataRequired()],
                         render_kw={"placeholder": "Search" })
    
    submit = SubmitField("Search")
