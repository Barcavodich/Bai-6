# /***************************/
# Mã sinh viên: 202418908
# Họ tên: Nguyễn Đăng Hiếu
# /***************************/
"""Phiếu mượn (BorrowingSlip) và từng dòng mượn (BorrowItem)."""

from datetime import timedelta
from decimal import Decimal

from enums import DeviceStatus
from exceptions import (
    BorrowLimitExceededException,
    DeviceAlreadyReturnedException,
    DeviceNotInSlipException,
    DeviceUnavailableException,
    DuplicateDeviceException,
    InvalidBorrowPeriodException,
    InvalidReturnDateException,
)

# Phí phạt cho mỗi ngày trả muộn (VNĐ)
LATE_FEE_PER_DAY = Decimal("50000")


class BorrowItem:
  """Một thiết bị được mượn trong phiếu. Chỉ tham chiếu tới Device."""

  def __init__(
      self, device, borrowed_date, due_date, from_period=1, to_period=5
  ):
    if device is None:
      raise ValueError("Thiết bị không được null")
    if due_date < borrowed_date:
      raise ValueError("Ngày hết hạn không được trước ngày mượn")
    if from_period < 1 or to_period < from_period:
      raise ValueError("Tiết mượn không hợp lệ (từ tiết phải <= đến tiết)")

    self.device = device
    self.borrowed_date = borrowed_date
    self.due_date = due_date
    self.from_period = from_period
    self.to_period = to_period
    self._returned_date = None  # Ban đầu chưa trả

  @property
  def returned_date(self):
    return self._returned_date

  @property
  def is_returned(self):
    return self._returned_date is not None

  def return_item(self, returned_date):
    """Ghi nhận trả: kiểm tra hết rồi mới thay đổi trạng thái."""
    if self.is_returned:
      raise DeviceAlreadyReturnedException(self.device.device_id)
    if returned_date < self.borrowed_date:
      raise InvalidReturnDateException(
          self.device.device_id, returned_date, self.borrowed_date
      )
    self._returned_date = returned_date
    self.device.mark_as_available()

  def calculate_late_fee(self):
    """Phí phạt = số ngày trễ x 50.000; chưa trả hoặc đúng hạn thì 0."""
    if not self.is_returned:
      return Decimal("0")
    late_days = (self._returned_date.date() - self.due_date.date()).days
    return LATE_FEE_PER_DAY * late_days if late_days > 0 else Decimal("0")

  def __str__(self):
    status = (
        f"đã trả {self._returned_date:%d/%m/%Y}"
        if self.is_returned
        else "chưa trả"
    )
    return (
        f"{self.device.device_id} - {self.device.name} | hạn"
        f" {self.due_date:%d/%m/%Y} | {status}"
    )


class BorrowingSlip:
  """Phiếu mượn của một người mượn; hợp thành nhiều BorrowItem."""

  def __init__(self, slip_id, borrower, teaching_room, borrowed_date):
    if not slip_id or not str(slip_id).strip():
      raise ValueError("Mã phiếu không được để trống")
    if borrower is None:
      raise ValueError("Người mượn không được null")
    if not teaching_room or not str(teaching_room).strip():
      raise ValueError("Phòng dạy không được để trống")
    self.slip_id = slip_id
    self.borrower = borrower
    self.teaching_room = teaching_room
    self.borrowed_date = borrowed_date
    self._items = []

  @property
  def items(self):
    """Danh sách chỉ đọc (tuple) các BorrowItem."""
    return tuple(self._items)

  def _find_item(self, device_id):
    return next((i for i in self._items if i.device.device_id == device_id), None)

  def _validate_borrowing(self, device, borrow_days):
    """Kiểm tra mọi điều kiện, KHÔNG thay đổi bất kỳ trạng thái nào."""
    if device is None:
      raise ValueError("Thiết bị không được null")
    max_days = device.max_borrow_days
    if borrow_days <= 0 or borrow_days > max_days:
      raise InvalidBorrowPeriodException(device.device_id, borrow_days, max_days)
    if self._find_item(device.device_id) is not None:
      raise DuplicateDeviceException(device.device_id)
    maximum = self.borrower.get_maximum_devices()
    if len(self._items) >= maximum:
      raise BorrowLimitExceededException(self.borrower.borrower_id, maximum)
    if device.status != DeviceStatus.AVAILABLE:
      raise DeviceUnavailableException(device.device_id, device.status)

  def add_device(self, device, borrow_days):
    """Thêm thiết bị vào phiếu, giữ nhất quán nếu thất bại."""
    self._validate_borrowing(device, borrow_days)  # 1. Kiểm tra trước
    due_date = self.borrowed_date + timedelta(days=borrow_days)
    item = BorrowItem(device, self.borrowed_date, due_date)  # 2. Tạo item
    device.mark_as_borrowed()  # 3. Đổi trạng thái thiết bị
    self._items.append(item)  # 4. Thêm vào phiếu

  def return_device(self, device_id, returned_date):
    """Trả thiết bị và trả về phí phạt của thiết bị đó."""
    if not device_id or not str(device_id).strip():
      raise ValueError("Mã thiết bị không được để trống")
    item = self._find_item(device_id)
    if item is None:
      raise DeviceNotInSlipException(device_id)
    item.return_item(returned_date)  # Tự kiểm tra: đã trả, ngày trả sai
    return item.calculate_late_fee()

  def calculate_total_late_fee(self):
    return sum((i.calculate_late_fee() for i in self._items), Decimal("0"))

  def get_unreturned_items(self):
    """Các thiết bị chưa trả."""
    return [i for i in self._items if not i.is_returned]

  def get_late_items(self):
    """Các thiết bị đã trả muộn (có phí phạt)."""
    return [i for i in self._items if i.calculate_late_fee() > 0]
