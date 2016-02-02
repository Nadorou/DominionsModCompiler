from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

toggleplusicon = Image.open('bullet_toggle_plus.png')
toggleminusicon = Image.open('bullet_toggle_minus.png')

class Collapse(Frame):

    def __init__(self, master, text='', width=1, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)

        self.open = IntVar()
        self.open.set(0)
        self.label = text
        self.itemlist = []
        self.columncount = 1

        self.plusicon = ImageTk.PhotoImage(toggleplusicon)
        self.minusicon = ImageTk.PhotoImage(toggleminusicon)
        self.button = ttk.Button(self, text=text, image=self.plusicon, compound='right',
                                 command=self.toggle, width=width)
        self.button.grid(column=0, row=0, columnspan=2, sticky=E+W)
        self.grid_columnconfigure(1, weight=1)

        self.spaceframe = Frame(self, width=10)
        self.subframe = ttk.Frame(self, relief='groove', borderwidth=1, padding=5)

        self.button.bind('<Configure>', self.on_resizebutton)

    def toggle(self):
        if not bool(self.open.get()):
            self.spaceframe.grid(column=0, row=1, sticky=W)
            self.subframe.grid(column=1, row=1, sticky=N+E+W+S)
            self.button.config(image=self.minusicon)
            self.open.set(1)
            self.subframe.bind('<Configure>', self.on_resizewindow)
        else:
            self.subframe.grid_forget()
            self.spaceframe.grid_forget()
            self.button.config(image=self.plusicon)
            self.open.set(0)
            self.subframe.bind('<Configure>')

    def on_resizebutton(self, event):
        self.button.config(text=self.label+' '*int(event.width/3))

    def on_resizewindow(self, event):
        column_widths = 0
        for column in range(self.subframe.grid_size()[0]):
            column_widths += self.subframe.grid_bbox(column,0)[2]
        if column_widths + self.subframe.grid_bbox(0,0)[2] < event.width - self.subframe.grid_bbox(0,0)[0]:
            self.columncount += 1
            self.forget_items()
            self.update_items()
        elif column_widths >= event.width - self.subframe.grid_bbox(0,0)[0]:
            self.columncount -= 1
            self.forget_items()
            self.update_items()

    def update_items(self):
        o = 0
        j = 0
        for item in self.itemlist:
            item.grid(column=o, row=j, in_=self.subframe)
            o += 1
            if o >= self.columncount:
                j += 1
                o = 0

    def forget_items(self):
        for item in self.itemlist:
            item.grid_forget()

    def add(self, child):
        self.forget_items()
        self.itemlist.append(child)
        self.update_items()



class ToggledFrame(Frame):

    def __init__(self, parent, text="", *args, **options):
        Frame.__init__(self, parent, *args, **options)

        self.show = IntVar()
        self.show.set(0)

        self.title_frame = Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        Label(self.title_frame, text=text).pack(side="left", fill="x", expand=1)

        self.toggle_button = ttk.Checkbutton(self.title_frame, width=2, text='+', command=self.toggle,
                                            variable=self.show, style='Toolbutton')
        self.toggle_button.pack(side="left")

        self.sub_frame = Frame(self, relief="sunken", borderwidth=1)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.configure(text='-')
        else:
            self.sub_frame.forget()
            self.toggle_button.configure(text='+')

if __name__ == "__main__":
    root = Tk()

    t = Collapse(root, text='Rotate', relief="raised")
    t.pack(fill="x", pady=2, padx=2, anchor="n")

    Entry(t.subframe).pack(side="left")

    t2 = Collapse(root, text='Resize', relief="raised")
    t2.pack(fill="x", pady=2, padx=2, anchor="n")

    for i in range(10):
        t2.add(Label(t2.subframe, text='Test' + str(i)))

    t3 = Collapse(root, text='Fooo', relief="raised")
    t3.pack(fill="x", pady=2, padx=2, anchor="n")

    a1 = Label(root, text='Rotation [deg]:')
    a2 = Label(root, text='Rotation [deg]:2')
    t3.add(a1)
    t3.add(a2)

    root.mainloop()
