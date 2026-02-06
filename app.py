"""
Super Bowl Props Web App - Main Application
"""
import os
import secrets
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect

from config import Config
from database import (
    init_db, User, PropQuestion, UserAnswer, Settings, get_db_connection,
    FreeformField, UserFreeformAnswer, GameConfig
)
from nfl_teams import NFL_TEAMS, get_team, get_teams_by_conference, get_all_teams

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home'
login_manager.login_message = '🏈 Please use your personal invite link to access the game.'
login_manager.login_message_category = 'info'

# Initialize database tables on startup
init_db()

# Create admin user if none exists, or fix if password is missing
def ensure_admin_exists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE is_admin = 1 LIMIT 1')
    admin_row = cursor.fetchone()
    conn.close()
    
    admin_password = os.environ.get('MASTER_KEY', 'superbowl2025')
    
    if admin_row is None:
        # No admin exists - create one
        admin = User(
            display_name='Commissioner',
            access_token=secrets.token_urlsafe(16),
            is_admin=True
        )
        admin.set_admin_password(admin_password)
        admin.save()
        print(f"✓ Created admin user (password from {'MASTER_KEY env' if os.environ.get('MASTER_KEY') else 'default'})")
    else:
        # Admin exists - check if password is set
        admin = User.from_row(admin_row)
        if not admin.admin_password:
            admin.set_admin_password(admin_password)
            admin.save()
            print(f"✓ Fixed admin password (from {'MASTER_KEY env' if os.environ.get('MASTER_KEY') else 'default'})")

ensure_admin_exists()

mail = Mail(app)


@app.before_request
def ensure_session():
    """Ensure session is initialized for CSRF to work"""
    session.permanent = True


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Commissioner access required.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# CONTEXT PROCESSORS
# ============================================================================

@app.context_processor
def inject_game_config():
    """Make game configuration available to all templates"""
    config = GameConfig.get_all()
    team_a = get_team(config.get('team_a_code', ''))
    team_b = get_team(config.get('team_b_code', ''))
    
    # Add formatted display date
    config['display_date'] = GameConfig.get_display_date()
    config['venue_display'] = GameConfig.get_venue_display()
    
    return {
        'game_config': config,
        'game_team_a': team_a,
        'game_team_b': team_b
    }


# ============================================================================
# PUBLIC ROUTES
# ============================================================================

@app.route('/')
def home():
    """Landing page"""
    if current_user.is_authenticated:
        if Settings.is_locked():
            return redirect(url_for('dashboard'))
        return redirect(url_for('prop_form'))
    return render_template('welcome.html')


@app.route('/play/<token>')
def access_game(token):
    """Access the game via unique link"""
    user = User.get_by_access_token(token)
    
    if user is None:
        flash('Invalid or expired link. Please contact the host for a new invite.', 'error')
        return redirect(url_for('home'))
    
    # Log them in
    user.last_visit = datetime.utcnow().isoformat()
    user.save()
    login_user(user, remember=True)
    
    flash(f'Welcome to the game, {user.display_name}!', 'success')
    
    if Settings.is_locked():
        return redirect(url_for('dashboard'))
    return redirect(url_for('prop_form'))


