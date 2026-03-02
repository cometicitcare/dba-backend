from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.gramasewaka import GramasewakaOut


class GnDivisionNode(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    gn_id: int
    gn_gnc: str
    gn_gnname: Optional[str] = None
    gn_dvcode: str


class DivisionalSecretariatNode(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    dv_id: int
    dv_dvcode: str
    dv_distrcd: str
    dv_dvname: Optional[str] = None
    gn_divisions: List[GnDivisionNode] = Field(default_factory=list)


class DistrictNode(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    dd_id: int
    dd_dcode: str
    dd_dname: Optional[str] = None
    dd_prcode: str
    divisional_secretariats: List[DivisionalSecretariatNode] = Field(default_factory=list)


class ProvinceNode(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    cp_id: int
    cp_code: str
    cp_name: Optional[str] = None
    districts: List[DistrictNode] = Field(default_factory=list)


class LocationHierarchyResponse(BaseModel):
    status: str
    message: str
    data: List[ProvinceNode]


class DivisionalGramasewakaResponse(BaseModel):
    status: str
    message: str
    data: List[GramasewakaOut]
