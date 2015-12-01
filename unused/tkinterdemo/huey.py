#!/usr/local/bin/python
#================================================================
# huey:  A color and font selection tool
#   For documentation, see:
#     http://www.nmt.edu/tcc/help/lang/python/examples/huey/ims/
#----------------------------------------------------------------

PROGRAM_NAME      =  "huey"
EXTERNAL_VERSION  =  "1.0"
import math
import os
from Tkinter import *
import tkFont
from Dialog import Dialog
from scrolledlist import ScrolledList
from fontselect import FontSelect
#================================================================
# Manifest constants
#----------------------------------------------------------------

MAX_PARAM  =  65535
N_PARAMS  =  3
MAX_BYTE  =  255
BUTTON_FONT  =  ('times', 12)
MONO_FONT  =  ('lucidatypewriter', 14, 'bold')
# - - - - -   m a i n

def main():
    """Main program.

      [ display a graphical application that allows the user to
        test various fonts in various colors displayed on various
        background colors ]
    """

    #-- 1 --
    # [ the screen  :=  the screen with a graphical application
    #   app  :=  the graphical application ]
    app  =  Application()
    #-- 2 --
    # [ app  :=  app with its window title set to the name of
    #            this application ]
    app.winfo_toplevel().title( "%s %s" %
                                (PROGRAM_NAME,  EXTERNAL_VERSION) )
    #-- 3 --
    # [ app  :=  app responding to user events ]
    app.mainloop()

# - - - - -   c l a s s   C o l o r

class Color:
    """Represents an arbitrary color.

      Exports:
        Color ( red, green, blue ):
          [ (red is the red value as a float in [0.0,1.0] or as an
            int in [0,MAX_PARAM]) and
            (green is the green value as a float in [0.0,1.0] or as an
            int in [0,MAX_PARAM]) and
            (blue is the blue value as a float in [0.0,1.0] or as an
            int in [0,MAX_PARAM]) ->
              return a new Color instance with those color values ]
        .r:    [ the red component as an int in [0,MAX_PARAM] ]
        .g:    [ the green component as an int in [0,MAX_PARAM] ]
        .b:    [ the blue component as an int in [0,MAX_PARAM] ]
        .__str__(self):
          [ return self as a string "#RRGGBB" ]
        .__cmp__(self, other):
          [ other is a Color instance ->
              if self's color name is less than other's ->
                return a negative number
              else if self's color name is greater than other's ->
                return a positive number
              else -> return 0 ]
    """
# - - -   C o l o r . _ _ i n i t _ _

    def __init__ ( self, red, green, blue ):
        """Constructor for Color
        """

        #-- 1 --
        # [ if red is a float in [0.0, 1.0] ->
        #     self.r  :=  red mapped onto [0, MAX_PARAM]
        #   if red is an int in [0,MAX_PARAM] ->
        #     self.r  :=  red ]
        self.r  =  self.__standardize ( red )

        #-- 2 --
        # [ simile ]
        self.g  =  self.__standardize ( green )

        #-- 3 --
        self.b  =  self.__standardize ( blue )
# - - -   C o l o r . _ _ s t a n d a r d i z e

    def __standardize ( self, rawValue ):
        """Standardize representation of a color component.

          [ if rawValue is a float in [0.0, 1.0] ->
              return int ( rawValue * MAX_PARAM )
            if rawValue is an int in [0, MAX_PARAM] ->
              return rawValue
            else -> raise ValueError ]
        """
        if  type(rawValue) is float:
            if  not 0.0 <= rawValue <= 1.0:
                raise ValueError, ( "Float color value %.4f "
                    "out of bounds." % rawValue )
            return  int ( rawValue * MAX_PARAM )
        elif type(rawValue) is int:
            if  not 0 <= rawValue <= MAX_PARAM:
                raise ValueError, ( "Int color value %d "
                    "out of bounds." % rawValue )
            return rawValue
        else:
            raise ValueError, ( "Color component %s "
                "not int or float." % rawValue )
# - - -   C o l o r . _ _ s t r _ _

    def __str__ ( self ):
        """Convert self to an X color name.
        """
        r8  =  self.r >> 8
        g8  =  self.g >> 8
        b8  =  self.b >> 8
        return "#%02X%02X%02X" % (r8, g8, b8)
# - - -   C o l o r . _ _ c m p _ _

    def __cmp__ ( self, other ):
        """Compare two colors."""
        return  cmp ( str(self), str(other) )

# - - - - -   c l a s s   C o l o r M o d e l

class ColorModel:
    """Base class for color models.

      Exports:
        ColorModel ( modelName, labelList ):
          [ (modelName is the name of this model as a string) and
            (labelList is a sequence of three strings naming
            the parameters of this model) ->
              return a ColorModel object with those names ]
        .modelName:     [ as passed to constructor, read-only ]
        .labelList:     [ as passed to constructor, read-only ]
        .paramsToColor ( params ):
          [ params is a sequence of three numbers in [0,MAX_PARAM] ->
              return that color in self's model as a Color instance ]
        .colorToParams ( color ):
          [ color is a Color instance ->
              return color's parameters in self's model as a
              sequence of three numbers in [0,MAX_PARAM] ]
        ColorModel.normalize(n):
           [ n is an int in [0,MAX_PARAM] ->
               return float(n)/MAX_PARAM ]
         ColorModel.discretize(n):
           [ n is a float in [0.0, 1.0] ->
               return int(n*MAX_PARAM) ]
    """
# - - -   C o l o r M o d e l . _ _ i n i t _ _

    def __init__ ( self, modelName, labelList ):
        """Constructor for ColorModel."""
        self.modelName  =  modelName
        self.labelList  =  labelList
# - - -   C o l o r M o d e l . p a r a m s T o C o l o r

    def paramsToColor ( self, params ):
        raise NotImplementedError, "ColorModel.paramsToColor"
# - - -   C o l o r M o d e l . c o l o r T o P a r a m s

    def colorToParams ( self, params ):
        raise NotImplementedError, "ColorModel.colorToParams"
# - - -   C o l o r M o d e l . n o r m a l i z e

#   @staticmethod
    def normalize ( n ):
        result  =  float(n)/MAX_PARAM
        if  result < 0.0:
           return 0.0
        elif result > 1.0:
           return 1.0
        else:
           return result

    normalize  =  staticmethod ( normalize )
# - - -   C o l o r M o d e l . d i s c r e t i z e

#   @staticmethod
    def discretize ( n ):
        result  =  int(n*MAX_PARAM)
        if  result < 0:
           return 0
        elif result > MAX_PARAM:
           return MAX_PARAM
        else:
           return result

    discretize  =  staticmethod ( discretize )

# - - - - -   c l a s s   H S V M o d e l

class HSVModel(ColorModel):
    """Represents the hue-saturation-value color model.
    """
# - - -   H S V M o d e l . _ _ i n i t _ _

    def __init__ ( self ):
        ColorModel.__init__ ( self, "HSV",
            ("hue", "saturation", "value") )
# - - -   H S V M o d e l . p a r a m s T o C o l o r

    def paramsToColor ( self, params ):
        """Convert the three HSV color parameters to a Color.
        """
        h  =  ColorModel.normalize ( params[0] )
        s  =  ColorModel.normalize ( params[1] )
        v  =  ColorModel.normalize ( params[2] )
        if  s == 0.0:
            return Color ( v, v, v )
        if  h >= 1.0:
            h = 0.0
        else:
            h = h * 6.0
        (f,i) = math.modf(h)
        i     = int ( i )
        p     = v * ( 1.0 - s )
        q     = v * ( 1.0 - s * f )
        t     = v * ( 1.0 - s * ( 1.0 - f ) )

        if  i == 0:
            return Color ( v, t, p )
        elif i == 1:
            return Color ( q, v, p )
        elif i == 2:
            return Color ( p, v, t )
        elif i == 3:
            return Color ( p, q, v )
        elif i == 4:
            return Color ( t, p, v )
        else:
            return Color ( v, p, q )
# - - -   H S V M o d e l . c o l o r T o P a r a m s

    def colorToParams ( self, color ):
        """Convert a Color to the three HSV parameters.
        """
        rNorm  =  ColorModel.normalize(color.r)
        gNorm  =  ColorModel.normalize(color.g)
        bNorm  =  ColorModel.normalize(color.b)
        v = maxColor = max ( rNorm, gNorm, bNorm )
        minColor = min ( rNorm, gNorm, bNorm )
        if  maxColor == 0.0:
            s = 0.0
        else:
            s = ( maxColor - minColor ) / maxColor
        if  s == 0.0:
            h = 0.0     # Hue is undefined; use red arbitrarily
        else:
            delta = maxColor - minColor

            if  rNorm == maxColor:        # Between Y and M
                h = ( gNorm - bNorm ) / delta
            elif gNorm == maxColor:       # Between C and Y
                h = 2.0 + ( bNorm - rNorm ) / delta
            else:                       # Between M and C
                h = 4.0 + ( rNorm - gNorm ) / delta

            if h < 0.0:
                h = h + 6.0

            h  =  h / 6.0       # Normalize to [0,1]
        return ( ColorModel.discretize ( h ),
                 ColorModel.discretize ( s ),
                 ColorModel.discretize ( v ) )

# - - - - -   c l a s s   R G B M o d e l

class RGBModel(ColorModel):
    """Represents the red-green-blue color model.
    """
# - - -   R G B M o d e l . _ _ i n i t _ _

    def __init__ ( self ):
        """Constructor for RGBModel."""
        ColorModel.__init__ ( self, "RGB",
          ("red", "green", "blue") )
# - - -   R G B M o d e l . p a r a m s T o C o l o r

    def paramsToColor ( self, params ):
        """Convert three RGB parameters to a Color.
        """
        return  Color ( *params )
# - - -   R G B M o d e l . c o l o r T o P a r a m s

    def colorToParams ( self, color ):
        """Convert a Color to the three RGB parameters.
        """
        return ( ( color.r, color.g, color.b ) )

# - - - - -   c l a s s   C M Y M o d e l

class CMYModel(ColorModel):
    """Represents the cyan-yellow-magenta color model.
    """
# - - -   C M Y M o d e l . _ _ i n i t _ _

    def __init__ ( self ):
        """Constructor for CMYModel."""
        ColorModel.__init__ ( self, "CMY",
          ("cyan", "yellow", "magenta") )
# - - -   C M Y M o d e l . p a r a m s T o C o l o r

    def paramsToColor ( self, params ):
        """Convert CMY parameters to a Color.
        """
        cyan, magenta, yellow  =  params
        red    =  MAX_PARAM - cyan
        green  =  MAX_PARAM - magenta
        blue   =  MAX_PARAM - yellow
        return  Color ( red, green, blue )
# - - -   C M Y M o d e l . c o l o r T o P a r a m s

    def colorToParams ( self, color ):
        """Convert a color to CMY parameters.
        """
        cyan     =  MAX_PARAM - color.r
        magenta  =  MAX_PARAM - color.g
        yellow   =  MAX_PARAM - color.b
        return (cyan, magenta, yellow)

# - - - - -   c l a s s   A p p l i c a t i o n

class Application(Frame):
    """Contains the entire application.

      Contained widgets:
        .menuBar:       [ a MenuBar widget ]
        .namePicker:    [ a NamePicker widget ]
        .adjuster:      [ an Adjuster widget ]
        .swatch:        [ a Swatch widget ]

      Grid plan:
         0             1           2
        +---------------+-------------+-----------+
      0 | .__menuBar                              |
        +---------------+-------------+-----------+
      1 | .__namePicker | .__adjuster | .__swatch |
        +---------------+-------------+-----------+
    """
# - - -   A p p l i c a t i o n . _ _ i n i t _ _

    def __init__ ( self ):
        """Constructor for Application.
        """
        #-- 1 --
        # [ self  :=  self as a new root window Frame ]
        Frame.__init__ ( self, None )
        self.grid()
        #-- 2 --
        # [ self  :=  self with all widgets created and gridded ]
        self.__createWidgets()
# - - -   A p p l i c a t i o n . _ _ c r e a t e W i d g e t s

    def __createWidgets ( self ):
        """Create and grid all widgets.
        """
        #-- 1 --
        # [ self  :=  self with a new MenuBar widget added
        #   self.__menuBar  :=  that widget ]
        self.__menuBar  =  MenuBar ( self )
        self.__menuBar.grid ( row=0, column=0, columnspan=3,
                              sticky=W )
        #-- 2 --
        # [ self  :=  self with a new NamePicker widget added that
        #             calls self.__nameHandler when a name is picked
        #   self.__namePicker  :=  that NamePicker ]
        self.__namePicker  =  NamePicker ( self, self.__nameHandler )
        self.__namePicker.grid ( row=1, column=0, sticky=NW )
        #-- 3 --
        # [ self  :=  self with a new Adjuster widget added that calls
        #             self.__adjustHandler when the color is adjusted
        #   self.__adjuster  :=  that Adjuster widget
        self.__adjuster  =  Adjuster ( self, self.__adjustHandler )
        self.__adjuster.grid ( row=1, column=1, sticky=N, padx=4 )
        #-- 4 --
        # [ self  :=  self with a new Swatch widget added, using
        #       the background and text colors from self.__adjuster
        #   self.__swatch  :=  that widget ]
        self.__swatch  =  Swatch ( self, self.__adjuster.bgColor(),
                                   self.__adjuster.textColor() )
        self.__swatch.grid ( row=1, column=2, sticky=N )
# - - -   A p p l i c a t i o n . _ _ n a m e H a n d l e r

    def __nameHandler ( self, newColor ):
        """Handler for the NamePicker widget.

          [ newColor is a Color instance ->
              self  :=  self with its Adjuster displaying newColor ]
        """
        self.__adjuster.set ( newColor )
