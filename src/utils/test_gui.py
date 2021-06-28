
import tkinter as tk
import pandas as pd
from comparator import Comparator
from visualization import visualize


class CheckBar:
    def __init__(self, window, names, row, col, only_one=True):
        self.vars = []
        self.names = names
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
        print(self.last_checked_index)
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

    def get_checked_name(self):
        return self.names[self.last_checked_index]


class TestGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Vergleichstool')
        self.window.geometry('500x200')

        start_button = tk.Button(self.window, text="Aktion durchführen", command=self.show_plot)
        start_button.grid(row = 6, column=5)

        self.level1 = CheckBar(self.window, ['Ball', 'Car'], 1, 1)
        self.level2 = CheckBar(self.window, ['Physics', 'Jumped', 'Boost'], 1, 2)
        self.level3 = CheckBar(self.window, ['Location', 'Rotation', 'Velocity', 'Angular_Velocity'], 1, 3)
        self.level4 = CheckBar(self.window, ['x', 'y', 'z'], 1, 4)
    
        self.comp = Comparator()

        self.window.mainloop()

    def show_plot(self):
        df_plot, title, labels = self.extract_df_to_plot(self.level1.get_checked_name(), self.level2.get_checked_name(), self.level3.get_checked_name(), self.level4.get_checked_name())
        visualize(df_plot, title, labels)

    def extract_df_to_plot(self, *args):
        rlbot_results = self.comp.rlbot_results 
        roboleague_results = self.comp.roboleague_results
        title = ""

        for arg in args:
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