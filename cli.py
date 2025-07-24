#!/usr/bin/env python3
"""
PixelArt Colors Tool - A fully featured CLI for pixel art color palette processing
"""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from pathlib import Path
from typing import List, Optional, Tuple
import sys

from palette_swap import process_picture, ImagePalette
from palettes import PaletteCollection

console = Console()

@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="1.0.0", prog_name="pixelart-colors")
def cli(ctx):
    """PixelArt Colors Tool - Transform images with retro color palettes
    
    A powerful CLI tool for downscaling images, applying color quantization,
    swapping palettes, and creating pixel art effects.
    """
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(
            "[bold blue]PixelArt Colors Tool[/bold blue]\n\n"
            "Transform your images with retro color palettes!\n\n"
            "Use [bold]--help[/bold] to see available commands.",
            title="Welcome"
        ))

@cli.command()
@click.argument('input_path', type=click.Path(exists=True, path_type=Path))
@click.argument('output_path', type=click.Path(path_type=Path))
@click.option('--width', '-w', default=256, help='Target width resolution for downscaling')
@click.option('--palette', '-p', multiple=True, help='Palette name or path to palette image')
@click.option('--colors', '-c', multiple=True, type=int, help='Force quantization to specific color counts')
@click.option('--contrast', multiple=True, type=float, help='Adjust contrast (0.0 to infinity)')
@click.option('--saturation', '-s', multiple=True, type=float, help='Adjust saturation (0.0 to infinity)')
@click.option('--dither', '-d', type=click.Choice(['none', 'floyd', 'both']), default='none',
              help='Dithering method: none, floyd-steinberg, or both')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def process(input_path: Path, output_path: Path, width: int, palette: Tuple[str], 
           colors: Tuple[int], contrast: Tuple[float], saturation: Tuple[float], 
           dither: str, verbose: bool):
    """Process images with pixel art effects
    
    INPUT_PATH: Path to image file or directory
    OUTPUT_PATH: Path for output file or directory
    """
    try:
        # Validate input/output paths
        if input_path.is_dir() and not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        elif input_path.is_dir() and output_path.is_file():
            console.print("[red]Error:[/red] If input is a directory, output must also be a directory")
            sys.exit(1)
        
        # Initialize palette collection
        palette_collection = PaletteCollection()
        
        # Process palettes
        palette_images = []
        if palette:
            for plt in palette:
                if plt.lower() in palette_collection.list_palettes():
                    palette_img = palette_collection.create_palette_image(plt.lower())
                    palette_images.append(ImagePalette(plt.lower(), palette_img))
                    if verbose:
                        console.print(f"[green]✓[/green] Loaded built-in palette: {plt}")
                else:
                    plt_path = Path(plt)
                    if plt_path.exists():
                        from PIL import Image
                        palette_img = Image.open(plt_path).convert(mode="P", palette=Image.Palette.WEB)
                        palette_images.append(ImagePalette(plt_path.stem, palette_img))
                        if verbose:
                            console.print(f"[green]✓[/green] Loaded custom palette: {plt}")
                    else:
                        console.print(f"[red]Error:[/red] Palette not found: {plt}")
                        sys.exit(1)
        
        # Convert dither option
        dither_map = {
            'none': 0,
            'floyd': 1,
            'both': 2
        }
        dither_value = dither_map[dither]
        
        # Process files
        if input_path.is_dir():
            image_files = list(input_path.rglob("*.png")) + list(input_path.rglob("*.jpg")) + list(input_path.rglob("*.jpeg"))
            
            if not image_files:
                console.print("[yellow]Warning:[/yellow] No image files found in directory")
                return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processing images...", total=len(image_files))
                
                for img_file in image_files:
                    if verbose:
                        console.print(f"Processing: {img_file.name}")
                    
                    output_file = output_path / img_file.name
                    process_picture(
                        img_file, output_file, width, dither_value,
                        list(colors) if colors else None,
                        list(saturation) if saturation else None,
                        list(contrast) if contrast else None,
                        palette_images if palette_images else None
                    )
                    progress.advance(task)
            
            console.print(f"[green]✓[/green] Processed {len(image_files)} images")
        else:
            if output_path.is_dir():
                output_path = output_path / input_path.name
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Processing image...", total=1)
                
                process_picture(
                    input_path, output_path, width, dither_value,
                    list(colors) if colors else None,
                    list(saturation) if saturation else None,
                    list(contrast) if contrast else None,
                    palette_images if palette_images else None
                )
                progress.advance(task)
            
            console.print(f"[green]✓[/green] Image processed: {output_path}")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        if verbose:
            console.print_exception()
        sys.exit(1)

