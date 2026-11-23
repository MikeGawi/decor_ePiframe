"""Decor_ePiframe: decorative borders with quotes (ePiframe Plugin API v2).

A border image (and optionally a random quote at its free spot) is drawn over
the converted photo (``postprocess_photo``). Borders: free images from
https://www.rawpixel.com/, font: Freehand from Google Fonts.
"""

import random

from PIL import Image, ImageColor, ImageDraw, ImageFont

from epiframe.config.property import ConfigProperty, PropertyType
from epiframe.plugins.base import PhotoFile
from epiframe.plugins.base import Plugin as PluginBase

# border name (= file borders/<name>.png) -> quote position (x, y) as fractions
# of the photo size
BORDERS = {
    "dots": (0.36, 0.075),
    "stars": (0.36, 0.075),
    "hearts": (0.5, 0.075),
    "flowers": (0.66, 0.92),
    "grunge": (0.5, 0.9),
    "smoke": (0.5, 0.9),
    "leaves": (0.66, 0.92),
    "winter": (0.64, 0.075),
}
BORDERS_DIR = "borders"
FONT = "fonts/Freehand-Regular.ttf"
COLORS = ["white", "black"]  # the outline has the other one
STROKE_WIDTH = 2
QUOTES_DELIMITER = ";"


class Plugin(PluginBase):
    name = "Decor"
    author = "MikeGawi"
    description = "Displays borders with quotes on frame"
    site = "https://github.com/MikeGawi/decor_ePiframe"
    info = "Uses free images from https://www.rawpixel.com/"

    def settings(self) -> list[ConfigProperty]:
        return [
            *super().settings(),  # is_enabled
            ConfigProperty("font", PropertyType.INTEGER, min_value=8),
            ConfigProperty("font_color", possible=COLORS),
            ConfigProperty("random_border", PropertyType.BOOLEAN),
            # used only when random_border is 0
            ConfigProperty(
                "border",
                possible=list(BORDERS),
                dependency="random_border",
                dependency_value="0",
            ),
            ConfigProperty("quotes", not_empty=False),  # empty: no quotes
        ]

    def postprocess_photo(self, photo: PhotoFile) -> None:
        border = self.pick_border()
        with Image.open(photo.path) as source:
            image = source.copy()
        mode = image.mode  # black & white photos stay black & white
        image = self.upright(image, photo, back=False).convert("RGBA")
        self.paste_border(image, border)
        image = image.convert(mode)
        quotes = [q for q in self.config.get("quotes").split(QUOTES_DELIMITER) if q]
        if quotes:
            self.draw_quote(image, random.choice(quotes), BORDERS[border])
        self.upright(image, photo, back=True).save(photo.path)

    def pick_border(self) -> str:
        if bool(self.config.getint("random_border")):
            return random.choice(list(BORDERS))
        return self.config.get("border")

    @staticmethod
    def upright(image: Image.Image, photo: PhotoFile, back: bool) -> Image.Image:
        # a vertical frame stores the photo turned: draw on the upright photo
        if photo.horizontal:
            return image
        turn_left = (photo.rotation == 90) != back
        return image.transpose(
            Image.Transpose.ROTATE_90 if turn_left else Image.Transpose.ROTATE_270
        )

    def paste_border(self, image: Image.Image, border: str) -> None:
        path = self.path / BORDERS_DIR / f"{border}.png"  # self.path: plugin folder
        with Image.open(path) as source:
            frame = source.convert("RGBA").resize(image.size)
        image.paste(frame, (0, 0), frame)  # the border's alpha is the mask

    def draw_quote(
        self, image: Image.Image, quote: str, position: tuple[float, float]
    ) -> None:
        color = self.config.get("font_color")
        outline = COLORS[1 - COLORS.index(color)]
        font = ImageFont.truetype(str(self.path / FONT), self.config.getint("font"))
        ImageDraw.Draw(image).text(
            (position[0] * image.width, position[1] * image.height),
            quote,
            anchor="mm",  # centered at the position
            font=font,
            fill=ImageColor.getcolor(color, image.mode),
            stroke_width=STROKE_WIDTH,
            stroke_fill=ImageColor.getcolor(outline, image.mode),
        )
