from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk
import tkinter.filedialog
import os
__author__ = 'Nadorou'


# Function for splitting an imported line into a 2-tuple containing the command itself (sans #) and its conditions.
def commandsplit(line):
    splitline = line.split(" ", 1)
    command = splitline[0][1:]
    try:
        parameter = splitline[1].split("--", 1)[0]
        return command, parameter
    except IndexError:
        parameter = None
        return command, parameter


# Prints out a given list. Primarily for printing the contents of an entity's 'write' method.
def printlist(a):
    for entry in a:
        print(entry)


# Help function for reading raws. Creates a dictionary based on a supplied dictionary of keys and their default values,
# then looks for the specified keys in the raw. If found, they are set to their parameter value. Unspecified commands
# are put into a list under the 'tags' key. All commands without parameter values should be excluded from the keylist.
def readraws(rawlist, keydict):
    tardict = {'tags': []}
    for key in keydict:
        tardict[key] = keydict[key]
    for line in rawlist:
        command = commandsplit(line)

        if command[0] in tardict:
            try:
                tardict[command[0]] = command[1]
            except IndexError:
                print('Undefined command "%s" found in %s.' % (line, rawlist))
        else:
            tardict['tags'].append(line[1:])
    return tardict


# Function for sorting treeview columns
def treeview_sort_column(tv, col, reverse=False, master=''):
    if col == '#0':
        l = [(tv.item(k)['text'], int(k)) for k in tv.get_children(master)]
    else:
        try:
            l = [(int(tv.set(k, col)), int(k)) for k in tv.get_children(master)]
        except ValueError:
            l = [(tv.set(k, col), int(k)) for k in tv.get_children(master)]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(int(k), master, index)

    tv.heading(col,
               command=lambda: treeview_sort_column(tv, col, not reverse))

    for child in tv.get_children(master):
        treeview_sort_column(tv, col, reverse, master=child)


# Mod class
class Modentry:

    def __init__(self, dm):

        self.modname = 'Unnamed'
        self.description = ''
        self.iconpath = ''
        self.version = ''
        self.domversion = ''
        self.rawsdict = {'selectweapon': [], 'selectarmor': [], 'selectmonster': [],
                         'selectspell': [], 'selectitem': [], 'selectnametype': [],
                         'newmerc': [], 'selectsite': [], 'selectnation': [],
                         'selectpoptype': [], 'selectevent': [], 'misc': []}
        self.monsters = {}
        self.weapons = {}
        self.nametypes = {}
        self.armors = {}

        isreadingentry = False
        entrytype = ''
        entry = []

        for line in dm:
            if line[0] == '#':
                rawline = line.split('\n')[0]
                splitline = commandsplit(rawline)
                param = splitline[0]
                paraval = splitline[1]

                # Check if entry is being written. If not, check for entry type.
                if not isreadingentry:
                    if param == 'modname':
                        self.modname = paraval[1:-1]
                    elif param == 'description':
                        self.description = paraval[1:-1]
                    elif param == 'version':
                        self.version = paraval
                    elif param == 'icon':
                        self.iconpath = paraval[2:-1]
                    elif param == 'domversion':
                        self.domversion = paraval
                    elif param in ('selectweapon', 'newweapon', 'selectarmor', 'newarmor', 'selectmonster',
                                   'newmonster', 'selectspell', 'newspell', 'selectitem', 'newitem',
                                   'selectnametype', 'newmerc', 'selectsite', 'newsite', 'selectnation',
                                   'newnation', 'selectpoptype', 'newevent'):
                        isreadingentry = True
                        if param[0:3] == 'new':
                            entrytype = 'select' + param[3:]
                        else:
                            entrytype = param
                        entry.append(rawline)
                    else:
                        self.rawsdict['misc'].append(rawline)
                else:
                    if param == 'end':
                        isreadingentry = False
                        self.rawsdict[entrytype].append(entry)
                        entry = []
                    else:
                        entry.append(rawline)
        print('Finished reading .dm file.')
        dm.close()

        # TODO Read raw data and create entries based on it.
        for key in self.rawsdict:
            self.buildentries(key)

        self.printstats()

    def buildentries(self, category):
        for raw in self.rawsdict[category]:
            if category == 'selectweapon':
                entry = Weapon(raw)
                self.weapons[entry.ID] = entry
            elif category == 'selectnametype':
                entry = Nametype(raw)
                self.nametypes[entry.ID] = entry
            elif category == 'selectarmor':
                entry = Armor(raw)
                self.armors[entry.ID] = entry
            elif category == 'selectmonster':
                entry = Monster(raw)
                self.monsters[entry.ID] = entry
            else:
                print('Class for %s not yet built' % category)

    def printstats(self):
        print(self.modname)
        print(self.description)
        print(self.iconpath)
        print(self.version)
        print(self.domversion)
        for entry in self.rawsdict['misc']:
            print('miscentry',entry)


