"""管理文件的服务"""
import os
from enum import Enum
from os import remove
from pathlib import Path

from service.Utils import queryConfig


class FILETYPE(Enum):
    """文件类型 枚举项，value需要与文件夹名保持一致"""
    BOOK_COVER = "bookCover"
    JOURNAL_HEADER = "journalHeader"
    PROFILE_PHOTO = "profilePhoto"
    GROUP_ICON = "groupIcon"
    ERROR_IMAGE = "errorImage"


class FileManager:
    """文件管理"""

    def __init__(self):
        self._project_path: Path = Path(os.getcwd())  # 项目路径
        self._storage_path: Path = Path(str(self._project_path) + queryConfig("Path", "StoragePath"))  # static文件夹
        if not self._storage_path.exists():
            raise FileNotFoundError(f"Config item StoragePath: {self._storage_path} not found!")

    def _getFilePath(
            self, file_type: FILETYPE, pattern: str = None, enable_default: bool = False
    ) -> tuple[str, str]:
        """
        查找文件，返回绝对路径和相对路径(相对于self._project_path)
        :param file_type: 文件类型
        :param pattern: 文件名pattern，如1.*表示查找形如1.xxx的文件，不提供则返回默认文件
        """
        folder_path: Path = self._storage_path / file_type.value
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder {folder_path} not found!")

        if pattern and list(folder_path.glob(pattern)):
            res = list(folder_path.glob(pattern))
            absolute_path = res[0].as_posix()
            relative_path = absolute_path.replace(self._project_path.as_posix(), "")
        else:  # 未提供pattern或未找到文件
            if enable_default:
                absolute_path: str = (self._storage_path / file_type.value / "default.webp").as_posix()
                relative_path: str = absolute_path.replace(self._project_path.as_posix(), "")
            else:
                absolute_path, relative_path = "", ""
        return absolute_path, relative_path

    """book"""

    def getBookCoverPath(self, book_id: int, abs_path: bool = False, enable_default: bool = True) -> str:
        """
        寻找书籍封面路径
        :param book_id: 书籍ID
        :param abs_path: 是否返回绝对路径
        :param enable_default: 是否允许返回默认路径(找不到的情况下)
        :return: 封面图路径
        """
        absolute_path, relative_path = self._getFilePath(FILETYPE.BOOK_COVER, f"{book_id}.*", enable_default)
        return absolute_path if abs_path else relative_path

    def generateBookCoverPath(self, book_id: int, abs_path: bool = False) -> str:
        """
        生成书籍封面图片应存放的路径
        :param book_id: 书籍ID
        :param abs_path: 是否返回绝对路径
        :return:
        """
        absolute_path: str = (self._storage_path / FILETYPE.BOOK_COVER.value / f"{book_id}.jpg").as_posix()
        relative_path: str = absolute_path.replace(self._project_path.as_posix(), "")
        return absolute_path if abs_path else relative_path

    """journal"""

    def getJournalHeaderPath(self, journal_id: int, abs_path=False, enable_default=True) -> str:
        """
        寻找书评封面路径
        :param journal_id: 书评ID
        :param abs_path: 是否返回绝对路径
        :param enable_default: 是否允许返回默认路径(找不到的情况下)
        :return: 封面图路径
        """
        absolute_path, relative_path = self._getFilePath(FILETYPE.JOURNAL_HEADER, f"{journal_id}.*", enable_default)
        return absolute_path if abs_path else relative_path

    def generateJournalHeaderPath(self, journal_id, abs_path=False) -> str:
        """
        生成书评封面图片应存放的路径
        :param journal_id: 书评ID
        :param abs_path: 是否返回绝对路径
        :return:
        """
        absolute_path: str = (self._storage_path / FILETYPE.JOURNAL_HEADER.value / f"{journal_id}.jpg").as_posix()
        relative_path: str = absolute_path.replace(self._project_path.as_posix(), "")
        return absolute_path if abs_path else relative_path

    def deleteJournalHeader(self, journal_id) -> bool:
        """
        删除书评封面图片
        :param journal_id: 书评ID
        :return: True(删除成功)/False(文件不存在)
        """
        absolute_path, _ = self._getFilePath(FILETYPE.JOURNAL_HEADER, f"{journal_id}.*")
        if absolute_path:
            remove(absolute_path)
            return True
        else:
            return False

    """profile"""

    def getProfilePhotoPath(self, user_id, abs_path=False, enable_default=True) -> str:
        """
        寻找头像路径
        :param user_id: 用户ID
        :param abs_path: 是否返回绝对路径
        :param enable_default: 是否允许返回默认路径
        :return: 头像路径
        """
        absolute_path, relative_path = self._getFilePath(FILETYPE.PROFILE_PHOTO, f"{user_id}.*", enable_default)
        return absolute_path if abs_path else relative_path

    def generateProfilePhotoPath(self, user_id, abs_path=False) -> str:
        """
        生成头像图片应存放的路径
        :param user_id: 用户ID
        :param abs_path: 是否返回绝对路径
        :return:
        """
        absolute_path: str = (self._storage_path / FILETYPE.PROFILE_PHOTO.value / f"{user_id}.jpg").as_posix()
        relative_path: str = absolute_path.replace(self._project_path.as_posix(), "")
        return absolute_path if abs_path else relative_path

    def deleteProfilePhoto(self, user_id) -> bool:
        """
        删除头像图片
        :param user_id: 用户ID
        :return: True(删除成功)/False(文件不存在)
        """
        absolute_path, _ = self._getFilePath(FILETYPE.PROFILE_PHOTO, f"{user_id}.*")
        if absolute_path:
            remove(absolute_path)
            return True
        else:
            return False

    """group"""

    def getGroupIconPath(self, group_id, abs_path=False, enable_default=True) -> str:
        """
        寻找群组头像路径
        :param group_id:
        :param abs_path:
        :param enable_default:
        :return:
        """
        absolute_path, relative_path = self._getFilePath(FILETYPE.GROUP_ICON, f"{group_id}.*", enable_default)
        return absolute_path if abs_path else relative_path

    def deleteGroupIcon(self, group_id) -> bool:
        """
        删除群组头像图片
        :param group_id: 群组ID
        :return: True(删除成功)/False(文件不存在)
        """
        absolute_path, _ = self._getFilePath(FILETYPE.GROUP_ICON, f"{group_id}.*")
        if absolute_path:
            remove(absolute_path)
            return True
        else:
            return False

    def generateGroupIconPath(self, group_id, abs_path=False) -> str:
        """
        生成圈子icon应存放的路径
        :param group_id: 圈子ID
        :param abs_path: 是否返回绝对路径
        :return:
        """
        absolute_path: str = (self._storage_path / FILETYPE.GROUP_ICON.value / f"{group_id}.jpg").as_posix()
        relative_path: str = absolute_path.replace(self._project_path.as_posix(), "")
        return absolute_path if abs_path else relative_path

    """error"""

    def getErrorImagePath(self, error_code: int, abs_path=False):
        """
        获取错误详情页的图片
        :param error_code: 错误码
        :param abs_path: 是否返回绝对路径
        :return:
        """
        absolute_path, relative_path = self._getFilePath(FILETYPE.ERROR_IMAGE, f"{error_code}.*")
        return absolute_path if abs_path else relative_path
