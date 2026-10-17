# /***************************/
# Mã sinh viên: 202418908
# Họ tên: Nguyễn Đăng Hiếu
# /***************************/
"""Phòng học: kết tập danh sách thiết bị."""

from datetime import datetime
from decimal import Decimal

from enums import DeviceStatus
from exceptions import DuplicateDeviceException

# Thiết bị dùng quá số năm này thì cần bảo trì
MAX_YEARS_BEFORE_MAINTENANCE = 5


class ClassRoom:
  """Phòng học chứa nhiều thiết bị (kết tập: thiết bị tồn tại độc lập)."""

  def __init__(self, room_id, room_name, capacity):
    if not room_id or not str(room_id).strip():
      raise ValueError("Mã phòng không được để trống")
    if capacity <= 0:
      raise ValueError("Sức chứa phải lớn hơn 0")
    self.room_id = room_id
    self.room_name = room_name
    self.capacity = capacity
    self._devices = []

  @property
  def devices(self):
    """Trả về bản sao để bên ngoài không sửa trực tiếp danh sách."""
    return tuple(self._devices)

  def add_device(self, device):
    """Thêm thiết bị; từ chối null và mã bị trùng."""
    if device is None:
      raise ValueError("Thiết bị không được null")
    if self.find_device(device.device_id) is not None:
      raise DuplicateDeviceException(device.device_id)
    self._devices.append(device)

  def remove_device(self, device_id):
    """Xóa thiết bị theo mã; trả True nếu xóa được."""
    device = self.find_device(device_id)
    if device is None:
      return False
    self._devices.remove(device)
    return True

  def find_device(self, device_id):
    """Tìm thiết bị theo mã; trả None nếu không có."""
    return next((d for d in self._devices if d.device_id == device_id), None)

  def calculate_annual_maintenance_cost(self):
    """Tổng chi phí bảo trì năm - dùng đa hình, không kiểm tra kiểu lớp."""
    return sum(
        (d.calculate_annual_maintenance_cost() for d in self._devices),
        Decimal("0"),
    )

  def get_devices_requiring_maintenance(self):
    """Thiết bị đang bảo trì hoặc đã dùng trên 5 năm."""
    current_year = datetime.now().year
    return [
        d
        for d in self._devices
        if d.status == DeviceStatus.UNDER_MAINTENANCE
        or (current_year - d.year_of_introduction)
        > MAX_YEARS_BEFORE_MAINTENANCE
    ]
