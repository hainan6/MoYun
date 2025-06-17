"""
Image Processing Module
Handles image manipulation operations including cropping, resizing, and optimization
"""
import os
from enum import Enum
from pathlib import Path
from typing import Tuple, Optional

import cv2
import numpy as np


class ImageProcessingError(Exception):
    """Custom exception for image processing errors"""
    pass


class AlignmentOption(Enum):
    """Image alignment options"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


class ImageProcessor:
    """
    Modern image processing with improved error handling and type safety
    """
    
    @staticmethod
    def get_image_dimensions(image_path: str) -> Tuple[int, int]:
        """
        Get image dimensions (height, width)
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (height, width)
            
        Raises:
            ImageProcessingError: If image cannot be read
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError(f"Image file not found: {image_path}")
        
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ImageProcessingError(f"Failed to read image: {image_path}")
            
            return image.shape[0], image.shape[1]
            
        except Exception as e:
            raise ImageProcessingError(f"Error reading image dimensions: {e}")
    
    @staticmethod
    def crop_image(
        image_path: str,
        target_width: int,
        target_height: int,
        horizontal_align: AlignmentOption = AlignmentOption.CENTER,
        vertical_align: AlignmentOption = AlignmentOption.CENTER,
        backup_original: bool = False
    ) -> bool:
        """
        Crop image to specified dimensions
        
        Args:
            image_path: Path to the image file
            target_width: Desired width after cropping
            target_height: Desired height after cropping
            horizontal_align: Horizontal alignment for cropping
            vertical_align: Vertical alignment for cropping
            backup_original: Whether to create backup of original image
            
        Returns:
            True if cropping successful, False if target dimensions exceed original
            
        Raises:
            ImageProcessingError: If image processing fails
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError(f"Image file not found: {image_path}")
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ImageProcessingError(f"Failed to read image: {image_path}")
            
            original_height, original_width = image.shape[:2]
            
            # Check if target dimensions are valid
            if target_width > original_width or target_height > original_height:
                return False
            
            # Create backup if requested
            if backup_original:
                backup_path = f"{image_path}.backup"
                cv2.imwrite(backup_path, image)
            
            # Calculate cropping coordinates
            width_range = ImageProcessor._calculate_crop_range(
                original_width, target_width, horizontal_align
            )
            height_range = ImageProcessor._calculate_crop_range(
                original_height, target_height, vertical_align
            )
            
            # Perform cropping
            cropped_image = image[
                height_range[0]:height_range[1],
                width_range[0]:width_range[1]
            ]
            
            # Save cropped image
            cv2.imwrite(image_path, cropped_image)
            return True
            
        except Exception as e:
            raise ImageProcessingError(f"Error cropping image: {e}")
    
    @staticmethod
    def _calculate_crop_range(
        original_size: int,
        target_size: int,
        alignment: AlignmentOption
    ) -> Tuple[int, int]:
        """Calculate crop range based on alignment"""
        if alignment in [AlignmentOption.LEFT, AlignmentOption.TOP]:
            return 0, target_size
        elif alignment in [AlignmentOption.CENTER]:
            start = (original_size - target_size) // 2
            return start, start + target_size
        elif alignment in [AlignmentOption.RIGHT, AlignmentOption.BOTTOM]:
            return original_size - target_size, original_size
        else:
            raise ValueError(f"Invalid alignment option: {alignment}")
    
    @staticmethod
    def crop_image_by_aspect_ratio(
        image_path: str,
        aspect_width: int,
        aspect_height: int,
        backup_original: bool = False
    ) -> bool:
        """
        Crop image to match specified aspect ratio with maximum size preservation
        
        Args:
            image_path: Path to the image file
            aspect_width: Width component of aspect ratio
            aspect_height: Height component of aspect ratio
            backup_original: Whether to create backup of original image
            
        Returns:
            True if cropping successful
            
        Raises:
            ImageProcessingError: If image processing fails
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError(f"Image file not found: {image_path}")
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ImageProcessingError(f"Failed to read image: {image_path}")
            
            original_height, original_width = image.shape[:2]
            
            # Create backup if requested
            if backup_original:
                backup_path = f"{image_path}.backup"
                cv2.imwrite(backup_path, image)
            
            # Calculate target dimensions based on aspect ratio
            if original_width / original_height > aspect_width / aspect_height:
                # Image is wider than target ratio
                new_width = original_height * aspect_width // aspect_height
                new_height = original_height
            else:
                # Image is taller than target ratio
                new_width = original_width
                new_height = original_width * aspect_height // aspect_width
            
            # Calculate center-aligned crop coordinates
            start_x = (original_width - new_width) // 2
            end_x = start_x + new_width
            start_y = (original_height - new_height) // 2
            end_y = start_y + new_height
            
            # Perform cropping
            cropped_image = image[start_y:end_y, start_x:end_x]
            
            # Save result
            cv2.imwrite(image_path, cropped_image)
            return True
            
        except Exception as e:
            raise ImageProcessingError(f"Error cropping image by aspect ratio: {e}")
    
    @staticmethod
    def crop_image_to_square(image_path: str, backup_original: bool = False) -> bool:
        """
        Crop image to square format (maximum size preservation)
        
        Args:
            image_path: Path to the image file
            backup_original: Whether to create backup of original image
            
        Returns:
            True if cropping successful
            
        Raises:
            ImageProcessingError: If image processing fails
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError(f"Image file not found: {image_path}")
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ImageProcessingError(f"Failed to read image: {image_path}")
            
            original_height, original_width = image.shape[:2]
            
            # If already square, no processing needed
            if original_width == original_height:
                return True
            
            # Create backup if requested
            if backup_original:
                backup_path = f"{image_path}.backup"
                cv2.imwrite(backup_path, image)
            
            # Calculate square dimensions (use smaller dimension)
            square_size = min(original_width, original_height)
            
            # Calculate center-aligned crop coordinates
            if original_width > original_height:
                # Wider image - crop width
                start_x = (original_width - square_size) // 2
                cropped_image = image[:, start_x:start_x + square_size]
            else:
                # Taller image - crop height
                start_y = (original_height - square_size) // 2
                cropped_image = image[start_y:start_y + square_size, :]
            
            # Save result
            cv2.imwrite(image_path, cropped_image)
            return True
            
        except Exception as e:
            raise ImageProcessingError(f"Error cropping image to square: {e}")
    
    @staticmethod
    def resize_image(
        image_path: str,
        target_width: int,
        target_height: int,
        maintain_aspect_ratio: bool = True,
        backup_original: bool = False
    ) -> bool:
        """
        Resize image to specified dimensions
        
        Args:
            image_path: Path to the image file
            target_width: Target width
            target_height: Target height
            maintain_aspect_ratio: Whether to maintain original aspect ratio
            backup_original: Whether to create backup of original image
            
        Returns:
            True if resizing successful
            
        Raises:
            ImageProcessingError: If image processing fails
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError(f"Image file not found: {image_path}")
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ImageProcessingError(f"Failed to read image: {image_path}")
            
            # Create backup if requested
            if backup_original:
                backup_path = f"{image_path}.backup"
                cv2.imwrite(backup_path, image)
            
            if maintain_aspect_ratio:
                # Calculate dimensions maintaining aspect ratio
                original_height, original_width = image.shape[:2]
                aspect_ratio = original_width / original_height
                
                if target_width / target_height > aspect_ratio:
                    # Fit to height
                    new_height = target_height
                    new_width = int(target_height * aspect_ratio)
                else:
                    # Fit to width
                    new_width = target_width
                    new_height = int(target_width / aspect_ratio)
            else:
                new_width, new_height = target_width, target_height
            
            # Perform resizing
            resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Save result
            cv2.imwrite(image_path, resized_image)
            return True
            
        except Exception as e:
            raise ImageProcessingError(f"Error resizing image: {e}")
    
    @staticmethod
    def optimize_image_for_web(
        image_path: str,
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85,
        backup_original: bool = False
    ) -> bool:
        """
        Optimize image for web usage
        
        Args:
            image_path: Path to the image file
            max_width: Maximum allowed width
            max_height: Maximum allowed height
            quality: JPEG quality (1-100)
            backup_original: Whether to create backup of original image
            
        Returns:
            True if optimization successful
            
        Raises:
            ImageProcessingError: If image processing fails
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError(f"Image file not found: {image_path}")
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ImageProcessingError(f"Failed to read image: {image_path}")
            
            original_height, original_width = image.shape[:2]
            
            # Create backup if requested
            if backup_original:
                backup_path = f"{image_path}.backup"
                cv2.imwrite(backup_path, image)
            
            # Resize if image exceeds maximum dimensions
            if original_width > max_width or original_height > max_height:
                aspect_ratio = original_width / original_height
                
                if original_width > max_width:
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                else:
                    new_width = original_width
                    new_height = original_height
                
                if new_height > max_height:
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)
                
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Save with optimized quality
            cv2.imwrite(
                image_path,
                image,
                [cv2.IMWRITE_JPEG_QUALITY, quality]
            )
            
            return True
            
        except Exception as e:
            raise ImageProcessingError(f"Error optimizing image: {e}") 