# - - -   A p p l i c a t i o n . _ _ a d j u s t H a n d l e r

    def __adjustHandler ( self, isText, newColor ):
        """Handler for the Adjuster widget.

          [ newColor is a Color instance ->
              if  isText ->
                self  :=  self with its Swatch displaying its
                          text in color (newColor)
              else ->
                self  :=  self with its Swatch displaying its
                          background in color (newColor) ]
        """
        if  isText:
            self.__swatch.setTextColor ( newColor )
        else:
            self.__swatch.setBgColor ( newColor )

# - - - - -   c l a s s   M e n u B a r

class MenuBar(Frame):
    """Compound widget containing general program controls.

      Contained widgets:
        .__helpButton:  [ a Menubutton that displays help text ]
        .__quitButton:  [ a Button that terminates the application ]

      Grid plan:
          0               1
         +---------------+---------------+
       0 | .__helpButton | .__quitButton |
         +---------------+---------------+
    """
# - - -   M e n u B a r . _ _ i n i t _ _

    def __init__ ( self, parent ):
        """Constructor for MenuBar"""
        #-- 1 --
        # [ self  :=  self as a Frame, ungridded ]
        Frame.__init__ ( self, parent )
        #-- 2 --
        # [ self  :=  self with a new Menubutton added and
        #       gridded, leading to the help menu cascades ]
        self.__helpButton  =  self.__createHelp()
        self.__helpButton.grid ( row=0, column=0 )
        #-- 3 --
        # [ self  :=  self with a Quit button added and gridded
        #             that terminates execution ]
        self.__quitButton  =  Button ( self, text='Quit',
            font=BUTTON_FONT, command=self.quit )
        self.__quitButton.grid ( row=0, column=1 )
# - - -   M e n u B a r . _ _ c r e a t e H e l p

    def __createHelp ( self ):
        """Create the help menubutton and its cascade.

          [ self is a Frame ->
              self  :=  self with a new Menubutton added but not
                        gridded, leading to the help text
              return that new Menubutton ]
        """
        #-- 1 --
        # [ mb  :=  a new Menubutton with self as its parent ]
        mb  =  Menubutton ( self, font=BUTTON_FONT,
                            relief=RAISED,
                            text="Help" )
        #-- 2 --
        # [ menu  :=  a new Menu with mb as its parent
        #   mb    :=  mb with its 'menu' attribute set to that
        #             new Menu ]
        menu  =  Menu ( mb )
        mb['menu']  =  menu
        #-- 3 --
        # [ menu  :=  menu with a cascade added about selecting
        #             colors by name ]
        self.__cascadeNamePicker ( menu )

        #-- 4 --
        # [ menu  :=  menu with a cascade added about adjusting
        #             colors ]
        self.__cascadeAdjuster ( menu )

        #-- 5 --
        # [ menu  :=  menu with a cascade added about viewing colors ]
        self.__cascadeViewing ( menu )

        #-- 6 --
        # [ menu  :=  menu with a pop-up added about importing
        #             colors into other applications
        menu.add_command ( command=self.__helpImporting,
            label="Importing colors into other applications" )

        #-- 7 --
        # [ menu  :=  menu with a pop-up added about the author ]
        menu.add_command ( command=self.__helpAuthor,
            label="Who made this tool?" )
        #-- 8 --
        return mb
# - - -   M e n u B a r . _ _ c a s c a d e N a m e P i c k e r

    def __cascadeNamePicker ( self, menu ):
        """Add the help cascade for picking colors by name

          [ menu is a Menu widget ->
              menu  :=  menu with choices added for help topics
                        about picking colors by name ]
        """
        #-- 1 --
        # [ menu    :=  menu with a new cascade added
        #   select  :=  that cascade ]
        select  =  Menu ( menu )
        menu.add_cascade ( menu=select,
            label="Selecting a standard color" )
        #-- 2 --
        # [ select  :=  select with a pop-up added about typing
        #       standard color names ]
        select.add_command ( command=self.__helpTyping,
            label="Typing in a standard color name" )

        #-- 3 --
        # [ select  :=  select with a pop-up added about picking
        #       standard color names ]
        select.add_command ( command=self.__helpPicking,
            label="Picking a standard color name" )
# - - -   M e n u B a r . _ _ h e l p T y p i n g

    def __helpTyping ( self ):
        """Pop-up help for typing standard color names
        """

        self.__dialog ( "Help: Typing in a standard color name",
            "If you already know the name of the color you want, "
            "move the cursor into the field labeled 'Enter a color "
            "name:', type the color name, and press Enter."
            "\n\tYour color will be displayed."
            "\n\tIf the color name you type is not known to the "
            "system, you will get a popup dialog menu." )
# - - -   M e n u B a r . _ _ h e l p P i c k i n g

    def __helpPicking ( self ):
        """Help for the color pick list
        """
        self.__dialog ( "Help: Picking a standard color name",
            "Under the label 'Or click on a name:' you will see a "
            "list of all the standard color names.  Click on the color "
            "name to select that color." )
# - - -   M e n u B a r . _ _ c a s c a d e A d j u s t e r

    def __cascadeAdjuster ( self, menu ):
        """Add the 'adjust' choice and cascade to the menu.

          [ menu is a Menu ->
              menu  :=  menu with a cascade added about adjusting
                        colors ]
        """
        #-- 1 --
        # [ menu    :=  menu with a new cascade added
        #   select  :=  that cascade ]
        select  =  Menu ( menu )
        menu.add_cascade ( menu=select,
                           label="Adjusting a color" )
        #-- 2 --
        # [ select  :=  select with pop-ups added that relate to
        #               color adjustment ]
        select.add_command ( label='Selecting background or text color',
            command=self.__helpReadout )

        select.add_command ( label='Color models and color space',
            command=self.__helpModelSelector )

        select.add_command ( label='The HSV color model',
            command=self.__helpHSV )

        select.add_command ( label='The RGB color model',
            command=self.__helpRGB )

        select.add_command ( label='The CMY color model',
            command=self.__helpCMY )

        select.add_command ( label='Using the color sliders',
            command=self.__helpSliders )
# - - -   M e n u B a r . _ _ h e l p R e a d o u t

    def __helpReadout ( self ):
        """Help for selecting bg/text color
        """
        self.__dialog ( 'Help: Selecting background or text color',
            "When the radiobuttons labeled 'Background color' is set, "
            "you can select the background color by name or by "
            "adjusting the three color sliders."
            "\n\t When 'Text color' is selected, you can select the "
            "color of the displayed text." )
# - - -   M e n u B a r . _ _ h e l p M o d e l S e l e c t o r

    def __helpModelSelector ( self ):
        """Help for selecting a color model.
        """
        self.__dialog ( 'Help: Selecting a color model',
            "A 'color model' is a way of describing a specific color as "
            "a set of three values from 0 and 255. Use the radiobuttons "
            "under 'Select a color model' to pick one of the color "
            "models." )
# - - -   M e n u B a r . _ _ h e l p H S V

    def __helpHSV ( self ):
        """Help for the HSV color model.
        """
        self.__dialog ( 'Help: The HSV color model',
            "In the HSV color model, color is specified by these three "
            "parameters:"
            "\n\t* Hue controls the base color.  As you drag the Hue "
            "slider, the color goes through red, yellow, green, cyan, "
            "blue, magenta, and then back to red again."
            "\n\t* Saturation controls color intensity. Drag the "
            "Saturation slider down for pale colors, drag it up for "
            "intense colors."
            "\n\t* Value controls brightness. Drag the Value slider "
            "down to darken a color, up to lighten it." )
# - - -   M e n u B a r . _ _ h e l p R G B

    def __helpRGB ( self ):
        """Help for the RGB color model.
        """
        self.__dialog ( 'Help: The RGB color model',
            "In the RGB color model, color is specified by three "
            "parameters: red, green, and blue.  These are called the "
            "'additive primary colors;' if you drag all three "
            "sliders all the way up, you get white.  RGB color mixing "
            "is used in display screens and also in stage lighting." )
# - - -   M e n u B a r . _ _ h e l p C M Y

    def __helpCMY ( self ):
        """Help for the CMY color model.
        """
        self.__dialog ( 'Help: The CMY color model',
            "In the CMY color model, color is specified by three "
            "parameters: cyan, magenta, and yellow.  These are called "
            "the 'subtractive primary colors;' if you drag all three "
            "sliders all the way up, you get black. CMY color mixing "
            "is used in printing and in color darkroom work." )
# - - -   M e n u B a r . _ _ h e l p S l i d e r s

    def __helpSliders ( self ):
        """Help for the color sliders.
        """
        self.__dialog ( 'Help: The color sliders',
            "To adjust a color, drag any of the three sliders with the "
            "mouse.  Each one controls one parameter of the color; see "
            "Help -> Creating new colors -> Color models and color "
            "space for an explanation of these parameters."
            "\n\tYou can also click on the '+' or '-' buttons to make "
            "fine adjustments." )
    def __cascadeViewing ( self, menu ):
        """Add the help cascade for viewing colors

          [ menu is a Menu widget ->
              menu  :=  menu with choices added for help topics
                        about viewing colors ]
        """
        #-- 1 --
        # [ menu    :=  menu with a new cascade added
        #   select  :=  that cascade ]
        select  =  Menu ( menu )
        menu.add_cascade ( menu=select,
            label="Viewing colors and fonts" )
        #-- 2 --
        # [ select  :=  select with a pop-up added about the
        #               color swatch ]
        select.add_command ( command=self.__helpSwatch,
            label="The color swatch" )

        #-- 3 --
        # [ select  :=  select with a cascade added for font help ]
        self.__cascadeFonts ( select )
# - - -   M e n u B a r . _ _ h e l p S w a t c h

    def __helpSwatch ( self ):
        """Help for the color swatch.
        """
        self.__dialog ( "Help: The color swatch",
            "The top right corner of the window displays your "
            "currently selected background color, with some text in "
            "your currently selected font displayed using the "
            "current text (foreground) color." )
# - - -   M e n u B a r . _ _ c a s c a d e F o n t s

    def __cascadeFonts ( self, menu ):
        """Add the font help cascade.

          [ menu is a Menu widget ->
              menu  :=  menu with help topics added on fonts ]
        """
        #-- 1 --
        # [ menu  :=  menu with a new cascade added
        #   select  :=  that cascade ]
        select  =  Menu ( menu )
        menu.add_cascade ( menu=select,
            label="Selecting a font" )
        #-- 2 --
        # [ select  :=  select with a pop-up added about font
        #               families ]
        select.add_command ( command=self.__helpFontFamily,
            label="Selecting a font family" )

        #-- 3 --
        # [ simile ]
        select.add_command ( command=self.__helpFontSize,
            label="Changing the font size" )

        #-- 4 --
        select.add_command ( command=self.__helpFontStyle,
            label="Changing font weight and slant" )
# - - -   M e n u B a r . _ _ h e l p F o n t F a m i l y

    def __helpFontFamily ( self ):
        """Help for font family selection.
        """
        self.__dialog ( "Help: Selecting a font family",
            "Under 'Click to select font family:' is a scrollable "
            "list containing the names of all the locally installed "
            "font families.  Click on any of these names to select "
            "that family." )
# - - -   M e n u B a r . _ _ h e l p F o n t S i z e

    def __helpFontSize ( self ):
        """Help for changing font size.
        """
        self.__dialog ( "Help: Changing the font size",
            "To change the size of the text, enter a number in the "
            "field labeled 'Size:'.  This number gives the font size "
            "in points.  You can also enter a negative number to "
            "specify a size in pixels.  After changing the size, "
            "either press the Enter key or click on the 'Set size' "
            "button. " )
# - - -   M e n u B a r . _ _ h e l p F o n t S t y l e

    def __helpFontStyle ( self ):
        """Popup for changing font weight and slant.
        """
        self.__dialog ( "Help: Changing the font weight and slant",
            "To change from normal to boldface type or back to normal, "
            "click the 'Bold' button."
            "\n\tTo change from normal to italic type or back to "
            "normal, click the 'Italic' button." )
# - - -   M e n u B a r . _ _ h e l p I m p o r t i n g

    def __helpImporting ( self ):
        """Pop-up help for importing color names.
        """
        self.__dialog ( "Help: Using colors in other applications",
            "To use one of the standard color names in an application, "
            "you can just use the name as it appears in the list of "
            "standard colors."
            "\n\tYou can also use the hexadecimal form of the color "
            "name that appears under #RRGGBB for either the background "
            "or text (foreground) color." )
# - - -   M e n u B a r . _ _ h e l p A u t h o r

    def __helpAuthor ( self ):
        """Pop-up for author credit.
        """
        self.__dialog ( "Help: Who made this tool?",
            "%s was written by John W. Shipman (john@nmt.edu) "
            "of the New Mexico Tech Computer Center, Socorro, NM "
            "87801."
            "\n\tThis is version %s."
            "\n\tFor documentation, see:\n%s" %
                (PROGRAM_NAME, EXTERNAL_VERSION, "http://www.nmt.edu/tcc/help/lang/python/examples/huey/ims/") )
# - - -   M e n u B a r . _ _ d i a l o g

    def __dialog ( self, title, text ):
        """Pop up a Dialog widget.

          [ (title is the frame title as a string) and
            (text is the help text as a multiline string containing
            newlines and tab characters) ->
              desktop  :=  desktop with a Dialog widget displaying
                  title and text ]
        """
        Dialog ( self, default=0, strings=('Dismiss',), bitmap='info',
                 title=title, text=text )

# - - - - -   c l a s s   N a m e P i c k e r

class NamePicker(Frame):
    """A compound widget for selecting a color by its name.

      Exports:
        NamePicker ( parent, callback=None ):
          [ (parent is a Frame) and
            (callback is a function or None) ->
              parent  :=  parent with a new NamePicker widget
                  added but not gridded, that calls callback
                  whenever a color is selected
              return that NamePicker widget ]

      Contained widgets:
        .__entryLabel: [ a Label widget that labels self.__entry ]
        .__entry:      [ an Entry widget for entering a color name ]
        .__pickLabel:  [ a Label widget that labels self.__pickList ]
        .__pickList:   [ a ScrolledList widget with color names ]

      Grid plan:  Vertical stacking.
      State/Invariants:
        .__parent:     [ as passed to constructor ]
        .__callback:   [ as passed to constructor ]
        .__entryVar:
          [ a StringVar control variable for self.__entry ]
    """
    NAME_WIDTH  =  20
