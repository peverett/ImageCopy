#!/usr/bin/python
"""Copy Digital Camera IMages (DCIM) from a source 
Memory Card or USB to a specified destination folder. 

Allows image preview for selective copying,
file renaming based on EXIF data such as Date 
and Time image was made."""

__version__ = "1.0"
__author__ = "simon.peverett@gmail.com"
__all__ = ['__version__', '__author__']

import os
import configparser
import glob
import sys
if sys.version_info[0] > 2:
    import tkinter.font as tkFont
    from tkinter import *
    from tkinter import messagebox, filedialog
else:
    import tkFont
    from Tkinter import *
from PIL import Image, ImageTk
from ImageScale import ImageCanvas
from datetime import datetime
from shutil import copyfile

def GetConfigFilename():
    """Return the config file name based on the following rules:
    * Config file is in the same directory as the python script.
    * Config file has the same name but with extention '.ini'
    """
    thisfile = os.path.splitext(
            os.path.abspath(__file__)
            )[0]
    return os.path.join(
            '.'.join([thisfile, 'ini'])
            )
    
def UpdateConfigFile(config):
    """Update the Config File by writing it."""
    with open(GetConfigFilename(), 'w') as cf:
        config.write(cf)

def LoadConfigFile():
    """Load the Config File. If it doesn't exist, then create it."""
    config = configparser.ConfigParser()

    # If we can't read a config, create one.
    if not config.read(GetConfigFilename()):
        home = os.path.expanduser('~')
        
        config['DEFAULT'] = {
                'source': 'C:\\',
                'destination': home,
                'use_date': 'no',
                'use_time': 'no',
                'use_user': 'no',
                'use_name': 'yes',
                }

        UpdateConfigFile(config)

    return config

def ListJpgFiles(path):
    """return a list of all files with the .jpg extension in the path passed."""
    jpgfiles = glob.glob(
            os.path.join(path, '*.jpg')
            )
    return jpgfiles

