from pydantic import BaseModel, Field
from typing import List, Any, Union, Optional, Dict

class TypeVars(BaseModel):
    name: str
    description: str

class RequiredResources(BaseModel):
    name: str
    description: str

class ResourceAssignments(BaseModel):
    attribute: str
    type: str
    key: str

class OptionalResources(BaseModel):
    attribute: str
    type: str
    key: str
    description: str

class Parameters(BaseModel):
    name: str
    type: str
    description: str

class Returns(BaseModel):
    type: str
    description: str

class RaisesException(BaseModel):
    exception: str
    description: str

class Methods(BaseModel):
    name: str
    docstring: str
    parameters: Optional[List[Parameters]] = Field(default_factory=list)
    returns: Returns
    body: str
    raises: Optional[List[RaisesException]] = Field(default=None)
    is_property: Optional[bool] = Field(default=None)

class PDFProcessor(BaseModel):
    class_name: str
    format_name: str
    class_docstring: str
    type_vars: List[TypeVars]
    imports: List[str]
    required_resources: List[RequiredResources]
    resource_assignments: List[ResourceAssignments]
    optional_resources: List[OptionalResources]
    example_output: str
    methods: List[Methods]