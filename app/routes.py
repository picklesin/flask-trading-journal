from app.models import User, Entry, TradeEntry
import app.forms as forms
from datetime import date
from sqlalchemy import select, or_
from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, url_for, redirect, flash, request, Blueprint, current_app
from werkzeug.exceptions import abort
from flask_mail import Message
from itsdangerous import SignatureExpired, BadSignature
from app.func import trade_calc
from itsdangerous import URLSafeTimedSerializer
from app import login_manager, bcrypt, mail, db

main = Blueprint("main", __name__)


# email token
def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


login_manager.login_view = "login"
@login_manager.user_loader
def login_manager(user_id):

    return db.session.get(User, int(user_id))

# cache Control
@main.after_request
def add_cache_headers(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@main.route('/')
def home():
    return render_template('home.html')



# user registation
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()

    if form.validate_on_submit():
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data,
                        password=hashed_password,
                        email=form.email.data)   
        
        db.session.add(new_user)
        db.session.commit()

        s = get_serializer()
        token = s.dumps(new_user.email, salt='email-confirm')
        link = url_for('main.confirm_email', token=token, _external=True)

        msg = Message(
            subject='Tradefy Email Verification',
            recipients=[new_user.email],
            body='Please click the link to verify your registration: {}'.format(link)
        )
        mail.send(msg)
        flash("Please check your email (including your spam folder) and click the verification link to verify your account.")
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)


# confirm email verification token
@main.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    try:
        s = get_serializer()
        email = s.loads(token, salt='email-confirm', max_age=300)
        user = User.query.filter_by(email=email).first()
        user.email_verified = True
        db.session.commit()


    except SignatureExpired:
        return 'Token has expired'
    
    except BadSignature:
        return 'Invalid token'
    
    flash('Your account has been verified')
    return redirect(url_for('main.login'))


# login Page
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if not user:
            flash("Wrong username or password")

        else:
            if not bcrypt.check_password_hash(user.password, form.password.data):
                flash("Wrong username or password")

            else:
                login_user(user)
                return redirect(url_for('main.dashboard'))

    return render_template('login.html', form=form)


# dashboard
@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    username=current_user.username

    stmt = (
        select(TradeEntry)
        .join(Entry)
        .where(Entry.user_id == current_user.id)
        .order_by(TradeEntry.exit_date.asc())
    )
    trades = db.session.scalars(stmt).all()

    
    # method to handle calculations for trades and returns the values in a dict
    stats = trade_calc(trades)

  
    return render_template('dashboard.html', 
                           wins=stats['wins'], 
                           loss=stats['loss'], 
                           total_pnl_dashboard=stats['total_pnl_dashboard'], 
                           win_rate=stats['win_rate'],
                           std_dev_win=stats['std_dev_win'],
                           std_dev_loss=stats['std_dev_loss'],
                           largest_win=stats['largest_win'],
                           largest_loss=stats['largest_loss'], 
                           username=username, 
                           profit_factor=stats['profit_factor'], 
                           total_trades=stats['total_trades'],
                           trading_summary=stats['trading_summary'],
                           trading_summary_json=stats['trading_summary_json']
                           )

   

# logout
@main.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# adding entry
@main.route('/entry', methods=['GET', 'POST'])
@login_required
def journal_trade_entry():
    form = forms.EntryForm()

    if form.validate_on_submit():
    
        new_entry=Entry(
            created_time=date.today(),
            user_id=current_user.id
        )

        db.session.add(new_entry)
        db.session.commit()

        new_entry.trade_info=TradeEntry(
            entry_journal=form.entry_journal.data,
            stock_sym=form.stock_sym.data,
            price_entry=form.price_entry.data,
            price_exit=form.price_exit.data,
            qty=form.qty.data,
            entry_date=form.entry_date.data,
            exit_date=form.exit_date.data,
            status=form.status.data,
            user_id=current_user.id,
            entry_id=new_entry.id
          
        )
      

        
        db.session.add(new_entry)
        db.session.commit()
        flash("Entry saved", "success")

        return redirect(url_for('main.trades', page_num=1)) 
    
    return render_template('entry.html', form=form)



# viewing all trades
@main.route('/trades')
@login_required
def trades():
    page = request.args.get('page', 1, type=int)
    q = request.args.get("q", "")

    if q:
        posts = TradeEntry.query.filter(TradeEntry.user_id == current_user.id,
                                            or_(TradeEntry.stock_sym.ilike('%' + q + '%'),
                                            TradeEntry.status.ilike('%' + q + '%')
                                            )).order_by(TradeEntry.entry_date.asc()).paginate(page=page, per_page=5, error_out=True)
    
    else:
        posts = TradeEntry.query.filter(TradeEntry.user_id == current_user.id).order_by(TradeEntry.entry_id.asc()).paginate(page=page, per_page=5, error_out=True)
              
   
    return render_template('view_trades.html', posts=posts, page=page, q=q)



