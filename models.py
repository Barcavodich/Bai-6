from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from exceptions import (
    BorrowingException,
    DuplicateDeviceException,
    DeviceUnavailableException,
)


class DeviceStatus(Enum):
  AVAILABLE = "Available"
  BORROWED = "Borrowed"
  UNDER_MAINTENANCE = "UnderMaintenance"
  ACTIVE = "Active"
  RETIRED = "Retired"


class IBorrower(ABC):

  @property
  @abstractmethod
  def borrower_id(self):
    pass

  @property
  @abstractmethod
  def full_name(self):
    pass

  @abstractmethod
  def get_maximum_devices(self):
    pass


class Lecturer(IBorrower):

  def __init__(self, borrower_id, full_name):
    self._borrower_id = borrower_id
    self._full_name = full_name

  @property
  def borrower_id(self):
    return self._borrower_id

  @property
  def full_name(self):
    return self._full_name

  def get_maximum_devices(self):
    return 3


class TeachingAssistant(IBorrower):

  def __init__(self, borrower_id, full_name):
    self._borrower_id = borrower_id
    self._full_name = full_name

  @property
  def borrower_id(self):
    return self._borrower_id

  @property
  def full_name(self):
    return self._full_name

  def get_maximum_devices(self):
    return 2


class Device(ABC):

  def __init__(
      self,
      device_id,
      name,
      year_of_introduction,
      purchase_price,
      status=DeviceStatus.AVAILABLE,
  ):
    if not device_id:
      raise ValueError("Mã thiết bị không được để trống")
    if purchase_price <= 0:
      raise ValueError("Giá mua phải lớn hơn 0")
    if year_of_introduction > datetime.now().year:
      raise ValueError("Năm sản xuất không hợp lệ")

    self._device_id = device_id
    self.name = name
    self._year_of_introduction = year_of_introduction
    self.purchase_price = purchase_price
    self.status = status

  @property
  def device_id(self):
    return self._device_id

  @property
  def year_of_introduction(self):
    return self._year_of_introduction

  @abstractmethod
  def calculate_annual_maintenance_cost(self):
    pass

  def mark_as_borrowed(self):
    if self.status != DeviceStatus.AVAILABLE:
      raise DeviceUnavailableException(self._device_id, self.status)
    self.status = DeviceStatus.BORROWED

  def mark_as_available(self):
    self.status = DeviceStatus.AVAILABLE


class AirConditionerRemote(Device):

  def calculate_annual_maintenance_cost(self):
    return self.purchase_price * 0.10


class Microphone(Device):

  def calculate_annual_maintenance_cost(self):
    return self.purchase_price * 0.05


class ProjectorRemote(Device):

  def calculate_annual_maintenance_cost(self):
    return self.purchase_price * 0.15


class ClassRoom:

  def __init__(self, room_id, room_name, capacity):
    self.room_id = room_id
    self.room_name = room_name
    self.capacity = capacity
    self._devices = []

  @property
  def devices(self):
    return self._devices

  def add_device(self, device):
    if not device:
      raise ValueError("Thiết bị không hợp lệ")
    if any(d.device_id == device.device_id for d in self._devices):
      raise DuplicateDeviceException(device.device_id)
    self._devices.append(device)

  def remove_device(self, device_id):
    dev = self.find_device(device_id)
    if dev:
      self._devices.remove(dev)
      return True
    return False

  def find_device(self, device_id):
    return next((d for d in self._devices if d.device_id == device_id), None)

  def calculate_annual_maintenance_cost(self):
    return sum(d.calculate_annual_maintenance_cost() for d in self._devices)

  def get_devices_requiring_maintenance(self):
    cur_year = datetime.now().year
    return [
        d
        for d in self._devices
        if d.status == DeviceStatus.UNDER_MAINTENANCE
        or (cur_year - d.year_of_introduction) > 5
    ]