# TODO Classes for:
# TODO      Spells
# TODO      Magic items
# TODO      Mercs
# TODO      Sites
# TODO      Nations
# TODO      Poptypes.
# TODO      Events

# region Entity classes
# Entity class
class Entity:

    def __init__(self, stats):

        self.statdict = {'tags': []}
        self.misctags = []
        self.readraws(stats)

    def readraws(self, rawlist):
        for line in rawlist:
            command = commandsplit(line)
            if command[1] is not None:
                if command[0] in self.statdict:
                    if type(self.statdict[command[0]]) is list:
                        self.statdict[command[0]].append(command[1])
                    else:
                        self.statdict[command[0]] = [self.statdict[command[0]], command[1]]
                else:
                    self.statdict[command[0]] = command[1]
            else:
                self.misctags.append(command[0])

    def appendparam(self, tag, targetlist):
        if tag in self.statdict:
            if type(self.statdict[tag]) is list:
                for entry in self.statdict[tag]:
                    targetlist.append('#%s %s' % (tag, entry))
            else:
                targetlist.append('#%s %s' % (tag, self.statdict[tag]))

    def appendtag(self, tag, targetlist):
        if tag in self.misctags:
            targetlist.append('#%s' % tag)


# Monster subclass
class Monster(Entity):

    def __init__(self, stats):

        Entity.__init__(self, stats)

        self.name = ''
        for tag in self.statdict:
            if tag == 'newmonster':
                self.ID = self.statdict['newmonster'].split(" ", 1)[0]
                self.isnew = True
            elif tag == 'selectmonster':
                self.statdict['selectmonster'] = self.statdict['selectmonster'].split(" ", 1)[0]
                self.ID = self.statdict['selectmonster']
                self.isnew = False
            elif tag == 'name':
                self.statdict['name'] = self.statdict['name'].split('"', 2)[1]
                self.name = self.statdict['name']


# Weapon subclass
class Weapon(Entity):

    def __init__(self, stats):
        Entity.__init__(self, stats)

        # region stats
        self.name = ''
        self.soundiscustom = False
        for tag in self.statdict:
            if tag == 'newweapon':
                self.ID = self.statdict['newweapon'].split(" ", 1)[0]
                self.isnew = True
            elif tag == 'selectweapon':
                self.statdict['selectweapon'] = self.statdict['selectweapon'].split(" ", 1)[0]
                self.ID = self.statdict['selectweapon']
                self.isnew = False
            elif tag == 'name':
                self.statdict['name'] = self.statdict['name'].split('"', 2)[1]
                self.name = self.statdict['name']
            elif tag == 'sample':
                self.soundiscustom = True


        # endregion

    def write(self):
        towrite = []
        if self.isnew:
            self.appendparam('newweapon', towrite)
        else:
            self.appendparam('selectweapon', towrite)
        self.appendparam('name', towrite)

        for tag in self.misctags:
            self.appendtag(tag, towrite)
        towrite.append('#end')

        return towrite

    def tags(self):
        for tag in self.misctags:
            print(tag)


# Armor subclass
class Armor(Entity):

    def __init__(self, stats):
        Entity.__init__(self, stats)

        # region stats
        self.name = ''
        for tag in self.statdict:
            if tag == 'newarmor':
                self.isnew = True
                self.ID = self.statdict['newarmor'].split(" ", 1)[0]
            elif tag == 'selectarmor':
                self.isnew = False
                self.statdict['selectarmor'] = self.statdict['selectarmor'].split(" ", 1)[0]
                self.ID = self.statdict['selectarmor']
            elif tag == 'name':
                self.statdict['name'] = self.statdict['name'].split('"', 2)[1]
                self.name = self.statdict['name']
        # endregion


# Nametype subclass
class Nametype(Entity):

    def __init__(self, stats):

        Entity.__init__(self, stats)
        self.ID = self.statdict['selectnametype']

    def write(self):
        towrite = ['#selectnametype %s' % self.ID]
        self.appendparam('addname', towrite)
        towrite.append('#end')

        return towrite

