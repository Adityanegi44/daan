from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# Route for the homepage
@app.route('/')
def home():
    # This will render the home page template
    return render_template('home.html')

@app.route('/login_ngo', methods=['GET', 'POST'])
def login_ngo():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = NGOLoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            ngo = NGO.query.filter_by(email=form.email.data).first()
            if ngo and check_password_hash(ngo.password, form.password.data):
                login_user(ngo)
                flash('Successfully logged in!', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid email or password', 'error')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
    
    return render_template('login_ngo.html', form=form)

@app.route('/register_ngo', methods=['GET', 'POST']) 
def register_ngo():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = NGORegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if NGO.query.filter_by(email=form.email.data).first():
                flash('Email already registered', 'error')
                return redirect(url_for('register_ngo'))
                
            hashed_password = generate_password_hash(form.password.data)
            ngo = NGO(
                name=form.name.data,
                email=form.email.data,
                password=hashed_password,
                description=form.description.data
            )
            db.session.add(ngo)
            try:
                db.session.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login_ngo'))
            except:
                db.session.rollback()
                flash('An error occurred. Please try again.', 'error')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
    
    return render_template('register_ngo.html', form=form)

@app.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
    form = DonationForm()
    if request.method == 'GET':
        campaigns = Campaign.query.filter_by(active=True).all()
        return render_template('donate.html', campaigns=campaigns, form=form)
        
    if request.method == 'POST':
        if form.validate_on_submit():
            campaign = Campaign.query.get_or_404(form.campaign_id.data)
            
            donation = Donation(
                amount=form.amount.data,
                campaign_id=campaign.id,
                donor_id=current_user.id,
                message=form.message.data
            )
            
            db.session.add(donation)
            try:
                db.session.commit()
                flash('Thank you for your donation!', 'success')
                return redirect(url_for('campaign_detail', campaign_id=campaign.id))
            except:
                db.session.rollback()
                flash('An error occurred processing your donation. Please try again.', 'error')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'error')
                    
    return render_template('donate.html', form=form)

# Ensure the dashboard route exists
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')  # Ensure this template exists