class ImageCopyController(object):
    """ImageCopy Controller Class"""
    
    def __init__(self, root):
        self.root = root

        # Tkinter variables 
        self.src_str = StringVar()
        self.dst_str = StringVar()
        self.zoom_str = StringVar()
        self.user_str = StringVar()
        self.date_str = StringVar()
        self.time_str = StringVar()
        self.fn_str = StringVar()
        self.fnum_str = StringVar()

        self.cb_date = IntVar()
        self.cb_time = IntVar()
        self.cb_name = IntVar()
        self.cb_user = IntVar()

        # Get defaults from Config file, or set them!
        self.config = LoadConfigFile()
        self.jpgfiles = ListJpgFiles(self.config['DEFAULT']['source'])
        self.jpgidx = 0     # Index on first image in the list.
        self.jpglen = len(self.jpgfiles)
        self.cb_date.set(self.config.getboolean('DEFAULT','use_date'))
        self.cb_time.set(self.config.getboolean('DEFAULT','use_time'))
        self.cb_user.set(self.config.getboolean('DEFAULT','use_user'))
        self.cb_name.set(self.config.getboolean('DEFAULT','use_name'))

        self.root.bind('<Destroy>', self.destroy_cmd)

        self.MenuBar()                             

        left_frm = Frame(self.root)
        left_frm.pack(side=LEFT, fill=BOTH, expand=YES)

        self.ic = ImageCanvas(left_frm)
        self.button_frame(left_frm)
        self.source_frame(left_frm)
        self.destination_frame(left_frm)

        right_frm = Frame(self.root)
        right_frm.pack(side=RIGHT, fill=Y, expand=NO)

        self.file_info_frame(right_frm)
        self.user_input_frame(right_frm)
        self.image_options_frame(right_frm)

        #root.state('zoomed')

        if self.jpgfiles:
            self.update_image_source()
                    
    def copy_file_cmd(self):
        copyfile(self.src_str.get(), self.dst_str.get())

    def destroy_cmd(self, event):
        """What happens when the app is closed down."""
        UpdateConfigFile(self.config)

    def options_cmd(self):
        """Action on check box being ticked."""
        self.update_options()
        self.update_destination()

    def update_options(self):
        """Update options such as image file options or source and destination
        directories."""
        self.config['DEFAULT']['use_date'] = 'yes' if self.cb_date.get() else 'no'
        self.config['DEFAULT']['use_time'] = 'yes' if self.cb_time.get() else 'no'
        self.config['DEFAULT']['use_user'] = 'yes' if self.cb_user.get() else 'no'
        self.config['DEFAULT']['use_name'] = 'yes' if self.cb_name.get() else 'no'

    def update_destination(self):
        """Update the destination file name."""
        image =self.jpgfiles[self.jpgidx]
        cdt = datetime.fromtimestamp(os.path.getctime(image))
        self.date_str.set(cdt.strftime('%Y-%m-%d'))
        self.time_str.set(cdt.strftime('%H:%M:%S'))

        cfn = list()
        if self.cb_date.get():
            cfn.append(cdt.strftime('%Y%m%d'))
        if self.cb_time.get():
            cfn.append(cdt.strftime('%H%M%S'))
        ud = self.user_str.get()
        if len(ud) and self.cb_user.get():
            cfn.append(ud)
        if self.cb_name.get():
            cfn.append(self.fn_str.get())

        copy_name = os.path.join(
                self.config['DEFAULT']['Destination'],
                "{}.jpg".format('_'.join(cfn)))
        self.dst_str.set(copy_name)


    def update_image_source(self):
        image =self.jpgfiles[self.jpgidx]

        self.src_str.set(image)
        self.fn_str.set(os.path.basename(image))
        self.fnum_str.set("{} of {}".format(self.jpgidx+1, self.jpglen))
    
        self.ic.load_image(image)
        self.zoom_str.set("{:d} %".format(self.ic.get_zoom()))
        self.update_destination()

    def next_cmd(self):
        if self.jpgfiles:
            if self.jpgidx < self.jpglen-1:
                self.jpgidx += 1
                self.update_image_source()

    def prev_cmd(self):
        if self.jpgfiles:
            if self.jpgidx > 0:
                self.jpgidx -= 1
                self.update_image_source()

    def zoom_in(self):
        self.ic.zoom_in()
        self.zoom_str.set("{:d} %".format(self.ic.get_zoom()))

    def zoom_out(self):
        self.ic.zoom_out()
        self.zoom_str.set("{:d} %".format(self.ic.get_zoom()))

    def SetConfigDir(self, directory='destination'):
        """Set the 'directory' in the configuration. By default this is the
        'destination' directory.
        """
        new_dir = os.path.normpath(
                filedialog.askdirectory(
                    initialdir=self.config['DEFAULT'][directory],
                    title="Select {} folder".format(directory)
                    )
                )
        
        if self.config['DEFAULT'][directory]  != new_dir:
            self.config['DEFAULT'][directory] = new_dir

    def SetDestinationDir(self):
        self.SetConfigDir()
        self.update_destination()

    def SetSourceDir(self):
        self.SetConfigDir('Source')
        self.jpgfiles = ListJpgFiles( self.config['DEFAULT']['source'] )
        self.jpgidx = 0
        self.jpglen = len(self.jpgfiles)

        if not self.jpgfiles:
            messagebox.showwarning(
                    "No JPG files found!",
                    '\n'.join([
                        "No JPG files found In directory:",
                        self.config['DEFAULT']['source']
                        ])
                    )
        else:
            self.update_image_source()

    def AboutImageCopy(self):
        messagebox.showinfo(
                "About: ImageCopy",
                ''.join([
                    __doc__, '\n\n',
                    'Author:  ', __author__, '\n\n'
                    'Version: ', __version__,
                    ])
                )

    def MenuBar(self):
        """Application Menu Bar"""
        menubar = Menu(self.root)
        
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Set Source Dir", command=self.SetSourceDir)
        filemenu.add_command(
                label="Set Destination Dir", command=self.SetDestinationDir)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.AboutImageCopy)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.root.config(menu=menubar)

    def button_frame(self, parent):
        """Frame to contain buttons for moving through images and zooming the
        current image."""
        frm = Frame(parent, bd=5)
        frm.pack(side=TOP, fill=X, expand=NO)

        prev = Button(
                frm, text="<< Prev", padx=5, pady=5, command=self.prev_cmd)
        prev.pack(side=LEFT, fill=X, expand=YES)

        zoom_in = Button(
                frm, text="Zoom In (+)", padx=5, pady=5, command=self.zoom_in)
        zoom_in.pack(side=LEFT, fill=X, expand=YES)

        copy_image = Button(
                frm, text="Copy Image", padx=5, pady=5, 
                command=self.copy_file_cmd)
        copy_image.pack(side=LEFT, fill=X, expand=YES)

        zoom_out = Button(
                frm, text="Zoom Out (-)", padx=5, pady=5, command=self.zoom_out)
        zoom_out.pack(side=LEFT, fill=X, expand=YES)

        next = Button(
                frm, text="Next >>", padx=5, pady=5, command=self.next_cmd)
        next.pack(side=LEFT, fill=X, expand=YES)

    def source_frame(self, parent):
        """Frame to contain the labels for displaying the source path & file"""
        frm = Frame(parent, bd=1)
        frm.pack(side=TOP, fill=X, expand=NO)

        legend = Label(
                frm, text="Source:", width=15, anchor=W, padx=5)
        legend.pack(side=LEFT, fill=X, expand=NO)

        info = Label(
                frm, bd=5, bg='black', fg='white', anchor=W, 
                textvariable=self.src_str, width=85, padx=5) 
        info.pack(side=LEFT, fill=X, expand=YES)
        
    def destination_frame(self, parent):
        """Frame to contain the labels for displaying the destination path
        and filename."""
        frm = Frame(parent, bd=1)
        frm.pack(side=TOP, fill=X, expand=NO)

        legend = Label(
                frm, text="Destination:", anchor=W, width=15, padx=5)
        legend.pack(side=LEFT, fill=X, expand=NO)

        info = Label(
                frm, bd=5, bg='black', fg='white', anchor=W, 
                textvariable=self.dst_str, width=85, padx=5) 
        info.pack(side=LEFT, fill=X, expand=YES)

    def file_info_frame(self, parent):
        """Frame to display the image information."""
        frm = Frame(parent, relief=RIDGE, bd=5)
        frm.pack(side=TOP, fill=X, expand=NO)

        title = Label(
                frm, text="File Information", width=30, 
                justify=CENTER, pady=10, padx=5)
        title.pack(side=TOP, fill=X, expand=NO)

        fnum_frame = Frame(frm)
        fnum_frame.pack(side=TOP, fill=X, expand=NO)
        fn_legend = Label(
                fnum_frame, text="File #:", width=10, 
                anchor=W, padx=5, pady=5)
        fn_legend.pack(side=LEFT, fill=X, expand=NO)
        filenum = Label(
                fnum_frame, textvariable=self.fnum_str, bg='black', fg='white',
                anchor=W, width=20)
        filenum.pack(side=LEFT, fill=X, expand=NO)

        fn_frame = Frame(frm)
        fn_frame.pack(side=TOP, fill=X, expand=NO)
        fn_legend = Label(
                fn_frame, text="File name:", width=10, 
                anchor=W, padx=5, pady=5)
        fn_legend.pack(side=LEFT, fill=X, expand=NO)
        filename = Label(
                fn_frame, textvariable=self.fn_str, bg='black', fg='white',
                anchor=W, width=20)
        filename.pack(side=LEFT, fill=X, expand=NO)

        dt_frame = Frame(frm)
        dt_frame.pack(side=TOP, fill=X, expand=NO)
        dt_legend = Label(
                dt_frame, text="Create date:", width=10, 
                anchor=W, padx=5, pady=5)
        dt_legend.pack(side=LEFT, fill=X, expand=NO)
        date = Label(
                dt_frame, textvariable=self.date_str, bg='black', fg='white',
                anchor=W, width=20)
        date.pack(side=LEFT, fill=X, expand=NO)

        tm_frame = Frame(frm)
        tm_frame.pack(side=TOP, fill=X, expand=NO)
        tm_legend = Label(
                tm_frame, text="Create time:", width=10, 
                anchor=W, padx=5, pady=5)
        tm_legend.pack(side=LEFT, fill=X, expand=NO)
        date = Label(
                tm_frame, textvariable=self.time_str, bg='black', fg='white',
                anchor=W, width=20)
        date.pack(side=LEFT, fill=X, expand=NO)

        zm_frame = Frame(frm)
        zm_frame.pack(side=TOP, fill=X, expand=NO)
        zm_legend = Label(
                zm_frame, text="Image zoom:", width=10, 
                anchor=W, padx=5, pady=5)
        zm_legend.pack(side=LEFT, fill=X, expand=NO)
        date = Label(
                zm_frame, textvariable=self.zoom_str, bg='black', fg='white',
                anchor=W, width=20)
        date.pack(side=LEFT, fill=X, expand=NO)

    def user_input_frame(self, parent):
        """Frame for user to input a part of the filename when copied."""
        frm = Frame(parent, relief=RIDGE, bd=5)
        frm.pack(side=TOP, fill=X, expand=NO)

        title = Label(
                frm, text="User Description", width=30, 
                justify=CENTER, pady=5, padx=5)
        title.pack(side=TOP, fill=X, expand=NO)
        
        ufrm = Frame(frm)
        ufrm.pack(side=TOP, fill=X, expand=NO)

        user_entry = Entry(
                ufrm, textvariable=self.user_str, width=20, bd=5, 
                bg='black', fg='white')
        user_entry.pack(side=LEFT, fill=X, expand=YES)

        set_btn = Button(
                ufrm, text="Set", padx=10, pady=5, anchor=E,
                command=self.update_destination)
        set_btn.pack(side=LEFT, fill=X, expand=NO)

    def image_options_frame(self, parent):
        frm = Frame(parent, relief=RIDGE, bd=5)
        frm.pack(side=TOP, fill=X, expand=NO)

        title = Label(
                frm, text="Destination Name Options", width=30, 
                justify=CENTER, pady=5, padx=5)
        title.pack(side=TOP, fill=X, expand=NO)

        date= Checkbutton(
                frm, text="Created file date", padx=20,
                anchor=W, variable=self.cb_date, command=self.options_cmd)
        date.pack(side=TOP, fill=X, expand=NO)

        time= Checkbutton(
                frm, text="Created file time", padx=20,
                anchor=W, variable=self.cb_time, command=self.options_cmd)
        time.pack(side=TOP, fill=X, expand=NO)

        user = Checkbutton(
                frm, text="User description ", padx=20,
                anchor=W, variable=self.cb_user, command=self.options_cmd)
        user.pack(side=TOP, fill=X, expand=NO)

        name = Checkbutton(
                frm, text="Source file name ", padx=20,
                anchor=W, variable=self.cb_name, command=self.options_cmd)
        name.pack(side=TOP, fill=X, expand=NO)
        


def main():
    """Main function"""
    root = Tk()
    root.title("ImageCopy")
    control = ImageCopyController(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()