# - - -   N a m e P i c k e r . _ _ i n i t _ _

    def __init__ ( self, parent, callback=None ):
        """Constructor for the NamePicker compound widget.
        """
        #-- 1 --
        # [ self  :=  self as a Frame ]
        Frame.__init__ ( self, parent )

        #-- 2 --
        self.__parent    =  parent
        self.__callback  =  None

        #-- 3 --
        # [ self  :=  self with all contained widgets created and
        #             gridded ]
        self.__createWidgets()

        #-- 4 --
        self.__callback  =  callback
# - - -   N a m e P i c k e r . _ _ c r e a t e W i d g e t s

    def __createWidgets ( self ):
        """Create all widgets."""

        #-- 1 --
        # [ self  :=  self with a new Label to label the color
        #             name entry field
        #   self.__entryLabel  :=  that Label ]
        self.__entryLabel  =  Label ( self,
            font=BUTTON_FONT, text="Type a color name:" )
        rowx  =  0
        self.__entryLabel.grid ( row=rowx, column=0, sticky=W )
        #-- 2 --
        # [ self  :=  self with a new Entry whose control variable
        #       is self.__entryVar, and which calls self.__callback
        #       when the user presses the Enter key ]
        self.__entryVar  =  StringVar()
        self.__entry  =  Entry ( self, relief=SUNKEN,
            font=BUTTON_FONT,
            width=self.NAME_WIDTH,
            textvariable=self.__entryVar )
        rowx  +=  1
        self.__entry.grid ( row=rowx, column=0, sticky=W )
        self.__entry.bind ( "<Key-Return>", self.__entryHandler )
        #-- 3 --
        # [ self  :=  self with a Label added for the color pick list
        #   self.__pickLabel  :=  that Label ]
        self.__pickLabel  =  Label ( self,
            font=BUTTON_FONT,
            text="Or click on a name:" )
        rowx  +=  1
        self.__pickLabel.grid ( row=rowx, column=0, sticky=W )

        #-- 4 --
        # [ self  :=  self with a PickList added containing
        #       the color pick list, with bindings that will call
        #       self.__callback when a color is clicked
        #   self.__pickList  :=  that ScrolledList ]
        self.__pickList  =  PickList ( self, self.__pickListHandler )
        rowx  +=  1
        self.__pickList.grid ( row=rowx, column=0, sticky=W )
# - - -   N a m e P i c k e r . _ _ e n t r y H a n d l e r

    def __entryHandler ( self, event ):
        """Handle the Enter key in the color name field.

          [ event is an Event from self.__entry ->
              if  self.__entryVar is a valid color name ->
                call self.__callback with a Color representing
                that name
              else ->
                pop up a Dialog informing the user that the
                color name is not valid ]
        """
        #-- 1 --
        # [ colorName  :=  text from self.__entryVar ]
        colorName  =  self.__entryVar.get()

        #-- 2 --
        # [ if  self.__entryVar is a valid color name ->
        #     call self.__callback with a Color representing
        #     that name
        #   else ->
        #     pop up a Dialog informing the user that the
        #     color name is not valid ]
        self.__setByName ( colorName )
# - - -   N a m e P i c k e r . _ _ s e t B y N a m e

    def __setByName ( self, colorName ):
        """Convert a color name to RGB values as a Color instance.

          [ colorName is a string ->
              if colorName is defined in either Tkinter or our
              color pick list ->
                call self.__callback and pass it that color as
                a Color instance
              else ->
                pop up a Dialog window complaining about the
                undefined color name ]
        """
        #-- 1 --
        # [ if (Tkinter recognizes (colorName) as a color) or
        #   (colorName) is defined in self.__pickList) ->
        #     rgb  :=  that color as a tuple (r, g, b) of values
        #              in [0,MAX_PARAM]
        #   else ->
        #     pop up a Dialog complaining about the undefined
        #     color name
        #     return ]
        try:
            rgb  =  self.winfo_rgb ( colorName )
        except:
            rgb  =  self.__pickList.lookupName ( colorName )
            if  not rgb:
                Dialog ( self, title="Message", bitmap="info",
                    default=0, strings=("Dismiss",),
                    text=("Color '%s' is undefined." % colorName) )
                return
        #-- 2 --
        # [ if self.__callback is not None ->
        #     call self.__callback with a Color made from rgb
        #   else -> I ]
        if  self.__callback is not None:
            self.__callback ( Color ( *rgb ) )
# - - -   N a m e P i c k e r . _ _ p i c k L i s t H a n d l e r

    def __pickListHandler ( self, color ):
        """Handler for self.__pickList.
        """
        if  self.__callback is not None:
            self.__callback ( color )

# - - - - -   c l a s s   P i c k L i s t

