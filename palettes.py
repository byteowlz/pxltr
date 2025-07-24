from PIL import Image
from typing import Dict, List, Tuple, Any
import yaml
from pathlib import Path

class PaletteCollection:
    """Collection of well-known pixel art color palettes"""
    
    def __init__(self):
        self.palettes = self._load_palettes_from_yaml()
    
    def _load_palettes_from_yaml(self) -> Dict[str, List[Tuple[int, int, int]]]:
        """Load color palettes from YAML files"""
        palettes = {}
        palettes_dir = Path(__file__).parent / "palettes"
        
        if not palettes_dir.exists():
            # Fallback to hardcoded palettes if directory doesn't exist
            return self._get_fallback_palettes()
        
        for yaml_file in palettes_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    palette_data = yaml.safe_load(f)
                
                name = palette_data.get('name', yaml_file.stem)
                colors = palette_data.get('colors', [])
                
                # Convert colors to tuples
                color_tuples = [tuple(color) for color in colors]
                palettes[name] = color_tuples
                
            except Exception as e:
                print(f"Warning: Could not load palette from {yaml_file}: {e}")
                continue
        
        # If no palettes were loaded, use fallback
        if not palettes:
            return self._get_fallback_palettes()
            
        return palettes
    
    def _get_fallback_palettes(self) -> Dict[str, List[Tuple[int, int, int]]]:
        """Fallback palettes if YAML files cannot be loaded"""
        return {
            "nes": [
                (84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136),
                (68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0),
                (32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
                (0, 50, 60), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                (152, 150, 152), (8, 76, 196), (48, 50, 236), (92, 30, 228),
                (136, 20, 176), (160, 20, 100), (152, 34, 32), (120, 60, 0),
                (84, 90, 0), (40, 114, 0), (8, 124, 0), (0, 118, 40),
                (0, 102, 120), (0, 0, 0), (0, 0, 0), (0, 0, 0),
                (236, 238, 236), (76, 154, 236), (120, 124, 236), (176, 98, 236),
                (228, 84, 236), (236, 88, 180), (236, 106, 100), (212, 136, 32),
                (160, 170, 0), (116, 196, 0), (76, 208, 32), (56, 204, 108),
                (56, 180, 204), (60, 60, 60), (0, 0, 0), (0, 0, 0),
                (236, 238, 236), (168, 204, 236), (188, 188, 236), (212, 178, 236),
                (236, 174, 236), (236, 174, 212), (236, 180, 176), (228, 196, 144),
                (204, 210, 120), (180, 222, 120), (168, 226, 144), (152, 226, 180),
                (160, 214, 228), (160, 162, 160), (0, 0, 0), (0, 0, 0)
            ],
            "gameboy": [
                (15, 56, 15), (48, 98, 48), (139, 172, 15), (155, 188, 15)
            ],
            "pico8": [
                (0, 0, 0), (29, 43, 83), (126, 37, 83), (0, 135, 81),
                (171, 82, 54), (95, 87, 79), (194, 195, 199), (255, 241, 232),
                (255, 0, 77), (255, 163, 0), (255, 236, 39), (0, 228, 54),
                (41, 173, 255), (131, 118, 156), (255, 119, 168), (255, 204, 170)
            ]
        }
    
    def get_palette(self, name: str) -> List[Tuple[int, int, int]]:
        """Get a palette by name"""
        return self.palettes.get(name.lower(), [])
    
    def list_palettes(self) -> List[str]:
        """List all available palette names"""
        return list(self.palettes.keys())
    
    def create_palette_image(self, name: str) -> Image.Image:
        """Create a PIL Image from a palette"""
        colors = self.get_palette(name)
        if not colors:
            raise ValueError(f"Palette '{name}' not found")
        
        # Create a 1-pixel wide image with the palette colors
        img = Image.new('RGB', (len(colors), 1))
        img.putdata(colors)
        return img.convert('P')
    
    def get_palette_info(self, name: str) -> Dict[str, Any]:
        """Get information about a palette"""
        colors = self.get_palette(name)
        if not colors:
            return {}
        
        # Try to load metadata from YAML file
        metadata = self._load_palette_metadata(name)
        
        info = {
            "name": name,
            "color_count": len(colors),
            "colors": colors,
            "description": metadata.get("description", self._get_palette_description(name)),
            "source": metadata.get("source", "Unknown"),
            "notes": metadata.get("notes", [])
        }
        return info
    
    def _load_palette_metadata(self, name: str) -> Dict[str, Any]:
        """Load metadata for a palette from its YAML file"""
        palettes_dir = Path(__file__).parent / "palettes"
        yaml_file = palettes_dir / f"{name}.yaml"
        
        if not yaml_file.exists():
            return {}
        
        try:
            with open(yaml_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}
    
    def _get_palette_description(self, name: str) -> str:
        """Get description for a palette"""
        descriptions = {
            "nes": "Nintendo Entertainment System 54-color palette",
            "gameboy": "Original Game Boy 4-color green palette",
            "gameboy_pocket": "Game Boy Pocket improved 4-color palette",
            "pico8": "PICO-8 fantasy console 16-color palette",
            "commodore64": "Commodore 64 16-color palette",
            "cga": "IBM CGA 16-color palette",
            "msx": "MSX computer 16-color palette",
            "apple2": "Apple II 16-color palette",
            "zx_spectrum": "ZX Spectrum 16-color palette",
            "atari2600": "Atari 2600 16-color palette subset",
            "amiga": "Amiga OCS/ECS 32-color palette"
        }
        return descriptions.get(name, f"Color palette: {name}")