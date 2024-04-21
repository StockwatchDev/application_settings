"""Abstract base class for sections to be added to containers and container sections for configuration and settings."""
from abc import ABC, abstractmethod

from loguru import logger


class ContainerSectionBase(ABC):
    """Base class for all ContainerSection classes"""

    @classmethod
    @abstractmethod
    def kind_string(cls):
        """Return either 'Config' or 'Settings'"""

    @classmethod
    def get(cls):
        """Get the singleton; if not existing, create it. Loading from file only done for a container."""

        if (_the_container_or_none := cls._get()) is None:
            # no config section has been made yet
            cls.get_without_load()
            # so let's instantiate one and keep it in the global store
            return cls._create_instance()
        return _the_container_or_none

    @classmethod
    def get_without_load(cls):
        """Get has been called on a section before a load was done; handle this."""
        # get() is called on a Section but the application
        # has not yet created or loaded a config.
        logger.warning(
            f"{cls.kind_string()} section {cls.__name__} accessed before data has been loaded; "
            f"will try to load via command line parameter '--{cls.__name__}_file'"
        )

    @classmethod
    def set(cls, data):
        """Create a new dataclass instance using data and set the singleton."""
        return cls(**data)._set()

    @classmethod
    def _get(
        cls,
    ):  # pylint: disable=consider-alternative-union-syntax
        """Get the singleton."""
        if the_container := _ALL_CONTAINER_SECTION_SINGLETONS.get(id(cls)):
            return the_container
        return None

    @classmethod
    def _create_instance(
        cls, throw_if_file_not_found = False  # pylint: disable=unused-argument
    ):
        """Create a new ContainerSection with default values. Likely that this is wrong."""
        return cls.set({})

    def _set(self):
        """Store the singleton."""
        _check_dataclass_decorator(self)
        _ALL_CONTAINER_SECTION_SINGLETONS[id(self.__class__)] = self
        subsections = [
            attr
            for attr in vars(self).values()
            if isinstance(attr, ContainerSectionBase)
        ]
        for subsec in subsections:
            subsec._set()  # pylint: disable=protected-access
        return self


def _check_dataclass_decorator(obj):
    pass

    # if not (is_dataclass(obj)):
    #     raise TypeError(
    #         f"{obj} is not a dataclass instance; did you forget to add "
    #         f"'@dataclass(frozen=True)' when you defined {obj.__class__}?."
    #     )
    # if not obj.__class__.__dataclass_params__.frozen:
    #     raise TypeError(
    #         f"{obj} is not a frozen dataclass instance; did you forget "
    #         f"to add '(frozen=True)' when you defined {obj.__class__}?."
    #     )


_ALL_CONTAINER_SECTION_SINGLETONS = {}
