import os
import textwrap
from typing import Tuple, Optional

from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageFont import FreeTypeFont

RGB_COLOR = Tuple[int, int, int, int]


def add_gradient(
        image: Image.Image, gradient_color: RGB_COLOR = (0, 0, 0),
        on_side: bool = True) -> None:
    """
    WARNING: mutates the given image!

    & image should be in `rgba` format

    If on_side is False, gradient will be on the bottom
    """
    if image.mode != "RGBA":
        raise ValueError("Image should be in the RGBA format!")
    if on_side:
        start_x = image.width // 3
    else:
        start_y = image.height // 3
    gradient = Image.new("RGBA", (256, 1) if on_side else (1, 256))
    for x in range(256):
        gradient.putpixel((x, 0) if on_side else (0, x), (*gradient_color, x))
    # noinspection PyUnboundLocalVariable
    # because of start_x and start_y
    gradient = gradient.resize(
        (image.width - start_x, image.height)
        if on_side else
        (image.width, image.height - start_y)
    )
    image.alpha_composite(gradient, (start_x, 0) if on_side else (0, start_y))


# SOOOOOOO MANY BAD WORKAROUNDS, MY GOD...

def add_gradient_with_text(
        image: Image.Image, title: str, description: str,
        regular_font_file_name: str, bold_font_file_name: str,
        gradient_color: RGB_COLOR = (0, 0, 0),
        text_color: RGB_COLOR = (255, 255, 255),
        symbols_before_wrap: Optional[int] = None,
        on_side: bool = True) -> None:
    """
    WARNING: mutates the given image!

    & image should be in `rgba` format

    If symbols_before_wrap is not specified, then it's (quite badly) calculated

    If on_side is False, gradient will be on the bottom
    """
    if image.mode != "RGBA":
        raise ValueError("Image should be in the RGBA format!")
    font_size = min(image.size) // 22  # Approximately...
    regular_font = FreeTypeFont(regular_font_file_name, size=font_size)
    bold_font = FreeTypeFont(bold_font_file_name, size=font_size)
    add_gradient(image, gradient_color, on_side=on_side)
    side_padding = image.width // 100
    description_start_x = (image.width // 7 * 5) if on_side else side_padding
    place_for_description = image.width - (
        side_padding if on_side else side_padding * 2
    ) - description_start_x
    if symbols_before_wrap is None:
        symbols_before_wrap = 1
        while (
            max(
                regular_font.getsize(part)[0] for part in textwrap.wrap(
                    description, symbols_before_wrap
                )
            )
            < place_for_description  # While text fits
        ):
            symbols_before_wrap += 1
        symbols_before_wrap -= 1  # To remove overplus
    wrapped_description = "\n".join(textwrap.wrap(
        description, symbols_before_wrap
    ))
    title_width, title_height = bold_font.getsize(title)
    gap_between_texts = title_height // 2
    description_width, description_height = (
        regular_font.getsize_multiline(wrapped_description)
    )
    text_height = title_height + gap_between_texts + description_height
    if on_side:
        title_start_y = (image.height - text_height) // 2
    else:
        title_start_y = round(image.height / 8 * 7) - text_height // 2
        if title_start_y + text_height > image.height - side_padding:
            title_start_y = image.height - side_padding - text_height
        description_start_x = (
            (image.width - description_width) // 2
        )
    title_start_x = description_start_x + (description_width - title_width) // 2
    drawer = Draw(image)
    drawer.text(  # Title
        (title_start_x, title_start_y),
        title, fill=text_color, font=bold_font
    )
    drawer.multiline_text(  # Description
        (description_start_x, title_start_y + title_height + gap_between_texts),
        wrapped_description, fill=text_color, font=regular_font, align="center"
    )


# noinspection PyPep8Naming
def __main():
    INPUT_FOLDER_NAME = "input_photos"
    OUTPUT_FOLDER_NAME = "output_photos"
    TEXTS_FILE_NAME = "texts.txt"
    REGULAR_FONT_FILE_NAME = "regular_font.ttf"
    BOLD_FONT_FILE_NAME = "bold_font.ttf"
    TEXTS_FILE_FORMAT = (
        "filename\n"
        "Title\n"
        "Description\n"
        "filename 2\n"
        "Title 2\n"
        "Description 2\n"
        "...\n"
        "\n"
        "If you add # before the filename, it will be ignored. If you add > "
        "before the filename, side gradient will be applied."
    )

    for font_file_name in (REGULAR_FONT_FILE_NAME, BOLD_FONT_FILE_NAME):
        if not os.path.exists(font_file_name):
            raise FileNotFoundError(
                f"No file with font named {REGULAR_FONT_FILE_NAME} found!"
            )

    for path in (INPUT_FOLDER_NAME, OUTPUT_FOLDER_NAME):
        if not os.path.exists(path):
            os.mkdir(path)

    input_photos = os.listdir(INPUT_FOLDER_NAME)

    if not input_photos:
        raise FileNotFoundError(
            "No input photos provided.\n"
            f"You need to put some images in the {INPUT_FOLDER_NAME} folder."
        )
    else:
        try:
            with open(TEXTS_FILE_NAME, "r", encoding="utf-8") as f:
                file_lines = f.read().split("\n")
        except FileNotFoundError:
            raise FileNotFoundError(
                f"File {TEXTS_FILE_NAME} not found! Create it and fill with "
                f"the text of the following format:\n{TEXTS_FILE_FORMAT}"
            )
        if not file_lines:
            raise ValueError(
                f"File {TEXTS_FILE_NAME} is empty. You need to fill it with "
                f"some data of the following format:\n{TEXTS_FILE_FORMAT}"
            )
        if len(file_lines) % 3 != 0:
            raise ValueError(
                f"Amount of lines in {TEXTS_FILE_NAME} isn't multiple of "
                f"three!\n"
                f"I think, I should remind you, how to format it:\n"
                f"{TEXTS_FILE_FORMAT}"
            )
        filenames, titles, descriptions = (file_lines[i::3] for i in range(3))
        # Checking before doing something
        for i, filename in enumerate(filenames):
            if len(filename) == 0:
                raise ValueError(
                    f"Filename on line {(i + 1) * 3} in "
                    f"{TEXTS_FILE_NAME} is missing!"
                )
            if filename[0] == ">":
                filename = filename[1:]
            if filename not in input_photos and filename[0] != "#":
                raise FileNotFoundError(
                    f"File you stated in the {TEXTS_FILE_NAME} (exactly "
                    f"{filename}) is missing in the {INPUT_FOLDER_NAME}!"
                )
        images = []
        image_modes = []
        for filename in filenames:
            if filename[0] == "#":
                images.append(None)  # Stub
            else:
                if filename[0] == ">":
                    filename = filename[1:]
                image = Image.open(f"{INPUT_FOLDER_NAME}/{filename}")
                image_modes.append(image.mode)
                images.append(image.convert("RGBA"))
        for image, old_image_mode, filename, title, description in zip(
            images, image_modes, filenames, titles, descriptions
        ):
            if image is not None:  # It is ignored
                if filename[0] == ">":
                    on_side = True
                    filename = filename[1:]
                else:
                    on_side = False
                add_gradient_with_text(
                    image=image, title=title, description=description,
                    regular_font_file_name=REGULAR_FONT_FILE_NAME,
                    bold_font_file_name=BOLD_FONT_FILE_NAME,
                    on_side=on_side
                )
                image = image.convert(old_image_mode)
                image.save(f"{OUTPUT_FOLDER_NAME}/{filename}")


if __name__ == '__main__':
    __main()
