#!/usr/bin/env python3
"""
iOS ITHMB Thumbnail Image Extractor

This script extracts thumbnail images from iOS ITHMB files (iTunes Thumbnail).
ITHMB files contain raw binary thumbnail data without standard image headers.
"""

import sys
import os
import argparse
from pathlib import Path
from PIL import Image
import struct


class IthmhExtractor:
    """Extract thumbnail images from ITHMB files."""
    
    # Common ITHMB thumbnail sizes for different iOS devices
    KNOWN_SIZES = {
        '160x120': (160, 120),      # iPhone, iPad standard
        '320x240': (320, 240),      # iPhone 4+, iPad 2+
        '158x118': (158, 118),      # iPod Video
        '130x88': (130, 88),        # iPod Nano
        'auto': None,               # Auto-detect
    }
    
    # Color modes
    COLOR_MODES = {
        'RGB': ('RGB', 3),
        'RGBA': ('RGBA', 4),
        'BGR': ('RGB', 3),  # BGR is treated as RGB (bytes will be reversed)
    }
    
    def __init__(self, ithmb_path, width=160, height=120, color_mode='RGB', output_dir=None):
        """
        Initialize the extractor.
        
        Args:
            ithmb_path: Path to the ITHMB file
            width: Thumbnail width in pixels (default: 160)
            height: Thumbnail height in pixels (default: 120)
            color_mode: Color mode - 'RGB', 'RGBA', or 'BGR' (default: 'RGB')
            output_dir: Output directory for PNG files (default: current directory)
        """
        self.ithmb_path = Path(ithmb_path)
        self.width = width
        self.height = height
        self.color_mode = color_mode.upper()
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        
        # Validate color mode
        if self.color_mode not in self.COLOR_MODES:
            raise ValueError(f"Invalid color mode: {color_mode}. Must be RGB, RGBA, or BGR.")
        
        # Validate file exists
        if not self.ithmb_path.exists():
            raise FileNotFoundError(f"ITHMB file not found: {self.ithmb_path}")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get file size for validation
        self.file_size = self.ithmb_path.stat().st_size
        self.bytes_per_pixel = self.COLOR_MODES[self.color_mode][1]
        self.bytes_per_image = self.width * self.height * self.bytes_per_pixel
    
    def extract(self, verbose=True):
        """
        Extract all thumbnail images from the ITHMB file.
        
        Args:
            verbose: Print progress information (default: True)
            
        Returns:
            Number of successfully extracted images
        """
        if verbose:
            print(f"Extracting ITHMB file: {self.ithmb_path}")
            print(f"Parameters: {self.width}x{self.height}, {self.color_mode}, {self.bytes_per_pixel} bytes/pixel")
            print(f"File size: {self.file_size} bytes")
            print(f"Output directory: {self.output_dir}")
            print()
        
        extracted_count = 0
        
        try:
            with open(self.ithmb_path, 'rb') as f:
                image_index = 1
                
                while True:
                    # Read raw pixel data
                    raw_data = f.read(self.bytes_per_image)
                    
                    # Check if we have enough data for a complete image
                    if len(raw_data) < self.bytes_per_image:
                        if len(raw_data) > 0 and verbose:
                            print(f"Warning: Incomplete image data at the end of file ({len(raw_data)} bytes). Skipping.")
                        break
                    
                    try:
                        # Handle BGR format by converting to RGB
                        if self.color_mode == 'BGR':
                            raw_data = self._bgr_to_rgb(raw_data)
                            mode = 'RGB'
                        else:
                            mode = self.COLOR_MODES[self.color_mode][0]
                        
                        # Create image from raw bytes
                        img = Image.frombytes(mode, (self.width, self.height), raw_data)
                        
                        # Generate output filename with zero-padded index
                        output_filename = f"thumb_{image_index:04d}.png"
                        output_path = self.output_dir / output_filename
                        
                        # Save as PNG
                        img.save(output_path, 'PNG')
                        
                        if verbose:
                            print(f"✓ Extracted: {output_filename}")
                        
                        extracted_count += 1
                        image_index += 1
                        
                    except Exception as e:
                        print(f"Error processing image {image_index}: {e}")
                        image_index += 1
                        continue
        
        except Exception as e:
            print(f"Error reading ITHMB file: {e}")
            return extracted_count
        
        if verbose:
            print()
            print(f"Extraction complete: {extracted_count} images extracted.")
        
        return extracted_count
    
    @staticmethod
    def _bgr_to_rgb(data):
        """
        Convert BGR byte sequence to RGB.
        
        Args:
            data: Raw BGR data
            
        Returns:
            RGB data with channels swapped
        """
        result = bytearray(len(data))
        for i in range(0, len(data), 3):
            result[i] = data[i + 2]      # B -> R
            result[i + 1] = data[i + 1]  # G stays
            result[i + 2] = data[i]      # R -> B
        return bytes(result)
    
    @staticmethod
    def auto_detect_size(ithmb_path):
        """
        Attempt to auto-detect thumbnail size from file.
        
        Common sizes and their approximate file sizes:
        - 160x120 RGB: 57,600 bytes per image
        - 320x240 RGB: 230,400 bytes per image
        
        Args:
            ithmb_path: Path to ITHMB file
            
        Returns:
            Tuple of (width, height) or None if unable to detect
        """
        file_size = Path(ithmb_path).stat().st_size
        
        # Try to match against known sizes
        # Assuming typical RGB (3 bytes per pixel)
        for (w, h), bytes_count in [
            ((320, 240), 230400),
            ((160, 120), 57600),
            ((158, 118), 55884),
            ((130, 88), 34320),
        ]:
            if file_size % bytes_count == 0:
                num_images = file_size // bytes_count
                return (w, h, num_images)
        
        return None


