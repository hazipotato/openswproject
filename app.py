from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import os
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secure random secret key

# 데이터베이스 초기화
def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL
                          )''')
        conn.commit()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[2], password):
                session['username'] = username
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password')
                return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            if user:
                flash('Username already exists')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                           (username, hashed_password))
            conn.commit()

            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        if request.method == 'POST':
            try:
                # Execute make_rect.py
                logging.debug("Running make_rect.py")
                subprocess.run(['python', 'make_rect.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                
                # Execute make_prob.py
                logging.debug("Running make_prob.py")
                result_prob = subprocess.run(
                    ['python', 'make_prob.py'], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    encoding='utf-8',  # 인코딩 설정
                    check=True
                )
                logging.debug(f"make_prob.py output: {result_prob.stdout}, error: {result_prob.stderr}")

                # Return the problem output in JSON format
                return jsonify({
                    'problem_output': result_prob.stdout,
                    'stderr': result_prob.stderr,
                    'solution_available': True
                })
                
            except subprocess.CalledProcessError as e:
                logging.error(f"Subprocess error: {e.stderr}")
                return jsonify({
                    'error': f"Subprocess error: {e.stderr}",
                    'solution_available': False
                })
            except FileNotFoundError as e:
                logging.error(f"File not found: {e}")
                return jsonify({
                    'error': str(e),
                    'solution_available': False
                })
            except Exception as e:
                logging.error(f"General error: {e}")
                return jsonify({
                    'error': str(e),
                    'solution_available': False
                })
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/get_solution', methods=['POST'])
def get_solution():
    if 'username' in session:
        try:
            # Execute make_sol.py
            logging.debug("Running make_sol.py")
            result_sol = subprocess.run(
                ['python', 'make_sol.py'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                encoding='utf-8',  # 인코딩 설정
                check=True
            )
            logging.debug(f"make_sol.py output: {result_sol.stdout}, error: {result_sol.stderr}")

            # Return the solution output in JSON format
            return jsonify({
                'solution_output': result_sol.stdout,
                'stderr': result_sol.stderr
            })

        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess error: {e.stderr}")
            return jsonify({
                'error': f"Subprocess error: {e.stderr}"
            })
        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
            return jsonify({
                'error': str(e)
            })
        except Exception as e:
            logging.error(f"General error: {e}")
            return jsonify({
                'error': str(e)
            })
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)