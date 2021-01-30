import textwrap
from dataclasses import dataclass
from typing import Tuple, List

from PIL import Image
from PIL.ImageFont import FreeTypeFont

RGB_COLOR = Tuple[int, int, int, int]


@dataclass
class ImageInfo:
    source_filename: str
    title: str
    description: str
    gradient_on_side: bool = False
    text_size_multiplier: float = 1


def add_gradient(
        image: Image.Image, gradient_color: RGB_COLOR = (0, 0, 0),
        gradient_on_side: bool = True) -> None:
    """
    WARNING: mutates the given image!

    & image should be in `rgba` format

    If on_side is False, gradient will be on the bottom
    """
    if image.mode != "RGBA":
        raise ValueError("Image should be in the RGBA format!")
    if gradient_on_side:
        start_x = image.width // 3
    else:
        start_y = image.height // 3
    gradient = Image.new("RGBA", (256, 1) if gradient_on_side else (1, 256))
    for x in range(256):
        gradient.putpixel(
            (x, 0) if gradient_on_side else (0, x), (*gradient_color, x)
        )
    # noinspection PyUnboundLocalVariable
    # because of start_x and start_y
    gradient = gradient.resize(
        (image.width - start_x, image.height)
        if gradient_on_side else
        (image.width, image.height - start_y)
    )
    image.alpha_composite(
        gradient, (start_x, 0) if gradient_on_side else (0, start_y)
    )


def get_wrapped_text_by_max_width(
        font: FreeTypeFont, text: str, width_limit_in_pixels: int) -> List[str]:
    symbols_before_text_wrap = 1
    while True:
        wrapped_text = textwrap.wrap(text, symbols_before_text_wrap + 1)
        if (
            max(
                font.getsize(part)[0] for part in wrapped_text
            ) < width_limit_in_pixels  # If text fits
        ):
            if len(wrapped_text) != 1:  # And it is possible to wrap more
                symbols_before_text_wrap += 1
            else:
                break
        else:
            wrapped_text = textwrap.wrap(text, symbols_before_text_wrap)
            break
    return wrapped_text