# endregion


# TODO Create GUI:
# TODO      Build tabs for various classes
# TODO          Armor
# TODO          Monsters
# TODO          Nametypes
# TODO          Weapons
# TODO          Spells
# TODO          Magic items
# TODO          Mercs
# TODO          Nations
# TODO          Poptypes
# TODO          Events
# TODO      Methods for saving project/dm

# region GUI
class Mainwindow:
    def __init__(self, master):

        # region Variables
        self.defaultdomfolder = 'C:/Users/Nadorou/AppData/Roaming/Dominions4/mods'

        self.modname = StringVar()
        self.modversion = StringVar()
        self.domiversion = StringVar()
        self.iconpath = StringVar()
        self.loaddomfolder = StringVar()
        self.loaddomfolder.set(self.defaultdomfolder)

        # Variables to be filled
        self.bannerphoto = None
        # endregion

        # region Main frames
        # #Define
        self.topbuttonframe = Frame(master, padding=5)
        self.modview = LabelFrame(master, text='Mod View', padding=5)

        # #Draw
        self.topbuttonframe.grid(row=0, column=0, padx=5, pady=5, sticky=W+N+S)
        self.modview.grid(row=1, column=0, padx=5, pady=5, sticky=W+E+N+S)
        # endregion

        # region #Top buttons
        # ##Define
        self.newbutton = Button(self.topbuttonframe, text='New')
        self.openbutton = Button(self.topbuttonframe, text='Open', command=self.browsedm)
        self.savebutton = Button(self.topbuttonframe, text='Save')
        self.pathbutton = Button(self.topbuttonframe, text='Path')

        # ##Draw
        self.newbutton.grid(row=0, column=0, padx=5)
        self.openbutton.grid(row=0, column=1, padx=5)
        self.savebutton.grid(row=0, column=2, padx=5)
        self.pathbutton.grid(row=0, column=3, padx=5)
        # endregion

        # region ##Tab manager + Tabs

        self.tabmanager = Notebook(self.modview)
        self.overviewtab = Frame(self.tabmanager)
        self.tabmanager.pack(fill=BOTH, expand=1)
        self.tabmanager.add(self.overviewtab, text='Mod Overview', sticky='nsew')

        self.monstertab = Entitytab(self.tabmanager, label='Monsters')
        self.weapontab = Entitytab(self.tabmanager, label='Weapons')
        self.armortab = Entitytab(self.tabmanager, label='Armor')

        # region ###Overview tab
        # #Define
        # ##Frames and canvas
        self.bannerframe = LabelFrame(self.overviewtab, text='Banner', width=270, height=70)
        self.bannercanvas = Canvas(self.bannerframe, width=256, height=64)
        # ##Labels
        self.bannerlabel = Label(self.overviewtab, text='Banner subpath (e.g. "/folder/banner.tga"):')
        self.modnamelabel = Label(self.overviewtab, text='Mod Name', padding=(0, 5, 5, 0))
        self.versionlabel = Label(self.overviewtab, text='Mod Version:')
        self.domiversionlabel = Label(self.overviewtab, text='Dominions Version:')
        self.descriptionlabel = Label(self.overviewtab, text='Mod Description')
        self.folderlabel = Label(self.overviewtab, text='Mod Folder Path (if different from default):')
        # ##Entries/Text/Scrollbars
        self.bannerentry = Entry(self.overviewtab, textvariable=self.iconpath)
        self.modnameentry = Entry(self.overviewtab, textvariable=self.modname)
        self.versionentry = Entry(self.overviewtab, textvariable=self.modversion)
        self.domiversionentry = Entry(self.overviewtab, textvariable=self.domiversion)
        self.descboxscrollbar = AutoScrollbar(self.overviewtab)
        self.descriptionbox = Text(self.overviewtab, width=0, height=15, yscrollcommand=self.descboxscrollbar.set,
                                   undo=1, wrap=WORD)
        self.descboxscrollbar.config(command=self.descriptionbox.yview)
        self.pathentry = Entry(self.overviewtab, textvariable=self.loaddomfolder)

        # ##Buttons
        self.checkicon = ImageTk.PhotoImage(checkicon)
        self.bannerbutton = Button(self.overviewtab, image=self.checkicon, command=self.updatebanner)
        self.bannerbutton.image = self.checkicon
        self.pathbrowsebutton = Button(self.overviewtab, text='...', width=3)
        self.pathconfirmbutton = Button(self.overviewtab, image=self.checkicon)

        # #Draw
        # ##Frames and canvas
        self.bannerframe.grid(row=0, column=2, rowspan=3, columnspan=4, padx=5, sticky=W+S)
        self.bannercanvas.pack()
        # ##Labels
        self.bannerlabel.grid(row=3, column=2, padx=5, pady=5, sticky=W+S)
        self.modnamelabel.grid(row=0, column=0, padx=5, pady=5, sticky=N+W+S)
        self.versionlabel.grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.domiversionlabel.grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.descriptionlabel.grid(row=5, column=0, padx=5, pady=5, sticky=W)
        self.folderlabel.grid(row=7, column=0, columnspan=2, padx=5, pady=(5, 0), sticky=W)
        # ##Entries
        self.bannerentry.grid(row=4, column=2, columnspan=3, padx=5, sticky=W+E)
        self.modnameentry.grid(row=1, column=0, padx=5, columnspan=2, sticky=W+E+N)
        self.versionentry.grid(row=2, column=1, padx=5, sticky=W)
        self.domiversionentry.grid(row=3, column=1, padx=5, sticky=W)
        self.descriptionbox.grid(row=6, column=0, columnspan=5, padx=(5, 0), pady=5, sticky=W+E+N+S)
        self.descboxscrollbar.grid(row=6, column=5, padx=0, pady=5, sticky=N+S+W)
        self.pathentry.grid(row=8, column=0, columnspan=4, padx=5, pady=(0, 5), sticky=W+E)
        # ##Buttons
        self.bannerbutton.grid(row=4, column=5, columnspan=2, padx=(0, 5))
        self.pathbrowsebutton.grid(row=8, column=4, padx=(0, 5), pady=(0, 5))
        self.pathconfirmbutton.grid(row=8, column=5, padx=(0, 5), pady=(0, 5), sticky=W)
        # endregion

        # region ###Monster tab
        self.moncoll_info = Collapse(self.monstertab.editingframe, text='Information/Appearance', padding=(5, 5, 5, 0))
        self.moncoll_info.grid(sticky=N+E+W+S)

        self.moncoll_basicatt = Collapse(self.monstertab.editingframe, text='Basic Attributes', padding=(5, 0))
        self.moncoll_basicatt.grid(sticky=N+E+W+S)

        self.moncoll_clear = Collapse(self.monstertab.editingframe, text='Clear/Copy tags', padding=(5, 0))
        self.moncoll_clear.grid(sticky=N+E+W+S)
        self.moncoll_clear.addfields(monster_clearlist, monster_clearlabels, self.monstertab.treelist)

        # endregion

        # region ###Weapon tab
        self.weaponcoll_basic = Collapse(self.weapontab.editingframe, text='Weapon Attributes', padding=(5, 5, 5, 0))
        self.weaponcoll_basic.grid(sticky=N+E+W+S)
        self.weaponcoll_basic.add(Tagentry, sourcetree=self.weapontab.treelist, key='name', text='Name',
                                  width=40, column=0, row=0)
        self.weaponcoll_basic.addfields(weapon_basiclist, weapon_basiclabels, self.weapontab.treelist)
        # endregion

        # region ###Armor tab
        self.armorcoll = Collapse(self.armortab.editingframe, text='Armor Statistics', padding=(5, 5, 5, 0))
        self.armorcoll.grid(sticky=N+E+W+S)
        self.armorcoll.add(Tagentry, sourcetree=self.armortab.treelist, key='name', text='Name', width=40, column=0,
                           row=0)
        self.armorcoll.addfields(armor_list, armor_labels, self.armortab.treelist)
        # endregion

        # endregion

    def browsedm(self):
        targetdm = tkinter.filedialog.askopenfile(mode='r', filetypes=[('Dominions mod file', '.dm')], parent=root,
                                                  initialdir=self.defaultdomfolder, title='Please select a directory')
        if targetdm is None:
            print("No file selected")

        else:
            newmod = Modentry(targetdm)
            self.buildmod(newmod)

    def buildmod(self, mod):
        self.modname.set(mod.modname)
        self.modversion.set(mod.version)
        self.domiversion.set(mod.domversion)
        self.iconpath.set(mod.iconpath)
        self.descriptionbox.delete(1.0, END)
        self.descriptionbox.insert(END, mod.description)
        self.updatebanner()

        self.monstertab.modload(mod.monsters)
        self.weapontab.modload(mod.weapons)
        self.armortab.modload(mod.armors)

    def updatebanner(self):
        # TODO Handle incorrect banner format/sizes
        try:
            bannericon = Image.open(self.loaddomfolder.get() + self.iconpath.get())
            self.bannerphoto = ImageTk.PhotoImage(bannericon)
            self.bannercanvas.create_image(0, 0, image=self.bannerphoto, anchor=NW)
        except (PermissionError, FileNotFoundError, OSError):
            self.bannercanvas.delete(ALL)


