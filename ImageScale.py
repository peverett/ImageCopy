import sys
if sys.version_info[0] > 2:
    import tkinter.font as tkFont
    from tkinter import *
    from tkinter import messagebox, filedialog
else:
    import tkFont
    from Tkinter import *
from PIL import Image, ImageTk

def invfrange(start, stop, step):
    """Inverted (reverse) range inclusive of the final stop value, designed 
    to work with floats."""
    val = start
    vrange = []
    while val > stop:
        vrange.append(val)
        val = round(val - step, 2) # round to 2-decimal places.
    vrange.append(stop)
    return vrange

class ImageCanvas:
    def __init__(self, root):
        self.root = root
        self.image_id = None
        self.scale_range = []

        self.hsb = Scrollbar(root, orient='horizontal')
        self.vsb = Scrollbar(root, orient='vertical')
        self.max_zoom_out = 4.0

        self.canvas = Canvas(
                root, 
                bg='black', 
                width=800, 
                height=600,
                xscrollcommand=self.hsb.set,
                yscrollcommand=self.vsb.set
                )
        self.canvas.pack(side=TOP, fill='both', expand='yes')
        self.canvas.update()
        
        self.hsb.configure(command=self.canvas.xview)
        self.vsb.configure(command=self.canvas.yview)

        self.canvas.bind('<Enter>', self.enter)
        self.canvas.bind('<Leave>', self.leave)
        self.canvas.bind('<Configure>', self.resize)

        self.image = None
        self.scale_idx = 0
        self.scale_range = []

    def load_image(self, image_path):
        """Load the image indicated"""
        self.image = Image.open(image_path)
        self.calc_scale_range(self.image.size)
        self.scale_idx = len(self.scale_range)-1
        self.show_image()

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def enter(self, event):
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>',     self.move_to)
        self.canvas.bind_all('<MouseWheel>',    self.zoom)

    def leave(self, event):
        self.canvas.unbind('<ButtonPress-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind_all('<MouseWheel>')

    def zoom_in(self):
        """Make the image bigger up to actual size"""
        if self.scale_idx > 0:
            self.scale_idx -= 1
            self.show_image()

    def zoom_out(self):
        """Make image smaller down to size of canvas"""
        if self.scale_idx < (len(self.scale_range) - 1):
            self.scale_idx = self.scale_idx + 1
            self.show_image()

    def zoom(self, event):
        '''Resize and display the image''' 
        if event.delta == 120:      # Mouse wheel up
            self.zoom_in()
        if event.delta == -120:     # mouse wheel down
            self.zoom_out()

        #self.canvas.scale( 
        #        'all',
        #        self.canvas.canvasx(event.x),
        #        self.canvas.canvasy(event.y),
        #        self.scale_range[self.scale_idx], 
        #        self.scale_range[self.scale_idx]
        #        )

    def show_image(self):
        """Show image on the canvas"""
        if self.image_id:
            self.canvas.delete(self.image_id)

        width, height = self.image.size
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        nw = int(width * self.scale_range[self.scale_idx])
        nh = int(height * self.scale_range[self.scale_idx])
        self.imagetk = ImageTk.PhotoImage(
                self.image.resize( (nw, nh), Image.ANTIALIAS )
                )

        ow = (cw - nw) / 2 if nw < cw else 0
        oh = (ch - nh) / 2 if nh < ch else 0

        self.image_id = self.canvas.create_image(ow , oh, image=self.imagetk, anchor='nw')
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))


    def calc_scale_range(self, size):
        width, height = size
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if height < ch and width < cw:
            self.scale_range = [ 1.0 ]
        else:
           wratio = float(cw) / width
           hratio = float(ch) / height
           min_scale = round( min(wratio, hratio), 4)
        self.scale_range = invfrange(1.0, min_scale, 0.2)
        self.scale_idx = len(self.scale_range) - 1

    def resize(self, event):
        self.calc_scale_range(self.image.size)
        self.scale_idx = len(self.scale_range)-1
        self.show_image()

    def get_zoom(self):
        return int( self.scale_range[ self.scale_idx ] * 100.0 )

            
def main():
    root = Tk()
    root.title("Image Zoom")
    im = ImageCanvas(root)
    im.load_image("./TestImage.jpg")
    root.mainloop()

if __name__ == "__main__":
    main()
