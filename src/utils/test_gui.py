
import tkinter as tk
from tkinter.constants import DISABLED, NORMAL
import pandas as pd
from comparator import Comparator
from visualization import visualize


class CheckBar:
    def __init__(self, window, names, row, col, test_gui):
        self.test_gui = test_gui
        self.names = names
        self.vars = []
        self.checkboxes = []
        self.last_checked_index = 0
        for idx,  name in enumerate(names):
            var = tk.IntVar()
            checkbox = tk.Checkbutton(window, text=name, variable=var, command=self.checked)
            if(idx <= 0):
                checkbox.select()
            checkbox.grid(row=row + idx, column=col)
            self.checkboxes.append(checkbox)
            self.vars.append(var)
    
    def state(self):
       return map((lambda var: var.get()), self.vars)
    
    def checked(self):
        sumval = 0
        for var in self.vars:
            sumval += var.get()
        if( sumval >= 1 ):
            if(self.last_checked_index is not None):
                self.vars[self.last_checked_index].set(0)
                self.checkboxes[self.last_checked_index].deselect()
            for idx, var in enumerate(self.vars):
                if (var.get() ==  1):
                    self.last_checked_index = idx
        else:
            self.last_checked_index = None
        self.test_gui.update()

    def get_checked_name(self):
        if self.last_checked_index is None:
            return None
        return self.names[self.last_checked_index]
              
    def disable(self, disable_names = None):
        if disable_names is None:
            for var in self.vars:
                var.set(0)
            for checkbox in self.checkboxes:
                checkbox.deselect()
                checkbox.config(state=DISABLED)
            self.last_checked_index = None
        else:
            for idx, name in enumerate(self.names):
                self.vars[idx].set(0)
                self.checkboxes[idx].deselect()
                if name in disable_names:
                    self.checkboxes[idx].config(state=DISABLED)
            self.last_checked_index = None
            for idx, checkbox in enumerate(self.checkboxes):
                if checkbox.cget("state") == NORMAL:
                    self.last_checked_index = idx
                    checkbox.select()
                    self.vars[idx].set(1)
                    break

    def enable(self):
        for idx, checkbox in enumerate(self.checkboxes):
            if checkbox.cget("state") == DISABLED:
                checkbox.config(state=NORMAL)
                if self.last_checked_index is None:
                    self.last_checked_index = idx
                    self.vars[idx].set(1)
                    checkbox.select()



class TestGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Vergleichstool')
        self.window.geometry('500x200')

        start_button = tk.Button(self.window, text="Aktion durchführen", command=self.show_plot)
        start_button.grid(row = 6, column=5)

        self.level_1 = CheckBar(self.window, ['Ball', 'Car'], 1, 1, self)
        self.level_2 = CheckBar(self.window, ['Physics', 'Jumped', 'Boost'], 1, 2, self)
        self.level_3 = CheckBar(self.window, ['Location', 'Rotation', 'Velocity', 'Angular_Velocity'], 1, 3, self)
        self.level_4 = CheckBar(self.window, ['x', 'y', 'z'], 1, 4, self)

        self.update()

        self.comp = Comparator()

        self.window.mainloop()

    def show_plot(self):
        df_plot, title, labels = self.extract_df_to_plot(self.level_1.get_checked_name(), self.level_2.get_checked_name(), self.level_3.get_checked_name(), self.level_4.get_checked_name())
        visualize(df_plot, title, labels)

    def update(self):
        self.level_2.enable()
        if  self.level_1.get_checked_name() == 'Ball':
            self.level_2.disable(disable_names=["Jumped", "Boost"])
        if  self.level_2.get_checked_name() in ["Jumped", "Boost"]:
            self.level_3.disable()
            self.level_4.disable()
        else:
            self.level_3.enable()
            self.level_4.enable()


    def extract_df_to_plot(self, *args):
        rlbot_results = self.comp.rlbot_results 
        roboleague_results = self.comp.roboleague_results
        title = ""

        for arg in args:
            if arg is None:
                continue
            title += " " + arg
            rlbot_results = rlbot_results[arg.lower()]
            roboleague_results = roboleague_results[arg.lower()]

        rlbot_results.name = 'RLBot'
        roboleague_results.name = 'RoboLeague'

        df_plot = pd.concat([rlbot_results, roboleague_results], axis=1)
        return df_plot, title, {'value':'Unity units', 'index':'Frame'}

    def create_figure(self, df_plot, title, labels):
        return visualize(df_plot, title, labels)

def main():
    TestGUI()
    
if __name__ == "__main__":
    main()