class AutoScrollbar(Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)


class Collapse(Frame):

    def __init__(self, master, text='', width=1, **kwargs):
        Frame.__init__(self, master, **kwargs)

        self.open = IntVar()
        self.open.set(0)
        self.autolist = []
        self.itemlist = []
        self.labellist = []
        self.columncount = 1
        self.label = text

        self.plusicon = ImageTk.PhotoImage(toggleplusicon)
        self.minusicon = ImageTk.PhotoImage(toggleminusicon)
        self.button = Button(self, text=text, image=self.plusicon, compound='right',
                             command=self.toggle, width=width)
        self.button.grid(column=0, row=0, columnspan=2, sticky=E+W)
        self.grid_columnconfigure(1, weight=1)

        self.collapseframe = Frame(self, relief='groove', borderwidth=1, padding=5)
        self.collapseframe.grid_columnconfigure(0, weight=1)
        self.spaceframe = Frame(self, width=10)
        self.overframe = Frame(self.collapseframe)
        self.subframe = Frame(self.collapseframe)

        self.overframe.grid(column=0, row=0, sticky=N+E+W+S)
        self.subframe.grid(column=0, row=1, sticky=N+E+W+S)
        self.button.bind('<Configure>', self.on_resizebutton)

    def toggle(self):
        if not bool(self.open.get()):
            self.collapseframe.grid(column=1, row=1, sticky=N+E+W+S)

            self.spaceframe.grid(column=0, row=1, sticky=W)

            self.button.config(image=self.minusicon)
            self.open.set(1)
            self.subframe.bind('<Configure>', self.on_resizewindow)
        else:
            self.collapseframe.grid_forget()
            self.spaceframe.grid_forget()
            self.button.config(image=self.plusicon)
            self.open.set(0)
            self.subframe.bind('<Configure>')

    def on_resizebutton(self, event):
        self.button.config(text=self.label + ' '*int(event.width/3))

    def on_resizewindow(self, event):
        column_widths = 0
        for column in range(self.subframe.grid_size()[0]):
            column_widths += self.subframe.grid_bbox(column, 0)[2]
        if column_widths > 1:
            if column_widths + self.subframe.grid_bbox(0, 0)[2] < event.width - self.subframe.grid_bbox(0, 0)[0]:
                while column_widths + self.subframe.grid_bbox(0, 0)[2] < event.width - self.subframe.grid_bbox(0, 0)[0]:
                    if self.columncount < len(self.autolist):
                        self.columncount += 1
                        self.forget_items()
                        self.update_items()
                    column_widths += self.subframe.grid_bbox(0, 0)[2]

            elif column_widths >= event.width - self.subframe.grid_bbox(0, 0)[0]*2:
                while column_widths >= event.width - self.subframe.grid_bbox(0, 0)[0]*2 and self.columncount > 1:
                    self.columncount -= 1
                    self.forget_items()
                    self.update_items()
                    column_widths -= self.subframe.grid_bbox(self.columncount-1, 0)[2]

    # Adds tags + parameters to the specified master collapse. tagset should be a tuple containing a list of parameters
    # followed by a list of tags.
    def addfields(self, tagset, namedict, sourcetree):
        for param in tagset[0]:
            entry = Tagentry(self.subframe, sourcetree=sourcetree, key=param, text=namedict[param])
            self.subadd(entry)
        for tag in tagset[1]:
            if tag not in self.labellist:
                entry = Tagbutton(self.subframe, sourcetree=sourcetree, key=tag, text=namedict[tag])
                self.subadd(entry)

    def update_items(self):
        o = 0
        j = 0
        for item in self.autolist:
            item.grid(column=o, row=j, in_=self.subframe, sticky=W)
            o += 1
            if o >= self.columncount:
                j += 1
                o = 0

    def forget_items(self):
        for item in self.autolist:
            item.grid_forget()

    def subadd(self, child):
        if type(child).__name__ in ('Tagbutton', 'Tagentry'):
            if child.key not in self.labellist:
                self.itemlist.append(child)
                self.labellist.append(child.key)
                self.forget_items()
                self.autolist.append(child)
                self.update_items()
        else:
            self.itemlist.append(child)
            self.forget_items()
            self.autolist.append(child)
            self.update_items()

    def add(self, widget, **kwargs):
        if widget in ('Tagbutton', 'Tagentry'):
            if kwargs['key'] not in self.labellist:
                child = widget(self.overframe, **kwargs)
                self.itemlist.append(widget(child))
                self.labellist.append(kwargs['key'])
                child.grid()
        else:
            child = widget(self.overframe, **kwargs)
            self.itemlist.append(child)
            child.grid()


