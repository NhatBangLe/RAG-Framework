from pydantic import Field, BaseModel, field_validator

from src.config.model import Configuration


class RecognizerConfiguration(Configuration):
    """
    An interface for recognizer configuration classes
    """
    enable: bool = Field(default=True)
    path: str = Field(description="Model file location")
    min_probability: float = Field(description="A low probability limit for specifying classes.", ge=0.0, le=1.0)
    max_results: int = Field(description="The maximum number of results recognized is used for prompting.",
                             default=4, ge=1, le=50)
    output_config_path: str = Field(description="Path to an output configuration file.")


class ClassDescriptor(BaseModel):
    name: str = Field(description="Name of data class", min_length=1, max_length=150)
    description: str = Field(description="Description for this class, use to search relevant information.",
                             min_length=10, max_length=255)


# noinspection PyNestedDecorators
class RecognizerOutput(BaseModel):
    is_configured: bool = Field(default=False, description="Whether the recognizer is configured")
    classes: list[ClassDescriptor] = Field(description="A list of data classes")

    @field_validator("classes", mode="after")
    @classmethod
    def remove_classes_duplicate(cls, classes: list[ClassDescriptor]):
        class_names = set()
        nodup_classes: list[ClassDescriptor] = []
        for data_class in classes:
            if data_class.name not in class_names:
                class_names.add(data_class.name)
                nodup_classes.append(data_class)
        return nodup_classes
