# Super Bowl Props Web App

A lightweight web application for running Super Bowl prop bet pools with friends and family.

## Features

- 🏈 **Prop Bet Form**: Users can fill out their predictions for various Super Bowl prop bets
- 👥 **User Management**: Invite users via email with secure invite links
- ⏰ **Deadline System**: Set a lock time after which no more picks can be submitted
- 🔑 **Master Key**: Admin can enter correct answers as the game unfolds
- 🏆 **Leaderboard**: Real-time scoring and rankings after the deadline
- 📊 **Dashboard**: View everyone's picks and compare answers

## Quick Start (Development)

```bash
# Clone or download the project
cd superbowl-props

# Make the run script executable and run it
chmod +x run_dev.sh
./run_dev.sh
```

Then open http://localhost:5000 in your browser.

**Default admin login:**
- Email: `admin@example.com`
- Password: `admin123`

## Production Deployment (Ubuntu Server)

1. Copy all files to your server
2. Run the setup script:

```bash
chmod +x setup.sh
sudo ./setup.sh
```

This will:
- Install Python and nginx
- Create a virtual environment
- Install dependencies
- Set up a systemd service
- Configure nginx as a reverse proxy

The app will be available at `http://your-server-ip`

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
nano .env
```

Key settings:
- `SECRET_KEY`: Change this to a random string for production!
- `APP_URL`: Your server's URL (used in invite emails)
- `MAIL_*`: Email settings for sending invite links (optional)

### Email Configuration (Optional)

To send invite emails automatically, configure the MAIL settings in `.env`. 

For Gmail:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password at: https://myaccount.google.com/apppasswords
3. Use that app password in `MAIL_PASSWORD`

If email is not configured, invite links will be shown in the admin panel for manual sharing.

## Usage

### As Admin

1. Log in with admin credentials
2. Go to **Admin** panel
3. **Invite users**: Enter their email to send an invite (or get a link to share)
4. **Set deadline**: Choose when picks should be locked
5. **Manage questions**: Add, edit, or remove prop bet questions
6. **Set answers**: As the game progresses, enter the correct answers

### As a Participant

1. Click the invite link received via email
2. Set up your account (display name and password)
3. Go to **My Picks** and select your predictions
4. Wait for the deadline to see everyone's picks on the **Dashboard**

## File Structure

```
superbowl-props/
├── app.py              # Main Flask application
├── database.py         # Database models and functions
├── config.py           # Configuration settings
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependencies
├── setup.sh            # Production setup script
├── run_dev.sh          # Development server script
├── .env.example        # Example environment variables
├── templates/          # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── accept_invite.html
│   ├── prop_form.html
│   ├── dashboard.html
│   ├── admin/
│   │   ├── panel.html
│   │   ├── answers.html
│   │   └── questions.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
└── data/               # SQLite database (created automatically)
    └── superbowl_props.db
```

## Tech Stack

- **Backend**: Python 3 with Flask
- **Database**: SQLite (no separate database server needed)
- **Frontend**: Vanilla HTML/CSS/JavaScript (no build step required)
- **Server**: Gunicorn + nginx (production)

## Customizing Questions

The app loads prop questions from `props_config.json`. Edit this file to customize:

```json
{
  "event": {
    "name": "Super Bowl 60",
    "matchup": "Seahawks vs. Patriots",
    "type": "Party Prop Sheet"
  },
  "props": [
    {
      "id": "coin_toss",
      "category": "Pre-Game",
      "label": "Coin Toss",
      "options": [
        { "side": "A", "display": "Heads" },
        { "side": "B", "display": "Tails" }
      ]
    }
  ]
}
```

Each prop needs:
- `id`: Unique identifier (for your reference)
- `category`: Groups questions together on the form
- `label`: The question text shown to users
- `options`: Array with exactly 2 options (A and B)

After editing, reload the questions:
```bash
python init_db.py --reset
```

You can also add/edit questions in the admin panel at Admin > Manage Questions.

## Troubleshooting

### Can't send emails
- Check your MAIL_* settings in `.env`
- For Gmail, make sure you're using an App Password
- If email doesn't work, invite links are shown in the admin panel

### Database issues
- Delete `data/superbowl_props.db` and run `python init_db.py` to reset

### Service won't start (production)
```bash
sudo journalctl -u superbowl-props -f  # View logs
sudo systemctl status superbowl-props  # Check status
```

## Security Notes

- Change the default admin password immediately
- Set a strong `SECRET_KEY` in production
- Consider using HTTPS (you can add SSL with Let's Encrypt)
- The invite tokens expire after 72 hours

## License

MIT License - Feel free to use and modify for your Super Bowl party!