@cli.command()
def palettes():
    """List all available built-in color palettes"""
    palette_collection = PaletteCollection()
    
    table = Table(title="Available Built-in Palettes")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Colors", justify="right", style="magenta")
    
    for palette_name in sorted(palette_collection.list_palettes()):
        info = palette_collection.get_palette_info(palette_name)
        table.add_row(
            palette_name,
            info['description'],
            str(info['color_count'])
        )
    
    console.print(table)

@cli.command()
@click.argument('palette_name')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Save palette as image file')
def show_palette(palette_name: str, output: Optional[Path]):
    """Show colors in a specific palette
    
    PALETTE_NAME: Name of the built-in palette to display
    """
    palette_collection = PaletteCollection()
    
    if palette_name.lower() not in palette_collection.list_palettes():
        console.print(f"[red]Error:[/red] Palette '{palette_name}' not found")
        console.print("Use [bold]pixelart-colors palettes[/bold] to see available palettes")
        sys.exit(1)
    
    info = palette_collection.get_palette_info(palette_name.lower())
    
    console.print(f"\n[bold]{info['name'].upper()}[/bold] - {info['description']}")
    console.print(f"Colors: {info['color_count']}\n")
    
    # Display colors in a grid
    colors_per_row = 8
    for i in range(0, len(info['colors']), colors_per_row):
        row_colors = info['colors'][i:i + colors_per_row]
        color_blocks = []
        for r, g, b in row_colors:
            # Create colored block using rich color
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            color_blocks.append(f"[on {hex_color}]  [/on {hex_color}] {hex_color}")
        console.print(" ".join(color_blocks))
    
    if output:
        try:
            palette_img = palette_collection.create_palette_image(palette_name.lower())
            # Create a larger version for better visibility
            from PIL import Image
            large_palette = palette_img.resize((info['color_count'] * 32, 32), Image.Resampling.NEAREST)
            large_palette.save(output)
            console.print(f"\n[green]✓[/green] Palette saved to: {output}")
        except Exception as e:
            console.print(f"[red]Error saving palette:[/red] {str(e)}")

@cli.command()
@click.argument('input_path', type=click.Path(exists=True, path_type=Path))
@click.option('--colors', '-c', default=16, help='Number of colors to extract')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Save extracted palette as image')
def extract_palette(input_path: Path, colors: int, output: Optional[Path]):
    """Extract color palette from an image
    
    INPUT_PATH: Path to the image file
    """
    try:
        from PIL import Image
        
        # Load and process image
        img = Image.open(input_path).convert('RGB')
        quantized = img.quantize(colors=colors)
        palette_colors = quantized.getpalette()
        
        # Convert palette to RGB tuples
        rgb_colors = []
        if palette_colors:
            for i in range(0, len(palette_colors), 3):
                if i + 2 < len(palette_colors):
                    rgb_colors.append((palette_colors[i], palette_colors[i+1], palette_colors[i+2]))
        
        console.print(f"\n[bold]Extracted Palette[/bold] from {input_path.name}")
        console.print(f"Colors: {len(rgb_colors)}\n")
        
        # Display colors
        colors_per_row = 8
        for i in range(0, len(rgb_colors), colors_per_row):
            row_colors = rgb_colors[i:i + colors_per_row]
            color_blocks = []
            for r, g, b in row_colors:
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                color_blocks.append(f"[on {hex_color}]  [/on {hex_color}] {hex_color}")
            console.print(" ".join(color_blocks))
        
        if output:
            # Create palette image
            palette_img = Image.new('RGB', (len(rgb_colors), 1))
            palette_img.putdata(rgb_colors)
            large_palette = palette_img.resize((len(rgb_colors) * 32, 32), Image.Resampling.NEAREST)
            large_palette.save(output)
            console.print(f"\n[green]✓[/green] Palette saved to: {output}")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    cli()