class PickList(Frame):
    """Compound widget for the color pick list.

      Exports:
        PickList ( parent, callback=None ):
          [ (parent is a Frame) and
            (callback is a function or None) ->
              parent  :=  parent with a new PickList widget added
                  but not gridded
              return that new widget ]
        .lookupName ( colorName ):
          [ colorName is a string ->
              if colorName matches a color in self's list,
              case-insensitive ->
                return the corresponding value as a Color instance
              else -> return None ]

      Contained widgets:
        .__scrolledList:
          [ a scrolledlist.ScrolledList containing self's color
            names ]

      Grid plan:  Only one widget
      State/Invariants:
        .__callback:    [ as passed to the constructor ]
        .__colorList:
          [ a list of Color instances such that self.__colorList[i]
            is the value of the color displayed in the (i)th line
            of self.__scrolledList, as a Color instance ]
        .__nameList:
          [ a list of color names such that self.__nameList[i]
            is the name of the color displayed in the (i)th line
            of self.__scrolledList ]

        .__colorMap:
          [ a dictionary whose keys are the color names in self,
            uppercased, and each value is a tuple (index, color,
            name) where index orders the colors in their original
            source order, color is a Color instance, and name is
            the color name as a string ]
    """
    COLOR_NAMES_FILE  =  "rgb.txt"
    PATHS_LIST  =  [ '/usr/share/X11', '/usr/lib/X11' ]
    NAME_WIDTH  =  20
    NAME_LINES  =  22
    DEFAULT_COLORS  =  [
      '\xFF\xFA\xFAsnow',               '\xF8\xF8\xFFGhostWhite',
      '\xF5\xF5\xF5WhiteSmoke',         '\xDC\xDC\xDCgainsboro',
      '\xFF\xFA\xF0FloralWhite',        '\xFD\xF5\xE6OldLace',
      '\xFA\xF0\xE6linen',              '\xFA\xEB\xD7AntiqueWhite',
      '\xFF\xEF\xD5PapayaWhip',         '\xFF\xEB\xCDBlanchedAlmond',
      '\xFF\xE4\xC4bisque',             '\xFF\xDA\xB9PeachPuff',
      '\xFF\xDE\xADNavajoWhite',        '\xFF\xE4\xB5moccasin',
      '\xFF\xF8\xDCcornsilk',           '\xFF\xFF\xF0ivory',
      '\xFF\xFA\xCDLemonChiffon',       '\xFF\xF5\xEEseashell',
      '\xF0\xFF\xF0honeydew',           '\xF5\xFF\xFAMintCream',
      '\xF0\xFF\xFFazure',              '\xF0\xF8\xFFAliceBlue',
      '\xE6\xE6\xFAlavender',           '\xFF\xF0\xF5LavenderBlush',
      '\xFF\xE4\xE1MistyRose',          '\xFF\xFF\xFFwhite',
      '\x00\x00\x00black',              '\x2F\x4F\x4FDarkSlateGray',
      '\x69\x69\x69DimGray',            '\x70\x80\x90SlateGray',
      '\x77\x88\x99LightSlateGray',     '\xBE\xBE\xBEgray',
      '\xD3\xD3\xD3LightGray',          '\x19\x19\x70MidnightBlue',
      '\x00\x00\x80navy',               '\x00\x00\x80NavyBlue',
      '\x64\x95\xEDCornflowerBlue',     '\x48\x3D\x8BDarkSlateBlue',
      '\x6A\x5A\xCDSlateBlue',          '\x7B\x68\xEEMediumSlateBlue',
      '\x84\x70\xFFLightSlateBlue',     '\x00\x00\xCDMediumBlue',
      '\x41\x69\xE1RoyalBlue',          '\x00\x00\xFFblue',
      '\x1E\x90\xFFDodgerBlue',         '\x00\xBF\xFFDeepSkyBlue',
      '\x87\xCE\xEBSkyBlue',            '\x87\xCE\xFALightSkyBlue',
      '\x46\x82\xB4SteelBlue',          '\xB0\xC4\xDELightSteelBlue',
      '\xAD\xD8\xE6LightBlue',          '\xB0\xE0\xE6PowderBlue',
      '\xAF\xEE\xEEPaleTurquoise',      '\x00\xCE\xD1DarkTurquoise',
      '\x48\xD1\xCCMediumTurquoise',    '\x40\xE0\xD0turquoise',
      '\x00\xFF\xFFcyan',               '\xE0\xFF\xFFLightCyan',
      '\x5F\x9E\xA0CadetBlue',          '\x66\xCD\xAAMediumAquamarine',
      '\x7F\xFF\xD4aquamarine',         '\x00\x64\x00DarkGreen',
      '\x55\x6B\x2FDarkOliveGreen',     '\x8F\xBC\x8FDarkSeaGreen',
      '\x2E\x8B\x57SeaGreen',           '\x3C\xB3\x71MediumSeaGreen',
      '\x20\xB2\xAALightSeaGreen',      '\x98\xFB\x98PaleGreen',
      '\x00\xFF\x7FSpringGreen',        '\x7C\xFC\x00LawnGreen',
      '\x00\xFF\x00green',              '\x7F\xFF\x00chartreuse',
      '\x00\xFA\x9AMediumSpringGreen',  '\xAD\xFF\x2FGreenYellow',
      '\x32\xCD\x32LimeGreen',          '\x9A\xCD\x32YellowGreen',
      '\x22\x8B\x22ForestGreen',        '\x6B\x8E\x23OliveDrab',
      '\xBD\xB7\x6BDarkKhaki',          '\xF0\xE6\x8Ckhaki',
      '\xEE\xE8\xAAPaleGoldenrod',
      '\xFA\xFA\xD2LightGoldenrodYellow',
      '\xFF\xFF\xE0LightYellow',        '\xFF\xFF\x00yellow',
      '\xFF\xD7\x00gold',               '\xEE\xDD\x82LightGoldenrod',
      '\xDA\xA5\x20goldenrod',          '\xB8\x86\x0BDarkGoldenrod',
      '\xBC\x8F\x8FRosyBrown',          '\xCD\x5C\x5CIndianRed',
      '\x8B\x45\x13SaddleBrown',        '\xA0\x52\x2Dsienna',
      '\xCD\x85\x3Fperu',               '\xDE\xB8\x87burlywood',
      '\xF5\xF5\xDCbeige',              '\xF5\xDE\xB3wheat',
      '\xF4\xA4\x60SandyBrown',         '\xD2\xB4\x8Ctan',
      '\xD2\x69\x1Echocolate',          '\xB2\x22\x22firebrick',
      '\xA5\x2A\x2Abrown',              '\xE9\x96\x7ADarkSalmon',
      '\xFA\x80\x72salmon',             '\xFF\xA0\x7ALightSalmon',
      '\xFF\xA5\x00orange',             '\xFF\x8C\x00DarkOrange',
      '\xFF\x7F\x50coral',              '\xF0\x80\x80LightCoral',
      '\xFF\x63\x47tomato',             '\xFF\x45\x00OrangeRed',
      '\xFF\x00\x00red',                '\xFF\x69\xB4HotPink',
      '\xFF\x14\x93DeepPink',           '\xFF\xC0\xCBpink',
      '\xFF\xB6\xC1LightPink',          '\xDB\x70\x93PaleVioletRed',
      '\xB0\x30\x60maroon',             '\xC7\x15\x85MediumVioletRed',
      '\xD0\x20\x90VioletRed',          '\xFF\x00\xFFmagenta',
      '\xEE\x82\xEEviolet',             '\xDD\xA0\xDDplum',
      '\xDA\x70\xD6orchid',             '\xBA\x55\xD3MediumOrchid',
      '\x99\x32\xCCDarkOrchid',         '\x94\x00\xD3DarkViolet',
      '\x8A\x2B\xE2BlueViolet',         '\xA0\x20\xF0purple',
      '\x93\x70\xDBMediumPurple',       '\xD8\xBF\xD8thistle',
      '\xFF\xFA\xFAsnow1',              '\xEE\xE9\xE9snow2',
      '\xCD\xC9\xC9snow3',              '\x8B\x89\x89snow4',
      '\xFF\xF5\xEEseashell1',          '\xEE\xE5\xDEseashell2',
      '\xCD\xC5\xBFseashell3',          '\x8B\x86\x82seashell4',
      '\xFF\xEF\xDBAntiqueWhite1',      '\xEE\xDF\xCCAntiqueWhite2',
      '\xCD\xC0\xB0AntiqueWhite3',      '\x8B\x83\x78AntiqueWhite4',
      '\xFF\xE4\xC4bisque1',            '\xEE\xD5\xB7bisque2',
      '\xCD\xB7\x9Ebisque3',            '\x8B\x7D\x6Bbisque4',
      '\xFF\xDA\xB9PeachPuff1',         '\xEE\xCB\xADPeachPuff2',
      '\xCD\xAF\x95PeachPuff3',         '\x8B\x77\x65PeachPuff4',
      '\xFF\xDE\xADNavajoWhite1',       '\xEE\xCF\xA1NavajoWhite2',
      '\xCD\xB3\x8BNavajoWhite3',       '\x8B\x79\x5ENavajoWhite4',
      '\xFF\xFA\xCDLemonChiffon1',      '\xEE\xE9\xBFLemonChiffon2',
      '\xCD\xC9\xA5LemonChiffon3',      '\x8B\x89\x70LemonChiffon4',
      '\xFF\xF8\xDCcornsilk1',          '\xEE\xE8\xCDcornsilk2',
      '\xCD\xC8\xB1cornsilk3',          '\x8B\x88\x78cornsilk4',
      '\xFF\xFF\xF0ivory1',             '\xEE\xEE\xE0ivory2',
      '\xCD\xCD\xC1ivory3',             '\x8B\x8B\x83ivory4',
      '\xF0\xFF\xF0honeydew1',          '\xE0\xEE\xE0honeydew2',
      '\xC1\xCD\xC1honeydew3',          '\x83\x8B\x83honeydew4',
      '\xFF\xF0\xF5LavenderBlush1',     '\xEE\xE0\xE5LavenderBlush2',
      '\xCD\xC1\xC5LavenderBlush3',     '\x8B\x83\x86LavenderBlush4',
      '\xFF\xE4\xE1MistyRose1',         '\xEE\xD5\xD2MistyRose2',
      '\xCD\xB7\xB5MistyRose3',         '\x8B\x7D\x7BMistyRose4',
      '\xF0\xFF\xFFazure1',             '\xE0\xEE\xEEazure2',
      '\xC1\xCD\xCDazure3',             '\x83\x8B\x8Bazure4',
      '\x83\x6F\xFFSlateBlue1',         '\x7A\x67\xEESlateBlue2',
      '\x69\x59\xCDSlateBlue3',         '\x47\x3C\x8BSlateBlue4',
      '\x48\x76\xFFRoyalBlue1',         '\x43\x6E\xEERoyalBlue2',
      '\x3A\x5F\xCDRoyalBlue3',         '\x27\x40\x8BRoyalBlue4',
      '\x00\x00\xFFblue1',              '\x00\x00\xEEblue2',
      '\x00\x00\xCDblue3',              '\x00\x00\x8Bblue4',
      '\x1E\x90\xFFDodgerBlue1',        '\x1C\x86\xEEDodgerBlue2',
      '\x18\x74\xCDDodgerBlue3',        '\x10\x4E\x8BDodgerBlue4',
      '\x63\xB8\xFFSteelBlue1',         '\x5C\xAC\xEESteelBlue2',
      '\x4F\x94\xCDSteelBlue3',         '\x36\x64\x8BSteelBlue4',
      '\x00\xBF\xFFDeepSkyBlue1',       '\x00\xB2\xEEDeepSkyBlue2',
      '\x00\x9A\xCDDeepSkyBlue3',       '\x00\x68\x8BDeepSkyBlue4',
      '\x87\xCE\xFFSkyBlue1',           '\x7E\xC0\xEESkyBlue2',
      '\x6C\xA6\xCDSkyBlue3',           '\x4A\x70\x8BSkyBlue4',
      '\xB0\xE2\xFFLightSkyBlue1',      '\xA4\xD3\xEELightSkyBlue2',
      '\x8D\xB6\xCDLightSkyBlue3',      '\x60\x7B\x8BLightSkyBlue4',
      '\xC6\xE2\xFFSlateGray1',         '\xB9\xD3\xEESlateGray2',
      '\x9F\xB6\xCDSlateGray3',         '\x6C\x7B\x8BSlateGray4',
      '\xCA\xE1\xFFLightSteelBlue1',    '\xBC\xD2\xEELightSteelBlue2',
      '\xA2\xB5\xCDLightSteelBlue3',    '\x6E\x7B\x8BLightSteelBlue4',
      '\xBF\xEF\xFFLightBlue1',         '\xB2\xDF\xEELightBlue2',
      '\x9A\xC0\xCDLightBlue3',         '\x68\x83\x8BLightBlue4',
      '\xE0\xFF\xFFLightCyan1',         '\xD1\xEE\xEELightCyan2',
      '\xB4\xCD\xCDLightCyan3',         '\x7A\x8B\x8BLightCyan4',
      '\xBB\xFF\xFFPaleTurquoise1',     '\xAE\xEE\xEEPaleTurquoise2',
      '\x96\xCD\xCDPaleTurquoise3',     '\x66\x8B\x8BPaleTurquoise4',
      '\x98\xF5\xFFCadetBlue1',         '\x8E\xE5\xEECadetBlue2',
      '\x7A\xC5\xCDCadetBlue3',         '\x53\x86\x8BCadetBlue4',
      '\x00\xF5\xFFturquoise1',         '\x00\xE5\xEEturquoise2',
      '\x00\xC5\xCDturquoise3',         '\x00\x86\x8Bturquoise4',
      '\x00\xFF\xFFcyan1',              '\x00\xEE\xEEcyan2',
      '\x00\xCD\xCDcyan3',              '\x00\x8B\x8Bcyan4',
      '\x97\xFF\xFFDarkSlateGray1',     '\x8D\xEE\xEEDarkSlateGray2',
      '\x79\xCD\xCDDarkSlateGray3',     '\x52\x8B\x8BDarkSlateGray4',
      '\x7F\xFF\xD4aquamarine1',        '\x76\xEE\xC6aquamarine2',
      '\x66\xCD\xAAaquamarine3',        '\x45\x8B\x74aquamarine4',
      '\xC1\xFF\xC1DarkSeaGreen1',      '\xB4\xEE\xB4DarkSeaGreen2',
      '\x9B\xCD\x9BDarkSeaGreen3',      '\x69\x8B\x69DarkSeaGreen4',
      '\x54\xFF\x9FSeaGreen1',          '\x4E\xEE\x94SeaGreen2',
      '\x43\xCD\x80SeaGreen3',          '\x2E\x8B\x57SeaGreen4',
      '\x9A\xFF\x9APaleGreen1',         '\x90\xEE\x90PaleGreen2',
      '\x7C\xCD\x7CPaleGreen3',         '\x54\x8B\x54PaleGreen4',
      '\x00\xFF\x7FSpringGreen1',       '\x00\xEE\x76SpringGreen2',
      '\x00\xCD\x66SpringGreen3',       '\x00\x8B\x45SpringGreen4',
      '\x00\xFF\x00green1',             '\x00\xEE\x00green2',
      '\x00\xCD\x00green3',             '\x00\x8B\x00green4',
      '\x7F\xFF\x00chartreuse1',        '\x76\xEE\x00chartreuse2',
      '\x66\xCD\x00chartreuse3',        '\x45\x8B\x00chartreuse4',
      '\xC0\xFF\x3EOliveDrab1',         '\xB3\xEE\x3AOliveDrab2',
      '\x9A\xCD\x32OliveDrab3',         '\x69\x8B\x22OliveDrab4',
      '\xCA\xFF\x70DarkOliveGreen1',    '\xBC\xEE\x68DarkOliveGreen2',
      '\xA2\xCD\x5ADarkOliveGreen3',    '\x6E\x8B\x3DDarkOliveGreen4',
      '\xFF\xF6\x8Fkhaki1',             '\xEE\xE6\x85khaki2',
      '\xCD\xC6\x73khaki3',             '\x8B\x86\x4Ekhaki4',
      '\xFF\xEC\x8BLightGoldenrod1',    '\xEE\xDC\x82LightGoldenrod2',
      '\xCD\xBE\x70LightGoldenrod3',    '\x8B\x81\x4CLightGoldenrod4',
      '\xFF\xFF\xE0LightYellow1',       '\xEE\xEE\xD1LightYellow2',
      '\xCD\xCD\xB4LightYellow3',       '\x8B\x8B\x7ALightYellow4',
      '\xFF\xFF\x00yellow1',            '\xEE\xEE\x00yellow2',
      '\xCD\xCD\x00yellow3',            '\x8B\x8B\x00yellow4',
      '\xFF\xD7\x00gold1',              '\xEE\xC9\x00gold2',
      '\xCD\xAD\x00gold3',              '\x8B\x75\x00gold4',
      '\xFF\xC1\x25goldenrod1',         '\xEE\xB4\x22goldenrod2',
      '\xCD\x9B\x1Dgoldenrod3',         '\x8B\x69\x14goldenrod4',
      '\xFF\xB9\x0FDarkGoldenrod1',     '\xEE\xAD\x0EDarkGoldenrod2',
      '\xCD\x95\x0CDarkGoldenrod3',     '\x8B\x65\x08DarkGoldenrod4',
      '\xFF\xC1\xC1RosyBrown1',         '\xEE\xB4\xB4RosyBrown2',
      '\xCD\x9B\x9BRosyBrown3',         '\x8B\x69\x69RosyBrown4',
      '\xFF\x6A\x6AIndianRed1',         '\xEE\x63\x63IndianRed2',
      '\xCD\x55\x55IndianRed3',         '\x8B\x3A\x3AIndianRed4',
      '\xFF\x82\x47sienna1',            '\xEE\x79\x42sienna2',
      '\xCD\x68\x39sienna3',            '\x8B\x47\x26sienna4',
      '\xFF\xD3\x9Bburlywood1',         '\xEE\xC5\x91burlywood2',
      '\xCD\xAA\x7Dburlywood3',         '\x8B\x73\x55burlywood4',
      '\xFF\xE7\xBAwheat1',             '\xEE\xD8\xAEwheat2',
      '\xCD\xBA\x96wheat3',             '\x8B\x7E\x66wheat4',
      '\xFF\xA5\x4Ftan1',               '\xEE\x9A\x49tan2',
      '\xCD\x85\x3Ftan3',               '\x8B\x5A\x2Btan4',
      '\xFF\x7F\x24chocolate1',         '\xEE\x76\x21chocolate2',
      '\xCD\x66\x1Dchocolate3',         '\x8B\x45\x13chocolate4',
      '\xFF\x30\x30firebrick1',         '\xEE\x2C\x2Cfirebrick2',
      '\xCD\x26\x26firebrick3',         '\x8B\x1A\x1Afirebrick4',
      '\xFF\x40\x40brown1',             '\xEE\x3B\x3Bbrown2',
      '\xCD\x33\x33brown3',             '\x8B\x23\x23brown4',
      '\xFF\x8C\x69salmon1',            '\xEE\x82\x62salmon2',
      '\xCD\x70\x54salmon3',            '\x8B\x4C\x39salmon4',
      '\xFF\xA0\x7ALightSalmon1',       '\xEE\x95\x72LightSalmon2',
      '\xCD\x81\x62LightSalmon3',       '\x8B\x57\x42LightSalmon4',
      '\xFF\xA5\x00orange1',            '\xEE\x9A\x00orange2',
      '\xCD\x85\x00orange3',            '\x8B\x5A\x00orange4',
      '\xFF\x7F\x00DarkOrange1',        '\xEE\x76\x00DarkOrange2',
      '\xCD\x66\x00DarkOrange3',        '\x8B\x45\x00DarkOrange4',
      '\xFF\x72\x56coral1',             '\xEE\x6A\x50coral2',
      '\xCD\x5B\x45coral3',             '\x8B\x3E\x2Fcoral4',
      '\xFF\x63\x47tomato1',            '\xEE\x5C\x42tomato2',
      '\xCD\x4F\x39tomato3',            '\x8B\x36\x26tomato4',
      '\xFF\x45\x00OrangeRed1',         '\xEE\x40\x00OrangeRed2',
      '\xCD\x37\x00OrangeRed3',         '\x8B\x25\x00OrangeRed4',
      '\xFF\x00\x00red1',               '\xEE\x00\x00red2',
      '\xCD\x00\x00red3',               '\x8B\x00\x00red4',
      '\xFF\x14\x93DeepPink1',          '\xEE\x12\x89DeepPink2',
      '\xCD\x10\x76DeepPink3',          '\x8B\x0A\x50DeepPink4',
      '\xFF\x6E\xB4HotPink1',           '\xEE\x6A\xA7HotPink2',
      '\xCD\x60\x90HotPink3',           '\x8B\x3A\x62HotPink4',
      '\xFF\xB5\xC5pink1',              '\xEE\xA9\xB8pink2',
      '\xCD\x91\x9Epink3',              '\x8B\x63\x6Cpink4',
      '\xFF\xAE\xB9LightPink1',         '\xEE\xA2\xADLightPink2',
      '\xCD\x8C\x95LightPink3',         '\x8B\x5F\x65LightPink4',
      '\xFF\x82\xABPaleVioletRed1',     '\xEE\x79\x9FPaleVioletRed2',
      '\xCD\x68\x89PaleVioletRed3',     '\x8B\x47\x5DPaleVioletRed4',
      '\xFF\x34\xB3maroon1',            '\xEE\x30\xA7maroon2',
      '\xCD\x29\x90maroon3',            '\x8B\x1C\x62maroon4',
      '\xFF\x3E\x96VioletRed1',         '\xEE\x3A\x8CVioletRed2',
      '\xCD\x32\x78VioletRed3',         '\x8B\x22\x52VioletRed4',
      '\xFF\x00\xFFmagenta1',           '\xEE\x00\xEEmagenta2',
      '\xCD\x00\xCDmagenta3',           '\x8B\x00\x8Bmagenta4',
      '\xFF\x83\xFAorchid1',            '\xEE\x7A\xE9orchid2',
      '\xCD\x69\xC9orchid3',            '\x8B\x47\x89orchid4',
      '\xFF\xBB\xFFplum1',              '\xEE\xAE\xEEplum2',
      '\xCD\x96\xCDplum3',              '\x8B\x66\x8Bplum4',
      '\xE0\x66\xFFMediumOrchid1',      '\xD1\x5F\xEEMediumOrchid2',
      '\xB4\x52\xCDMediumOrchid3',      '\x7A\x37\x8BMediumOrchid4',
      '\xBF\x3E\xFFDarkOrchid1',        '\xB2\x3A\xEEDarkOrchid2',
      '\x9A\x32\xCDDarkOrchid3',        '\x68\x22\x8BDarkOrchid4',
      '\x9B\x30\xFFpurple1',            '\x91\x2C\xEEpurple2',
      '\x7D\x26\xCDpurple3',            '\x55\x1A\x8Bpurple4',
      '\xAB\x82\xFFMediumPurple1',      '\x9F\x79\xEEMediumPurple2',
      '\x89\x68\xCDMediumPurple3',      '\x5D\x47\x8BMediumPurple4',
      '\xFF\xE1\xFFthistle1',           '\xEE\xD2\xEEthistle2',
      '\xCD\xB5\xCDthistle3',           '\x8B\x7B\x8Bthistle4',
      '\x00\x00\x00gray0',              '\x03\x03\x03gray1',
      '\x05\x05\x05gray2',              '\x08\x08\x08gray3',
      '\x0A\x0A\x0Agray4',              '\x0D\x0D\x0Dgray5',
      '\x0F\x0F\x0Fgray6',              '\x12\x12\x12gray7',
      '\x14\x14\x14gray8',              '\x17\x17\x17gray9',
      '\x1A\x1A\x1Agray10',             '\x1C\x1C\x1Cgray11',
      '\x1F\x1F\x1Fgray12',             '\x21\x21\x21gray13',
      '\x24\x24\x24gray14',             '\x26\x26\x26gray15',
      '\x29\x29\x29gray16',             '\x2B\x2B\x2Bgray17',
      '\x2E\x2E\x2Egray18',             '\x30\x30\x30gray19',
      '\x33\x33\x33gray20',             '\x36\x36\x36gray21',
      '\x38\x38\x38gray22',             '\x3B\x3B\x3Bgray23',
      '\x3D\x3D\x3Dgray24',             '\x40\x40\x40gray25',
      '\x42\x42\x42gray26',             '\x45\x45\x45gray27',
      '\x47\x47\x47gray28',             '\x4A\x4A\x4Agray29',
      '\x4D\x4D\x4Dgray30',             '\x4F\x4F\x4Fgray31',
      '\x52\x52\x52gray32',             '\x54\x54\x54gray33',
      '\x57\x57\x57gray34',             '\x59\x59\x59gray35',
      '\x5C\x5C\x5Cgray36',             '\x5E\x5E\x5Egray37',
      '\x61\x61\x61gray38',             '\x63\x63\x63gray39',
      '\x66\x66\x66gray40',             '\x69\x69\x69gray41',
      '\x6B\x6B\x6Bgray42',             '\x6E\x6E\x6Egray43',
      '\x70\x70\x70gray44',             '\x73\x73\x73gray45',
      '\x75\x75\x75gray46',             '\x78\x78\x78gray47',
      '\x7A\x7A\x7Agray48',             '\x7D\x7D\x7Dgray49',
      '\x7F\x7F\x7Fgray50',             '\x82\x82\x82gray51',
      '\x85\x85\x85gray52',             '\x87\x87\x87gray53',
      '\x8A\x8A\x8Agray54',             '\x8C\x8C\x8Cgray55',
      '\x8F\x8F\x8Fgray56',             '\x91\x91\x91gray57',
      '\x94\x94\x94gray58',             '\x96\x96\x96gray59',
      '\x99\x99\x99gray60',             '\x9C\x9C\x9Cgray61',
      '\x9E\x9E\x9Egray62',             '\xA1\xA1\xA1gray63',
      '\xA3\xA3\xA3gray64',             '\xA6\xA6\xA6gray65',
      '\xA8\xA8\xA8gray66',             '\xAB\xAB\xABgray67',
      '\xAD\xAD\xADgray68',             '\xB0\xB0\xB0gray69',
      '\xB3\xB3\xB3gray70',             '\xB5\xB5\xB5gray71',
      '\xB8\xB8\xB8gray72',             '\xBA\xBA\xBAgray73',
      '\xBD\xBD\xBDgray74',             '\xBF\xBF\xBFgray75',
      '\xC2\xC2\xC2gray76',             '\xC4\xC4\xC4gray77',
      '\xC7\xC7\xC7gray78',             '\xC9\xC9\xC9gray79',
      '\xCC\xCC\xCCgray80',             '\xCF\xCF\xCFgray81',
      '\xD1\xD1\xD1gray82',             '\xD4\xD4\xD4gray83',
      '\xD6\xD6\xD6gray84',             '\xD9\xD9\xD9gray85',
      '\xDB\xDB\xDBgray86',             '\xDE\xDE\xDEgray87',
      '\xE0\xE0\xE0gray88',             '\xE3\xE3\xE3gray89',
      '\xE5\xE5\xE5gray90',             '\xE8\xE8\xE8gray91',
      '\xEB\xEB\xEBgray92',             '\xED\xED\xEDgray93',
      '\xF0\xF0\xF0gray94',             '\xF2\xF2\xF2gray95',
      '\xF5\xF5\xF5gray96',             '\xF7\xF7\xF7gray97',
      '\xFA\xFA\xFAgray98',             '\xFC\xFC\xFCgray99',
      '\xFF\xFF\xFFgray100',            '\xA9\xA9\xA9DarkGray',
      '\x00\x00\x8BDarkBlue',           '\x00\x8B\x8BDarkCyan',
      '\x8B\x00\x8BDarkMagenta',        '\x8B\x00\x00DarkRed',
      '\x90\xEE\x90LightGreen' ]
