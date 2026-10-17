# /***************************/
# Mã sinh viên: 202418908
# Họ tên: Nguyễn Đăng Hiếu
# /***************************/
"""Chương trình chính: chạy luồng thành công và các tình huống ngoại lệ."""

from datetime import datetime, timedelta

from borrowers import Lecturer, TeachingAssistant
from borrowing import BorrowingSlip
from classroom import ClassRoom
from devices import AirConditionerRemote, Microphone, ProjectorRemote
from enums import DeviceStatus
from exceptions import (
    BorrowingException,
    BorrowLimitExceededException,
    DeviceAlreadyReturnedException,
    DeviceNotInSlipException,
    DeviceUnavailableException,
    DuplicateDeviceException,
    InvalidBorrowPeriodException,
    InvalidReturnDateException,
)


def print_items(title, items):
  """In danh sách BorrowItem, hoặc '(không có)' nếu rỗng."""
  print(f"{title}:")
  if not items:
    print("  (không có)")
  for item in items:
    print(f"  - {item}")


def run_success_flow():
  """Luồng thành công: mượn 3 thiết bị, trả 2, một trả muộn, một chưa trả."""
  print("=== LUỒNG THÀNH CÔNG ===")
  lecturer = Lecturer("GV001", "Nguyễn Văn A")
  projector = ProjectorRemote("P01", "Điều khiển máy chiếu Sony", 2024, 500000)
  aircon = AirConditionerRemote("A01", "Điều khiển điều hòa Daikin", 2019, 800000)
  mic = Microphone("M01", "Micro không dây Shure", 2025, 1200000)

  # Kết tập thiết bị vào phòng học
  room = ClassRoom("P301", "Phòng 301", 60)
  for device in (projector, aircon, mic):
    room.add_device(device)

  borrowed_date = datetime.now()
  slip = BorrowingSlip("SLIP01", lecturer, "P301", borrowed_date)
  slip.add_device(projector, 5)
  slip.add_device(mic, 1)
  slip.add_device(aircon, 2)
  print(f"[OK] Phiếu {slip.slip_id} của {lecturer}: {len(slip.items)} thiết bị")

  # Máy chiếu trả đúng hạn, micro hạn 1 ngày nhưng trả sau 3 ngày (muộn 2 ngày)
  fee_projector = slip.return_device("P01", borrowed_date + timedelta(days=3))
  fee_mic = slip.return_device("M01", borrowed_date + timedelta(days=3))
  print(f"Phí phạt P01 (đúng hạn): {fee_projector:,.0f} VNĐ")
  print(f"Phí phạt M01 (muộn 2 ngày): {fee_mic:,.0f} VNĐ")
  print(f"Tổng phí phạt: {slip.calculate_total_late_fee():,.0f} VNĐ\n")

  print_items("Thiết bị trả muộn", slip.get_late_items())
  print_items("Thiết bị chưa trả", slip.get_unreturned_items())

  print("\nThông tin phòng học (đa hình):")
  for device in room.devices:
    print(f"  {device}")
  print(
      "Chi phí bảo trì dự kiến/năm:"
      f" {room.calculate_annual_maintenance_cost():,.0f} VNĐ"
  )
  print_items_text = [str(d) for d in room.get_devices_requiring_maintenance()]
  print("Thiết bị cần bảo trì:", print_items_text or "(không có)")
  print()


def expect_error(expected_type, action):
  """Chạy action, trả True nếu ném đúng loại ngoại lệ mong đợi."""
  try:
    action()
  except expected_type as ex:
    print(f"    Bắt đúng {type(ex).__name__}: {ex}")
    return True
  except Exception as ex:  # pylint: disable=broad-except
    print(f"    SAI loại ngoại lệ {type(ex).__name__}: {ex}")
    return False
  print("    Không có ngoại lệ nào được ném ra")
  return False


# Mỗi tình huống trả True nếu bắt đúng ngoại lệ VÀ trạng thái vẫn nhất quán.


def scenario_aircon_under_maintenance():
  slip = BorrowingSlip("S2", Lecturer("GV2", "B"), "P102", datetime.now())
  aircon = AirConditionerRemote(
      "A2", "Điều khiển hỏng", 2022, 500000, DeviceStatus.UNDER_MAINTENANCE
  )
  ok = expect_error(DeviceUnavailableException, lambda: slip.add_device(aircon, 2))
  return (
      ok
      and len(slip.items) == 0
      and aircon.status == DeviceStatus.UNDER_MAINTENANCE
  )