@app.route('/logout')
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('home'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_panel'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        
        # Find admin user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE is_admin = 1 LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            admin = User.from_row(row)
            if admin.check_admin_password(password):
                login_user(admin, remember=True)
                flash('Welcome, Commissioner!', 'success')
                return redirect(url_for('admin_panel'))
        
        flash('Invalid password.', 'error')
    
    return render_template('admin/login.html')


# ============================================================================
# PROP BET FORM
# ============================================================================

@app.route('/props', methods=['GET', 'POST'])
@login_required
def prop_form():
    """Main prop bet form"""
    is_locked = Settings.is_locked()
    lock_time = Settings.get_lock_time()
    
    if request.method == 'POST':
        if is_locked:
            flash('Time\'s up! Submissions are locked.', 'error')
            return redirect(url_for('dashboard'))
        
        # Get all answers from the form
        answers = {}
        freeform_answers = {}
        for key, value in request.form.items():
            if key.startswith('q_'):
                question_id = key[2:]
                answers[question_id] = value
            elif key.startswith('ff_'):
                field_id = key[3:]
                freeform_answers[field_id] = value
        
        # Save answers
        UserAnswer.save_all_answers(current_user.id, answers)
        UserFreeformAnswer.save_all_answers(current_user.id, freeform_answers)
        flash('Your picks have been saved!', 'success')
        return redirect(url_for('prop_form'))
    
    # Get questions by category
    questions_by_category = PropQuestion.get_by_category()
    
    # Get user's current answers
    user_answers = UserAnswer.get_user_answers(current_user.id)
    
    # Get freeform fields and answers
    freeform_fields = FreeformField.get_all()
    user_freeform_answers = UserFreeformAnswer.get_user_answers(current_user.id)
    
    # Count total questions for progress display
    total_count = sum(len(qs) for qs in questions_by_category.values())
    answered_count = len(user_answers)
    
    return render_template('prop_form.html',
                          questions_by_category=questions_by_category,
                          user_answers=user_answers,
                          freeform_fields=freeform_fields,
                          user_freeform_answers=user_freeform_answers,
                          answered_count=answered_count,
                          total_count=total_count,
                          is_locked=is_locked,
                          lock_time=lock_time)


# ============================================================================
# DASHBOARD & LEADERBOARD
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard showing all answers and leaderboard"""
    is_locked = Settings.is_locked()
    lock_time = Settings.get_lock_time()
    
    # Always allow viewing if admin, otherwise only after lock
    if not is_locked and not current_user.is_admin:
        flash('The scoreboard will be available after the deadline!', 'info')
        return redirect(url_for('prop_form'))
    
    # Get all data
    questions = PropQuestion.get_active()
    users = User.get_participants()
    all_answers = UserAnswer.get_all_answers()
    
    # Get freeform fields and all answers
    freeform_fields = FreeformField.get_all()
    all_freeform_answers = UserFreeformAnswer.get_all_answers()
    
    # Calculate scores
    scores = {}
    for user in users:
        correct = 0
        answered = 0
        user_ans = all_answers.get(user.id, {})
        for q in questions:
            if q.id in user_ans:
                answered += 1
                if q.correct_answer and user_ans[q.id] == q.correct_answer:
                    correct += 1
        
        # Calculate tiebreaker difference (for total score predictions)
        tiebreaker_diff = None
        user_ff = all_freeform_answers.get(user.id, {})
        for ff in freeform_fields:
            if ff.correct_value and ff.field_id in user_ff:
                try:
                    predicted = float(user_ff[ff.field_id])
                    actual = float(ff.correct_value)
                    tiebreaker_diff = abs(predicted - actual)
                except (ValueError, TypeError):
                    pass
        
        scores[user.id] = {
            'correct': correct,
            'answered': answered,
            'total': len(questions),
            'tiebreaker_diff': tiebreaker_diff
        }
    
    # Sort users by score for leaderboard (then by tiebreaker if tied)
    def sort_key(u):
        s = scores[u.id]
        # Higher correct is better, lower tiebreaker_diff is better
        # Use large number if no tiebreaker to sort them last among ties
        tb = s['tiebreaker_diff'] if s['tiebreaker_diff'] is not None else 9999
        return (-s['correct'], tb)
    
    leaderboard = sorted(users, key=sort_key)
    
    # Group questions by category for display
    questions_by_category = PropQuestion.get_by_category()
    
    return render_template('dashboard.html',
                          questions=questions,
                          questions_by_category=questions_by_category,
                          users=users,
                          all_answers=all_answers,
                          freeform_fields=freeform_fields,
                          all_freeform_answers=all_freeform_answers,
                          scores=scores,
                          leaderboard=leaderboard,
                          is_locked=is_locked,
                          lock_time=lock_time)


# ============================================================================
# ADMIN ROUTES
# ============================================================================

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    """Admin control panel"""
    users = User.get_all()
    participants = [u for u in users if not u.is_admin]
    questions = PropQuestion.get_all()
    lock_time = Settings.get_lock_time()
    is_locked = Settings.is_locked()
    
    # Count answered questions
    answered_questions = len([q for q in questions if q.correct_answer])
    
    return render_template('admin/panel.html',
                          users=users,
                          participants=participants,
                          questions=questions,
                          answered_questions=answered_questions,
                          lock_time=lock_time,
                          is_locked=is_locked,
                          app_url=Config.APP_URL)


@app.route('/admin/add-player', methods=['POST'])
@login_required
@admin_required
def admin_add_player():
    """Add a new player and generate their unique link"""
    display_name = request.form.get('display_name', '').strip()
    
    if not display_name:
        flash('Please enter a name for the player.', 'error')
        return redirect(url_for('admin_panel'))
    
    # Generate unique access token
    access_token = secrets.token_urlsafe(16)
    
    user = User(
        display_name=display_name,
        access_token=access_token,
        is_admin=False
    )
    user.save()
    
    flash(f'Added {display_name}! Their personal link is ready to share.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/player/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_player(user_id):
    """Delete a player"""
    user = User.get_by_id(user_id)
    if user:
        if user.is_admin:
            flash('Cannot delete admin users.', 'error')
        else:
            name = user.display_name
            user.delete()
            flash(f'{name} has been removed.', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/player/<int:user_id>/regenerate', methods=['POST'])
@login_required
@admin_required
def admin_regenerate_link(user_id):
    """Generate a new access link for a player"""
    user = User.get_by_id(user_id)
    if user and not user.is_admin:
        user.access_token = secrets.token_urlsafe(16)
        user.save()
        flash(f'New link generated for {user.display_name}!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/lock-time', methods=['POST'])
@login_required
@admin_required
def admin_set_lock_time():
    """Set the submission lock time"""
    lock_time_str = request.form.get('lock_time', '')
    
    if not lock_time_str:
        flash('Please select a deadline time.', 'error')
        return redirect(url_for('admin_panel'))
    
    try:
        lock_time = datetime.fromisoformat(lock_time_str)
        Settings.set_lock_time(lock_time)
        flash(f'Deadline set: {lock_time.strftime("%B %d at %I:%M %p")}', 'success')
    except ValueError:
        flash('Invalid date/time format.', 'error')
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/game-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_game_settings():
    """Configure game settings (teams, venue, date)"""
    if request.method == 'POST':
        # Save all game config values
        config_keys = ['super_bowl_number', 'game_date', 'game_time', 
                       'venue_name', 'venue_city', 'venue_state',
                       'team_a_code', 'team_b_code', 'pool_name', 'pool_tagline']
        
        for key in config_keys:
            value = request.form.get(key, '').strip()
            if value:
                GameConfig.set(key, value)
        
        flash('Game settings saved!', 'success')
        return redirect(url_for('admin_game_settings'))
    
    # Get current config
    config = GameConfig.get_all()
    
    # Get team data
    afc_teams = get_teams_by_conference('AFC')
    nfc_teams = get_teams_by_conference('NFC')
    
    team_a = get_team(config.get('team_a_code', ''))
    team_b = get_team(config.get('team_b_code', ''))
    
    return render_template('admin/game_settings.html',
                          config=config,
                          afc_teams=sorted(afc_teams, key=lambda x: x['full_name']),
                          nfc_teams=sorted(nfc_teams, key=lambda x: x['full_name']),
                          all_teams=NFL_TEAMS,
                          team_a=team_a,
                          team_b=team_b)


@app.route('/admin/answers', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_answers():
    """Set correct answers (master key)"""
    questions = PropQuestion.get_active()
    questions_by_category = PropQuestion.get_by_category()
    freeform_fields = FreeformField.get_all()
    
    if request.method == 'POST':
        print("DEBUG: POST received")
        print("DEBUG: Form data:", dict(request.form))
        
        # Handle clear all
        if request.form.get('clear_all'):
            print("DEBUG: Clearing all answers")
            for q in questions:
                q.correct_answer = None
                q.save()
            for field in freeform_fields:
                field.correct_value = None
                field.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'All cleared'})
            flash('All answers cleared!', 'success')
            return redirect(url_for('admin_answers'))
        
        # Handle clear single answer
        clear_id = request.form.get('clear_answer')
        if clear_id:
            print(f"DEBUG: Clearing answer for question {clear_id}")
            question = PropQuestion.get_by_id(int(clear_id))
            if question:
                question.correct_answer = None
                question.save()
                print(f"DEBUG: Cleared Q{clear_id}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True})
            return redirect(url_for('admin_answers'))
        
        # Handle regular answer updates
        for key, value in request.form.items():
            if key.startswith('answer_'):
                question_id = int(key[7:])
                question = PropQuestion.get_by_id(question_id)
                if question:
                    new_value = value if value else None
                    print(f"DEBUG: Setting Q{question_id} to {repr(new_value)}")
                    question.correct_answer = new_value
                    question.save()
            elif key.startswith('ff_'):
                field_id = key[3:]
                field = FreeformField.get_by_field_id(field_id)
                if field:
                    field.correct_value = value if value else None
                    field.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        
        flash('Correct answers saved!', 'success')
        return redirect(url_for('admin_answers'))
    
    return render_template('admin/answers.html',
                          questions=questions,
                          questions_by_category=questions_by_category,
                          freeform_fields=freeform_fields)


@app.route('/admin/questions', methods=['GET'])
@login_required
@admin_required
def admin_questions():
    """Manage prop questions"""
    questions = PropQuestion.get_all()
    return render_template('admin/questions.html', questions=questions)


@app.route('/admin/questions/add', methods=['POST'])
@login_required
@admin_required
def admin_add_question():
    """Add a new prop question"""
    category = request.form.get('category', '').strip()
    question = request.form.get('question', '').strip()
    option_a = request.form.get('option_a', '').strip()
    option_b = request.form.get('option_b', '').strip()
    
    if not all([category, question, option_a, option_b]):
        flash('All fields are required.', 'error')
        return redirect(url_for('admin_questions'))
    
    q = PropQuestion(
        category=category,
        question=question,
        option_a=option_a,
        option_b=option_b
    )
    q.save()
    
    flash('Question added!', 'success')
    return redirect(url_for('admin_questions'))


@app.route('/admin/questions/<int:question_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_question(question_id):
    """Delete a prop question"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_answers WHERE question_id = ?', (question_id,))
    cursor.execute('DELETE FROM prop_questions WHERE id = ?', (question_id,))
    conn.commit()
    conn.close()
    
    flash('Question deleted.', 'success')
    return redirect(url_for('admin_questions'))


@app.route('/admin/questions/reorder', methods=['POST'])
@login_required
@admin_required
def admin_reorder_questions():
    """Reorder questions via drag and drop"""
    data = request.get_json()
    if not data or 'order' not in data:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for index, question_id in enumerate(data['order']):
        cursor.execute(
            'UPDATE prop_questions SET display_order = ? WHERE id = ?',
            (index, question_id)
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


@app.route('/admin/change-password', methods=['POST'])
@login_required
@admin_required
def admin_change_password():
    """Change admin password"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not current_user.check_admin_password(current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('admin_panel'))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters.', 'error')
        return redirect(url_for('admin_panel'))
    
    if new_password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('admin_panel'))
    
    current_user.set_admin_password(new_password)
    current_user.save()
    
    flash('Password changed!', 'success')
    return redirect(url_for('admin_panel'))


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/save-answer', methods=['POST'])
@login_required
def api_save_answer():
    """Auto-save individual answers"""
    if Settings.is_locked():
        return jsonify({'success': False, 'error': 'Submissions are locked'})
    
    data = request.get_json()
    question_id = data.get('question_id')
    answer = data.get('answer')
    
    if question_id and answer:
        UserAnswer.save_answer(current_user.id, int(question_id), answer)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid data'})


@app.route('/api/save-freeform', methods=['POST'])
@login_required
def api_save_freeform():
    """Auto-save freeform field answers"""
    if Settings.is_locked():
        return jsonify({'success': False, 'error': 'Submissions are locked'})
    
    data = request.get_json()
    field_id = data.get('field_id')
    value = data.get('value')
    
    if field_id and value is not None:
        UserFreeformAnswer.save_answer(current_user.id, field_id, str(value))
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Invalid data'})


@app.route('/api/lock-status')
@login_required
def api_lock_status():
    """Get current lock status"""
    lock_time = Settings.get_lock_time()
    return jsonify({
        'is_locked': Settings.is_locked(),
        'lock_time': lock_time.isoformat() if lock_time else None
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


# ============================================================================
# TEMPLATE CONTEXT
# ============================================================================

@app.context_processor
def utility_processor():
    """Add utility functions to template context"""
    return {
        'now': datetime.utcnow,
        'is_locked': Settings.is_locked
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
