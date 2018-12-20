from flask import Flask, render_template, request
import os
import csv
import datetime
import time
import numpy as np

app = Flask(__name__)

# limit file size limit for form submission in Bytes
app.config['MAX_CONTENT_LENGTH'] = 9 * 1024 * 1024

DIR_DATA = "data"
FILE_USERS = "users.csv"
FILE_USERS_STATS = "stats.csv"
FILE_SCORES = "scores.csv"
FILE_SCORES_FINAl = "scores_final.csv"
FILE_VALIDATE = "qualifying.csv"
FILE_NP_VALIDATE_IDX = "qualifying_idx.npy"
FILE_NP_VALIDATE_IDX_FINAL = "qualifying_idx_final.npy"

ABS = os.path.dirname(os.path.abspath(__file__))
DIR_DATA = os.path.join(ABS, DIR_DATA)

COMMITS_PER_HOUR = 5

FINAL_VALIDATION_DATE = datetime.datetime(2019, 7, 30)
# FINAL_VALIDATION_DATE = datetime.datetime.now()


class WebException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def get_users():
    with open(os.path.join(DIR_DATA, FILE_USERS), "r") as file:
        users = [(user, nick)
                 for user, nick in csv.reader(file, delimiter=',')]
        users, nicks = zip(*users)
    return users, nicks


def get_scores(nick=None, format=True, allscores=False):
    if FINAL_VALIDATION_DATE < datetime.datetime.now():
        sf = FILE_SCORES_FINAl
    else:
        sf = FILE_SCORES
    high_scores = []
    high_score = np.inf
    with open(os.path.join(DIR_DATA, sf), "r") as file:
        reader = csv.reader(file)
        for user, score, timestamp in reader:
            if nick is not None and nick != user:
                continue
            if len(high_scores) == 0 or high_score >= score:
                high_scores.append((score, timestamp))
                high_score = score
            elif allscores:
                high_scores.append((score, timestamp))
    if format:
        high_score = "{:0.3f}".format(float(high_score))
        high_scores = [("{:0.3f}".format(float(s)), ts)
                       for s, ts in high_scores]
    return high_scores


def get_user_ranking(format=True):
    if FINAL_VALIDATION_DATE < datetime.datetime.now():
        sf = FILE_SCORES_FINAl
    else:
        sf = FILE_SCORES
    users, nicks = get_users()
    user_scores = {nick: np.inf for nick in nicks}
    with open(os.path.join(DIR_DATA, sf), "r") as file:
        reader = csv.reader(file)
        for nick, score, timestamp in reader:
            if float(user_scores[nick]) > float(score):
                user_scores[nick] = score
    ranking = sorted(user_scores.items(), key=lambda kv: float(kv[1]))
    ranking = [(i + 1, nick, score) for i, (nick, score) in enumerate(ranking)]
    if format:
        ranking = [(r, n, "{:0.3f}".format(float(s))) for r, n, s in ranking]
    return ranking


def add_score(user, score):
    if FINAL_VALIDATION_DATE < datetime.datetime.now():
        sf = FILE_SCORES_FINAl
    else:
        sf = FILE_SCORES
    timestamp = time.time()
    with open(os.path.join(DIR_DATA, sf), "a") as file:
        writer = csv.writer(file)
        writer.writerow([user, score, timestamp])


def calculate_rmse(X_act, X_exp):
    if FINAL_VALIDATION_DATE < datetime.datetime.now():
        idx = np.fromfile(os.path.join(
            DIR_DATA, FILE_NP_VALIDATE_IDX_FINAL), dtype=np.int)
    else:
        idx = np.fromfile(os.path.join(
            DIR_DATA, FILE_NP_VALIDATE_IDX), dtype=np.int)
    X_act = X_act[idx]
    X_exp = X_exp[idx]
    return np.sqrt(((X_act[:, 2] - X_exp[:, 2]) ** 2).mean())


def get_actual_predictions():
    X = np.genfromtxt(os.path.join(DIR_DATA, FILE_VALIDATE),
                      delimiter=",", dtype=np.int)
    X = X[np.lexsort((X[:, 0], X[:, 1]))]
    return X


@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html")


@app.route('/documentation', methods=['GET'])
def documentation():
    return render_template("documentation.html")


@app.route('/tasks', methods=['GET'])
def tasks():
    return render_template("tasks.html")


@app.route('/', methods=['GET'])
def index():
    final_validation = False
    if FINAL_VALIDATION_DATE < datetime.datetime.now():
            final_validation = True
    return render_template('home.html',
                           high_scores=get_scores(),
                           user_ranking=get_user_ranking(),
                           final_validation=final_validation)


def validate_user(request):
    users, nicks = get_users()
    user = request.form.get('user')
    if user not in users:
        raise WebException("Invalid or missing user")
    nick = nicks[users.index(user)]
    return nick


def validate_file(request):
    file = request.files.get("file")
    if not file:
        raise WebException("No file submitted!")
    try:
        data = file.read().decode("utf-8")
    except UnicodeDecodeError:
        raise WebException("Invalid encoding! Expecting utf-8!")
    X_exp = get_actual_predictions()
    nrows, ncols = X_exp.shape
    data = data.split("\n")
    if data[-1] == '':
        data = data[:-1]
    data = [row.split(",") for row in data]
    if len(data) != nrows or len(data[0]) != ncols:
        raise WebException(
            "Invalid shape! Expecting ({:d}, {:d})".format(nrows, ncols))
    try:
        X = np.array([[np.float(i) for i in row] for row in data])
    except ValueError:
        raise WebException("Invalid number format!")
    X = X[np.lexsort((X[:, 0], X[:, 1]))]
    if not X_exp.shape == X.shape:
        raise WebException(
            "Invalid shape 2! Expecting ({:d}, {:d})".format(nrows, ncols))
    if not np.array_equal(X[:, 0:2], X_exp[:, 0:2]):
        raise WebException("You must submit the right predictions!")
    return X, X_exp


def validate_file_content(X_act, X_exp):
    if not X_act.shape == X_exp.shape:
        raise WebException("Invalid shape!")
    if not np.array_equal(X_act[:, 0:2], X_exp[:, 0:2]):
        raise WebException("You must submit the right predictions!")


def can_submit(nick):
    scores = get_scores(nick, allscores=True)
    if not scores:
        return
    t1 = time.time()
    t0 = 0
    scores, times = zip(*scores)
    if len(times) > COMMITS_PER_HOUR:
        t0 = float(times[-COMMITS_PER_HOUR])
    if t1 - t0 < 3600:
        td = 3600 - int(t1 - t0)
        hms = str(datetime.timedelta(seconds=td))
        raise WebException("You can submit again in {:0>8} hours!".format(hms))


@app.route('/upload', methods=['POST'])
def file_submission():
    final_validation = False
    try:
        nick = validate_user(request)
        X_act, X_exp = validate_file(request)
        score = calculate_rmse(X_act, X_exp)
        can_submit(nick)
        add_score(nick, score)
        score = "{:0.3f}".format(score)
        if FINAL_VALIDATION_DATE < datetime.datetime.now():
            final_validation = True
    except WebException as e:
        return render_template('home.html',
                               errmsg=e.message,
                               high_scores=get_scores(),
                               user_ranking=get_user_ranking(),
                               final_validation=final_validation)
    else:
        return render_template('home.html',
                               score=score,
                               high_scores=get_scores(),
                               user_ranking=get_user_ranking(),
                               final_validation=final_validation)


if __name__ == '__main__':
    app.run(debug=True)
