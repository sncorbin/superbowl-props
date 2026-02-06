#!/usr/bin/env python3
"""
Initialize the database with tables and default data
"""
import os
import sys
import json
import sqlite3

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, User, PropQuestion, get_db_connection

PROPS_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'props_config.json')

def create_default_admin():
    """Create default admin user if it doesn't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE is_admin = 1 LIMIT 1')
    admin_row = cursor.fetchone()
    conn.close()
    
    if admin_row is None:
        import secrets
        admin = User(
            display_name='Commissioner',
            access_token=secrets.token_urlsafe(16),
            is_admin=True
        )
        # Use MASTER_KEY env var or default password
        admin_password = os.environ.get('MASTER_KEY', 'superbowl2025')
        admin.set_admin_password(admin_password)
        admin.save()
        print("✓ Created default admin user")
        print(f"  Admin Password: {'(from MASTER_KEY env var)' if os.environ.get('MASTER_KEY') else 'superbowl2025'}")
    else:
        print("• Admin user already exists")


def create_default_questions():
    """Create default Super Bowl prop questions from props_config.json"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM prop_questions')
    count = cursor.fetchone()['count']
    conn.close()
    
    if count > 0:
        print(f"• {count} questions already exist (use --reset to reload from config)")
        return
    
    # Load props from JSON config file
    if not os.path.exists(PROPS_CONFIG_FILE):
        print(f"⚠ Props config file not found: {PROPS_CONFIG_FILE}")
        print("  Create props_config.json or add questions manually in the admin panel.")
        return
    
    with open(PROPS_CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    event = config.get('event', {})
    props = config.get('props', [])
    
    if event:
        print(f"  Event: {event.get('name', 'Unknown')} - {event.get('matchup', '')}")
    
    for i, prop in enumerate(props):
        category = prop.get('category', 'Props')
        label = prop.get('label', f"Question {i+1}")
        options = prop.get('options', [])
        
        # Handle options - can be list of strings or list of objects with over/under
        if len(options) >= 2:
            if isinstance(options[0], dict):
                # Over/under format: {"side": "over", "value": 45.5}
                opt = options[0]
                if 'side' in opt and 'value' in opt:
                    option_a = f"Over {opt['value']}"
                    option_b = f"Under {options[1]['value']}"
                else:
                    option_a = opt.get('display', 'Option A')
                    option_b = options[1].get('display', 'Option B')
            else:
                # Simple string format: ["Heads", "Tails"]
                option_a = str(options[0])
                option_b = str(options[1])
        else:
            option_a = "Yes"
            option_b = "No"
        
        q = PropQuestion(
            category=category,
            question=label,
            option_a=option_a,
            option_b=option_b,
            display_order=i
        )
        q.save()
    
    print(f"✓ Loaded {len(props)} prop questions from config")
    
    # Load freeform fields (tiebreakers)
    freeform_fields = config.get('freeform_fields', [])
    if freeform_fields:
        conn = get_db_connection()
        cursor = conn.cursor()
        for i, field in enumerate(freeform_fields):
            cursor.execute('''
                INSERT OR REPLACE INTO freeform_fields (field_id, label, field_type, placeholder, display_order)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                field.get('id', f'field_{i}'),
                field.get('label', f'Field {i+1}'),
                field.get('type', 'number'),
                field.get('placeholder', ''),
                i
            ))
        conn.commit()
        conn.close()
        print(f"✓ Loaded {len(freeform_fields)} freeform fields (tiebreakers)")


def reset_questions():
    """Delete all questions and reload from config"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_answers')
    cursor.execute('DELETE FROM prop_questions')
    # Also reset freeform fields
    try:
        cursor.execute('DELETE FROM user_freeform_answers')
        cursor.execute('DELETE FROM freeform_fields')
    except sqlite3.OperationalError:
        pass  # Tables might not exist yet
    conn.commit()
    conn.close()
    print("✓ Cleared all existing questions and answers")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Initialize Super Bowl Props database')
    parser.add_argument('--reset', action='store_true', 
                        help='Reset and reload prop questions from props_config.json')
    parser.add_argument('--reset-all', action='store_true',
                        help='Reset entire database (WARNING: deletes all data)')
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("Super Bowl Props - Database Initialization")
    print("="*50 + "\n")
    
    if args.reset_all:
        confirm = input("⚠️  This will DELETE ALL DATA. Type 'yes' to confirm: ")
        if confirm.lower() == 'yes':
            db_path = os.path.join(os.path.dirname(__file__), 'data', 'superbowl_props.db')
            if os.path.exists(db_path):
                os.remove(db_path)
                print("✓ Database deleted")
        else:
            print("Cancelled.")
            return
    
    # Initialize tables
    print("Initializing database tables...")
    init_db()
    print("✓ Database tables created\n")
    
    # Create default admin
    print("Setting up default admin account...")
    create_default_admin()
    print()
    
    # Reset questions if requested
    if args.reset:
        print("Resetting prop questions...")
        reset_questions()
    
    # Create default questions
    print("Setting up prop questions...")
    create_default_questions()
    print()
    
    print("="*50)
    print("🏈 Database initialization complete!")
    print("="*50)
    print("\n🔐 Admin Panel: /admin/login")
    print("   Default Password: superbowl2025")
    print("\n⚠️  IMPORTANT: Change the admin password after first login!")
    print("\n📋 To reload props from config: python init_db.py --reset\n")


if __name__ == '__main__':
    main()
