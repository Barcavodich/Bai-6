from datetime import datetime, timedelta
from exceptions import (
    BorrowingException,
    BorrowLimitExceededException,
    DeviceAlreadyReturnedException,
    DeviceNotInSlipException,
    DeviceUnavailableException,
    DuplicateDeviceException,
    InvalidBorrowPeriodException,
)
from models import Device, IBorrower, Microphone


class BorrowItem:

  def __init__(
      self, device, borrowed_date, due_date, from_period=1, to_period=5
  ):
    if not device:
      raise ValueError("Thiết bị không được null")
    if due_date < borrowed_date:
      raise ValueError("Ngày hết hạn không được trước ngày mượn")

    self.device = device
    self.borrowed_date = borrowed_date
    self.due_date = due_date
    self.from_period = from_period
    self.to_period = to_period
    self.returned_date = None

  @property
  def is_returned(self):
    return self.returned_date is not None

  def return_item(self, returned_date):
    if self.is_returned:
      raise DeviceAlreadyReturnedException(self.device.device_id)
    if returned_date < self.borrowed_date:
      raise ValueError("Ngày trả không được trước ngày mượn")

    self.returned_date = returned_date
    self.device.mark_as_available()

  def calculate_late_fee(self):
    if not self.is_returned:
      return 0.0
    days = (self.returned_date.date() - self.due_date.date()).days
    return float(days * 50000) if days > 0 else 0.0


class BorrowingSlip:

  def __init__(self, slip_id, borrower, teaching_room, borrowed_date):
    self.slip_id = slip_id
    self.borrower = borrower
    self.teaching_room = teaching_room
    self.borrowed_date = borrowed_date
    self._items = []

  @property
  def items(self):
    return self._items

  def add_device(self, device, borrow_days):
    if not device:
      raise ValueError("Thiết bị không được null")
    if borrow_days <= 0:
      raise InvalidBorrowPeriodException(device.device_id, borrow_days, 30)
    if any(i.device.device_id == device.device_id for i in self._items):
      raise DuplicateDeviceException(device.device_id)
    if len(self._items) >= self.borrower.get_maximum_devices():
      raise BorrowLimitExceededException(
          self.borrower.borrower_id, self.borrower.get_maximum_devices()
      )
    if device.status.value != "Available":
      raise DeviceUnavailableException(device.device_id, device.status)

    if isinstance(device, Microphone) and borrow_days > 3:
      raise InvalidBorrowPeriodException(device.device_id, borrow_days, 3)

    device.mark_as_borrowed()
    due_date = self.borrowed_date + timedelta(days=borrow_days)
    self._items.append(BorrowItem(device, self.borrowed_date, due_date))

  def return_device(self, device_id, returned_date):
    item = next(
        (i for i in self._items if i.device.device_id == device_id), None
    )
    if not item:
      raise DeviceNotInSlipException(device_id)
    if item.is_returned:
      raise DeviceAlreadyReturnedException(device_id)

    item.return_item(returned_date)
    return item.calculate_late_fee()

  def calculate_total_late_fee(self):
    return sum(i.calculate_late_fee() for i in self._items)