class Entitytab:

    def __init__(self, master, label=None):

        self.moddict = {}

        self.mainframe = Frame(master)
        master.add(self.mainframe, text=label)

        # region Treeview
        self.treescrollbary = AutoScrollbar(self.mainframe, orient=VERTICAL)
        self.treescrollbarx = AutoScrollbar(self.mainframe, orient=HORIZONTAL)

        self.treelistcolumns = ['ID', 'Name']
        self.treelist = Treeview(self.mainframe, selectmode='browse', columns=('ID', 'Name'), show='headings',
                                 height=22, xscrollcommand=self.treescrollbarx.set,
                                 yscrollcommand=self.treescrollbary.set)

        self.treescrollbary.config(command=self.treelist.yview)
        self.treescrollbarx.config(command=self.treelist.xview)

        self.treelist.grid(column=0, row=0, pady=(5, 0), padx=(5, 0), sticky=NSEW)
        self.treescrollbary.grid(column=self.treelist.grid_info()['column']+1, row=self.treelist.grid_info()['row'],
                                 padx=(0, 5), pady=(5, 0), sticky=N+S+W)
        self.treescrollbarx.grid(column=self.treelist.grid_info()['column'], row=self.treelist.grid_info()['row']+1,
                                 padx=(5, 0), pady=(0, 5), sticky=E+W+N)

        for column in self.treelistcolumns:
            self.treelist.heading(column, text=column, command=lambda _col=column:
                                  treeview_sort_column(self.treelist, _col, False))

        self.treelist.column('ID', width=50, minwidth=40, anchor=CENTER)
        self.treelist.column('Name', anchor=W)
        # endregion

        self.editingscrollbar = AutoScrollbar(self.mainframe, orient=VERTICAL)
        self.editingcanvas = Canvas(self.mainframe, highlightthickness=0,
                                    yscrollcommand=self.editingscrollbar.set)
        self.editingframe = Frame(self.mainframe, borderwidth=1)
        self.editingscrollbar.config(command=self.editingcanvas.yview)

        self.editingcanvas.grid(column=2, row=0, sticky=N+E+W+S)
        self.editingscrollbar.grid(column=3, row=0, sticky=N+S)

        self.editingcanvas.create_window((0, 0), window=self.editingframe, anchor='nw', tags='self.editingframe')
        # self.editingframe.grid(column=0, row=0, in_=self.editingcanvas, sticky=N+E+W+S)

        self.editingframe.grid_columnconfigure(0, weight=1)
        self.mainframe.grid_columnconfigure(2, weight=1)
        self.mainframe.grid_rowconfigure(0, weight=1)

        self.treelist.bind('<Double-1>', self.onclick)
        self.editingcanvas.bind('<Configure>', self.onframeconfigure)

    def modload(self, itemdict):

        for child in self.treelist.get_children():
            self.treelist.delete(child)

        self.moddict = itemdict

        for key in itemdict:
            self.treelist.insert('', 'end', self.moddict[key].ID, values=[self.moddict[key].ID, self.moddict[key].name])

    def onclick(self, event):
        try:
            item = self.treelist.selection()[0]
            print(item)
            for collapse in self.editingframe.winfo_children():
                for field in collapse.itemlist:
                    self.fillfield(field, item)
        except IndexError:
            pass

    def onframeconfigure(self, event):
        self.editingcanvas.itemconfig('self.editingframe', width=self.mainframe.grid_bbox(2, 0)[2])
        self.editingcanvas.configure(scrollregion=self.editingcanvas.bbox('self.editingframe'))

    def fillfield(self, field, item):
        print(type(field).__name__)
        if type(field).__name__ == 'Tagbutton':
            if field.key in self.moddict[item].misctags:
                field.var.set(1)
            else:
                field.var.set(0)
        elif type(field).__name__ == 'Tagentry':
            if field.key in self.moddict[item].statdict:
                field.var.set(self.moddict[item].statdict[field.key])
            else:
                field.var.set('')


