import json
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from professions import PROFESSION_DICT

SKIP_EXISTING = True


@lru_cache
def _get_empty_draw() -> ImageDraw.ImageDraw:
    return ImageDraw.Draw(Image.new('RGBA', (0, 0)))


def get_text_height(text: str, font: ImageFont.FreeTypeFont, **kwargs) -> float:
    return (_get_empty_draw().multiline_textbbox((0, 0), text, font, 'la', **kwargs)[3]
            - _get_empty_draw().multiline_textbbox((0, 0), text, font, 'ld', **kwargs)[3])


def get_text_width(text: str, font: ImageFont.FreeTypeFont, **kwargs) -> float:
    return (_get_empty_draw().multiline_textbbox((0, 0), text, font, 'la', **kwargs)[2]
            - _get_empty_draw().multiline_textbbox((0, 0), text, font, 'ra', **kwargs)[2])


font_path = r"C:\Users\Administrator\AppData\Local\Microsoft\Windows\Fonts\SourceHanSansSC-Medium.otf"
game_resource_path = Path(r"D:\BioHazard\Projects\github-clone\ArknightsGameResource")
avatar_folder = game_resource_path / "avatar"
with open(game_resource_path / "gamedata/excel/character_table.json", "r", encoding="utf-8") as f:
    character_table = json.load(f)


avatar_pixels = 360
horizontal_padding = 0
elite_width = 64/180
profession_size = 26/180 * 3/2
rarity_height = 25/180 * 4/3
font_size_big = 28/180
font_size_small = 24/180
font_padding = 45/180


elite_images = []
for i in range(3):
    image = Image.open(f"resources/精英_{i}_大图.png")
    width = round(elite_width * avatar_pixels)
    height = round(elite_width * image.height / image.width * avatar_pixels)
    image = image.resize((width, height))
    elite_images.append(image)


profession_images = {}
for profession_id, profession_name in PROFESSION_DICT.items():
    image = Image.open(f"resources/图标_职业_{profession_name}.png")
    image = image.resize((round(profession_size * avatar_pixels), round(profession_size * avatar_pixels)))
    profession_images[profession_id] = image


rarity_images = []
for i in range(6):
    image = Image.open(f"resources/稀有度_黄_{i}.png")
    height = round(rarity_height * avatar_pixels)
    width = round(rarity_height * image.width / image.height * avatar_pixels)
    image = image.resize((width, height))
    rarity_images.append(image)


font_big = ImageFont.truetype(font_path, round(font_size_big * avatar_pixels))
font_small = ImageFont.truetype(font_path, round(font_size_small * avatar_pixels))


def make_avatar(avatar_image: Image.Image, char_name: str, elite_level: int | None, char_rarity: int, char_profession: str) -> Image.Image:
    image_width = round((1 + 2 * horizontal_padding) * avatar_pixels)
    image_height = round((1 + font_padding) * avatar_pixels)
    image = Image.new("RGBA", (image_width, image_height), "#0000")
    draw = ImageDraw.Draw(image)

    # 把头像粘贴到画布中上
    avatar_image = avatar_image.resize((avatar_pixels, avatar_pixels))
    image.paste(avatar_image, ((image_width - avatar_pixels) // 2, 0))

    # 把 elite 图片粘贴到头像的左下角
    if elite_level is not None:
        image.alpha_composite(elite_images[elite_level],
                              (round(horizontal_padding * avatar_pixels), round(avatar_pixels) - elite_images[elite_level].height))

    # 把职业图片粘贴到头像的左上角
    image.alpha_composite(profession_images[char_profession],
                          (round(horizontal_padding * avatar_pixels), 0))

    # 把稀有度图片粘贴到头像的右下角
    image.alpha_composite(rarity_images[char_rarity],
                          (round((horizontal_padding + 1) * avatar_pixels) - rarity_images[char_rarity].width, round((1 - rarity_height) * avatar_pixels)))

    # 画名字
    if get_text_width(char_name, font_big) <= image_width:
        font = font_big
    else:
        font = font_small
    draw.text((image_width // 2, avatar_pixels), char_name, font=font, fill="white", anchor="ma")
    return image


for char_id, char_data in character_table.items():
    if not char_id.startswith("char_"):
        continue

    char_name = char_data["name"]
    char_rarity = char_data["rarity"]
    char_profession = char_data["profession"]
    for elite_level in (None, 0, 1, 2):
        if elite_level in (None, 0, 1):
            avatar_path = avatar_folder / f"{char_id}.png"
        elif elite_level == 2:
            avatar_path = avatar_folder / f"{char_id}_2.png"
        else:
            raise

        if not avatar_path.is_file():
            print(f"Avatar not found: {str(avatar_path)!r} ({char_name!r}, elite {elite_level})")
            continue

        output_path = Path("avatars") / f"{char_name}_{elite_level}.png"
        if SKIP_EXISTING and output_path.is_file():
            # print(f"Skipping existing: {output_path}")
            continue

        print("Making", output_path)
        avatar_image = Image.open(avatar_path)
        image = make_avatar(avatar_image, char_name, elite_level, char_rarity, char_profession)

        image.save(output_path)
