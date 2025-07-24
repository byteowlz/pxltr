from PIL import Image, ImageEnhance
from pathlib import Path
import sys
import argparse
import itertools
from typing import List, Optional
from palettes import PaletteCollection

class ImagePalette:
    def __init__(self, name: str, image: Image.Image):
        self.name = name
        self.image = image

def process_picture_internal(image: Image.Image, output_path: Path, og_width: int, og_height: int, constrast: float, saturation: float, dither: Image.Dither, colors: int, palette: Optional[ImagePalette] = None):
    if constrast != 1.0:
        output_path = output_path.with_name(f"{output_path.stem}_C{constrast}{output_path.suffix}")
        contrast_enhancer = ImageEnhance.Contrast(image)
        image = contrast_enhancer.enhance(constrast)
    if saturation != 1.0:
        output_path = output_path.with_name(f"{output_path.stem}_S{saturation}{output_path.suffix}")
        saturation_enhancer = ImageEnhance.Color(image)
        image = saturation_enhancer.enhance(saturation)
    output_path = output_path.with_name(f"{output_path.stem}_D{dither.name}{output_path.suffix}")
    if palette:
        output_path = output_path.with_name(f"{output_path.stem}_P{palette.name}{output_path.suffix}")
        image = image.quantize(palette=palette.image, dither=dither)
        palette_colors = palette.image.getcolors()
        colors = len(palette_colors) if palette_colors and not colors else colors
    else:
        image = image.quantize(dither=dither)
    if colors and colors > 0:
        output_path = output_path.with_name(f"{output_path.stem}_{colors}{output_path.suffix}")
        image = image.quantize(colors=colors).convert('RGB')
    image = image.resize((og_width, og_height), Image.Resampling.NEAREST)
    image.save(output_path)

def process_picture(input_path: Path, output_path: Path, downscale_width_resolution: int, dither: int, colors: Optional[List[int]] = None, saturation: Optional[List[float]] = None, constrast: Optional[List[float]] = None, palettes: Optional[List[ImagePalette]] = None):
    # Get the input image
    image = Image.open(input_path).convert('RGB')
    og_width, og_height = image.size
    # Downscale the image
    downscale_ratio = downscale_width_resolution / og_width
    new_height = int(og_height * downscale_ratio)
    image = image.resize((downscale_width_resolution, new_height), Image.Resampling.NEAREST)
    contrasts = constrast if constrast else [1.0]
    saturations = saturation if saturation else [1.0]
    dithers = [Image.Dither.FLOYDSTEINBERG, Image.Dither.NONE] if dither == 2 else [Image.Dither.NONE] if dither == 0 else [Image.Dither.FLOYDSTEINBERG]
    colors_list = colors if colors else [0]
    palettes_list = palettes if palettes else [None]
    # Generate all permutations (Cartesian product) of the lists
    all_permutations = itertools.product(contrasts, saturations, dithers, colors_list, palettes_list)
    for contrast_val, saturation_val, dither_val, colors_val, palette_val in all_permutations:
        process_picture_internal(image.copy(), output_path, og_width, og_height, contrast_val, saturation_val, dither_val, colors_val, palette_val)

def main():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Downscale an image, quantize colors, swap palettes and resize back to original size.")

    # Add arguments
    parser.add_argument('input', type=str, help='Path to the directory containing all pictures to process or to a single picture')
    parser.add_argument('output', type=str, help='Path to the directory for the output pictures or to a single picture')
    parser.add_argument('--twr', type=int, help='Target width resolution for the downscale. Height will be calculated to keep the aspect ratio.', default=256)
    parser.add_argument('--palette', nargs='+', type=str, help='Path to the palette image (1x, see https://lospec.com/palette-list) or built-in palette name', default=None)
    parser.add_argument('--list-palettes', action='store_true', help='List all available built-in palettes')
    parser.add_argument('--colors', nargs='+', type=int, help='Force quantization to this color count. If unspecified, colors will be limited to the palette size. If no palette have been specified, no quantization will be done.', default=None)
    parser.add_argument('--constrast', nargs='+', type=float, help='Between 0 and infinity, change picture constrast before processing', default=None)
    parser.add_argument('--saturation', nargs='+', type=float, help='Between 0 and infinity, change picture saturation before processing', default=None)
    parser.add_argument('--dither', type=int, help='Apply dithering to the quantized image. 0 for no dithering, 1 for Floyd-Steinberg dithering, 2 for both', default=0)

    # Check for list-palettes first
    if '--list-palettes' in sys.argv:
        # Initialize palette collection
        palette_collection = PaletteCollection()
        print("Available built-in palettes:")
        for palette_name in palette_collection.list_palettes():
            info = palette_collection.get_palette_info(palette_name)
            print(f"  {palette_name}: {info['description']} ({info['color_count']} colors)")
        sys.exit(0)

    # Check if no arguments are provided
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    # Parse the arguments
    args = parser.parse_args()

    # Initialize palette collection
    palette_collection = PaletteCollection()

    palettes_images = []
    if args.palette:
        if Path(args.palette[0]).is_dir():
            for plt in Path(args.palette[0]).rglob("*.png"):
                palettes_images.append(ImagePalette(plt.stem, Image.open(plt).convert(mode="P", palette=Image.Palette.WEB)))
        else:
            for plt in args.palette:
                # Check if it's a built-in palette first
                if plt.lower() in palette_collection.list_palettes():
                    palette_img = palette_collection.create_palette_image(plt.lower())
                    palettes_images.append(ImagePalette(plt.lower(), palette_img))
                else:
                    # Treat as file path
                    palettes_images.append(ImagePalette(Path(plt).stem, Image.open(plt).convert(mode="P", palette=Image.Palette.WEB)))
    input_path = Path(args.input)
    output_path = Path(args.output)
    if input_path.is_dir():
        if not output_path.is_dir():
            print("If input is a directory, output must also be a directory")
            sys.exit(1)
        for ipt in Path(args.input).rglob("*.png"):
            process_picture(ipt, output_path / ipt.name, args.twr, args.dither, args.colors, args.saturation, args.constrast, palettes_images)
    else:
        if output_path.is_dir():
            output_path = output_path / input_path.name
        process_picture(input_path, output_path, args.twr, args.dither, args.colors, args.saturation, args.constrast, palettes_images)

if __name__ == '__main__':
    main()