class Tagbutton(Checkbutton):

    def __init__(self, master, **kwargs):
        self.var = IntVar()
        self.key = kwargs['key']
        self.sourcetree = kwargs['sourcetree']
        Checkbutton.__init__(self, master, variable=self.var, command=self.callback, padding=(5, 0),
                             text=kwargs['text'])

    def callback(self):
        cblist = [self.key, self.var.get()]
        print(cblist, )


class Tagentry(Frame):

    def __init__(self, master, **kwargs):
        self.var = StringVar()
        self.key = kwargs['key']
        self.sourcetree = kwargs['sourcetree']
        if 'width' in kwargs:
            self.width = kwargs['width']
        else:
            self.width = 12
        Frame.__init__(self, master, padding=(5, 0))
        self.label = Label(self, text=kwargs['text']+': ')
        self.entry = Entry(self, textvariable=self.var, width=self.width)
        self.label.grid(column=0, row=0, sticky=W)
        self.entry.grid(column=0, row=1, sticky=W)
        self.columnconfigure(1, weight=1)

        self.var.trace('w', lambda name, index, mode, var=self.var: self.callback(var))

    def callback(self, var):
        cblist = [self.key, var.get()]
        print(cblist)

# endregion


# region Global variables

# Tag reference groups for writing and building entries in GUI.
# region Monstertab
monster_clearparams = ['copystats', 'copyspr']
monster_cleartags = ['clear', 'clearweapons', 'cleararmor', 'clearmagic', 'clearspec']
monster_clearlabels = {'clear': 'Clear all', 'clearweapons': 'Clear weapons', 'cleararmor': 'Clear armor',
                       'clearmagic': 'Clear magic', 'clearspec': 'Clear special abilities',
                       'copystats': 'Copy stats from monster ID', 'copyspr': 'Copy sprite from monster ID'}