def scenario_assistant_third_device():
  slip = BorrowingSlip("S3", TeachingAssistant("TA1", "C"), "P201", datetime.now())
  slip.add_device(ProjectorRemote("P1", "Máy chiếu 1", 2024, 100000), 1)
  slip.add_device(ProjectorRemote("P2", "Máy chiếu 2", 2024, 100000), 1)
  third = ProjectorRemote("P3", "Máy chiếu 3", 2024, 100000)
  ok = expect_error(BorrowLimitExceededException, lambda: slip.add_device(third, 1))
  return ok and len(slip.items) == 2 and third.status == DeviceStatus.AVAILABLE


def scenario_duplicate_device():
  slip = BorrowingSlip("S4", Lecturer("GV3", "D"), "P302", datetime.now())
  mic = Microphone("M99", "Micro", 2025, 1000000)
  slip.add_device(mic, 1)
  ok = expect_error(DuplicateDeviceException, lambda: slip.add_device(mic, 1))
  return ok and len(slip.items) == 1 and mic.status == DeviceStatus.BORROWED


def scenario_microphone_too_long():
  slip = BorrowingSlip("S5", Lecturer("GV4", "E"), "P303", datetime.now())
  mic = Microphone("M88", "Micro VIP", 2025, 1000000)
  ok = expect_error(InvalidBorrowPeriodException, lambda: slip.add_device(mic, 3))
  return ok and len(slip.items) == 0 and mic.status == DeviceStatus.AVAILABLE


def scenario_non_positive_days():
  slip = BorrowingSlip("S5b", Lecturer("GV4b", "E2"), "P303", datetime.now())
  mic = Microphone("M77", "Micro", 2025, 1000000)
  ok = expect_error(InvalidBorrowPeriodException, lambda: slip.add_device(mic, 0))
  return ok and len(slip.items) == 0 and mic.status == DeviceStatus.AVAILABLE


def scenario_return_device_not_in_slip():
  slip = BorrowingSlip("S6", Lecturer("GV5", "F"), "P304", datetime.now())
  ok = expect_error(
      DeviceNotInSlipException,
      lambda: slip.return_device("NOT_EXIST", datetime.now()),
  )
  return ok and len(slip.items) == 0


def scenario_return_twice():
  slip = BorrowingSlip("S7", Lecturer("GV6", "G"), "P305", datetime.now())
  projector = ProjectorRemote("PT", "Test", 2024, 1000000)
  slip.add_device(projector, 2)
  slip.return_device("PT", datetime.now())
  ok = expect_error(
      DeviceAlreadyReturnedException,
      lambda: slip.return_device("PT", datetime.now()),
  )
  return ok and projector.status == DeviceStatus.AVAILABLE


def scenario_return_before_borrowed():
  slip = BorrowingSlip("S8", Lecturer("GV7", "H"), "P306", datetime.now())
  projector = ProjectorRemote("PT2", "Test2", 2024, 1000000)
  slip.add_device(projector, 2)
  ok = expect_error(
      InvalidReturnDateException,
      lambda: slip.return_device("PT2", datetime.now() - timedelta(days=5)),
  )
  return (
      ok
      and not slip.items[0].is_returned
      and projector.status == DeviceStatus.BORROWED
  )


SCENARIOS = [
    ("Mượn điều khiển điều hòa đang UnderMaintenance", scenario_aircon_under_maintenance),
    ("Trợ giảng mượn thiết bị thứ ba", scenario_assistant_third_device),
    ("Thêm cùng một micro hai lần", scenario_duplicate_device),
    ("Mượn micro 3 ngày (giới hạn 1 ngày)", scenario_microphone_too_long),
    ("Số ngày mượn không dương", scenario_non_positive_days),
    ("Trả thiết bị không thuộc phiếu", scenario_return_device_not_in_slip),
    ("Trả cùng một thiết bị hai lần", scenario_return_twice),
    ("Trả thiết bị với ngày trả trước ngày mượn", scenario_return_before_borrowed),
]


def run_exception_tests():
  """Chạy các tình huống ngoại lệ và in tổng kết."""
  print("=== KIỂM THỬ CÁC TÌNH HUỐNG NGOẠI LỆ ===")
  passed = 0
  for index, (name, scenario) in enumerate(SCENARIOS, start=1):
    print(f"{index}. {name}")
    ok = scenario()
    print(f"    => {'ĐẠT' if ok else 'KHÔNG ĐẠT'}")
    passed += ok
  print(f"\nKết quả: {passed}/{len(SCENARIOS)} tình huống đạt")


def main():
  print("=== CHƯƠNG TRÌNH QUẢN LÝ THIẾT BỊ HỌC TẬP ===\n")
  try:
    run_success_flow()
  except BorrowingException as ex:
    print("Lỗi nghiệp vụ ở luồng thành công:", ex)
  finally:
    print("--- Kết thúc luồng thành công ---\n")
  run_exception_tests()


if __name__ == "__main__":
  main()