# - - -   P i c k L i s t . l o o k u p N a m e

    def lookupName ( self, colorName ):
        """Look up a color name.
        """
        #-- 1 --
        # [ colorKey  :=  colorName, uppercased ]
        colorKey  =  colorName.upper()

        #-- 2 --
        # [ if  colorKey is a key in self.__colorMap ->
        #     return the corresponding value
        #   else ->
        #     return None ]
        try:
            index, color, name  =  self.__colorMap[colorKey]
            return  color
        except KeyError:
            return None
# - - -   P i c k L i s t . _ _ i n i t _ _

    def __init__ ( self, parent, callback=None ):
        """Constructor for the color name PickList."""
        #-- 1 --
        # [ parent  :=  parent with a new Frame added
        #   self    :=  that Frame ]
        Frame.__init__ ( self, parent )
        #-- 2 --
        self.__colorList  =  []
        self.__nameList   =  []
        self.__colorMap   =  {}
        self.__callback   =  None
        #-- 3 --
        # [ self  :=  self with a new ScrolledList widget added
        #             and gridded
        #   self.__scrolledList  :=  that widget ]
        self.__scrolledList  =  ScrolledList ( self,
            width=self.NAME_WIDTH, height=self.NAME_LINES,
            callback=self.__pickHandler )
        self.__scrolledList.listbox["font"]  =  BUTTON_FONT
        self.__scrolledList.grid ( row=0, column=0 )
        #-- 4 --
        # [ self.__scrolledList  :=  self.__scrolledList populated
        #       with non-redundant color names from the standard
        #       file if found, defaulting to an internal color list
        #   self.__colorMap   +:=  as invariant
        #   self.__colorList  +:=  as invariant
        #   self.__nameList   +:=  as invariant ]
        self.__addColors()
        #-- 5 --
        self.__callback   =  callback
# - - -   P i c k L i s t . _ _ a d d C o l o r s

    def __addColors ( self ):
        """Populate the color set

          [ if a readable, valid self.COLOR_NAMES_FILE exists in
            one of the directories named in self.PATHS_LIST ->
              self.__scrolledList   :=  self.pickList with the color
                  names added from that file in the same order
              self.__colorMap   :=  as invariant from that file
              self.__colorList  :=  as invariant from that file
              self.__nameList   :=  as invariant from that file
            else ->
              self.__scrolledList   :=  self.pickList with the color
                  names added from the internal default list
              self.__colorMap   :=  as invariant from that list
              self.__colorList  :=  as invariant from that list
              self.__nameList   :=  as invariant from that file ]
        """
        #-- 1 --
        # [ if self.COLOR_NAMES_FILE names a readable, valid
        #   rgb.txt file in one of the directories named in
        #   self.PATHS_LIST ->
        #       self.__colorMap  :=  as invariant from that file
        #   else ->
        #       self.__colorMap  :=  an empty dictionary ]
        self.__findColorsFile()
        #-- 2 --
        # [ if self.__colorMap is empty ->
        #     self.__colorMap  +:=  as invariant from self.DEFAULT_COLORS
        #   else -> I ]
        if  len(self.__colorMap) == 0:
            self.__useDefaultColors()
        #-- 3 --
        # [ self.__colorMap  :=  self.__colorMap with redundant colors
        #       removed ]
        self.__cleanColorMap()
        #-- 4 --
        # [ valueList  :=  values from self.__colorMap, sorted ]
        valueList  =  self.__colorMap.values()
        valueList.sort()

        #-- 5 --
        # [ valueList is a list of tuples (index, color, name) ->
        #     self.__scrolledList  +:=  names from valueList in the
        #                               same order
        #     self.__colorList  +:=  colors from valueList in the
        #                           same order ]
        for index, color, name in valueList:
            self.__scrolledList.append ( name )
            self.__nameList.append ( name )
            self.__colorList.append ( color )
# - - -   P i c k L i s t . _ _ f i n d C o l o r s F i l e

    def __findColorsFile ( self ):
        """Try to find and read the standard colors file.

          [ if self.COLOR_NAMES_FILE names a readable, valid
            rgb.txt file in one of the directories named in
            self.PATHS_LIST ->
                self.__colorMap  :=  as invariant from that file
            else ->
                self.__colorMap  :=  an empty dictionary ]
        """

        #-- 1 --
        inFile  =  None

        #-- 2 --
        # [ if self.PATHS_LIST names a directory that contains
        #   a readable file named self._COLOR_NAMES_FILE ->
        #     inFile  :=  that file opened for reading
        #   else -> I ]
        for  dir in self.PATHS_LIST:
            fileName  =  os.path.join ( dir, self.COLOR_NAMES_FILE )
            try:
                inFile  =  open ( fileName )
                break
            except IOError:
                pass
        #-- 2 --
        if inFile is None:
            self.__colorMap  = {}
            return
        #-- 3 --
        # [ if inFile is a valid colors file ->
        #     self.__colorMap  :=  as invariant from that file
        #   else ->
        #     self.__colorMap  :=  an empty dictionary ]
        self.__readColorsFile ( inFile )
# - - -   P i c k L i s t . _ _ r e a d C o l o r s F i l e

    def __readColorsFile ( self, inFile ):
        """Try to read the file of standard colors.

          [ inFile is a readable file ->
              if inFile is a valid colors file ->
                self.__colorMap  :=  as invariant from that file
              else ->
                self.__colorMap  :=  an dictionary ]
        """
        #-- 1 --
        # [ lineList  :=  the lines from inFile as a list of strings ]
        lineList  =  inFile.readlines()
        #-- 2 --
        # [ if all the non-comment lines in inFile are valid ->
        #     self.__colorMap  :=  as invariant from those lines
        #   else ->
        #     self.__colorMap  :=  an empty list ]
        try:
            for  index in range ( len ( lineList ) ):
                #-- 2 body --
                # [ if lineList[index] is a comment -> I
                #   else if lineList[index] is a valid color line ->
                #     self.__colorMap  +:=  an entry mapping the
                #         uppercased color name |-> a tuple (index,
                #         the color from that line as a Color instance),
                #         the name from that line)
                #   else ->
                #     self.__colorMap  :=  {}
                #     return ]
                self.__readColorLine ( index, lineList[index] )
        except IOError:
            self.__colorMap  =  {}
# - - -   P i c k L i s t . _ _ r e a d C o l o r L i n e

    def __readColorLine ( self, index, rawLine ):
        """Process one line from the rgb.txt file.

          [ (index is a nonnegative integer) and
            (rawLine is a string) ->
              if rawLine is a comment -> I
              else if rawLine is valid ->
                  self.__colorMap  +:=  an entry mapping the
                      uppercased color name |-> a tuple (index,
                      the color from that line as a Color instance),
                      the name from that line)
              else -> raise IOError ]
        """
        #-- 1 --
        # [ line  :=  rawLine with trailing whitespace removed ]
        line  =  rawLine.rstrip()
        #-- 2 --
        if  line.startswith('!'):
             return
        #-- 3 --
        # [ fieldList  :=  line split on whitespace regions, but never
        #                  more than the first four ]
        fieldList  =  line.split ( None, 3 )
        #-- 4 --
        if len(fieldList) < 4:
            raise IOError, "rgb.txt lines must have four fields"
        else:
            colorName  =  fieldList[-1]

        #-- 5 --
        # [ if the first three elements of fieldList can be
        #   converted to integers in [0,255] ->
        #       red8    :=  int(fieldList[0])
        #       green8  :=  int(fieldList[1])
        #       blue8   :=  int(fieldList[2])
        #   else -> raise IOError ]
        red8    =  self.__convert8 ( fieldList[0] )
        green8  =  self.__convert8 ( fieldList[1] )
        blue8   =  self.__convert8 ( fieldList[2] )
        #-- 6 --
        # [ color  :=  a new Color instance made from red8, green8,
        #              and blue8, each shifted left 8 bits ]
        color  =  Color ( red8<<8, green8<<8,
                          blue8<<8 )
        #-- 7 --
        colorKey  =  colorName.upper()
        colorTuple  =  (index, color, colorName)
        self.__colorMap [ colorKey ]  =  colorTuple
