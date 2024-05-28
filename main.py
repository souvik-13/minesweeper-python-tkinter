from tkinter import *
from tkinter import ttk
from tkinter import messagebox as tkMessageBox
import customtkinter as ctk
from PIL import Image, ImageTk
from enum import Enum
import random
from typing import Tuple
import time
import os


class GameState(Enum):
    LOBBY = 0
    PAUSED = 1
    PLAYING = 2
    WIN = 3
    OVER = 4


class Minesweeper:

    _revealed_cell_count = 0

    # variables
    mines_left = 0
    flags_left = 0
    clock = None

    # game result variables
    game_over = False
    game_won = False

    revealed = None
    flagged = None

    def __init__(self, rows: int = 10, columns: int = 10, mines: int = 10) -> None:
        self.rows = rows
        self.columns = columns
        self.mines = mines
        self.mines_left = mines
        self.flags_left = mines
        self.board = [[0 for _ in range(columns)] for _ in range(rows)]
        self.revealed = [[False for _ in range(columns)] for _ in range(rows)]
        self.flagged = [[False for _ in range(columns)] for _ in range(rows)]

    def place_mines(self, exclude_cell: Tuple[int]) -> None:
        cells = [(i, j) for i in range(self.rows) for j in range(self.columns)]

        dx = [-1, 0, 1, -1, 1, -1, 0, 1]
        dy = [-1, -1, -1, 0, 0, 1, 1, 1]

        for i in range(8):
            for j in range(8):
                ni = exclude_cell[0] + dx[i]
                nj = exclude_cell[1] + dy[j]
                if (ni, nj) in cells:
                    cells.remove((ni, nj))

        mine_cells = random.sample(cells, self.mines)
        for cell in mine_cells:
            self.board[cell[0]][cell[1]] = -1

    def place_numbers(self) -> None:
        dx = [-1, 0, 1, -1, 1, -1, 0, 1]
        dy = [-1, -1, -1, 0, 0, 1, 1, 1]

        for i in range(self.rows):
            for j in range(self.columns):
                if self.board[i][j] == -1:
                    continue
                for k in range(8):
                    ni = i + dx[k]
                    nj = j + dy[k]
                    if (
                        0 <= ni < self.rows
                        and 0 <= nj < self.columns
                        and self.board[ni][nj] == -1
                    ):
                        self.board[i][j] += 1

    def polulate_board(self, exclude_cell: Tuple[int]) -> None:
        self.place_mines(exclude_cell)
        self.place_numbers()

    def flag_cell(self, cell: Tuple[int]) -> None:
        if self.flags_left == 0 and not self.flagged[cell[0]][cell[1]]:
            return
        self.flagged[cell[0]][cell[1]] = not self.flagged[cell[0]][cell[1]]
        if self.flagged[cell[0]][cell[1]]:
            self.flags_left -= 1
            if self.board[cell[0]][cell[1]] == -1:  # flagged cell have mine
                self.mines_left -= 1
        else:
            self.flags_left += 1
            if self.board[cell[0]][cell[1]] == -1:  # unflagged cell have mine
                self.mines_left += 1

    def reveal_cell(self, cell: Tuple[int]) -> bool:
        if self.flagged[cell[0]][cell[1]]:  # cell is flagged
            return True

        if self.revealed[cell[0]][cell[1]]:  # already revealed
            return
        self.revealed[cell[0]][cell[1]] = True
        self._revealed_cell_count += 1
        if self.board[cell[0]][cell[1]] == -1:  # mine
            self.game_over = True
            return False

        if self.board[cell[0]][cell[1]] == 0:  # empty cell
            self.reveal_neighbours(cell)

        if self._revealed_cell_count == self.rows * self.columns - self.mines:
            self.game_won = True

        return True

    def reveal_neighbours(self, cell: Tuple[int]) -> None:
        dx = [-1, 0, 1, -1, 1, -1, 0, 1]
        dy = [-1, -1, -1, 0, 0, 1, 1, 1]
        for i in range(8):
            ni = cell[0] + dx[i]
            nj = cell[1] + dy[i]
            if (
                0 <= ni < self.rows
                and 0 <= nj < self.columns
                and not self.revealed[ni][nj]
            ):
                self.reveal_cell((ni, nj))

    def reveal_all_mines(self) -> None:
        for i in range(self.rows):
            for j in range(self.columns):
                if self.board[i][j] == -1:  # if the cell is a mine
                    self.revealed[i][j] = True  # reveal the cell


