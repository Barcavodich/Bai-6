# /***************************/
# Mã sinh viên: 202418908
# Họ tên: Nguyễn Đăng Hiếu
# /***************************/
"""Thiết bị học tập: lớp trừu tượng Device và các lớp dẫn xuất."""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from enums import DeviceStatus
from exceptions import DeviceUnavailableException


class Device(ABC):
  """Lớp trừu tượng cho mọi thiết bị phục vụ giảng dạy."""

  def __init__(
      self,
      device_id,
      name,
      year_of_introduction,
      purchase_price,
      status=DeviceStatus.AVAILABLE,
  ):
    # Kiểm tra dữ liệu đầu vào theo yêu cầu của đề
    if not device_id or not str(device_id).strip():
      raise ValueError("Mã thiết bị không được để trống")
    price = Decimal(str(purchase_price))
    if price <= 0:
      raise ValueError("Giá mua phải lớn hơn 0")
    if year_of_introduction > datetime.now().year:
      raise ValueError("Năm đưa vào sử dụng không hợp lệ")

    self._device_id = device_id  # Chỉ gán một lần khi khởi tạo
    self.name = name
    self._year_of_introduction = year_of_introduction
    self.purchase_price = price
    self._status = status

  @property
  def device_id(self):
    return self._device_id

  @property
  def year_of_introduction(self):
    return self._year_of_introduction

  @property
  def status(self):
    """Chỉ đọc từ bên ngoài; đổi trạng thái qua mark_as_*."""
    return self._status

  @property
  @abstractmethod
  def max_borrow_days(self):
    """Số ngày mượn tối đa của loại thiết bị này."""

  @abstractmethod
  def calculate_annual_maintenance_cost(self):
    """Chi phí bảo trì dự kiến trong một năm (Decimal)."""

  def mark_as_borrowed(self):
    """Chuyển sang Borrowed; lỗi nếu thiết bị không sẵn sàng."""
    if self._status != DeviceStatus.AVAILABLE:
      raise DeviceUnavailableException(self._device_id, self._status)
    self._status = DeviceStatus.BORROWED

  def mark_as_available(self):
    """Trả thiết bị về Available (chỉ khi đang được mượn)."""
    if self._status == DeviceStatus.BORROWED:
      self._status = DeviceStatus.AVAILABLE

  def __str__(self):
    return (
        f"[{self._device_id}] {type(self).__name__} - {self.name} | Năm:"
        f" {self._year_of_introduction} | Giá: {self.purchase_price:,.0f} VNĐ"
        f" | Trạng thái: {self._status.value}"
    )


class AirConditionerRemote(Device):
  """Điều khiển điều hòa: bảo trì 10% giá mua, mượn tối đa 3 ngày."""

  @property
  def max_borrow_days(self):
    return 3

  def calculate_annual_maintenance_cost(self):
    return self.purchase_price * Decimal("0.10")


class Microphone(Device):
  """Micro: bảo trì 5% giá mua, mượn tối đa 1 ngày."""

  @property
  def max_borrow_days(self):
    return 1

  def calculate_annual_maintenance_cost(self):
    return self.purchase_price * Decimal("0.05")


class ProjectorRemote(Device):
  """Điều khiển máy chiếu: bảo trì 15% giá mua, mượn tối đa 5 ngày."""

  @property
  def max_borrow_days(self):
    return 5

  def calculate_annual_maintenance_cost(self):
    return self.purchase_price * Decimal("0.15")
