import elizabeth
import random

import tkinter as tk

person = elizabeth.Personal('nl')
address = elizabeth.Address('nl')
data = elizabeth.Text('nl')

class GenDummpyData():

	def dummpyhorecalijst(self):
		#dummpy horecaLijst
		f = open('dummpyhorecaLijst','w+')
		for _ in range(0,20):
			num = random.randint(0,100)
			sex = 'female' if num % 2 == 0  else 'male'
			horecaLid = person.full_name(sex)
			team = 'Dames ' if sex == 'female' else 'Heren '
			team += str(num)
			f.write(horecaLid + ',' + team + '\n')
		f.close()

	def dummpytegenstanderplaces(self):
		#dummpy input places googlemaps
		f = open('dummpyplacesdata','w+')
		sport = ', hockey'
		for _ in range(0,20):
			stad = address.city()
			tegenstander = stad + sport
			f.write(tegenstander + '\n')
		f.close()

	def scheldenG(self):
		return data.swear_word()

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = 'Druk voor scheldwoord G'
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=root.destroy)
        self.quit.pack(side="bottom")

    def say_hi(self):
        bad = GenDummpyData().scheldenG()
        print(bad)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
