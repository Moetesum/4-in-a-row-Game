import sys
import numpy as np
import random
import math
import streamlit as st

# ---- CONFIGURATION ----
row_count = 7
col_count = 8
human = 0 
AI = 1
human_ball = 1
AI_ball = 2
win_length = 4
empty = 0

# ---- STREAMLIT UI SETUP ----
st.set_page_index = 0
st.title("🔴 Connect 4 AI Game 🟡")
st.write("Desktop layout ke bajaye yeh app ab direct browser mein chalegi!")

# Initialize state variables inside Streamlit Session State
if "board" not in st.session_state:
    st.session_state.board = np.zeros((row_count, col_count))
    st.session_state.turn = random.randint(human, AI)
    st.session_state.game_over = False
    st.session_state.winner_msg = ""

# ---- GAME LOGIC FUNCTIONS (SAME AS YOURS) ----
def ball_placement(b, row, column, ball):
    b[row][column] = ball

def check_row(b, column):
    for i in range(row_count):
        if b[i][column] == 0:
            return i

def is_valid_column(b, column):
    return b[row_count-1][column] == 0

def check_win(b, ball):
    # Horizontal
    for i in range(row_count):
        for j in range(col_count - 3):
            if b[i][j] == ball and b[i][j + 1] == ball and b[i][j + 2] == ball and b[i][j + 3] == ball:
                return True
    # Vertical
    for i in range(row_count - 3):
        for j in range(col_count):
            if b[i][j] == ball and b[i + 1][j] == ball and b[i + 2][j] == ball and b[i + 3][j] == ball:
                return True
    # Diagonal (+)
    for i in range(row_count - 3):
        for j in range(col_count - 3):
            if b[i][j] == ball and b[i + 1][j + 1] == ball and b[i + 2][j + 2] == ball and b[i + 3][j + 3] == ball:
                return True
    # Diagonal (-)
    for i in range(row_count - 3):
        for j in range(3, col_count):
            if b[i][j] == ball and b[i + 1][j - 1] == ball and b[i + 2][j - 2] == ball and b[i + 3][j - 3] == ball:
                return True
    return False

def eval_window(window, ball):
    opp_piece = human_ball
    if ball == human_ball:
        opp_piece = AI_ball
    score = 0
    if window.count(ball) == 4:
        score += 100
    elif window.count(ball) == 3 and window.count(empty) == 1:
        score += 5
    elif window.count(ball) == 2 and window.count(empty) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(empty) == 1:
        score -= 4
    return score

def win_position(b, ball):
    score = 0
    center_arr = [int(k) for k in list(b[:, col_count // 2])]
    center_count = center_arr.count(ball)
    score += center_count * 3

    for i in range(row_count):
        row_arr = [int(k) for k in list(b[i, :])]
        for j in range(col_count - 3):
            window = row_arr[j:j + win_length]
            score += eval_window(window, ball)

    for j in range(col_count):
        col_arr = [int(k) for k in list(b[:, j])]
        for i in range(row_count - 3):
            window = col_arr[i:i + win_length]
            score += eval_window(window, ball)

    for i in range(row_count - 3):
        for j in range(col_count - 3):
            window = [b[i + k][j + k] for k in range(win_length)]
            score += eval_window(window, ball)

    for i in range(row_count - 3):
        for j in range(col_count - 3):
            window = [b[i + 3 - k][j + k] for k in range(win_length)]
            score += eval_window(window, ball)
    return score

def get_valid_locations(b):
    valid_locations = []
    for i in range(col_count):
        if is_valid_column(b, i):
            valid_locations.append(i)
    return valid_locations

def find_terminal_node(b):
    return check_win(b, human_ball) or check_win(b, AI_ball) or len(get_valid_locations(b)) == 0

def minmax_algo(b, depth, maximizingplayer):
    valid_location = get_valid_locations(b)
    terminal_node = find_terminal_node(b)
    if depth == 0 or terminal_node:
        if terminal_node:
            if check_win(b, AI_ball):
                return (None, 100000000000000)
            elif check_win(b, human_ball):
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, win_position(b, AI_ball))
            
    if maximizingplayer:
        value = -math.inf
        columnn = random.choice(valid_location) if valid_location else 0
        for j in valid_location:
            i = check_row(b, j)
            b_copy = b.copy()
            ball_placement(b_copy, i, j, AI_ball)
            new_score = minmax_algo(b_copy, depth - 1, False)[1]
            if new_score > value:
                value = new_score
                columnn = j
        return columnn, value
    else:
        value = math.inf
        column = random.choice(valid_location) if valid_location else 0
        for j in valid_location:
            i = check_row(b, j)
            b_copy = b.copy()
            ball_placement(b_copy, i, j, human_ball)
            new_score = minmax_algo(b_copy, depth - 1, True)[1]
            if new_score < value:
                value = new_score
                column = j
        return column, value

# ---- GAME STEP HANDLERS ----
def make_human_move(col):
    if st.session_state.game_over:
        return
        
    b = st.session_state.board
    if is_valid_column(b, col):
        row = check_row(b, col)
        ball_placement(b, row, col, human_ball)
        
        if check_win(b, human_ball):
            st.session_state.winner_msg = "🏆 PLAYER 1 WINS!!!"
            st.session_state.game_over = True
        else:
            st.session_state.turn = AI

def run_ai_move():
    b = st.session_state.board
    column, minmax_score = minmax_algo(b, 3, True) # depth 3 keeps it responsive on web
    if column is not None and is_valid_column(b, column):
        row = check_row(b, column)
        ball_placement(b, row, column, AI_ball)
        
        if check_win(b, AI_ball):
            st.session_state.winner_msg = "🤖 AI WINS!!!"
            st.session_state.game_over = True
        else:
            st.session_state.turn = human

# ---- TRIGGER AI TURNS AUTOMATICALLY ----
if st.session_state.turn == AI and not st.session_state.game_over:
    run_ai_move()
    st.rerun()

# ---- RENDER STREAMLIT INTERFACE ----
if st.session_state.game_over:
    if "🏆" in st.session_state.winner_msg:
        st.success(st.session_state.winner_msg)
    else:
        st.error(st.session_state.winner_msg)
        
    if st.button("Reset Game"):
        st.session_state.board = np.zeros((row_count, col_count))
        st.session_state.game_over = False
        st.session_state.turn = random.randint(human, AI)
        st.session_state.winner_msg = ""
        st.rerun()

# Interactive columns for row drops
st.write("### Drop your Piece:")
cols_buttons = st.columns(col_count)
for c in range(col_count):
    with cols_buttons[c]:
        is_disabled = st.session_state.game_over or (st.session_state.turn == AI) or not is_valid_column(st.session_state.board, c)
        if st.button(f"👇 C{c+1}", key=f"btn_{c}", disabled=is_disabled):
            make_human_move(c)
            st.rerun()

# Draw visual grid using Grid Columns & Emojis
st.write("### Game Board:")
for r in reversed(range(row_count)):
    cols_visual = st.columns(col_count)
    for c in range(col_count):
        val = st.session_state.board[r][c]
        if val == human_ball:
            cols_visual[c].markdown("<h2 style='text-align: center; margin:0;'>🔴</h2>", unsafe_allow_html=True)
        elif val == AI_ball:
            cols_visual[c].markdown("<h2 style='text-align: center; margin:0;'>🟡</h2>", unsafe_allow_html=True)
        else:
            cols_visual[c].markdown("<h2 style='text-align: center; margin:0;'>⚫</h2>", unsafe_allow_html=True)