monster_clearlist = (monster_clearparams, monster_cleartags)

monster_baseatts = ['hp', 'size', 'ressize', 'prot', 'mr', 'mor', 'str', 'att', 'def', 'prec', 'enc',
                    'mapmove', 'ap', 'eyes', 'voidsanity']

monster_pretenderatts = ['pathcost', 'startdom', 'homerealm']
# endregion

# region Weapontab
weapon_basicparams = ['selectweapon', 'newweapon', 'name', 'dmg', 'nratt', 'att', 'def', 'len', 'range', 'ammo',
                      'rcost', 'sound', 'sample']
weapon_basiclabels = {'selectweapon': 'ID', 'newweapon': 'ID', 'name': 'Name', 'dmg': 'Damage',
                      'nratt': 'Number of attacks', 'att': 'Attack', 'def': 'Defense', 'len': 'Length',
                      'range': 'Range', 'ammo': 'Ammo', 'rcost': 'Resource cost', 'sound': 'Sound',
                      'sample': 'Custom sound (filename)', 'twohanded': 'Two-handed'}
weapon_basiclist = (weapon_basicparams, ['twohanded'])
# endregion

# region Armortab
armor_params = ['name', 'type', 'prot', 'def', 'enc', 'rcost']
armor_labels = {'name': 'Name', 'type': 'Armor Type', 'prot': 'Protection', 'def': 'Defense', 'enc': 'Encumbrance',
                'rcost': 'Resource Cost'}
armor_list = (armor_params, '')
# endregion

# Images
checkicon = Image.open('check.png')
toggleplusicon = Image.open('bullet_toggle_plus.png')
toggleminusicon = Image.open('bullet_toggle_minus.png')
# endregion

# region Main program

root = Tk()
# root.resizable(width=FALSE, height=FALSE)
root.wm_title("Dominions 4 Mod Editor")
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)
frame = Frame(root)
frame.pack(fill=BOTH, expand=1)
frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)

start = Mainwindow(frame)

mainloop()
# endregion