# - - -   P i c k L i s t . _ _ c o n v e r t 8

    def __convert8 ( self, s ):
        """Convert a string to an 8-bit number.

          [ if s is the string representation of a number in
            [0,255] ->
              return s as an integer
            else -> raise IOError ]
        """
        #-- 1 --
        # [ if s can be converted to an integer ->
        #     result  :=  s converted to an integer
        #   else -> raise IOError ]
        try:
            result  =  int ( s )
        except ValueError:
            raise IOError, "Bad color value: '%s'" % s

        #-- 2 --
        return result
# - - -   P i c k L i s t . _ _ u s e D e f a u l t C o l o r s

    def __useDefaultColors ( self ):
        """Set up self's colors from the default list.

          [ self.__colorMap  +:=  as invariant from
                                  self.DEFAULT_COLORS ]
        """
        #-- 1 --
        for  index in range ( len ( self.DEFAULT_COLORS ) ):
            # [ self.DEFAULT_COLORS[index] is a string with the
            #   8-bit red, green, and blue values followed by the
            #   color name ->
            #     self.__colorMap  +:=  an entry mapping the uppercased
            #         color name |-> a tuple (index, a Color instance
            #         made from those color values, the color name) ]
            #-- 1.1 --
            colorString  =  self.DEFAULT_COLORS [ index ]
            red    =  ord ( colorString[0] ) <<8
            green  =  ord ( colorString[1] ) <<8
            blue   =  ord ( colorString[2] ) <<8
            color  =  Color ( red, green, blue )
            colorName  =  colorString[3:]

            #-- 1.2 --
            colorKey  =  colorName.upper()
            colorTuple  =  (index, color, colorName)

            #-- 1.3 --
            self.__colorMap [ colorKey ]  =  colorTuple
# - - -   P i c k L i s t . _ _ c l e a n C o l o r M a p

    def __cleanColorMap ( self ):
        """Remove redundant colors from the color map.

          [ self.__colorMap  :=  self.__colorMap with redundant colors
                removed ]
        """

        #-- 1 --
        # [ nameList  :=  keys of self.__colorMap ]
        nameList  =  self.__colorMap.keys()
        #-- 2 --
        # [ self.__colorMap  :=  self.__colorMap with names removed
        #      when those names are less preferred alternatives to
        #      names in nameList ]
        for  colorName in nameList:
            self.__nameCleaner ( colorName )
# - - -   P i c k L i s t . _ _ n a m e C l e a n e r

    def  __nameCleaner ( self, colorName ):
        """Remove any redundant names dominated by colorName.

          [ colorName is a key in self.__colorMap ->
              self.__colorMap  :=  self.__colorMap with any entries
                  removed whose keys are less-preferred alternatives
                  to colorName ]
        """
        #-- 1 --
        # [ if colorName is a key in self.__colorMap ->
        #     origName  :=  corresponding value's color
        #   else -> return ]
        try:
            origName  =  self.__colorMap [ colorName.upper() ] [ 2 ]
        except KeyError:
            return
        #-- 2 --
        # [ anglican  :=  colorName with 'gray' -> 'grey' ]
        anglican  =  self.__anglicize ( origName )

        #-- 2 --
        # [ if self.__colorMap has a key (anglican) ->
        #     self.__colorMap  :=  self.__colorMap with that key's
        #                          entry removed
        #   else -> I ]
        self.__purgeName ( origName, anglican )

        #-- 3 --
        # [ if self.__colorMap has a key self.__lowerize(colorName) ->
        #     self.__colorMap  :=  self.__colorMap with that key's
        #                          entry removed
        #   else -> I ]
        self.__purgeName ( origName, self.__lowerize ( origName ) )

        #-- 4 --
        # [ if self.__colorMap has a key self.__lowerize(anglican) ->
        #     self.__colorMap  :=  self.__colorMap with that key's
        #                          entry removed
        #   else -> I ]
        self.__purgeName ( origName, self.__lowerize ( anglican ) )
# - - -   P i c k L i s t . _ _ a n g l i c i z e

    def  __anglicize ( self, name ):
        """Anglicize a name.

          [ name is a string ->
              if name contains "gray" ->
                  return name with the first occurrence of "gray"
                  replaced by "grey"
              else -> return name ]
        """
        where  =  name.find ( "gray" )

        if  where >= 0:
            return name[:where] + "grey" + name[where+4:]
        else:
            where  =  name.find ( "Gray" )
            if  where >= 0:
                return name[:where] + "Grey" + name[where+4:]
            else:
                return name
# - - -   P i c k L i s t . _ _ l o w e r i z e

    def __lowerize ( self, name ):
        """Convert an intercapitalized color name to lowercase form.

          [ name is a string ->
              return name with all letters lowercased, and single
              spaces inserted at each lowercase->uppercase transition ]
        """
        #-- 1 --
        # [ letters  :=  a list of the characters in name ]
        letters  =  list ( name )

        #-- 2 --
        # [ letters  :=  letters with a space prefixed to any
        #       uppercase letter preceded by a lowercase letter ]
        for  i in range ( 1, len ( letters ) ):
            if  ( letters[i-1].islower() and
                  letters[i].isupper() ):
                letters[i]  =  " " + letters[i]

        #-- 3 --
        return  "".join ( letters )
# - - -   P i c k L i s t . _ _ p u r g e N a m e

    def __purgeName ( self, goodName, badName ):
        """If badName is redundant for goodName, remove it.

          [ (goodName is a color name in self.__colorMap) and
            (badName is a string) ->
              if  goodName == badName ->
                I
                else if  badName is a color name in self.__colorMap
                that is the same color as self.__colorMap[goodName] ->
                self.__colorMap  :=  self.__colorName with its
                    entry for badName removed
              else -> I ]              
        """
        #-- 1 --
        if  goodName == badName:
            return
        #-- 2 --
        # [ if  badName is a key in self.__colorMap ->
        #     goodColor  :=  self's color for goodName
        #     badColor   :=  self's color for badName
        #   else ->
        #     return ]
        badColor  =  self.lookupName ( badName )
        if  badColor is None:
            return
        else:
            goodColor  =  self.lookupName ( goodName )
        #-- 3 --
        # [ if  badColor == goodColor ->
        #     self.__colorMap  :=  self.__colorMap with the entry
        #         for badColor removed
        #   else -> I ]
        if  badColor == goodColor:
            badKey  =  badName.upper()
            del  self.__colorMap [ badKey ]
# - - -   P i c k L i s t . _ _ p i c k H a n d l e r   - -

    def __pickHandler ( self, linex ):
        """Handler for user click on a color name.
        """
        #-- 1 --
        color  =  self.__colorList[linex]

        #-- 2 --
        if  self.__callback is not None:
            self.__callback ( color )

# - - - - -   c l a s s   A d j u s t e r

class Adjuster(Frame):
    """Widgets to store and adjust the current colors.

      Exports:
        Adjuster ( parent, callback=None ):
          [ (parent is a Frame) and
            (callback is a function or None) ->
              parent  :=  parent with a new Adjuster widget added
                  but not gridded, which will call callback
                  whenever the displayed color is changed, where
                  the calling sequence is
                    callback(isText, newColor)
                  and isText is True to set the text color, False
                  to set the background color, and newColor is a
                  the new color as a Color instance
              return that new Adjuster widget ]
        .textColor():
           [ return the current text color as a Color instance ]
        .bgColor():
           [ return the current background color as a Color instance ]
        .set ( color ):
          [ color is a Color instance ->
              if self is displaying the text color ->
                 self's text color  :=  color
              else ->
                 self's background color  :=  color ]
        .isText():
           [ if self is displaying the text color ->
               return True
             else -> return False ]
      Contained widgets:
         .__colorReadout:
           [ a ColorReadout widget that displays self's text and
             background colors, and a pair of radiobuttons to
             switch between them ]
         .__modelSelector:
           [ a ModelSelector widget that lets the user select
             which color model to display ]
         .__colorSliders:
           [ a ColorSliders widget that lets the user adjust
             the color model's parameters ]

       Grid plan:  Vertically stacked in a single column.
    """
    DEFAULT_TEXT_COLOR  =  Color ( 0, 0, 0 )
    DEFAULT_BG_COLOR  =  Color ( MAX_PARAM, 0, 0 )
# - - -   A d j u s t e r . s e t

    def set ( self, color ):
        """Change the currently displayed color.
        """
        #-- 1 --
        # [ self.__colorReadout  :=  self.__colorReadout
        #       displaying color ]
        self.__colorReadout.set ( color )
        #-- 2 --
        # [ self.__colorSliders  :=  self.__colorSliders
        #       displaying color ]
        self.__colorSliders.setColor ( color )
# - - -   A d j u s t e r . t e x t C o l o r

    def textColor ( self ):
        """Return self's current text color.
        """
        return  self.__colorReadout.textColor()
# - - -   A d j u s t e r . b g C o l o r

    def bgColor ( self ):
        """Return self's current background color.
        """
        return  self.__colorReadout.bgColor()
# - - -   A d j u s t e r . i s T e x t

    def isText ( self ):
        """Is self displaying the text color?
        """
        return  self.__colorReadout.isText()
# - - -   A d j u s t e r . _ _ i n i t _ _

    def __init__ ( self, parent, callback ):
        """Constructor for the Adjuster compound widget.
        """
        #-- 1 --
        # [ parent  :=  parent with self added as a new Frame ]
        Frame.__init__ ( self, parent )
        #-- 2 --
        self.__callback  =  None
        #-- 3 --
        # [ self  :=  self with all contained widgets created and
        #             gridded ]
        self.__createWidgets()
        #-- 4 --
        # [ self.__colorSliders  :=  self.__colorSliders displaying
        #       the color model currently selected in 
        #       self.__modelSelector ]
        model  =  self.__modelSelector.getModel()
        self.__colorSliders.setModel ( model )
        #-- 5 --
        self.__callback  =  callback
# - - -   A d j u s t e r . _ _ c r e a t e W i d g e t s

    def __createWidgets ( self ):
        """Create and grid all internal widgets
        """
        #-- 1 --
        # [ self  :=  self with a new ColorReadout added and gridded
        #       that will call self.__callback() when the user
        #       changes the text/background choice
        #   self.__colorReadout  :=  that new ColorReadout ]
        self.__colorReadout  =  ColorReadout ( self,
            self.DEFAULT_BG_COLOR, self.DEFAULT_TEXT_COLOR,
            self.__readoutHandler )
        rowx  =  0
        self.__colorReadout.grid ( row=rowx, column=0, sticky=E+W )
        #-- 2 --
        # [ self  :=  self with a new ModelSelector added and gridded
        #       that will select the color model displayed in
        #       self.__colorSliders, and call self.__modelHandler
        #       when the color model is changed ]
        self.__modelSelector  =  ModelSelector ( self,
                                 self.__modelHandler )
        rowx  +=  1
        self.__modelSelector.grid ( row=rowx, column=0, sticky=E+W,
            pady=4 )
        #-- 3 --
        # [ self  :=  self with a new ColorSliders widget added
        #       that displays the current color model parameters
        #       and calls self.__modelHandler whenever the user
        #       changes a color model parameter
        #   self.__colorSliders  :=  that ColorSliders widget ]
        self.__colorSliders  =  ColorSliders ( self, self.bgColor(),
            self.__sliderHandler )
        rowx  +=  1
        self.__colorSliders.grid ( row=rowx, column=0, sticky=W )
# - - -   A d j u s t e r . _ _ r e a d o u t H a n d l e r

    def __readoutHandler ( self ):
        """Change the internal and external colors.

          [ if  self.isText() ->
              self  :=  self displaying the text color
              call self.__callback(True, self.textColor())
            else ->
              self  :=  self displaying the background color
              call self.__callback(False, self.bgColor()) ]
        """
        #-- 1 --
        if self.isText():
            sliderColor  =  self.textColor()
        else:
            sliderColor  =  self.bgColor()

        #-- 2 --
        # [ self.__colorSliders  :=  self.__colorSliders displaying
        #                            sliderColor ]
        self.__colorSliders.setColor ( sliderColor )
        #-- 3 --
        if  self.__callback is not None:
            self.__callback ( self.isText(), sliderColor )
# - - -   A d j u s t e r . _ _ m o d e l H a n d l e r

    def __modelHandler ( self, model ):
        """Change the color model used in the color sliders.

          [ model is a concrete subclass of ColorModel ->
              self.__colorSliders  :=  self.__colorSliders
                  displaying its current color using (model) ]
        """
        self.__colorSliders.setModel ( model )
# - - -   A d j u s t e r . _ _ s l i d e r H a n d l e r

    def __sliderHandler ( self, color ):
        """Notify observers of a change in the color sliders.
        """
        #-- 1 --
        # [ self.__colorReadout  :=  self.__colorReadout displaying
        #       color
        self.__colorReadout.internalSet ( color )

        #-- 2 --
        if  self.__callback is not None:
            self.__callback ( self.isText(), color )

# - - - - -   c l a s s   C o l o r R e a d o u t

class ColorReadout(Frame):
    """Displays text and background colors, and switches between them.

      Exports:
        ColorReadout ( parent, bg, fg, callback=None ):
          [ (parent is a Frame) and
            (bg is a background color as a Color) and
            (fg is a foreground color as a Color) and
            (callback is a function or None) ->
              parent  :=  parent with a new ColorReadout widget
                  added but not gridded, initially displaying
                  the background color, which will call
                  callback() whenever the user changes
                  between text to bg color ]
        .textColor():
          [ return self's current text color as a Color instance ]
        .bgColor:
          [ return self's current background color as a Color instance ]
        .set ( color ):
          [ if self is currently displaying the text color ->
              self's text color  :=  color
            else ->
              self's background color  :=  color
            In any case ->
              call self.__callback(color) ]
        .isText():
          [ if self is currently displaying the text color ->
              return True
            else -> return False ]
      Contained widgets:
        .__rgbLabel:      [ text label '#RRGGBB' ]
        .__textColorName:
          [ an Entry widget displaying self.__textColorVar ]
        .__bgColorName:
          [ an Entry widget displaying self.__bgColorVar ]
        .__textRadio:   [ a Radiobutton selecting text color ]
        .__bgRadio:     [ a Radiobutton selecting background color ]

      Grid plan:
           0              1
          +--------------+-------------------+
        0 |              | .__rgbLabel       |
          +--------------+-------------------+
        1 | .__bgRadio   | .__bgColorName    |
          +--------------+-------------------+
        2 | .__textRadio | .__textColorName  |
          +--------------+-------------------+

      State/Internals:
        .__callback:     [ as passed to constructor, read-only ]
        .__isTextVar:
          [ an IntVar that is 1 if displaying text color,
            0 if displaying background color ]
        .__bgColor:
          [ self's current background color as a Color instance ]
        .__bgColorVar:
          [ a StringVar displaying self.__bgColor as #RRGGBB ]
        .__textColor:
          [ self's current text color as a Color instance ]
        .__textColorVar:
          [ a StringVar displaying self.__textColor as #RRGGBB ]
    """
