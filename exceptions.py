# /***************************/
# Mã sinh viên: 202418908
# Họ tên: Nguyễn Đăng Hiếu
# /***************************/
"""Hệ phân cấp ngoại lệ nghiệp vụ của chương trình mượn thiết bị."""


class BorrowingException(Exception):
  """Ngoại lệ cơ sở cho mọi lỗi nghiệp vụ mượn/trả thiết bị."""

  def __init__(self, message, inner_exception=None):
    super().__init__(message)
    # Ngoại lệ gốc (nếu có) để truy vết nguyên nhân
    self.inner_exception = inner_exception


class DeviceUnavailableException(BorrowingException):
  """Thiết bị không ở trạng thái Available."""

  def __init__(self, device_id, current_status):
    super().__init__(
        f"Thiết bị {device_id} không ở trạng thái sẵn sàng"
        f" ({current_status.value})"
    )
    self.device_id = device_id
    self.current_status = current_status


class BorrowLimitExceededException(BorrowingException):
  """Người mượn đã đạt số thiết bị tối đa trên một phiếu."""

  def __init__(self, borrower_id, maximum_devices):
    super().__init__(
        f"Người mượn {borrower_id} đã đạt giới hạn {maximum_devices} thiết bị"
    )
    self.borrower_id = borrower_id
    self.maximum_devices = maximum_devices


class InvalidBorrowPeriodException(BorrowingException):
  """Số ngày mượn không dương hoặc vượt giới hạn của thiết bị."""

  def __init__(self, device_id, requested_days, max_days):
    super().__init__(
        f"Số ngày mượn {requested_days} không hợp lệ cho thiết bị {device_id}"
        f" (phải từ 1 đến {max_days} ngày)"
    )
    self.device_id = device_id
    self.requested_days = requested_days
    self.max_days = max_days


class DuplicateDeviceException(BorrowingException):
  """Thiết bị đã tồn tại trong phiếu (hoặc trong phòng học)."""

  def __init__(self, device_id):
    super().__init__(f"Thiết bị {device_id} bị trùng lặp")
    self.device_id = device_id


class DeviceNotInSlipException(BorrowingException):
  """Trả một thiết bị không thuộc phiếu mượn."""

  def __init__(self, device_id):
    super().__init__(f"Thiết bị {device_id} không thuộc phiếu mượn này")
    self.device_id = device_id


class DeviceAlreadyReturnedException(BorrowingException):
  """Trả một thiết bị đã được trả trước đó."""

  def __init__(self, device_id):
    super().__init__(f"Thiết bị {device_id} đã được trả trước đó")
    self.device_id = device_id


class InvalidReturnDateException(BorrowingException):
  """Ngày trả trước ngày mượn.

  Ngoại lệ bổ sung: đề bài yêu cầu báo lỗi "ngày trả không hợp lệ" bằng
  ngoại lệ nghiệp vụ, nên tách riêng để lớp ứng dụng chỉ cần bắt
  BorrowingException thay vì ValueError.
  """

  def __init__(self, device_id, returned_date, borrowed_date):
    super().__init__(
        f"Ngày trả {returned_date:%d/%m/%Y} của thiết bị {device_id} không"
        f" được trước ngày mượn {borrowed_date:%d/%m/%Y}"
    )
    self.device_id = device_id
    self.returned_date = returned_date
    self.borrowed_date = borrowed_date
