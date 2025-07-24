# pxltr - a pixel art color tool

A fully featured CLI tool for transforming images with retro color palettes and pixel art effects.

## Installation

Install using uv (recommended):

```bash
uv sync 
```

## Usage

The tool provides several commands for different operations:

### Process Images

Transform images with pixel art effects:

```bash
cli process input.png output.png [OPTIONS]
```

**Options:**

- `--width, -w`: Target width resolution for downscaling (default: 256)
- `--palette, -p`: Palette name or path to palette image (can be used multiple times)
- `--colors, -c`: Force quantization to specific color counts (can be used multiple times)
- `--contrast`: Adjust contrast (0.0 to infinity, can be used multiple times)
- `--saturation, -s`: Adjust saturation (0.0 to infinity, can be used multiple times)
- `--dither, -d`: Dithering method: `none`, `floyd`, or `both` (default: none)
- `--verbose, -v`: Enable verbose output

**Examples:**

```bash
# Basic usage with built-in palette
cli process input.png output.png --palette gameboy

# Multiple effects and settings
cli process input.png output.png \
  --palette nes \
  --width 128 \
  --contrast 1.2 \
  --saturation 0.8 \
  --dither floyd

# Process entire directory
cli process input_dir/ output_dir/ --palette pico8

# Multiple palettes and color counts
cli process input.png output.png \
  --palette gameboy nes \
  --colors 8 16 \
  --contrast 1.0 1.2
```

### List Available Palettes

View all built-in color palettes:

```bash
cli palettes
```

### Show Palette Details

Display colors in a specific palette:

```bash
cli show-palette gameboy
cli show-palette nes --output nes_palette.png
```

### Extract Palette from Image

Extract a color palette from an existing image:

```bash
cli extract-palette input.png --colors 16
cli extract-palette input.png --colors 8 --output extracted_palette.png
```

## Built-in Color Palettes

The tool includes a comprehensive collection of retro gaming and computer palettes:

| Palette | Description | Colors |
|---------|-------------|--------|
| **nes** | Nintendo Entertainment System palette | 54 |
| **gameboy** | Original Game Boy green palette | 4 |
| **gameboy_pocket** | Game Boy Pocket improved palette | 4 |
| **pico8** | PICO-8 fantasy console palette | 16 |
| **commodore64** | Commodore 64 palette | 16 |
| **cga** | IBM CGA palette | 16 |
| **msx** | MSX computer palette | 16 |
| **apple2** | Apple II palette | 16 |
| **zx_spectrum** | ZX Spectrum palette | 16 |
| **atari2600** | Atari 2600 palette subset | 16 |
| **amiga** | Amiga OCS/ECS palette | 32 |

## Features

- **Multiple Input Formats**: Supports PNG, JPG, and JPEG files
- **Batch Processing**: Process entire directories of images
- **Rich Output**: Beautiful terminal output with progress bars and color previews
- **Flexible Options**: Mix and match multiple palettes, colors, and effects
- **Custom Palettes**: Use your own palette images alongside built-in ones
- **Parameter Combinations**: Generate all combinations of specified parameters
- **Palette Extraction**: Extract color palettes from existing images
- **Visual Palette Display**: Preview palettes with color swatches in the terminal

## Advanced Usage

### Multiple Parameter Combinations

When you specify multiple values for parameters, the tool generates all combinations:

```bash
# This creates 4 output variations (2 contrasts × 2 saturations)
cli process input.png output.png \
  --contrast 1.0 1.2 \
  --saturation 0.8 1.0
```

### Custom Palettes

You can use custom palette images (1-pixel tall images with your desired colors):

```bash
cli process input.png output.png --palette custom_palette.png
```

### Directory Processing

Process all images in a directory:

```bash
cli process images/ processed_images/ --palette gameboy --verbose
```

## Attribution

Adapted from [PixelArtColorsTool](https://github.com/Mardjak/PixelArtColorsTool)
