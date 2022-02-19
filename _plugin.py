from modules.base.pluginbase import pluginbase
from modules.base.configbase import configbase
from misc.configprop import configprop
from misc.constants import constants
from PIL import Image, ImageDraw, ImageFont, ImageColor
import os, random

class plugin(pluginbase):
	
	name = 'Decor'
	author = 'MikeGawi'
	description = 'Displays borders an quotes on frame'
	site = 'https://github.com/MikeGawi/borders-ePiframe'
	info = 'Uses free images from https://www.rawpixel.com/'
	
	__COLORS = {
		'WHITE' : 		255,
		'BLACK' : 		0
	}
	
	#Key is also a filename, the tuple represents x,y percentage position
	__BORDERS = {
		'DOTS' : (0.36,0.075),
		'STARS' : (0.36,0.075),
		'HEARTS' : (0.5,0.075),
		'FLOWERS' : (0.66,0.92),
		'GRUNGE' : (0.5,0.9),
		'SMOKE' : (0.5,0.9),
		'LEAVES' : (0.66,0.92),
		'WINTER' : (0.64,0.075)
	}
	
	__BORDERS_DIR = "borders"
	__FONT = "fonts/Freehand-Regular.ttf"
		
	class configmgr (configbase):
		#building settings according to config.default file
		#notice that referring to plugin class is done with self.main_class
		def load_settings(self):
			self.SETTINGS = [
				configprop('is_enabled', self, prop_type=configprop.BOOLEAN_TYPE),
				configprop('font', self, minvalue=8, prop_type=configprop.INTEGER_TYPE),
				configprop('font_color', self, possible=self.main_class.get_colors()),
				configprop('random_border', self, prop_type=configprop.BOOLEAN_TYPE),				
				configprop('border', self, dependency=['random_border', '0'], possible=self.main_class.get_borders()), #enabled only when random_border is false
				configprop('quotes', self, notempty=False) #this property can be empty
			]
	
	def __init__ (self, path, pidmgr, logging, globalconfig):
		super().__init__(path, pidmgr, logging, globalconfig) #default constructor
	
	#config possible values methods
	def get_colors (self):
		return [k.lower() for k in self.__COLORS.keys()]
	
	def get_borders (self):
		return [k.lower() for k in self.__BORDERS.keys()]
	
	#Overwriting only postprocess method
	def postprocess_photo (self, finalphoto, width, height, is_horizontal, convertmgr, photo, idlabel, creationlabel, sourcelabel):
		image = Image.open(finalphoto)
		mode = image.mode	
		if not is_horizontal: image = image.transpose(Image.ROTATE_90 if self.globalconfig.getint('rotation') == 90 else Image.ROTATE_270) #rotating image if frame not in horizontal position
		newimage = image.convert('RGBA') #converting to RGB with alpha
		wid, hei = newimage.size
		
		#get seletced border or get random one
		pic = self.config.get('border')
		if bool(self.config.getint('random_border')):
			pic = random.choice(list(self.__BORDERS.keys()))
		
		border = Image.open(os.path.join(self.path, self.__BORDERS_DIR, pic.lower() + '.png')).convert('RGBA') #self.path is a plugin path
		border = border.resize((wid, hei)) #resizing border to current photo size
		newimage.paste(border, (0,0), border) #pasting border over the photo and with border mask
		newimage = newimage.convert(mode) #convert back to original photo mode
		
		if self.config.get('quotes'):
			draw = ImageDraw.Draw(newimage)
			font = ImageFont.truetype(os.path.join(self.path, self.__FONT), self.config.getint('font'))		
			fillcolor = self.__COLORS[self.config.get('font_color').upper()] #getting fill and stroke colors...
			strokecolor = (self.__COLORS['WHITE'] + self.__COLORS['BLACK']) - fillcolor

			stroke = ImageColor.getcolor({value:key for key, value in self.__COLORS.items()}[strokecolor], mode) #...according to the image mode (can be black & white)
			fill = ImageColor.getcolor(self.config.get('font_color'), mode)
			
			pos = self.__BORDERS[pic.upper()]				
			draw.text((pos[0]*wid, pos[1]*hei), random.choice(self.config.get('quotes').split(';')), anchor="mm", font = font, fill = fill, stroke_width=2, stroke_fill=stroke) #drawing random text from quotes in the selected border position

		if not is_horizontal: newimage = newimage.transpose(Image.ROTATE_270 if self.globalconfig.getint('rotation') == 90 else Image.ROTATE_90) #rotating back if in vertical position

		newimage.save(finalphoto) #saving as final photo
