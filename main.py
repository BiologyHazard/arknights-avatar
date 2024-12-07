from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

from professions import PROFESSION_DICT

font_path = r"C:\Windows\Fonts\SourceHanSansCN-Medium.otf"
game_resource_path = Path(r"D:\BioHazard\Projects\github-clone\ArknightsGameResource")
avatar_folder = game_resource_path / "avatar"
with open(game_resource_path / "gamedata/excel/character_table.json", "r", encoding="utf-8") as f:
    character_table = json.load(f)


avatar_pixels = 360
horizontal_padding = 0
elite_size = 64/180
profession_size = 26/180 * 3/2
# rarity_width = 89/180 * 4/3
rarity_height = 25/180 * 4/3
font_size_big = 28/180
font_size_small = 24/180
font_padding = 40/180

elite_pixels = round(elite_size * avatar_pixels)
# rarity_width_pixels = round(rarity_width * avatar_pixels)
# rarity_height_pixels = round(rarity_height * avatar_pixels)


elite_images = []
for i in range(3):
    elite_image = Image.open(f"resources/精英_{i}_大图.png")
    # 把图片嵌入 256x256 的透明背景的正中
    image = Image.new("RGBA", (256, 256))
    image.paste(elite_image, (128 - elite_image.width // 2, 128 - elite_image.height // 2))
    image = image.resize((elite_pixels, elite_pixels))
    elite_images.append(image)


profession_images = {}
for profession_id, profession_name in PROFESSION_DICT.items():
    profession_image = Image.open(f"resources/图标_职业_{profession_name}.png")
    profession_image = profession_image.resize((round(profession_size * avatar_pixels), round(profession_size * avatar_pixels)))
    profession_images[profession_id] = profession_image


rarity_images = []
for i in range(6):
    rarity_image = Image.open(f"resources/稀有度_黄_{i}.png")
    height = round(rarity_height * avatar_pixels)
    width = round(rarity_height * rarity_image.width / rarity_image.height * avatar_pixels)
    # 把图片嵌入 89x25 的透明背景的右下角
    # image = Image.new("RGBA", (89, 25))
    # image.paste(rarity_image, (89 - rarity_image.width, 25 - rarity_image.height))
    image = image.resize((width, height))
    rarity_images.append(image)


for char_id, char_data in character_table.items():
    if not char_id.startswith("char_"):
        continue

    char_name = char_data["name"]
    char_rarity = char_data["rarity"]
    char_profession = char_data["profession"]
    for elite_level in (0, 1, 2):
        if elite_level in (0, 1):
            avatar_path = avatar_folder / f"{char_id}.png"
        elif elite_level == 2:
            avatar_path = avatar_folder / f"{char_id}_2.png"
        if not avatar_path.is_file():
            print(f"Avatar not found: {str(avatar_path)!r} ({char_name!r}, elite {elite_level})")
            continue

        image_width = round((1 + 2 * horizontal_padding) * avatar_pixels)
        image_height = round((1 + font_padding) * avatar_pixels)
        image = Image.new("RGBA", (image_width, image_height), "#0000")
        draw = ImageDraw.Draw(image)

        avatar = Image.open(avatar_path).resize((avatar_pixels, avatar_pixels))
        image.paste(avatar, ((image_width - avatar_pixels) // 2, 0))
        # 把 elite 图片粘贴到头像的左下角
        image.alpha_composite(elite_images[elite_level], (round(horizontal_padding * avatar_pixels), round((1 - elite_size + 5/180) * avatar_pixels)))
        # 把职业图片粘贴到头像的左上角
        image.alpha_composite(profession_images[char_profession], (round(horizontal_padding * avatar_pixels), 0))
        # 把稀有度图片粘贴到头像的右下角
        image.alpha_composite(rarity_images[char_rarity], (round((horizontal_padding + 1 - rarity_width) * avatar_pixels), round((1 - rarity_height) * avatar_pixels)))

        # 画名字
        font_size = font_size_big if len(char_name) <= 6 else font_size_small
        font = ImageFont.truetype(font_path, round(font_size * avatar_pixels))
        draw.text((image_width // 2, avatar_pixels), char_name, font=font, fill="white", anchor="ma")

        image.save(Path("output") / f"{char_name}_{elite_level}.png")