# edit trades
@main.route('/trades/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_trades(id):
    trade = db.session.get(TradeEntry, id)
    page = request.args.get('page', 1, type=int)
    q = request.args.get("q")

    if trade is None:
        return redirect(url_for('main.dashboard'))
    entry = trade.parent

    if current_user.id != trade.user_id:
        flash("You do not have permission to edit entry", "danger")
        return redirect(url_for('main.home'))
     
    form = forms.EntryForm(obj=trade)

    if form.validate_on_submit():

        # Update trade 
        form.populate_obj(trade)
        entry.updated_at = date.today()
        db.session.commit()

        flash("Updated journal entry", "success")
        return redirect(url_for('main.trades', page=page, q=q))
    

    # pre fill with data
    if request.method =='GET':
        form.entry_journal.data = trade.entry_journal
        form.stock_sym.data = trade.stock_sym
        form.price_entry.data = trade.price_entry
        form.price_exit.data = trade.price_exit
        form.qty.data = float(f"{trade.qty:g}")
        form.entry_date.data = trade.entry_date
        form.exit_date.data = trade.exit_date
        form.status.data = trade.status
            
    
    return render_template('edit_trade.html', trade=trade, form=form, page=page, q=q)


# delete a trade
@main.route('/trade/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_trade(id):
    post_to_delete = db.session.get(TradeEntry, id)
    page = request.args.get('page', 1, type=int)
    q = request.args.get("q")
    
    if post_to_delete is None:
        abort(404)

    if post_to_delete.user_id != current_user.id:
        flash("You do not have permission")
        logout_user()
    
    try: 
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Trade has been deleted", "success")
        return redirect(url_for('main.trades', page=page, q=q))

    except:
        flash("There was a problem, try again")
        return redirect(url_for('main.trades', page=page, q=q))
    


# settings
@main.route('/dashboard/settings', methods=['GET', 'POST'])
@login_required
def settings():
    username = current_user
   
    return render_template('settings.html', username=username)



# deleting a users account along with all files associated with user  
@main.route('/dashboard/settings/delete-user', methods=['GET', 'POST'])
@login_required
def delete_user():
    form = forms.DeleteAccountForm()
   
    if form.validate_on_submit() and current_user.is_authenticated:    
        user = current_user._get_current_object()
        
        db.session.delete(user)
        db.session.commit()
        logout_user()
        flash("Account deleted successfully", "success")
        return redirect(url_for('main.login'))

    return render_template('delete_user.html', form=form)
    

# change password
@main.route('/dashboard/settings/change-password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = forms.UpdatePasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        
        flash("Password updated successfully", "success")
        return redirect(url_for('main.update_password'))
    
    
    return render_template('update_password.html', form=form)



# change username
@main.route('/settings/change-username', methods=['GET', 'POST'])
@login_required
def update_username():
    form = forms.UpdateUserNameForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash("Username updated", "success")
        return redirect(url_for('main.update_username'))



    return render_template('update_username.html', form=form)


# password reset page
@main.route('/password-reset', methods=['GET', 'POST'])
def password_reset():
    form = forms.PassWordResetRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

            
        if user is not None:
            s = get_serializer()
            if user.email_verified:

                token = s.dumps(user.email, salt='password-reset')
                link = url_for('main.password_reset_confirm', token=token, _external=True)

                msg = Message(
                subject='Email Reset',
                sender='add email',
                recipients=[user.email],
                body=f'Please click the link below to reset your password \n{link}' 
                )
                mail.send(msg)   
                flash('If an account with that email exists, a reset link has been sent.', 'success')
                return redirect(url_for('main.login'))
            
            else: 

                token = s.dumps(user.email, salt='email-confirm')
                link = url_for('main.confirm_email', token=token, _external=True)

                msg = Message(
                    subject='Tradefy Email Verification',
                    recipients=[user.email],
                    body='Please click the link to verify your registration: {}'.format(link)
                )
          
                mail.send(msg)
              

                flash("Our system has indicates that you have not verified your email. Please check your email and click the verification link to activate your account before resetting your password.")
                return redirect(url_for('main.password_reset'))
        else:
            flash("We're sorry. We weren't able to identify you given the information provided.")
    
    
    return render_template('password_reset.html', form=form)



# password reset email verification 
@main.route('/password-reset/<token>', methods=['GET', 'POST'])
def password_reset_confirm(token):
    try:
        s = get_serializer()
        email = s.loads(token, salt='password-reset', max_age=300)       
        
    except SignatureExpired:
        return 'Token has expired, try again'
    
    except BadSignature:
        return 'Invalid token'
    
    # verify user email
    user = User.query.filter_by(email=email).first()

    if not user:
        flash('Invalid user', 'danger')
        return redirect(url_for('main.password_reset'))

    
    form = forms.PassWordResetForm()
    form.user = user

    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password has been reset')
        return redirect(url_for('main.login'))
  

    return render_template('password_reset_page.html', form=form)
    