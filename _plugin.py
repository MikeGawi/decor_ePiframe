from misc.configproperty import ConfigProperty
from modules.convertmanager import ConvertManager
from modules.base.pluginbase import PluginBase
from modules.base.configbase import ConfigBase
from modules.pidmanager import PIDManager
from misc.logs import Logs
from PIL import Image, ImageDraw, ImageFont, ImageColor
import os
import random


class Plugin(PluginBase):

    name = "Decor"
    author = "MikeGawi"
    description = "Displays borders an quotes on frame"
    site = "https://github.com/MikeGawi/decor_ePiframe"
    info = "Uses free images from https://www.rawpixel.com/"

    __COLORS = {"WHITE": 255, "BLACK": 0}

    # Key is also a filename, the tuple represents x,y percentage position
    __BORDERS = {
        "DOTS": (0.36, 0.075),
        "STARS": (0.36, 0.075),
        "HEARTS": (0.5, 0.075),
        "FLOWERS": (0.66, 0.92),
        "GRUNGE": (0.5, 0.9),
        "SMOKE": (0.5, 0.9),
        "LEAVES": (0.66, 0.92),
        "WINTER": (0.64, 0.075),
    }

    __BORDERS_DIR = "borders"
    __FONT = "fonts/Freehand-Regular.ttf"

    class PluginConfigManager(ConfigBase):
        # building settings according to config.default file
        # notice that referring to plugin class is done with self.main_class
        def load_settings(self):
            self.SETTINGS = [
                ConfigProperty(
                    "is_enabled", self, prop_type=ConfigProperty.BOOLEAN_TYPE
                ),
                ConfigProperty(
                    "font", self, minvalue=8, prop_type=ConfigProperty.INTEGER_TYPE
                ),
                ConfigProperty(
                    "font_color", self, possible=self.main_class.get_colors()
                ),
                ConfigProperty(
                    "random_border", self, prop_type=ConfigProperty.BOOLEAN_TYPE
                ),
                ConfigProperty(
                    "border",
                    self,
                    dependency=["random_border", "0"],
                    possible=self.main_class.get_borders(),
                ),  # enabled only when random_border is false
                ConfigProperty(
                    "quotes", self, not_empty=False
                ),  # this property can be empty
            ]

    def __init__(
        self,
        path: str,
        pid_manager: PIDManager,
        logging: Logs,
        global_config: ConfigBase,
    ):
        super().__init__(
            path, pid_manager, logging, global_config
        )  # default constructor

    # config possible values methods
    def get_colors(self):
        return [key.lower() for key in self.__COLORS.keys()]

    def get_borders(self):
        return [key.lower() for key in self.__BORDERS.keys()]

    # Overwriting only postprocess method
    def postprocess_photo(
        self,
        final_photo: str,
        width: int,
        height: int,
        is_horizontal: bool,
        convert_manager: ConvertManager,
        photo,
        id_label: str,
        creation_label: str,
        source_label: str,
    ):
        image = Image.open(final_photo)
        mode = image.mode
        if not is_horizontal:
            image = image.transpose(
                Image.ROTATE_90
                if self.global_config.getint("rotation") == 90
                else Image.ROTATE_270
            )  # rotating image if frame not in horizontal position
        new_image = image.convert("RGBA")  # converting to RGB with alpha
        image_width, image_height = new_image.size

        # get selected border or get random one
        picture = self.config.get("border")
        if bool(self.config.getint("random_border")):
            picture = random.choice(list(self.__BORDERS.keys()))

        border = Image.open(
            os.path.join(self.path, self.__BORDERS_DIR, picture.lower() + ".png")
        ).convert(
            "RGBA"
        )  # self.path is a plugin path
        border = border.resize(
            (image_width, image_height)
        )  # resizing border to current photo size
        new_image.paste(
            border, (0, 0), border
        )  # pasting border over the photo and with border mask
        new_image = new_image.convert(mode)  # convert back to original photo mode

        if self.config.get("quotes"):
            draw = ImageDraw.Draw(new_image)
            font = ImageFont.truetype(
                os.path.join(self.path, self.__FONT), self.config.getint("font")
            )
            fill_color = self.__COLORS[
                self.config.get("font_color").upper()
            ]  # getting fill and stroke colors...
            stroke_color = (
                self.__COLORS["WHITE"] + self.__COLORS["BLACK"]
            ) - fill_color

            stroke = ImageColor.getcolor(
                {value: key for key, value in self.__COLORS.items()}[stroke_color], mode
            )  # ...according to the image mode (can be black & white)
            fill = ImageColor.getcolor(self.config.get("font_color"), mode)

            position = self.__BORDERS[picture.upper()]
            draw.text(
                (position[0] * image_width, position[1] * image_height),
                random.choice(self.config.get("quotes").split(";")),
                anchor="mm",
                font=font,
                fill=fill,
                stroke_width=2,
                stroke_fill=stroke,
            )  # drawing random text from quotes in the selected border position

        if not is_horizontal:
            new_image = new_image.transpose(
                Image.ROTATE_270
                if self.global_config.getint("rotation") == 90
                else Image.ROTATE_90
            )  # rotating back if in vertical position

        new_image.save(final_photo)  # saving as final photo
