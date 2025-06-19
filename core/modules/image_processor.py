"""
图像处理模块
==========

本模块负责处理图像操作，包括裁剪、缩放和优化。

主要功能:
    - 图像裁剪
    - 尺寸调整
    - 纵横比调整
    - 图像优化
    - 图像信息获取

依赖:
    - OpenCV (cv2): 图像处理核心库
    - NumPy: 数值计算库
"""

import os
from enum import Enum
from pathlib import Path
from typing import Tuple, Optional

import cv2
import numpy as np


class ImageProcessingError(Exception):
    """图像处理相关的自定义异常"""
    pass


class AlignmentOption(Enum):
    """
    图像对齐选项枚举
    
    枚举值:
        LEFT: 左对齐
        CENTER: 居中对齐
        RIGHT: 右对齐
        TOP: 顶部对齐
        BOTTOM: 底部对齐
    """
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


class ImageProcessor:
    """
    现代化的图像处理器，提供改进的错误处理和类型安全
    
    主要职责:
        1. 图像尺寸获取和验证
        2. 图像裁剪和缩放
        3. 纵横比调整
        4. 图像质量优化
        
    设计特点:
        - 类型安全：使用枚举和类型注解
        - 错误处理：详细的异常信息
        - 备份机制：支持原图备份
    """
    
    @staticmethod
    def get_image_dimensions(image_path: str) -> Tuple[int, int]:
        """
        获取图像尺寸（高度，宽度）
        
        参数:
            image_path: 图像文件路径
            
        返回:
            (高度, 宽度) 的元组
            
        异常:
            ImageProcessingError: 当图像无法读取时
            
        说明:
            使用OpenCV读取图像并返回其尺寸信息
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError(f"图像文件未找到: {image_path}")
        
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ImageProcessingError(f"图像读取失败: {image_path}")
            
            return image.shape[0], image.shape[1]
            
        except Exception as e:
            raise ImageProcessingError(f"读取图像尺寸时出错: {e}")
    
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
        将图像裁剪为指定尺寸
        
        参数:
            image_path: 图像文件路径
            target_width: 目标宽度
            target_height: 目标高度
            horizontal_align: 水平对齐方式
            vertical_align: 垂直对齐方式
            backup_original: 是否备份原图
            
        返回:
            裁剪成功返回True，如果目标尺寸超过原图则返回False
            
        异常:
            ImageProcessingError: 当图像处理失败时
            
        说明:
            1. 支持多种对齐方式
            2. 可选择是否备份原图
            3. 自动验证目标尺寸的有效性
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError(f"图像文件未找到: {image_path}")
        
        try:
            # 加载图像
            image = cv2.imread(image_path)
            if image is None:
                raise ImageProcessingError(f"图像读取失败: {image_path}")
            
            original_height, original_width = image.shape[:2]
            
            # 检查目标尺寸是否有效
            if target_width > original_width or target_height > original_height:
                return False
            
            # 如果需要则创建备份
            if backup_original:
                backup_path = f"{image_path}.backup"
                cv2.imwrite(backup_path, image)
            
            # 计算裁剪坐标
            width_range = ImageProcessor._calculate_crop_range(
                original_width, target_width, horizontal_align
            )
            height_range = ImageProcessor._calculate_crop_range(
                original_height, target_height, vertical_align
            )
            
            # 执行裁剪
            cropped_image = image[
                height_range[0]:height_range[1],
                width_range[0]:width_range[1]
            ]
            
            # 保存裁剪后的图像
            cv2.imwrite(image_path, cropped_image)
            return True
            
        except Exception as e:
            raise ImageProcessingError(f"裁剪图像时出错: {e}")
    
    @staticmethod
    def _calculate_crop_range(
        original_size: int,
        target_size: int,
        alignment: AlignmentOption
    ) -> Tuple[int, int]:
        """
        根据对齐方式计算裁剪范围
        
        参数:
            original_size: 原始尺寸
            target_size: 目标尺寸
            alignment: 对齐方式
            
        返回:
            (起始位置, 结束位置) 的元组
            
        异常:
            ValueError: 当对齐选项无效时
            
        说明:
            - 左对齐/顶部对齐：从0开始
            - 居中对齐：居中裁剪
            - 右对齐/底部对齐：从末尾向前裁剪
        """
        if alignment in [AlignmentOption.LEFT, AlignmentOption.TOP]:
            return 0, target_size
        elif alignment in [AlignmentOption.CENTER]:
            start = (original_size - target_size) // 2
            return start, start + target_size
        elif alignment in [AlignmentOption.RIGHT, AlignmentOption.BOTTOM]:
            return original_size - target_size, original_size
        else:
            raise ValueError(f"无效的对齐选项: {alignment}")
    
    @staticmethod
    def crop_image_by_aspect_ratio(
        image_path: str,
        aspect_width: int,
        aspect_height: int,
        backup_original: bool = False
    ) -> bool:
        """
        将图像裁剪为指定纵横比，同时保持最大尺寸
        
        参数:
            image_path: 图像文件路径
            aspect_width: 纵横比的宽度分量
            aspect_height: 纵横比的高度分量
            backup_original: 是否备份原图
            
        返回:
            裁剪成功返回True
            
        异常:
            ImageProcessingError: 当图像处理失败时
            
        说明:
            1. 自动计算最佳裁剪尺寸
            2. 居中裁剪以保持主要内容
            3. 可选择是否备份原图
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError(f"图像文件未找到: {image_path}")
        
        try:
            # 加载图像
            image = cv2.imread(image_path)
            if image is None:
                raise ImageProcessingError(f"图像读取失败: {image_path}")
            
            original_height, original_width = image.shape[:2]
            
            # 如果需要则创建备份
            if backup_original:
                backup_path = f"{image_path}.backup"
                cv2.imwrite(backup_path, image)
            
            # 根据纵横比计算目标尺寸
            if original_width / original_height > aspect_width / aspect_height:
                # 图像比目标比例更宽
                new_width = original_height * aspect_width // aspect_height
                new_height = original_height
            else:
                # 图像比目标比例更高
                new_width = original_width
                new_height = original_width * aspect_height // aspect_width
            
            # 计算居中裁剪的坐标
            start_x = (original_width - new_width) // 2
            end_x = start_x + new_width
            start_y = (original_height - new_height) // 2
            end_y = start_y + new_height
            
            # 执行裁剪
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