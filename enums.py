# /***************************/
# Mã sinh viên: 202418908
# Họ tên: Nguyễn Đăng Hiếu
# /***************************/
"""Khai báo các kiểu liệt kê (enum) dùng chung trong hệ thống."""

from enum import Enum


class DeviceStatus(Enum):
  """Trạng thái của một thiết bị học tập."""

  AVAILABLE = "Available"  # Sẵn sàng cho mượn
  BORROWED = "Borrowed"  # Đang được mượn
  UNDER_MAINTENANCE = "UnderMaintenance"  # Đang bảo trì
  RETIRED = "Retired"  # Đã thanh lý, ngừng sử dụng