class MinesweeperApp(ctk.CTk):

    rows = 20
    cols = 20
    mines = 10

    _steps = 0

    img_width = 35

    def __init__(self):
        super().__init__()
        self.title("Minesweeper")
        self.geometry("900x700+100+100")
        self.resizable(False, False)

        self.game = None
        self.cells = None
        self.game_frame = None
        self.settings_frame = None
        self.t_frame = None

        self.time_start = 0
        self.time_elapsed = 0

        self._game_state = GameState.LOBBY

        self.imgs = {
            "mine": None,
            "flag": None,
            "clock": None,
            "block": None,
            "nums": [None for _ in range(8)],
        }

        self.load_imgs()

        # settings frame
        self.settings_frame = self.create_settings_frame()

    def reset_game(self):
        self.game = None
        self.cells = None
        if self.game_frame:
            self.game_frame.destroy()
        if self.settings_frame:
            self.settings_frame.destroy()

        # reload the images
        self.load_imgs()

        self.game_frame = None
        self.settings_frame = None
        self.t_frame = None
        self._steps = 0
        self._game_state = GameState.LOBBY

        self.settings_frame = self.create_settings_frame()

    def resize_imgs(self):
        # resize the images
        for key in self.imgs_paths:
            if key == "nums":
                for i in range(0, 8):
                    image = Image.open(self.imgs_paths[key][i])
                    image = image.resize((self.img_width, self.img_width))
                    self.imgs[key][i] = ImageTk.PhotoImage(image)

            else:
                image = Image.open(self.imgs_paths[key])
                image = image.resize((self.img_width, self.img_width))
                self.imgs[key] = ImageTk.PhotoImage(image)

    def load_imgs(self):
        self.imgs_paths = {
            "mine": os.path.join("images", "MINESWEEPER_M.png"),
            "flag": os.path.join("images", "MINESWEEPER_F.png"),
            "clock": os.path.join("images", "MINESWEEPER_C.png"),
            "block": os.path.join("images", "MINESWEEPER_X.png"),
            "nums": [
                os.path.join("images", f"MINESWEEPER_{i}.png") for i in range(0, 8)
            ],
        }

    def create_settings_frame(self):
        settings_frame = ctk.CTkFrame(
            self, bg_color="transparent", fg_color="transparent"
        )
        settings_frame.pack(side=TOP, fill=BOTH, expand=True, padx=10)
        settings_frame.grid_columnconfigure(0, weight=1)

        # select rows
        rows_frame = ctk.CTkFrame(
            settings_frame, bg_color="transparent", fg_color="transparent"
        )
        ctk.CTkLabel(rows_frame, text="Rows:").pack(side=LEFT, padx=(0, 10))
        self.rows_var = IntVar(value=self.rows)
        set_rows = ctk.CTkComboBox(
            rows_frame,
            # values=[str(i * 2) for i in range(5, 15)],
            values=["10", "20", "30"],
            variable=self.rows_var,
        )
        set_rows.pack(side=LEFT)

        cols_frame = ctk.CTkFrame(
            settings_frame, bg_color="transparent", fg_color="transparent"
        )
        ctk.CTkLabel(cols_frame, text="Columns:").pack(side=LEFT, padx=(0, 10))
        self.cols_var = IntVar(value=self.cols)
        set_cols = ctk.CTkComboBox(
            cols_frame, values=["10", "20", "30"], variable=self.cols_var
        )
        set_cols.pack(side=LEFT)

        mines_frame = ctk.CTkFrame(
            settings_frame, bg_color="transparent", fg_color="transparent"
        )
        ctk.CTkLabel(mines_frame, text="Mines:").pack(side=LEFT, padx=(0, 10))
        self.mines_var = IntVar(value=self.mines)
        set_mines = ctk.CTkComboBox(
            mines_frame,
            values=[str(i) for i in range(10, 50)],
            variable=self.mines_var,
        )
        set_mines.pack(side=LEFT)

        rows_frame.grid(row=0, column=0, sticky=W + E, pady=(10, 0))
        cols_frame.grid(row=1, column=0, sticky=W + E, pady=(10, 0))
        mines_frame.grid(row=2, column=0, sticky=W + E, pady=(10, 0))
        # rows_frame.pack(side=TOP, fill=X, expand=True)
        # cols_frame.pack(side=TOP, fill=X, expand=True)
        # mines_frame.pack(side=TOP, fill=X, expand=True)

        ctk.CTkButton(
            settings_frame, text="Start", command=self.create_game_frame
        ).grid(row=3, column=0, pady=(10, 0))

        return settings_frame

    def create_game_frame(self):
        # set rows, cols, mines
        self.rows = self.rows_var.get()
        self.cols = self.cols_var.get()
        self.mines = self.mines_var.get()

        self.img_width = int((600 // max(self.rows, self.cols)) * 1.4)
        self.resize_imgs()

        self.game = Minesweeper(self.rows, self.cols, self.mines)

        self.game_frame = ctk.CTkFrame(self)

        ###################################### info frame ############################
        info_frame = ctk.CTkFrame(
            self.game_frame, width=200, fg_color="transparent", corner_radius=0
        )
        flags_left_frame = ctk.CTkFrame(
            info_frame, corner_radius=0, height=50, width=150
        )
        mines_left_frame = ctk.CTkFrame(
            info_frame, corner_radius=0, height=50, width=150
        )
        clock_frame = ctk.CTkFrame(info_frame, corner_radius=0, height=50, width=150)

        mines_left_frame.pack(side=TOP, padx=25, pady=(10, 0))
        flags_left_frame.pack(side=TOP, padx=25, pady=(10, 0))
        clock_frame.pack(side=TOP, padx=25, pady=(30, 0))

        # flag
        _flag_img = ctk.CTkImage(
            light_image=Image.open(self.imgs_paths["flag"]),
            dark_image=Image.open(self.imgs_paths["flag"]),
            size=(40, 40),
        )
        ctk.CTkLabel(
            flags_left_frame,
            image=_flag_img,
            text="",
        ).pack(side=LEFT)
        self.flags_left_label = ctk.CTkLabel(
            flags_left_frame,
            text=(
                self.game.flags_left
                if self.game.flags_left > 9
                else f" {self.game.flags_left}"
            ),
            font=ctk.CTkFont(family="Courier", size=20, weight="bold"),
        )
        self.flags_left_label.pack(side=RIGHT, padx=10)

        # Mines
        _mine_img = ctk.CTkImage(
            light_image=Image.open(self.imgs_paths["mine"]),
            dark_image=Image.open(self.imgs_paths["mine"]),
            size=(40, 40),
        )
        ctk.CTkLabel(
            mines_left_frame,
            image=_mine_img,
            text="",
        ).pack(side=LEFT)
        self.mines_left_label = ctk.CTkLabel(
            mines_left_frame,
            text=self.game.mines_left,
            font=ctk.CTkFont(family="Courier", size=20, weight="bold"),
        )
        self.mines_left_label.pack(side=RIGHT, padx=10)

        # Clock
        _clk_img = ctk.CTkImage(
            light_image=Image.open(self.imgs_paths["clock"]),
            dark_image=Image.open(self.imgs_paths["clock"]),
            size=(50, 50),
        )
        ctk.CTkLabel(clock_frame, image=_clk_img, text="").pack(side=TOP)
        self.time_label = ctk.CTkLabel(
            clock_frame,
            text="00:00:00",
            font=ctk.CTkFont(family="Courier", size=18, weight="bold"),
        )
        self.time_label.pack(side=TOP)

        self.pause_play_button = ctk.CTkButton(
            info_frame,
            text=("Resume" if self._game_state == GameState.PAUSED else f"Pause"),
            command=self.pause_resume_game,
        )

        self.pause_play_button.pack(side=BOTTOM, padx=10, pady=20)

        self.restart_button = ctk.CTkButton(
            info_frame, text="Restart", command=self.reset_game_button
        )
        self.restart_button.pack(side=BOTTOM, padx=10, pady=20)

        ##################################### board frame ############################
        board_frame = ctk.CTkFrame(self.game_frame)

        board_frame.grid_columnconfigure(list(range(self.cols + 2)), weight=1)
        board_frame.grid_columnconfigure(list(range(self.rows + 2)), weight=1)

        self.t_frame = ctk.CTkFrame(board_frame, corner_radius=0, fg_color="blue")
        self.t_frame.place(anchor="center", relx=0.5, rely=0.5)
        # self.t_frame.pack(fill="both", expand=TRUE, anchor="center")

        self.init_board()

        self.settings_frame.destroy()
        info_frame.pack(
            side=LEFT,
            fill=Y,
        )
        board_frame.pack(side=LEFT, fill="both", expand=TRUE)

        self.game_frame.pack(side=TOP, fill=BOTH, expand=True)

    def on_left_click(self, event):
        if self._game_state != GameState.PLAYING:
            if self._steps != 0:
                return
        info = event.widget.grid_info()
        if self._steps == 0:
            self._game_state = GameState.PLAYING
            self.start_clock()
            self.game.polulate_board((int(info["row"]) - 1, int(info["column"]) - 1))
        self._steps += 1
        if not self.game.reveal_cell((int(info["row"]) - 1, int(info["column"]) - 1)):
            self.game_over()
            return
        if self.game.game_won:
            self.game_won()
            return
        self.render_board()

    def on_ctrl_left_click(self, event):
        if self._game_state != GameState.PLAYING:
            if self._steps != 0:
                return
        info = event.widget.grid_info()
        self.game.flag_cell((int(info["row"]) - 1, int(info["column"]) - 1))
        self.update_flags()
        self.render_board()

    def game_over(self):
        self._game_state = GameState.OVER
        self.game.reveal_all_mines()
        self.render_board()
        if tkMessageBox.askretrycancel("Game Over", "You Lost!"):
            self.reset_game()

    def game_won(self):
        self._game_state = GameState.WIN
        self.game.reveal_all_mines()
        self.render_board()
        if tkMessageBox.askyesno("Game Over", "You Won! Play Again?"):
            self.reset_game()

    def init_board(self):
        self.cells = [
            [
                ttk.Label(self.t_frame, image=self.imgs["block"])
                for _ in range(self.cols)
            ]
            for _ in range(self.rows)
        ]
        for i in range(1, self.rows + 1):
            for j in range(1, self.cols + 1):
                self.cells[i - 1][j - 1].grid(
                    row=i, column=j, sticky=N + S + E + W, padx=1, pady=1
                )
                self.cells[i - 1][j - 1].bind("<Button-1>", self.on_left_click)
                self.cells[i - 1][j - 1].bind(
                    "<Control-Button-1>", self.on_ctrl_left_click
                )
                self.cells[i - 1][j - 1].bind("<Button-3>", self.on_ctrl_left_click)

    def render_board(self):
        # create the board
        for i in range(1, self.rows + 1):
            for j in range(1, self.cols + 1):
                _img = None
                if self.game.revealed[i - 1][j - 1]:
                    if self.game.board[i - 1][j - 1] == -1:
                        _img = self.imgs["mine"]
                    else:
                        _img = self.imgs["nums"][self.game.board[i - 1][j - 1]]

                elif self.game.flagged[i - 1][j - 1]:
                    _img = self.imgs["flag"]
                else:
                    _img = self.imgs["block"]

                # If the image has changed, update the label
                if _img != self.cells[i - 1][j - 1].cget("image"):
                    self.cells[i - 1][j - 1].config(image=_img)

    def hide_board(self):
        for i in range(1, self.rows + 1):
            for j in range(1, self.cols + 1):
                self.cells[i - 1][j - 1].config(image=self.imgs["block"])

    def update_flags(self):
        self.flags_left_label.configure(
            text=(
                self.game.flags_left
                if self.game.flags_left > 9
                else f" {self.game.flags_left}"
            )
        )

    def update_mines(self):
        self.mines_left_label.configure(text=self.game.mines_left)

    def start_clock(self):
        self.time_start = time.time() - self.time_elapsed
        self.update_clock()

    def update_clock(self):
        if self._game_state == GameState.PLAYING:
            self.time_elapsed = time.time() - self.time_start
            hours, rem = divmod(self.time_elapsed, 3600)
            minutes, seconds = divmod(rem, 60)
            t = "{:0>2}:{:0>2}:{:02}".format(int(hours), int(minutes), int(seconds))
            self.time_label.configure(text=t)

        self.after(500, self.update_clock)

    def pause_resume_game(self):
        if self._game_state == GameState.PLAYING:
            self._game_state = GameState.PAUSED
            self.time_elapsed = time.time() - self.time_start
            self.pause_play_button.configure(text="Resume")
            self.hide_board()
        elif self._game_state == GameState.PAUSED:
            self._game_state = GameState.PLAYING
            self.start_clock()
            self.pause_play_button.configure(text="Pause")
            self.render_board()

    def reset_game_button(self):
        t = tkMessageBox.askretrycancel("Restart", "Are you sure you want to restart?")
        self.pause_resume_game()
        if t:
            self.reset_game()
        else:
            self.pause_resume_game()


if __name__ == "__main__":
    try:
        app = MinesweeperApp()
        app.mainloop()
    except:
        print("app stopped")
