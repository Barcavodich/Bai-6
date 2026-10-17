class BorrowingException(Exception):
  pass


class DeviceUnavailableException(BorrowingException):

  def __init__(self, device_id, status):
    super().__init__(f"Thiết bị {device_id} không ở trạng thái sẵn sàng ({status})")
    self.device_id = device_id
    self.status = status


class BorrowLimitExceededException(BorrowingException):

  def __init__(self, borrower_id, max_dev):
    super().__init__(f"Người mượn {borrower_id} đã đạt giới hạn {max_dev} thiết bị")
    self.borrower_id = borrower_id
    self.max_devices = max_dev


class InvalidBorrowPeriodException(BorrowingException):

  def __init__(self, device_id, days, max_days):
    super().__init__(
        f"Số ngày mượn {days} không hợp lệ cho thiết bị {device_id} (Tối đa:"
        f" {max_days} ngày)"
    )
    self.device_id = device_id
    self.requested_days = days
    self.max_days = max_days


class DuplicateDeviceException(BorrowingException):

  def __init__(self, device_id):
    super().__init__(f"Thiết bị {device_id} bị trùng lặp trong phiếu")
    self.device_id = device_id


class DeviceNotInSlipException(BorrowingException):

  def __init__(self, device_id):
    super().__init__(f"Thiết bị {device_id} không thuộc phiếu mượn này")
    self.device_id = device_id


class DeviceAlreadyReturnedException(BorrowingException):

  def __init__(self, device_id):
    super().__init__(f"Thiết bị {device_id} đã được trả trước đó")
    self.device_id = device_id