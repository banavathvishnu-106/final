from flask import Flask, render_template, request, redirect, session
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load words from a file
try:
    with open("words.txt", "r") as file:
        words_list = [word.strip().lower() for word in file if word.strip()]
        if not words_list:
            raise ValueError("The words list is empty.")
except FileNotFoundError:
    print("The file 'words.txt' was not found.")
    words_list = []

def random_word():
    if not words_list:
        raise ValueError("The words list is empty.")
    return random.choice(words_list)

def initialize_word_state(word, level):
    """Set up the word display based on difficulty."""
    state = ["_"] * len(word)
    if level == "easy":
        state[0] = word[0]
        state[-1] = word[-1]
    elif level == "normal":
        state[0] = word[0]
    return state

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/start', methods=['POST'])
def start():
    """Initialize a new game."""
    level = request.form['level'].lower()
    word = random_word()
    session['word'] = word
    session['display'] = initialize_word_state(word, level)
    session['wrong_guesses'] = 0
    session['max_wrong'] = 6
    session['guessed_letters'] = []
    session['level'] = level
    return redirect('/play')

@app.route('/play', methods=['GET', 'POST'])
def play():
    """Handle gameplay."""
    if 'word' not in session:
        return redirect('/')

    word = session['word']
    display = session['display']
    guessed_letters = session['guessed_letters']
    wrong_guesses = session['wrong_guesses']
    max_wrong = session['max_wrong']
    message = ""

    if request.method == 'POST':
        guess = request.form['guess'].lower()
        if guess in guessed_letters:
            message = f"You already guessed '{guess}'."
        elif len(guess) != 1 or not guess.isalpha():
            message = "Please guess a single letter."
        else:
            guessed_letters.append(guess)
            if guess in word:
                for i, letter in enumerate(word):
                    if letter == guess:
                        display[i] = guess
                message = f"Good job! '{guess}' is in the word."
            else:
                session['wrong_guesses'] += 1
                message = f"'{guess}' is not in the word."

        # Update session variables
        session['display'] = display
        session['guessed_letters'] = guessed_letters

        # Check win/lose conditions
        if "_" not in display:
            return render_template('result.html', result="win", word=word)
        elif session['wrong_guesses'] >= max_wrong:
            return render_template('result.html', result="lose", word=word)

    return render_template(
        "play.html",
        display=display,
        guessed_letters=guessed_letters,
        wrong_guesses=wrong_guesses,
        max_wrong=max_wrong,
        message=message
    )

@app.route('/reset')
def reset():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)