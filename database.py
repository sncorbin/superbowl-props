"""
Database module for Super Bowl Props Web App
Uses SQLite for minimal dependencies
"""
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config


def get_db_connection():
    """Get a database connection with row factory enabled"""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table - simplified with access token auth
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            display_name TEXT NOT NULL,
            access_token TEXT UNIQUE NOT NULL,
            is_admin INTEGER DEFAULT 0,
            admin_password TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_visit TEXT
        )
    ''')
    
    # Settings table for app-wide settings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Prop questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prop_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            correct_answer TEXT,
            display_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # User answers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            answer TEXT NOT NULL,
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (question_id) REFERENCES prop_questions (id),
            UNIQUE (user_id, question_id)
        )
    ''')
    
    # Freeform fields table (for tiebreakers, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS freeform_fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_id TEXT UNIQUE NOT NULL,
            label TEXT NOT NULL,
            field_type TEXT DEFAULT 'number',
            placeholder TEXT,
            correct_value TEXT,
            display_order INTEGER DEFAULT 0
        )
    ''')
    
    # User freeform answers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_freeform_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            field_id TEXT NOT NULL,
            value TEXT NOT NULL,
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE (user_id, field_id)
        )
    ''')
    
    conn.commit()
    conn.close()


class User:
    """User model class - simplified with access token auth"""
    
    def __init__(self, id=None, display_name=None, access_token=None,
                 is_admin=False, admin_password=None, created_at=None, last_visit=None):
        self.id = id
        self.display_name = display_name
        self.access_token = access_token
        self.is_admin = is_admin
        self.admin_password = admin_password
        self.created_at = created_at
        self.last_visit = last_visit
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    def check_admin_password(self, password):
        if not self.admin_password:
            return False
        return check_password_hash(self.admin_password, password)
    
    def set_admin_password(self, password):
        self.admin_password = generate_password_hash(password)
    
    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return User(
            id=row['id'],
            display_name=row['display_name'],
            access_token=row['access_token'],
            is_admin=bool(row['is_admin']),
            admin_password=row['admin_password'],
            created_at=row['created_at'],
            last_visit=row['last_visit']
        )
    
    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return User.from_row(row)
    
    @staticmethod
    def get_by_access_token(token):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE access_token = ?', (token,))
        row = cursor.fetchone()
        conn.close()
        return User.from_row(row)
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY display_name')
        rows = cursor.fetchall()
        conn.close()
        return [User.from_row(row) for row in rows]
    
    @staticmethod
    def get_active_users():
        """Get all non-admin users"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE is_admin = 0 ORDER BY display_name')
        rows = cursor.fetchall()
        conn.close()
        return [User.from_row(row) for row in rows]
    
    @staticmethod
    def get_participants():
        """Get all participants (non-admin users)"""
        return User.get_active_users()
    
    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if self.id is None:
            cursor.execute('''
                INSERT INTO users (display_name, access_token, is_admin, admin_password)
                VALUES (?, ?, ?, ?)
            ''', (self.display_name, self.access_token, int(self.is_admin), self.admin_password))
            self.id = cursor.lastrowid
        else:
            cursor.execute('''
                UPDATE users SET display_name = ?, access_token = ?,
                                 is_admin = ?, admin_password = ?, last_visit = ?
                WHERE id = ?
            ''', (self.display_name, self.access_token, int(self.is_admin),
                  self.admin_password, self.last_visit, self.id))
        
        conn.commit()
        conn.close()
        return self
    
    def delete(self):
        if self.id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_answers WHERE user_id = ?', (self.id,))
            cursor.execute('DELETE FROM user_freeform_answers WHERE user_id = ?', (self.id,))
            cursor.execute('DELETE FROM users WHERE id = ?', (self.id,))
            conn.commit()
            conn.close()


class PropQuestion:
    """Prop question model class"""
    
    def __init__(self, id=None, category=None, question=None, option_a=None,
                 option_b=None, correct_answer=None, display_order=0, is_active=True):
        self.id = id
        self.category = category
        self.question = question
        self.option_a = option_a
        self.option_b = option_b
        self.correct_answer = correct_answer
        self.display_order = display_order
        self.is_active = is_active
    
    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return PropQuestion(
            id=row['id'],
            category=row['category'],
            question=row['question'],
            option_a=row['option_a'],
            option_b=row['option_b'],
            correct_answer=row['correct_answer'],
            display_order=row['display_order'],
            is_active=bool(row['is_active'])
        )
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prop_questions ORDER BY display_order, id')
        rows = cursor.fetchall()
        conn.close()
        return [PropQuestion.from_row(row) for row in rows]
    
    @staticmethod
    def get_active():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prop_questions WHERE is_active = 1 ORDER BY display_order, id')
        rows = cursor.fetchall()
        conn.close()
        return [PropQuestion.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(question_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prop_questions WHERE id = ?', (question_id,))
        row = cursor.fetchone()
        conn.close()
        return PropQuestion.from_row(row)
    
    @staticmethod
    def get_by_category():
        """Get questions grouped by category"""
        questions = PropQuestion.get_active()
        categories = {}
        for q in questions:
            if q.category not in categories:
                categories[q.category] = []
            categories[q.category].append(q)
        return categories
    
    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if self.id is None:
            cursor.execute('''
                INSERT INTO prop_questions (category, question, option_a, option_b,
                                            correct_answer, display_order, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.category, self.question, self.option_a, self.option_b,
                  self.correct_answer, self.display_order, int(self.is_active)))
            self.id = cursor.lastrowid
        else:
            cursor.execute('''
                UPDATE prop_questions SET category = ?, question = ?, option_a = ?,
                                          option_b = ?, correct_answer = ?,
                                          display_order = ?, is_active = ?
                WHERE id = ?
            ''', (self.category, self.question, self.option_a, self.option_b,
                  self.correct_answer, self.display_order, int(self.is_active), self.id))
        
        conn.commit()
        conn.close()
        return self


class UserAnswer:
    """User answer model class"""
    
    def __init__(self, id=None, user_id=None, question_id=None, answer=None, submitted_at=None):
        self.id = id
        self.user_id = user_id
        self.question_id = question_id
        self.answer = answer
        self.submitted_at = submitted_at
    
    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return UserAnswer(
            id=row['id'],
            user_id=row['user_id'],
            question_id=row['question_id'],
            answer=row['answer'],
            submitted_at=row['submitted_at']
        )
    
    @staticmethod
    def get_user_answers(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_answers WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return {row['question_id']: row['answer'] for row in rows}
    
    @staticmethod
    def get_all_answers():
        """Get all user answers as a dict: {user_id: {question_id: answer}}"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_answers')
        rows = cursor.fetchall()
        conn.close()
        
        answers = {}
        for row in rows:
            if row['user_id'] not in answers:
                answers[row['user_id']] = {}
            answers[row['user_id']][row['question_id']] = row['answer']
        return answers
    
    @staticmethod
    def save_answer(user_id, question_id, answer):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_answers (user_id, question_id, answer, submitted_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, question_id, answer, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
    
    @staticmethod
    def save_all_answers(user_id, answers_dict):
        """Save multiple answers at once"""
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        for question_id, answer in answers_dict.items():
            cursor.execute('''
                INSERT OR REPLACE INTO user_answers (user_id, question_id, answer, submitted_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, int(question_id), answer, now))
        
        conn.commit()
        conn.close()


class Settings:
    """App settings helper class"""
    
    @staticmethod
    def get(key, default=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        return row['value'] if row else default
    
    @staticmethod
    def set(key, value):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_lock_time():
        """Get the lock time as a datetime object"""
        lock_time_str = Settings.get('lock_time')
        if lock_time_str:
            return datetime.fromisoformat(lock_time_str)
        return None
    
    @staticmethod
    def set_lock_time(dt):
        """Set the lock time from a datetime object"""
        Settings.set('lock_time', dt.isoformat())
    
    @staticmethod
    def is_locked():
        """Check if submissions are currently locked"""
        lock_time = Settings.get_lock_time()
        if lock_time is None:
            return False
        return datetime.now() >= lock_time


class GameConfig:
    """Game configuration helper class for Super Bowl settings"""
    
    # Default game configuration keys
    KEYS = {
        'super_bowl_number': 'LX',
        'game_date': '2026-02-08',
        'game_time': '18:30',
        'venue_name': "Levi's Stadium",
        'venue_city': 'Santa Clara',
        'venue_state': 'CA',
        'team_a_code': 'KC',
        'team_b_code': 'PHI',
        'pool_name': 'Pioneer Hill Super Bowl Pool',
        'pool_tagline': 'Pullman\'s Premier Prop Bet Experience'
    }
    
    @staticmethod
    def get(key, default=None):
        """Get a game config value"""
        if default is None:
            default = GameConfig.KEYS.get(key, '')
        return Settings.get(f'game_{key}', default)
    
    @staticmethod
    def set(key, value):
        """Set a game config value"""
        Settings.set(f'game_{key}', value)
    
    @staticmethod
    def get_all():
        """Get all game configuration as a dictionary"""
        config = {}
        for key, default in GameConfig.KEYS.items():
            config[key] = GameConfig.get(key, default)
        return config
    
    @staticmethod
    def set_all(config_dict):
        """Set multiple game config values"""
        for key, value in config_dict.items():
            if key in GameConfig.KEYS:
                GameConfig.set(key, value)
    
    @staticmethod
    def get_team_a():
        """Get team A data"""
        from nfl_teams import get_team
        code = GameConfig.get('team_a_code', 'KC')
        return get_team(code)
    
    @staticmethod
    def get_team_b():
        """Get team B data"""
        from nfl_teams import get_team
        code = GameConfig.get('team_b_code', 'PHI')
        return get_team(code)
    
    @staticmethod
    def get_game_datetime():
        """Get game date and time as datetime object"""
        date_str = GameConfig.get('game_date', '2026-02-08')
        time_str = GameConfig.get('game_time', '18:30')
        try:
            return datetime.fromisoformat(f"{date_str}T{time_str}")
        except:
            return datetime(2026, 2, 8, 18, 30)
    
    @staticmethod
    def get_display_date():
        """Get formatted display date"""
        dt = GameConfig.get_game_datetime()
        return dt.strftime('%B %d, %Y')
    
    @staticmethod
    def get_venue_display():
        """Get formatted venue string"""
        venue = GameConfig.get('venue_name')
        city = GameConfig.get('venue_city')
        state = GameConfig.get('venue_state')
        return f"{venue} • {city}, {state}"


class FreeformField:
    """Freeform field model (for tiebreakers, etc.)"""
    
    def __init__(self, id=None, field_id=None, label=None, field_type='number',
                 placeholder=None, correct_value=None, display_order=0):
        self.id = id
        self.field_id = field_id
        self.label = label
        self.field_type = field_type
        self.placeholder = placeholder
        self.correct_value = correct_value
        self.display_order = display_order
    
    @staticmethod
    def from_row(row):
        if row is None:
            return None
        return FreeformField(
            id=row['id'],
            field_id=row['field_id'],
            label=row['label'],
            field_type=row['field_type'],
            placeholder=row['placeholder'],
            correct_value=row['correct_value'],
            display_order=row['display_order']
        )
    
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM freeform_fields ORDER BY display_order')
            rows = cursor.fetchall()
        except:
            rows = []
        conn.close()
        return [FreeformField.from_row(row) for row in rows]
    
    @staticmethod
    def get_by_field_id(field_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM freeform_fields WHERE field_id = ?', (field_id,))
        row = cursor.fetchone()
        conn.close()
        return FreeformField.from_row(row)
    
    def save(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO freeform_fields 
            (field_id, label, field_type, placeholder, correct_value, display_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.field_id, self.label, self.field_type, self.placeholder,
              self.correct_value, self.display_order))
        conn.commit()
        conn.close()


class UserFreeformAnswer:
    """User freeform answer model"""
    
    @staticmethod
    def get_user_answers(user_id):
        """Get all freeform answers for a user as {field_id: value}"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT field_id, value FROM user_freeform_answers WHERE user_id = ?', (user_id,))
            rows = cursor.fetchall()
        except:
            rows = []
        conn.close()
        return {row['field_id']: row['value'] for row in rows}
    
    @staticmethod
    def get_all_answers():
        """Get all freeform answers as {user_id: {field_id: value}}"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM user_freeform_answers')
            rows = cursor.fetchall()
        except:
            rows = []
        conn.close()
        
        answers = {}
        for row in rows:
            if row['user_id'] not in answers:
                answers[row['user_id']] = {}
            answers[row['user_id']][row['field_id']] = row['value']
        return answers
    
    @staticmethod
    def save_answer(user_id, field_id, value):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_freeform_answers (user_id, field_id, value, submitted_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, field_id, value, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
    
    @staticmethod
    def save_all_answers(user_id, answers_dict):
        """Save multiple freeform answers at once"""
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        
        for field_id, value in answers_dict.items():
            if value:  # Only save non-empty values
                cursor.execute('''
                    INSERT OR REPLACE INTO user_freeform_answers (user_id, field_id, value, submitted_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, field_id, str(value), now))
        
        conn.commit()
        conn.close()