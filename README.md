# ImageCopy

Copy image files from a memory card or USB stick that conform to the [Design 
rule for Camera File System (DCF)](https://en.wikipedia.org/wiki/Design_rule_for_Camera_File_system).

That means that
* Images will be under a 'DCIM' folder (**D**igital **C**amera **IM**ages).
* Images will be in [JPEG](https://en.wikipedia.org/wiki/JPEG) format.
* Images will contain [EXIF](https://en.wikipedia.org/wiki/Exif) data.

The application will allow the user to:
* Allow the user to define a default local path to copy the image to
* Allow the user to rename the file automatically when copied to contain the 
  date and time the image was taken, taken from the EXIF data of the image.
* Allow the user to go through the images one at a time, selectively copying 
  an image at a time. 
* Allow the user to append to the new filename

Application to be implemented in Python.
