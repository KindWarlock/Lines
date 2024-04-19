import threading
import time
import customtkinter as ctk
import database

import game

APPEARANCE_MODE = "light"  # Modes: system (default), light, dark
COLOR_THEME = "dark-blue"  # Themes: blue (default), dark-blue, green


class Timer:
    timer_counter = 0
    time_on_end = 5
    isEnded = False

    def main(self):
        while self.timer_counter < self.time_on_end:
            time.sleep(1)
            self.timer_counter += 1
        LooseClass = Loose()
        LooseThread = threading.Thread(target=LooseClass.main())
        LooseThread.start()


class MainMenu:
    usernameInputField = ""

    def __init__(self):
        self.username = None
        self.CameraClass = None

    # @staticmethod
    def on_exit(self):
        self.app.destroy()

    def on_start_game(self):
        print("Started")
        # self.CameraClass = ball_tracking.Camera(username=self.usernameInputField.get())
        self.CameraClass = game.Game(username=self.usernameInputField.get())
        Timer_Class = Timer()
        Timer_Thread = threading.Thread(target=Timer_Class.main)
        camera_Thread = threading.Thread(target=self.CameraClass.main)
        Timer_Thread.start()
        camera_Thread.start()

    @staticmethod
    def on_leader_board():
        print("LeaderBoard")
        LeaderBoardClass = LeaderBoard()
        LeaderBoardThread = threading.Thread(target=LeaderBoardClass.main())
        LeaderBoardThread.start()

    def main(self):
        # Modes: system (default), light, dark
        ctk.set_appearance_mode(APPEARANCE_MODE)
        # Themes: blue (default), dark-blue, green
        ctk.set_default_color_theme(COLOR_THEME)

        self.app = ctk.CTk()  # create CTk window like you do with the Tk window
        self.app.geometry("400x240")
        self.app.title("Main Menu")

        # Use CTkButton instead of tkinter Button
        PerpetuaFont = ctk.CTkFont(family='Perpetua', size=30)
        ctk_label = ctk.CTkLabel(
            master=self.app, text="DRAW BASKETBALL", font=PerpetuaFont)
        button_start = ctk.CTkButton(
            master=self.app, text="Start", command=self.on_start_game)
        button_exit = ctk.CTkButton(
            master=self.app, text="Exit", command=self.on_exit)
        button_leaderboard = ctk.CTkButton(master=self.app, text="LeaderBoard",
                                           command=self.on_leader_board)
        usernameInputField = ctk.CTkEntry(
            self.app, placeholder_text="Username")
        usernameInputField.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)
        self.username = usernameInputField.get()
        self.usernameInputField = usernameInputField
        button_start.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        button_leaderboard.place(relx=0.5, rely=0.7, anchor=ctk.CENTER)
        button_exit.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)

        ctk_label.place(relx=0.5, rely=0.1, anchor=ctk.CENTER)
        self.app.mainloop()


class Loose:

    def onExit(self):
        self.app.destroy()

    def main(self):
        # Modes: system (default), light, dark
        ctk.set_appearance_mode(APPEARANCE_MODE)
        # Themes: blue (default), dark-blue, green
        ctk.set_default_color_theme(COLOR_THEME)

        self.app = ctk.CTk()
        self.app.geometry("400x240")
        self.app.title("Loose")

        # Use CTkButton instead of tkinter Button
        Perpetua_font_label = ctk.CTkFont(
            family='Perpetua', size=40, weight="bold")
        Perpetua_font_leader = ctk.CTkFont(
            family='Perpetua', size=20, weight="bold")
        button_exit = ctk.CTkButton(
            master=self.app, text="Exit", command=self.onExit)
        ctk_label = ctk.CTkLabel(
            master=self.app, text="Loose!", font=Perpetua_font_label)
        ctk_label.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)
        button_exit.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)
        self.app.mainloop()


class LeaderBoard:
    def __init__(self):
        self.leaderText = self.parseLeaders()

    def parseLeaders(self) -> str:
        string_to_return = ""
        lines = database.Login().get_users()
        for line in lines:
            name = line[0]
            score = line[1]
            string_to_return += f"Player {name}: {score}\n"
        string_to_return.lstrip()
        print(string_to_return)
        if string_to_return == "":
            return "Nothing"
        return string_to_return

    def onExit(self):
        self.app.destroy()

    def main(self):
        # Modes: system (default), light, dark
        ctk.set_appearance_mode(APPEARANCE_MODE)
        # Themes: blue (default), dark-blue, green
        ctk.set_default_color_theme(COLOR_THEME)

        self.app = ctk.CTk()  # create CTk window like you do with the Tk window
        self.app.geometry("400x240")
        self.app.title("LeaderBoard")

        # Use CTkButton instead of tkinter Button
        Perpetua_font_label = ctk.CTkFont(
            family='Perpetua', size=40, weight="bold")
        Perpetua_font_leader = ctk.CTkFont(
            family='Perpetua', size=20, weight="bold")
        ctk_label = ctk.CTkLabel(
            master=self.app, text="LeaderBoard", font=Perpetua_font_label)
        ctk_labelListOfLeaders = ctk.CTkLabel(
            master=self.app, text=self.leaderText, font=Perpetua_font_leader)
        button_exit = ctk.CTkButton(
            master=self.app, text="Exit", command=self.onExit)

        ctk_label.place(relx=0.5, rely=0.2, anchor=ctk.CENTER)
        ctk_labelListOfLeaders.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)
        button_exit.place(relx=0.5, rely=0.9, anchor=ctk.CENTER)
        self.app.mainloop()


if __name__ == '__main__':
    MainMenu().main()