# - - -   C o l o r R e a d o u t . i s T e x t

    def isText ( self ):
        """Is self showing the text color?
        """
        return  self.__isTextVar.get()
# - - -   C o l o r R e a d o u t . s e t

    def set ( self, color ):
        """Change the currently selected color.
        """
        #-- 1 --
        # [ if self.isText() ->
        #     self's text color  :=  color
        #   else ->
        #     self's background color  :=  color ]
        self.internalSet ( color )
        #-- 2 --
        if  self.__callback is not None:
            self.__callback ( )
# - - -   C o l o r R e a d o u t . i n t e r n a l S e t

    def internalSet ( self, color ):
        """Change the currently selected color without calling callbacks.

          [ color is a Color instance ->
              if self.isText() ->
                self's text color  :=  color
              else ->
                self's background color  :=  color ]
        """
        if  self.isText():
            self.__textColor  =  color
            self.__textColorVar.set ( str ( color ) )
        else:
            self.__bgColor  =  color
            self.__bgColorVar.set ( str ( color ) )
# - - -   C o l o r R e a d o u t . t e x t C o l o r

    def textColor ( self ):
        """Return self's current text color.
        """
        return  self.__textColor
# - - -   C o l o r R e a d o u t . b g C o l o r

    def bgColor ( self ):
        """Return self's current background color.
        """
        return  self.__bgColor
# - - -   C o l o r R e a d o u t . _ _ i n i t _ _

    def __init__ ( self, parent, bg, fg, callback=None ):
        """Constructor for ColorReadout.
        """

        #-- 1 --
        # [ parent  :=  parent with self added as a new Frame ]
        Frame.__init__ ( self, parent, relief=SUNKEN, bd=4 )

        #-- 2 --
        # [ self.__isTextVar  :=  a new IntVar control variable
        #                         initialized to 0
        #   self.__bgColor  :=  bg
        #   self.__bgColorVar  :=  a new StringVar control
        #       variable set to str(bg)
        #   self.__textColor  :=  fg
        #   self.__textColorVar  :=  a new StringVar control
        #       variable set to str(fg) ]
        self.__isTextVar  =  IntVar()
        self.__isTextVar.set(0)
        self.__bgColor  =  bg
        self.__bgColorVar  =  StringVar()
        self.__bgColorVar.set ( str ( bg ) )
        self.__textColor  =  fg
        self.__textColorVar  =  StringVar()
        self.__textColorVar.set ( str ( fg ) )

        #-- 3 --
        # [ self  :=  self with all internal widgets created and
        #             gridded ]
        self.__createWidgets()

        #-- 4 --
        self.__callback  =  callback
# - - -   C o l o r R e a d o u t . _ _ c r e a t e W i d g e t s

    def __createWidgets ( self ):
        """Create and grid all internal widgets.
        """
        #-- 1 --
        # [ self.__rgbLabel  :=  a new Label added and gridded ]
        self.__rgbLabel  =  Label ( self, font=MONO_FONT,
            text="#RRGGBB" )
        rowx  =  0
        self.__rgbLabel.grid ( row=rowx, column=1, sticky=E+W )
        #-- 2 --
        # [ self  :=  self with a new Radiobutton widget that sets
        #       self.__isTextVar to 0 and calls self.__radioHandler
        #       when the radiobutton is changed
        #   self.__bgRadio  :=  that Radiobutton widget ]
        self.__bgRadio  =  Radiobutton ( self,
            command=self.__radioHandler,
            font=BUTTON_FONT, text="Background color",
            value=0, variable=self.__isTextVar )
        rowx  +=  1
        self.__bgRadio.grid ( row=rowx, column=0, sticky=W )
        #-- 3 --
        # [ self.__bgColorName  :=  a new Entry whose text is
        #       linked to self.__bgColorVar ]
        self.__bgColorName  =  Entry ( self,
            exportselection=1, takefocus=0, width=7,
            relief=RAISED, bd=4, bg="white",
            font=MONO_FONT, textvariable=self.__bgColorVar )
        self.__bgColorName.grid ( row=rowx, column=1,
            padx=4, sticky=W )
        #-- 4 --
        # [ self  :=  self with a new Radiobutton widget that sets
        #       self.__isTextVar to 1 and calls self.__radioHandler
        #       when the radiobutton is changed
        #   self.__textRadio  :=  that Radiobutton widget ]
        self.__textRadio  =  Radiobutton ( self,
            command=self.__radioHandler,
            font=BUTTON_FONT, text="Text color",
            value=1, variable=self.__isTextVar )
        rowx  +=  1
        self.__textRadio.grid ( row=rowx, column=0, sticky=W )

        #-- 5 --
        # [ self.__textColorName  :=  a new Entry whose text is
        #       linked to self.__textColorVar ]
        self.__textColorName  =  Entry ( self,
            exportselection=1, takefocus=0, width=7,
            relief=RAISED, bd=4, bg="white",
            font=MONO_FONT, textvariable=self.__textColorVar )
        self.__textColorName.grid ( row=rowx, column=1,
            padx=4, sticky=W )
        #-- 6 --
        # [ self.__bgColorName  :=  self.__bgColorName set up so
        #       that any user keypresses cause self.__bgColorVar
        #       to be set to str(self.__bgColor)
        #   self.__textColorName  :=  self.__textColorName set up so
        #       that any user keypresses cause self.__textColorVar
        #       to be set to str(self.__textColor) ]
        self.__bgColorName.bind ( "<Any-KeyRelease>",
                                  self.__fixNames )
        self.__textColorName.bind ( "<Any-KeyRelease>",
                                  self.__fixNames )
# - - -   C o l o r R e a d o u t . _ _ r a d i o H a n d l e r

    def __radioHandler ( self ):
        """Handler for a change between text and background color.
        """
        if  self.__callback is not None:
            self.__callback ( )
# - - -   C o l o r R e a d o u t . _ _ f i x N a m e s

    def __fixNames ( self, event ):
        """Prevent the user from modifying color name Entry widgets.
        """
        self.__bgColorVar.set ( str ( self.__bgColor ) )
        self.__textColorVar.set ( str ( self.__textColor ) )

# - - - - -   c l a s s   M o d e l S e l e c t o r

class ModelSelector(Frame):
    """Compound widget for selecting color models.

      Exports:
        ModelSelector ( parent, callback=None ):
          [ (parent is a Frame) and
            (callback is a function or None) ->
              parent  :=  parent with a new ModelSelector widget
                  added but not gridded, that lets the user select
                  a color model (initially RGB), and calls
                  callback(model) when a selection is made, where
                  model is a concrete class that inherits from ColorModel
              return that new ModelSelector widget ]
        .getModel():
          [ returns self's model as a concrete class of ColorModel ]

      Internal widgets:
        .__topLabel:    [ a Label that labels the radiobuttons ]
        .__radioList:
          [ a list of Radiobutton widgets, one per model ]

      Grid plan:
           0                 1                 2...
          +-----------------+-----------------+-----+
        0 | .__topLabel                             |
          +-----------------+-----------------+-----+
        1 | .__radioList[0] | .__radioList[1] | ... |
          +-----------------+-----------------+-----+
      State/Invariants:
        .__callback:     [ as passed to constructor, read-only ]
        .__radioVar:
          [ an IntVar control variable for the radiobuttons whose
            value is the model's index in self.__modelList ]
        ModelSelector.__modelList:
          [ a list of instances of ColorModel concrete classes,
            in the same order as self.__radioList ]
    """
    __modelList  =  [ HSVModel(), RGBModel(), CMYModel() ]
# - - -   M o d e l S e l e c t o r . g e t M o d e l

    def getModel ( self ):
        """Returns self's current color model.
        """

        #-- 1 --
        # [ modelx  :=  index in self.__radioList of the currently
        #               selected color model ]
        modelx  =  self.__radioVar.get()
        
        #-- 2--
        return self.__modelList[modelx] 
# - - -   M o d e l S e l e c t o r . _ _ i n i t _ _

    def __init__ ( self, parent, callback ):
        """Constructor for the ModelSelector compound widget.
        """

        #-- 1 --
        # [ parent  :=  parent with a new Frame widget added but
        #               not gridded
        #   self  :=  that new Frame widget ]
        Frame.__init__ ( self, parent, relief=SUNKEN, bd=4 )
        #-- 2 --
        self.__callback  =  None
        self.__radioList  =  []
        self.__radioVar  =  IntVar()
        self.__radioVar.set(0)

        #-- 3 --
        # [ self  :=  self with all internal widgets created and
        #             gridded ]
        self.__createWidgets()

        #-- 4 --
        self.__callback  =  callback
# - - -   M o d e l S e l e c t o r . _ _ c r e a t e W i d g e t s

    def __createWidgets ( self ):
        """Create and grid all internal widgets.
        """

        #-- 1 --
        # [ self.__topLabel  :=  a Label labeling the radiobuttons ]
        self.__topLabel  =  Label ( self,
            font=BUTTON_FONT,
            text="Select a color model:" )
        rowx  =  0
        self.__topLabel.grid ( row=rowx, column=0, columnspan=3,
            sticky=W )
        #-- 2 --
        # [ self.__modelList is a list of ColorModel instances ->
        #     self  :=  self with one Radiobutton added and gridded for
        #         each element of self.__modelList, labeled with the
        #         model name of that element, and setting self.__radioVar
        #         to the position of that element in self.__modelList
        #     self.__radioList  +:=  those Radiobuttons in the
        #         same order ]
        rowx  +=  1
        colx  =   0
        for  radiox in range(len(self.__modelList)):
            #-- 2 body --
            # [ radiox is an index in self.__modelList ->
            #     self  :=  self with a new Radiobutton added and
            #         gridded, labeled with the model name from
            #         self.__modelList[radiox], and setting
            #         self.__radioVar to radiox ]
            model  =  self.__modelList[radiox]
            radio  =  Radiobutton ( self, font=BUTTON_FONT,
                command=self.__radioHandler,
                value=radiox, variable=self.__radioVar,
                text=model.modelName )
            radio.grid ( row=rowx, column=colx, sticky=W, padx=6 )
            colx  +=  1
            self.__radioList.append ( radio )
# - - -   M o d e l S e l e c t o r . _ _ r a d i o H a n d l e r

    def __radioHandler ( self ):
        """The user selected a different color model.
        """
        #-- 1 --
        if  self.__callback is not None:
            modelx  =  self.__radioVar.get()
            self.__callback ( self.__modelList[modelx] )

# - - - - -   c l a s s   C o l o r S l i d e r s

class ColorSliders(Frame):
    """Compound widget for displaying and adjusting color parameters

      Exports:
        ColorSliders ( parent, color, callback=None ):
          [ (parent is a Frame) and
            (color is the initial color as a Color instance) and
            (callback is a function or None) ->
              parent  :=  parent with a new ColorSliders widget
                  added but not gridded, using the HSV model,
                  initially displaying white, that will call
                  callback(color) whenever the user changes a
                  color parameter
              return that new ColorSliders widget ]
        .setModel ( model ):
          [ model is a concrete subclass of ColorModel ->
              self  :=  self with its current color displayed
                        using model ]
        .setColor ( color ):
          [ color is a Color instance ->
              self  :=  self displaying color using its current
                        model ]
      Internal widgets:
        .__topLabel:    [ a Label that describes this widget ]
        .__sliderList:
          [ a list containing three ParamSlider widgets
            corresponding to the three parameters of self.__model
            in the same order ]

      Grid plan:
           0                  1                  2
          +------------------+------------------+------------------+
        0 | .__topLabel                                            |
          +------------------+------------------+------------------+
        1 | .__sliderList[0] | .__sliderList[1] | .__sliderList[2] |
          +------------------+------------------+------------------+
      State/Invariants:
        .__callback:  [ as passed to the constructor ]
        .__color:     [ the currently displayed color as a Color ]
        .__model:
          [ the current color model as a concrete subclass of
            ColorModel ]
    """
# - - -   C o l o r S l i d e r s . s e t M o d e l

    def setModel ( self, model ):
        """Change the displayed color model.
        """
        #-- 1 --
        self.__model  =  model

        #-- 2 --
        # [ self.__sliderList  :=  self.__sliderList with its
        #       contained widgets relabeled for model (model) ]
        for  paramx in range ( N_PARAMS ):
            self.__sliderList[paramx].setModel ( self.__model )

        #-- 3 --
        # [ self  :=  self displaying the parameters self.__color
        #             using model self.__model ]
        self.setColor ( self.__color )
# - - -   C o l o r S l i d e r s . s e t C o l o r

    def setColor ( self, color ):
        """Change the displayed color.
        """
        #-- 1 --
        self.__color  =  color

        #-- 2 --
        for  paramx in range ( N_PARAMS ):
            #-- 1 body --
            # [ self.__sliderList[paramx]  :=  self.__sliderList[paramx]
            #       displaying the (paramx)th parameter of (color)
            #       using its current color model ]
            self.__sliderList[paramx].setColor ( color )
