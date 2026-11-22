from abc import ABC, abstractmethod
from luxtronik.version import get_version_str


class LuxtronikInterfaceInfo:

    def __init__(self, _type, host, port, version):
        self.type = _type
        self.host = host
        self.port = port
        self.version = version

    def __str__(self):
        return self.long_desc

    @property
    def short_desc(self):
        return f"{self.host}"

    @property
    def long_desc(self):
        return f"{self.type}={self.host}:{self.port}/{get_version_str(self.version)}"


class LuxtronikBaseInterface(ABC):
    """
    Base class for each Luxtronik interface class.
    Defines common methods that must be implemented in the derived classes.
    """

    @property
    @abstractmethod
    def lock(self):
        """
        Get the unique lock object associated with a given host.
        The same thread can acquire a RLock as often as desired.

        Returns:
            RLock: The lock object of the interface.
        """
        pass

    @property
    @abstractmethod
    def info(self):
        """
        Retrieve the interface information object
        to identify the device/interface.

        Returns:
            LuxtronikInterfaceInfo: The general information
                (host, port, ...) of the interface.
        """
        pass

    @property
    @abstractmethod
    def version(self):
        """
        Get the specified or detected version.

        Returns:
            tuple[int]: The used version of the interface.
        """
        pass

    @abstractmethod
    def read_version(self):
        """
        Read the controller version via the first valid version field.

        Returns:
            tuple[int]: The read controller version.
        """

    @abstractmethod
    def create_data(self, safe=True):
        """
        Create a data vector collection only with fields that match the stored version.

        Args:
            safe (bool): If true, prevent write-able fields marked as
                not secure from being written to.

        Returns:
            type of the data collection: The created data-collection.
        """
        pass

    @abstractmethod
    def read(self, data=None):
        """
        Read the data of all fields within the data vector collection
        that are supported by the controller.

        Args:
            data (type of the data collection | None): Optional existing data vector collection.
                If None is provided, a new instance is created.

        Returns:
            type of the data collection: The passed / created data vector collection.
        """
        pass

    @abstractmethod
    def write(self, data):
        """
        Write the data of all fields within the data vector (collection)
        that are supported by the controller.

        Args:
            data (type of the data collection or data vector): The data vector (collection) containing field data.
                If None is provided, the write is aborted.

        Returns:
            bool: True if no errors occurred, otherwise False.
        """
        pass

    @abstractmethod
    def write_and_read(self, write_data, read_data=None):
        """
        Write and then read the data of all fields within the data vector (collection)
        that are supported by the controller.

        Args:
            write_data (type of the data collection or data vector):
                The data vector (collection) containing field data.
                If None is provided, the write is aborted.
            read_data (type of the data collection | None): Optional existing data vector collection
                for the read data. If None is provided, a new instance is created.

        Returns:
            type of the data collection: The passed / created data vector collection for the read data.
        """
        pass
