# /***************************/
# Mã sinh viên: 202418908
# Họ tên: Nguyễn Đăng Hiếu
# /***************************/
"""Người mượn thiết bị: interface IBorrower và các lớp thực thi."""

from abc import ABC, abstractmethod


class IBorrower(ABC):
  """Interface mô tả một người được phép mượn thiết bị."""

  @property
  @abstractmethod
  def borrower_id(self):
    """Mã người mượn."""

  @property
  @abstractmethod
  def full_name(self):
    """Họ tên người mượn."""

  @abstractmethod
  def get_maximum_devices(self):
    """Số thiết bị tối đa được mượn trên một phiếu."""


class Borrower(IBorrower):
  """Lớp cha chứa phần dùng chung của Lecturer và TeachingAssistant.

  Vẫn là lớp trừu tượng vì get_maximum_devices() do lớp con quyết định.
  """

  def __init__(self, borrower_id, full_name):
    if not borrower_id or not str(borrower_id).strip():
      raise ValueError("Mã người mượn không được để trống")
    if not full_name or not str(full_name).strip():
      raise ValueError("Họ tên người mượn không được để trống")
    self._borrower_id = borrower_id
    self._full_name = full_name

  @property
  def borrower_id(self):
    return self._borrower_id

  @property
  def full_name(self):
    return self._full_name

  def __str__(self):
    return f"{self._full_name} ({self._borrower_id})"


class Lecturer(Borrower):
  """Giảng viên: mượn tối đa 3 thiết bị trên một phiếu."""

  def get_maximum_devices(self):
    return 3


class TeachingAssistant(Borrower):
  """Trợ giảng: mượn tối đa 2 thiết bị trên một phiếu."""

  def get_maximum_devices(self):
    return 2