# - - -   C o l o r S l i d e r s . _ _ i n i t _ _

    def __init__ ( self, parent, color, callback ):
        """Constructor for the ColorSliders widget.
        """
        #-- 1 --
        # [ parent  :=  parent with a new Frame added but not
        #               gridded
        #   self  :=  that Frame ]
        Frame.__init__ ( self, parent )
        self.columnconfigure ( 0, weight=1, minsize="80" )
        self.columnconfigure ( 1, weight=1, minsize="80" )
        self.columnconfigure ( 2, weight=1, minsize="80" )
        #-- 2 --
        # [ self.__color     :=  red
        #   self.__model     :=  the HSV color model
        #   self.__callback  :=  callback ]
        self.__color  =  color
        self.__model  =  HSVModel()
        self.__callback  =  None

        #-- 3 --
        # [ self  :=  self with all internal widgets created and
        #             gridded ]
        self.__createWidgets()

        #-- 4 --
        self.__callback  =  callback
# - - -   C o l o r S l i d e r s . _ _ c r e a t e W i d g e t s

    def __createWidgets ( self ):
        """Create and grid all internal widgets.
        """
        #-- 1 --
        # [ self  :=  self with a new Label created and gridded
        #   self.__topLabel  :=  that new Label ]
        # 
        self.__topLabel  =  Label ( self,
            font=BUTTON_FONT,
            text="Adjust colors here:" )
        rowx  =  0
        self.__topLabel.grid ( row=rowx, column=0, columnspan=3,
            sticky=E+W )
        #-- 2 --
        self.__sliderList  =  []

        # [ self  :=  self with N_PARAMS new ParamSlider widgets
        #             added and gridded
        #   self.__sliderList  +:=  those widgets ]
        rowx  +=  1
        for  paramx in range ( N_PARAMS ):
            paramSlider  =  ParamSlider ( self, self.__model,
                self.__color, paramx, self.__sliderHandler )
            paramSlider.grid ( row=rowx, column=paramx, sticky=E+W )
            self.__sliderList.append ( paramSlider )
# - - -   C o l o r S l i d e r s . _ _ s l i d e r H a n d l e r

    def __sliderHandler ( self ):
        """Read the ParamSliders and convert them to a new color
        """
        #-- 1 --
        paramList  =  []

        #-- 2 --
        # [ paramList  +:=  parameter values of the ParamSlider
        #       widgets in self.__sliderList ]
        for  paramx in range(N_PARAMS):
            paramList.append (self.__sliderList[paramx].get() )
        #-- 3 --
        # [ paramList  is a list of N_PARAMS numbers, each in
        #   [0,MAX_PARAM] ->
        #     self.__color  :=  paramList converted to a color using
        #                       the color model in self.__model ]
        self.__color  =  self.__model.paramsToColor ( paramList )
        #-- 4 --
        if  self.__callback is not None:
            self.__callback ( self.__color )

# - - - - -   c l a s s   P a r a m S l i d e r

class ParamSlider(Frame):
    """Compound widget with a Scale for adjusting one color parameter.

      Exports:
        ParamSlider ( parent, model, color, paramx, callback=None ):
          [ (parent is a Frame) and
            (model is a ColorModel) and
            (color is a Color) and
            (param is an int in [0,N_PARAMS)) and
            (callback is a function or None) ->
              parent  :=  parent with a new ParamSlider widget added
                  but not gridded, that displays the (paramx)th
                  parameter of (color) using (model), and calls
                  callback() whenever its scale is moved
              return that new ParamSlider widget ]
        .get():  [ return self's slider value in [0,MAX_PARAM] ]
        .setModel ( model ):
          [ self  :=  self displaying labels for the (paramx)th
                      parameter of model ]
        .setColor ( color ):
          [ self  :=  self displaying the (paramx)th parameter of
                      self.model ]
      Internal widgets:
        .__topLabel:    [ Label showing the parameter's name ]
        .__plusButton:  [ Button that increments the parameter ]
        .__scale:       [ Scale for adjusting the parameter ]
        .__minusButton: [ Button that decrements the parameter ]

      Grid plan:  One vertical column.
      State/Invariants:
        .__paramx:      [ as passed to the constructor ]
        .__callback:    [ as passed to the constructor ]
        .__topLabelVar: [ StringVar for self.__topLabel ]
        .__scaleVar:    [ IntVar for self.__scale ]
        .__model:       [ current model as a ColorModel ]
        .__color:       [ current color as a Color ]
    """
# - - -   P a r a m S l i d e r . g e t

    def get ( self ):
        """Return self's parameter value in [0,MAX_PARAM].
        """
        return  self.__scaleVar.get() << 8
# - - -   P a r a m S l i d e r . s e t M o d e l

    def setModel ( self, model ):
        """Change the current color model."""
        #-- 1 --
        self.__model  =  model
        #-- 2 --
        # [ self.__topLabelVar  :=  self.__topLabelVar with its
        #       value set to the (self.__paramx)th parameter name
        #       of self.__model ]
        paramLabel  =  self.__model.labelList[self.__paramx]
        self.__topLabelVar.set ( paramLabel )
# - - -   P a r a m S l i d e r . s e t C o l o r

    def setColor ( self, color ):
        """Change the currently displayed color."""

        #-- 1 --
        self.__color  =  color
        #-- 2 --
        # [ paramList  :=  self.__color expressed as a list of
        #       N_PARAMS parameters using color model self.__model ]
        paramList  =  self.__model.colorToParams ( color )
        #-- 3 --
        scaleValue  =  paramList[self.__paramx] >> 8

        #-- 4 --
        # [ self.__scale  :=  self.__scale repositioned to value
        #                     (scaleValue) ]
        self.__scaleVar.set ( scaleValue )
        #-- 5 --
        if  self.__callback is not None:
            self.__callback()
# - - -   P a r a m S l i d e r . _ _ i n i t _ _

    def __init__ ( self, parent, model, color, paramx, callback=None ):
        """Constructor for ParamSlider.
        """
        #-- 1 --
        # [ parent  :=  parent with a new Frame widget added but
        #               not gridded
        #   self  :=  that Frame widget ]
        Frame.__init__ ( self, parent )

        #-- 2 --
        self.__model     =  model
        self.__color     =  color
        self.__paramx    =  paramx
        self.__callback  =  None
        #-- 3 --
        # [ self.__topLabelVar  :=  a new StringVar control variable
        #       set to the (paramxth) parameter name of self.__model
        #   self.__scaleVar  :=  a new IntVar control variable ]
        paramLabel  =  self.__model.labelList[self.__paramx]
        self.__topLabelVar  =  StringVar()
        self.__topLabelVar.set ( paramLabel )
        self.__scaleVar  =  IntVar()
        #-- 4 --
        # [ self  :=  self with all internal widgets created and
        #             gridded ]
        self.__createWidgets()

        #-- 5 --
        self.__callback  =  callback
# - - -   P a r a m S l i d e r . _ _ c r e a t e W i d g e t s

    def __createWidgets ( self ):
        """Create and grid all widgets.
        """
        #-- 1 --
        # [ self  :=  self with a new Label added and gridded,
        #             with control variable self.__topLabelVar
        #   self.topLabel  :=  that new Label ]
        self.__topLabel  =  Label ( self, font=BUTTON_FONT,
            textvariable=self.__topLabelVar )
        rowx  =  0
        self.__topLabel.grid ( row=rowx, column=0 )
        #-- 2 --
        # [ self  :=  self with a new Button widget added and gridded
        #       that adds 1 to self.__scaleVar but no higher than
        #       MAX_BYTE
        #   self.__plusButton  :=  that widget ]
        self.__plusButton  =  Button ( self, font=BUTTON_FONT,
            text="+", command=self.__plusHandler )
        rowx  +=  1
        self.__plusButton.grid ( row=rowx, column=0 )
        #-- 3 --
        # [ self  :=  self with a new Scale widget added and gridded,
        #       with control variable self.__scaleVar, and a length
        #       of (MAX_BYTE+1) pixels
        #   self.__scale  :=  that Scale widget ]
        self.__scale  =  Scale ( self, orient=VERTICAL,
            command=self.__scaleHandler,
            length=(MAX_BYTE+1), from_=MAX_BYTE, to=0,
            variable=self.__scaleVar )
        rowx  +=  1
        self.__scale.grid ( row=rowx, column=0 )
        #-- 4 --
        # [ self  :=  self with a new Button widget added and gridded
        #       that subtracts 1 to self.__scaleVar but no lower than 0
        #   self.__minusButton  :=  that widget ]
        self.__minusButton  =  Button ( self, font=BUTTON_FONT,
            text="-", command=self.__minusHandler )
        rowx  +=  1
        self.__minusButton.grid ( row=rowx, column=0 )
# - - -   P a r a m S l i d e r . _ _ p l u s H a n d l e r

    def __plusHandler ( self ):
        """Increment the parameter.
        """

        #-- 1 --
        # [ if self.__scaleVar has a value < MAX_BYTE _>
        #     self.__scaleVar  +=  1
        #   else -> I ]
        oldValue  =  self.__scaleVar.get()
        if  oldValue < MAX_BYTE:
            self.__scaleVar.set ( oldValue + 1 )
            if  self.__callback is not None:
                self.__callback()
# - - -   P a r a m S l i d e r . _ _ m i n u s H a n d l e r

    def __minusHandler ( self ):
        """Increment the parameter.
        """

        #-- 1 --
        # [ if self.__scaleVar has a value > 0 ->
        #     self.__scaleVar  -=  1
        #   else -> I ]
        oldValue  =  self.__scaleVar.get()
        if  oldValue > 0:
            self.__scaleVar.set ( oldValue - 1 )
            if  self.__callback is not None:
                self.__callback()
# - - -   P a r a m S l i d e r . _ _ s c a l e H a n d l e r

    def __scaleHandler ( self, value ):
        """Handler for self.__scale
        """
        #-- 1 --
        if  self.__callback is not None:
            self.__callback()

# - - - - -   c l a s s   S w a t c h

class Swatch(Frame):
    """Compound widget for text/background display and font selection.

      Exports:
        Swatch ( parent, bg, fg ):
          [ (parent is a Frame) and
            (bg is the initial background color as a Color instance) and
            (fg is the initial foreground color as a Color instance) ->
              parent  :=  parent with a new Swatch widget added but not
                          gridded
              return that new Swatch widget ]
        .setTextColor ( color ):
          [ color is a color as a Color instance ->
              self  :=  self with the text displayed in that color ]
        .setBgColor ( color ):
          [ color is a color as a Color instance ->
              self  :=  self with the background set to color ]

      Internal widgets:
        .__text:          [ a Text widget ]
        .__fontSelect:    [ a FontSelect widget ]

      Grid plan:  One vertical column.
      State/Invariants:
        .__textColor:   [ current text color as a Color ]
        .__bgColor:     [ current background color as a Color ]
        .__font:        [ current font as a tkFont.Font ]
    """
    SWATCH_TEXT  =  (
        "The quick brown fox jumps over\n"
        "the lazy dog.\n"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
        "abcdefghijklmnopqrstuvwxyz\n"
        "0123456789 !\"#$%&'()*+,-./\n"
        ":;<=>?@[\\]^_/{|}~" )
    SWATCH_WIDE  =  40        # Width of the color swatch in characters
    SWATCH_HIGH  =  8         # Height of the color swatch in lines
    FONT_FAMILIES  =  15
# - - -   S w a t c h . s e t T e x t C o l o r

    def setTextColor ( self, color ):
        """Sets the text color of self.__text.
        """
        self.__text["fg"]  =  str(color)
# - - -   S w a t c h . s e t B g C o l o r

    def setBgColor ( self, color ):
        """Sets the background color of self.__text.
        """
        self.__text["bg"]  =  str(color)
# - - -   S w a t c h . _ _ i n i t _ _

    def __init__ ( self, parent, bg, fg ):
        """Constructor for Swatch.
        """
        #-- 1 --
        # [ parent  :=  parent with a new Frame added
        #   self  :=  that Frame ]
        Frame.__init__ ( self, parent )

        #-- 2 --
        self.__textColor  =  fg
        self.__bgColor  =  bg

        #-- 3 --
        # [ self  :=  self with all internal widgets added and gridded ]
        self.__createWidgets()
        #-- 4 --
        # [ self.__text  :=  self.__text using the font from
        #                    self.__fontSelect ]
        self.__text["font"]  =  self.__fontSelect.get()

        #-- 5 --
        # [ self.__text  :=  self.__text with some sample text added ]
        self.__text.insert ( END, self.SWATCH_TEXT )
# - - -   S w a t c h . _ _ c r e a t e W i d g e t s

    def __createWidgets ( self ):
        """Create and grid all internal widgets.
        """
        #-- 1 --
        # [ self  :=  self with a new Text widget added
        #   self.__text  :=  that widget ]
        self.__text  =  Text ( self,
            bg=self.__bgColor, fg=self.__textColor,
            width=self.SWATCH_WIDE,
            height=self.SWATCH_HIGH )
        rowx  =  0
        self.__text.grid ( row=rowx, column=0, sticky=W )
        #-- 2 --
        # [ self  :=  self with a new FontSelect widget added that
        #       calls self.__fontHandler when the font is changed
        #   self.__fontSelect  :=  that widget ]
        self.__fontSelect  =  FontSelect ( self,
            font=BUTTON_FONT,
            listCount=self.FONT_FAMILIES,
            observer=self.__fontHandler )
        rowx  +=  1
        self.__fontSelect.grid ( row=rowx, column=0, sticky=W )
# - - -   S w a t c h . _ _ f o n t H a n d l e r

    def __fontHandler ( self, font ):
        """Handler for font changes.
        """
        self.__text["font"]  =  font
#================================================================
# Epilogue
#----------------------------------------------------------------

# [ if this file is being run as a script ->
#     run an instance of the Application class
#   else -> I ]
if  __name__ == '__main__':
    main()
