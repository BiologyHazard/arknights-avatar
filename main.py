import json
import logging
import multiprocessing
from functools import lru_cache
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

from professions import PROFESSION_DICT

# 日志配置
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


@lru_cache
def _get_empty_draw() -> ImageDraw.ImageDraw:
    return ImageDraw.Draw(Image.new("RGBA", (0, 0)))


def get_text_height(text: str, font: ImageFont.FreeTypeFont, **kwargs) -> float:
    return (
        _get_empty_draw().multiline_textbbox((0, 0), text, font, "la", **kwargs)[3]
        - _get_empty_draw().multiline_textbbox((0, 0), text, font, "ld", **kwargs)[3]
    )


def get_text_width(text: str, font: ImageFont.FreeTypeFont, **kwargs) -> float:
    return (
        _get_empty_draw().multiline_textbbox((0, 0), text, font, "la", **kwargs)[2]
        - _get_empty_draw().multiline_textbbox((0, 0), text, font, "ra", **kwargs)[2]
    )


skip_existing = True
"""是否跳过已存在的文件"""

resampling_method = Resampling.BICUBIC
"""PIL 图像缩放时使用的采样方法"""

font_path = Path("fonts/Alibaba-PuHuiTi-Bold.ttf")
game_resource_folder = Path("ArknightsGameResource")
avatar_background_path = Path("resources/干员头像底图.png")
avatar_folder = game_resource_folder / "avatar"
output_folder = Path("output")

# 图像参数
avatar_pixels = 360
horizontal_margin = 0
elite_width = 64 / 180
profession_size = 26 / 180 * 3 / 2
rarity_height = 25 / 180 * 4 / 3
font_size_big = 28 / 180
font_size_small = 24 / 180
spacing = 6 / 180
font_height = 40 / 180


def make_avatar(
    avatar_image: Image.Image,
    char_name: str,
    elite_level: int | None,
    char_rarity: int,
    char_profession: str,
) -> Image.Image:
    image_width = round((1 + 2 * horizontal_margin) * avatar_pixels)
    image_height = round((1 + spacing + font_height) * avatar_pixels)
    image = Image.new("RGBA", (image_width, image_height), "#0000")
    draw = ImageDraw.Draw(image)

    # 把背景图粘贴到画布中上
    image.alpha_composite(
        avatar_background_image, ((image_width - avatar_pixels) // 2, 0)
    )

    # 把头像粘贴到画布中上
    avatar_image = avatar_image.resize(
        (avatar_pixels, avatar_pixels), resample=resampling_method
    )
    image.alpha_composite(avatar_image, ((image_width - avatar_pixels) // 2, 0))

    # 把 elite 图片粘贴到头像的左下角
    if elite_level is not None:
        image.alpha_composite(
            elite_images[elite_level],
            (
                round(horizontal_margin * avatar_pixels),
                round(avatar_pixels) - elite_images[elite_level].height,
            ),
        )

    # 把职业图片粘贴到头像的左上角
    image.alpha_composite(
        profession_images[char_profession],
        (round(horizontal_margin * avatar_pixels), 0),
    )

    # 把稀有度图片粘贴到头像的右下角
    image.alpha_composite(
        rarity_images[char_rarity],
        (
            round((horizontal_margin + 1) * avatar_pixels)
            - rarity_images[char_rarity].width,
            round((1 - rarity_height) * avatar_pixels),
        ),
    )

    # 名字框
    draw.rectangle(
        ((0, round(avatar_pixels * (1 + spacing))), (image_width, image_height)),
        fill="#181818",
        outline=None,
    )

    # 画名字
    if get_text_width(char_name, font_big) <= image_width:
        font = font_big
    else:
        font = font_small
    draw.text(
        (image_width // 2, round(avatar_pixels * (1 + spacing + font_height / 2))),
        char_name,
        font=font,
        fill="white",
        anchor="mm",
    )
    return image


def make_char_avatar_and_save(char_id: str, char_data: dict[str, Any]) -> None:
    if not char_id.startswith("char_"):
        return

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
            logging.warning(
                f"Avatar not found: {str(avatar_path)!r} ({char_name!r}, "
                f"elite {elite_level})"
            )
            continue

        filename = (
            f"avatar_{char_name}.png"
            if elite_level is None
            else f"avatar_{char_name}_{elite_level}.png"
        )
        output_path = Path("output") / filename
        if skip_existing and output_path.is_file():
            logging.debug(f"Skipping existing: {output_path}")
            continue

        logging.info(f"Making {output_path}")
        avatar_image = Image.open(avatar_path)
        image = make_avatar(
            avatar_image, char_name, elite_level, char_rarity, char_profession
        )

        image.save(output_path)


# 加载图片素材
elite_images = []
for i in range(3):
    image = Image.open(f"resources/精英_{i}_大图.png")
    width = round(elite_width * avatar_pixels)
    height = round(elite_width * image.height / image.width * avatar_pixels)
    image = image.resize((width, height), resample=resampling_method)
    elite_images.append(image)

profession_images = {}
for profession_id, profession_name in PROFESSION_DICT.items():
    image = Image.open(f"resources/图标_职业_{profession_name}.png")
    image = image.resize(
        (
            round(profession_size * avatar_pixels),
            round(profession_size * avatar_pixels),
        ),
        resample=resampling_method,
    )
    profession_images[profession_id] = image

rarity_images = []
for i in range(6):
    image = Image.open(f"resources/稀有度_黄_{i}.png")
    height = round(rarity_height * avatar_pixels)
    width = round(rarity_height * image.width / image.height * avatar_pixels)
    image = image.resize((width, height), resample=resampling_method)
    rarity_images.append(image)

avatar_background_image = Image.open(avatar_background_path).resize(
    (avatar_pixels, avatar_pixels), resample=resampling_method
)

# 加载字体
font_big = ImageFont.truetype(font_path, round(font_size_big * avatar_pixels))
font_small = ImageFont.truetype(font_path, round(font_size_small * avatar_pixels))


if __name__ == "__main__":
    # 创建输出文件夹
    output_folder.mkdir(parents=True, exist_ok=True)

    # 读取角色数据
    with open(
        game_resource_folder / "gamedata/excel/character_table.json",
        "r",
        encoding="utf-8",
    ) as f:
        character_table = json.load(f)

    # 多进程生成头像
    with multiprocessing.Pool() as pool:
        pool.starmap(make_char_avatar_and_save, character_table.items())