def main():
    """Command-line interface for ITHMB extraction."""
    
    parser = argparse.ArgumentParser(
        description='Extract thumbnail images from iOS ITHMB files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract with default settings (160x120 RGB)
  python ithmb_extractor.py image.ithmb
  
  # Extract with custom size
  python ithmb_extractor.py image.ithmb -w 320 -H 240
  
  # Extract with RGBA format
  python ithmb_extractor.py image.ithmb -m RGBA
  
  # Auto-detect size and extract
  python ithmb_extractor.py image.ithmb --auto-detect
  
  # Specify output directory
  python ithmb_extractor.py image.ithmb -o ./thumbnails
        """
    )
    
    parser.add_argument(
        'ithmb_file',
        help='Path to the ITHMB file'
    )
    
    parser.add_argument(
        '-w', '--width',
        type=int,
        default=160,
        help='Thumbnail width in pixels (default: 160)'
    )
    
    parser.add_argument(
        '-H', '--height',
        type=int,
        default=120,
        help='Thumbnail height in pixels (default: 120)'
    )
    
    parser.add_argument(
        '-m', '--mode',
        choices=['RGB', 'RGBA', 'BGR'],
        default='RGB',
        help='Color mode (default: RGB)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output directory for PNG files (default: current directory)'
    )
    
    parser.add_argument(
        '--auto-detect',
        action='store_true',
        help='Auto-detect thumbnail size from file'
    )
    
    parser.add_argument(
        '--list-sizes',
        action='store_true',
        help='List known thumbnail sizes and exit'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    
    args = parser.parse_args()
    
    # Handle --list-sizes
    if args.list_sizes:
        print("Known ITHMB thumbnail sizes:")
        for size_name, dimensions in IthmhExtractor.KNOWN_SIZES.items():
            if dimensions:
                print(f"  {size_name}: {dimensions[0]}x{dimensions[1]} pixels")
        return 0
    
    try:
        # Auto-detect size if requested
        if args.auto_detect:
            detection_result = IthmhExtractor.auto_detect_size(args.ithmb_file)
            if detection_result:
                width, height, num_images = detection_result
                if not args.quiet:
                    print(f"Auto-detected: {width}x{height} ({num_images} images expected)\n")
                args.width = width
                args.height = height
            else:
                print("Warning: Could not auto-detect size. Using defaults (160x120).")
        
        # Create extractor and extract images
        extractor = IthmhExtractor(
            args.ithmb_file,
            width=args.width,
            height=args.height,
            color_mode=args.mode,
            output_dir=args.output
        )
        
        count = extractor.extract(verbose=not args.quiet)
        
        if count == 0:
            print("No images extracted. Check file format and parameters.")
            return 1
        
        return 0
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
