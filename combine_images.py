from collections.abc import Sequence
from pathlib import Path

from PIL import Image

avatars_path = Path("output")


def process_file_name(s: str) -> str:
    """
    - "见行者" -> "avatar_见行者"
    - "见行者0" -> "avatar_见行者_0"
    - "见行者1" -> "avatar_见行者_1"
    - "见行者2" -> "avatar_见行者_2"
    """
    if s[-1].isdigit():
        return f"avatar_{s[:-1]}_{s[-1]}"
    return f"avatar_{s}"


def get_paths(s: str) -> list[Path]:
    return [avatars_path / f"{process_file_name(p)}.png" for p in s.split()]


def combine_images(images: Sequence[Image.Image], gap: float) -> Image.Image:
    if not images:
        return Image.new("RGBA", (0, 0), "#00000000")

    image_width = images[0].width
    image_height = max(image.height for image in images)
    gap_width = round(image_width * gap)
    total_width = len(images) * image_width + (len(images) - 1) * gap_width

    combined = Image.new("RGBA", (total_width, image_height), "#00000000")
    x_offset = 0
    for image in images:
        combined.paste(image, (x_offset, 0))
        x_offset += image_width + gap_width

    return combined


def main():
    while True:
        input_str = input(
            "Enter gap and image names (gap followed by space-separated names) "
            "or 'exit' to quit: "
        ).strip()
        if input_str.lower() == "exit":
            break

        parts = input_str.split()
        if len(parts) < 2:
            print("Please enter gap followed by at least one image name.")
            continue

        try:
            gap = float(parts[0])
        except ValueError:
            print("Invalid gap value. Please enter a number.")
            continue

        image_names = " ".join(parts[1:])
        image_paths = get_paths(image_names)
        images = [Image.open(path) for path in image_paths if path.is_file()]

        if not images:
            print("No valid images found.")
            continue

        combined_image = combine_images(images, gap=gap)
        output_path = Path("combined_image.png")
        combined_image.save(output_path)
        print(f"Combined image saved to {output_path}")


if __name__ == "__main__":
    main()
