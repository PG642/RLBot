
import tkinter as tk
from tkinter import ttk
from tkinter.constants import DISABLED, NORMAL
import pandas as pd
import os
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

    def enable(self, rename=None):
        for idx, checkbox in enumerate(self.checkboxes):
            if checkbox.cget("state") == DISABLED:
                checkbox.config(state=NORMAL)
                if self.last_checked_index is None:
                    self.last_checked_index = idx
                    self.vars[idx].set(1)
                    checkbox.select()
        if rename is not None and rename == 'Rotation':
            self.names = ['pitch', 'yaw', 'roll']
            self.checkboxes[0].text = 'pitch'
        elif rename is not None:
            self.names = ['x', 'y', 'z']




class TestGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Comparison tool')
        self.window.geometry('500x200')

        
        dirname = os.path.dirname(__file__)

        path_rlbot_results = os.path.join(dirname, '../../../Physikabgleich/Ergebnisse/RLBot/')
        path_roboleague_results = os.path.join(dirname, '../../../Physikabgleich/Ergebnisse/RoboLeague/')

        results_rlbot = [f.split('.')[0] for f in os.listdir(path_rlbot_results) if os.path.isfile(os.path.join(path_rlbot_results, f))]
        results_roboleague = [f.split('.')[0] for f in os.listdir(path_roboleague_results) if os.path.isfile(os.path.join(path_roboleague_results, f))]

        scenarios = list(set(results_rlbot) & set(results_roboleague))
    
        if(len(scenarios) == 0):
            print("ERROR: No matching files in '../Ergebnisse/RLBot/' and '../Ergebnisse/RoboLeague/'!")
            return
        
        labelTop = tk.Label(self.window,  text = "Choose your scenario:")
        labelTop.grid(row = 1, column=5)

        self.combobox = ttk.Combobox(self.window, state="readonly", values=scenarios)
        self.combobox.grid(row = 2, column=5)
        self.combobox.current(0)

        start_button = tk.Button(self.window, text="Compare results", command=self.show_plot)
        start_button.grid(row = 3, column=5)

        self.level_1 = CheckBar(self.window, ['Ball', 'Car'], 1, 1, self)
        self.level_2 = CheckBar(self.window, ['Physics', 'Jumped', 'Boost'], 1, 2, self)
        self.level_3 = CheckBar(self.window, ['Location', 'Rotation', 'Velocity', 'Angular_Velocity'], 1, 3, self)
        self.level_4 = CheckBar(self.window, ['x/pitch', 'y/yaw', 'z/roll'], 1, 4, self)
        self.level_4.enable(rename="")

        self.update()
        self.comp = Comparator()
        self.comp.load_scenario_results(self.combobox.get())

        self.window.mainloop()

    def load_scenario(self):
        self.comp.load_scenario_results(self.combobox.get())

    def show_plot(self):
        self.load_scenario()
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
            self.level_4.enable( rename=self.level_3.get_checked_name())


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