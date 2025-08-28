from pydantic import BaseModel, model_validator
from typing import List, Literal, Optional

class MixedColumn(BaseModel):
    type: Literal["concat", "single"]
    cols: List[int]
    sep: Optional[str] = None  # optional

    @model_validator(mode="after")
    def _default_sep(self):
        # default empty separator for single; require for concat
        if self.type == "single" and self.sep is None:
            self.sep = ""
        if self.type == "concat" and not self.sep:
            raise ValueError("sep is required when type='concat'")
        return self

class DetectionConfig(BaseModel):
    mixed: MixedColumn
    quantity_col: int  # 0-based index
