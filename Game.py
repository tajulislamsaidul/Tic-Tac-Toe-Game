import tkinter as tk
from tkinter import messagebox
import random
import os
import pygame

pygame.mixer.init()

# Sound effect paths
SOUND_FOLDER = r"E:\Tic Tac Toe Game with GUI\Sound Effects"
WIN_SOUND = os.path.join(SOUND_FOLDER, "win.mp3")
DRAW_SOUND = os.path.join(SOUND_FOLDER, "draw.mp3")
CLICK_SOUND = os.path.join(SOUND_FOLDER, "click.mp3")
TYPE_SOUND = os.path.join(SOUND_FOLDER, "type.mp3")

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe GUI Edition")
        self.typing = False
        self.typing_job = None
        self.player1 = "Player 1"
        self.player2 = "Player 2"
        self.ai_mode = False
        self.difficulty = "easy"
        self.reset_game()
        self.create_widgets()

    def play_sound(self, file):
        try:
            pygame.mixer.Sound(file).play()
        except:
            print(f"Could not play {file}")

    def play_looping_sound(self, file):
        try:
            pygame.mixer.music.load(file)
            pygame.mixer.music.play(-1)
        except:
            print(f"Could not play {file}")

    def stop_looping_sound(self):
        pygame.mixer.music.stop()

    def create_widgets(self):
        self.intro_frame = tk.Frame(self.root)
        tk.Label(self.intro_frame, text="🎮 Welcome to Advanced Tic Tac Toe GUI", font=("Arial", 18, "bold"), fg="blue").pack(pady=10)

        self.name1_label = tk.Label(self.intro_frame, text="Enter Player 1 Name:")
        self.name1_label.pack()
        self.name1_entry = tk.Entry(self.intro_frame)
        self.name1_entry.pack()
        self.name1_entry.bind("<KeyPress>", self.typing_sound_on)
        self.name1_entry.bind("<KeyRelease>", self.typing_sound_off)

        self.name2_label = tk.Label(self.intro_frame, text="Enter Player 2 Name or select 'Computer':")
        self.name2_label.pack()
        self.name2_entry = tk.Entry(self.intro_frame)
        self.name2_entry.pack()
        self.name2_entry.bind("<KeyPress>", self.typing_sound_on)
        self.name2_entry.bind("<KeyRelease>", self.typing_sound_off)

        self.difficulty_label = tk.Label(self.intro_frame, text="AI Difficulty:")
        self.difficulty_label.pack()
        self.difficulty_var = tk.StringVar()
        self.difficulty_var.set("easy")  # Set default difficulty
        self.difficulty_dropdown = tk.OptionMenu(self.intro_frame, self.difficulty_var, "easy", "hard")
        self.difficulty_dropdown.pack()

        self.start_button = tk.Button(self.intro_frame, text="Start Game", command=self.start_game, bg="green", fg="white")
        self.start_button.pack(pady=10)
        self.intro_frame.pack()

    def typing_sound_on(self, event=None):
        if not self.typing:
            self.typing = True
            self.play_looping_sound(TYPE_SOUND)
        if self.typing_job:
            self.root.after_cancel(self.typing_job)

    def typing_sound_off(self, event=None):
        if self.typing_job:
            self.root.after_cancel(self.typing_job)
        self.typing_job = self.root.after(500, self._stop_typing_sound)

    def _stop_typing_sound(self):
        self.typing = False
        self.stop_looping_sound()

    def start_game(self):
        self._stop_typing_sound()
        name1 = self.name1_entry.get().strip()
        name2 = self.name2_entry.get().strip()
        difficulty = self.difficulty_var.get().strip()

        if not name1:
            messagebox.showwarning("Input Error", "⚠️ Please enter Player 1 name.")
            return

        if not name2:
            messagebox.showwarning("Input Error", "⚠️ Please enter Player 2 name or select 'Computer'.")
            return

        if name2.lower() == 'computer' and not difficulty:
            messagebox.showwarning("Input Error", "⚠️ Please select AI difficulty level.")
            return

        self.play_sound(CLICK_SOUND)
        self.player1 = name1
        self.player2 = name2
        self.difficulty = difficulty
        self.ai_mode = self.player2.lower() == 'computer'

        self.intro_frame.destroy()
        self.reset_game()
        self.create_board()
        if self.ai_mode and self.current == 'O':
            self.root.after(500, self.ai_move)

    def reset_game(self):
        self.board = [''] * 9
        self.current = 'X'
        self.buttons = []

    def create_board(self):
        self.board_frame = tk.Frame(self.root)
        for i in range(9):
            b = tk.Button(self.board_frame, text='', font=('Arial', 24), width=5, height=2,
                          command=lambda i=i: self.click(i))
            b.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.buttons.append(b)
        self.restart_button = tk.Button(self.root, text="Restart Game", command=self.restart_game, bg="orange")
        self.restart_button.pack(pady=10)
        self.board_frame.pack()

    def click(self, index):
        if self.board[index] or (self.ai_mode and self.current == 'O'):
            return

        self.play_sound(CLICK_SOUND)
        self.make_move(index)
        winner = self.check_winner()
        if winner:
            self.end_game(f"{self.get_player_name(winner)} wins!", WIN_SOUND)
            return
        if '' not in self.board:
            self.end_game("It's a draw!", DRAW_SOUND)
            return

        self.current = 'O' if self.current == 'X' else 'X'
        if self.ai_mode and self.current == 'O':
            self.root.after(500, self.ai_move)

    def make_move(self, index):
        self.board[index] = self.current
        self.buttons[index]['text'] = self.current

    def ai_move(self):
        if self.difficulty == 'hard':
            move = self.best_move()
        else:
            move = random.choice([i for i, x in enumerate(self.board) if not x])
        self.make_move(move)
        winner = self.check_winner()
        if winner:
            self.end_game(f"{self.get_player_name(winner)} wins!", WIN_SOUND)
            return
        if '' not in self.board:
            self.end_game("It's a draw!", DRAW_SOUND)
            return
        self.current = 'X'

    def best_move(self):
        best_score = -float('inf')
        move = None
        for i in range(9):
            if self.board[i] == '':
                self.board[i] = 'O'
                score = self.minimax(False)
                self.board[i] = ''
                if score > best_score:
                    best_score = score
                    move = i
        return move

    def minimax(self, is_max):
        winner = self.check_winner()
        if winner == 'O': return 1
        if winner == 'X': return -1
        if '' not in self.board: return 0

        if is_max:
            best = -float('inf')
            for i in range(9):
                if self.board[i] == '':
                    self.board[i] = 'O'
                    best = max(best, self.minimax(False))
                    self.board[i] = ''
            return best
        else:
            best = float('inf')
            for i in range(9):
                if self.board[i] == '':
                    self.board[i] = 'X'
                    best = min(best, self.minimax(True))
                    self.board[i] = ''
            return best

    def get_player_name(self, symbol):
        return self.player1 if symbol == 'X' else self.player2

    def check_winner(self):
        combos = [(0,1,2), (3,4,5), (6,7,8),
                  (0,3,6), (1,4,7), (2,5,8),
                  (0,4,8), (2,4,6)]
        for a,b,c in combos:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def end_game(self, message, sound):
        self.play_sound(sound)
        response = messagebox.askyesno("Game Over", f"{message}\n\nDo you want to try again?")
        self.board_frame.destroy()
        self.restart_button.destroy()

        if response:
            self.reset_game()
            self.create_board()
            if self.ai_mode and self.current == 'O':
                self.root.after(500, self.ai_move)
        else:
            self.reset_game()
            self.create_widgets()

    def restart_game(self):
        self.play_sound(CLICK_SOUND)
        self.board_frame.destroy()
        self.restart_button.destroy()
        self.reset_game()
        self.create_widgets()

if __name__ == '__main__':
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()