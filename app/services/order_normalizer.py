# services/order_normalizer.py (finalized for deterministic quantity handling)
import pandas as pd
from io import StringIO
import json
import re

# output structure
from app.schemas.normalized_order import NormalizedOrder, ConstructionComponent
from app.schemas.detection import DetectionConfig


class NormalizeCsvOrder:
    def __init__(self, contents: bytes, detection_config: DetectionConfig):
        """
        Accepts raw CSV file content and detection JSON config.
        Produces structured normalized data directly (no LLM for quantities).
        """
        self.detection_config = detection_config
        self.df = self._parse_contents(contents)
    def _parse_contents(self, contents: bytes) -> pd.DataFrame:
        """
        Decodes CSV bytes and parses to DataFrame.
        Ensures first row is treated as data, not header.
        """
        try:
            decoded = contents.decode("utf-8")
        except UnicodeDecodeError:
            decoded = contents.decode("shift-jis", errors="ignore")

        df = pd.read_csv(
            StringIO(decoded),
            dtype=str,
            header=None,   # 👈 make sure first row is data
            keep_default_na=False,
            na_values=["", "NA", "NaN"]
        )
        return df.fillna("")



    def _extract_quantity(self, value: str) -> float:
        """
        Extract numeric part from quantity like:
        - '1172ｍ' -> 1172
        - '10,297ｍ' -> 10297
        - '1.325ｍ3' -> 1.325
        - '71.8' -> 71.8
        Returns float (but can be cast to int if needed).
        """
        if not value or str(value).strip() == "":
            return 0

        cleaned = str(value).replace(",", "").strip()

        # Match integer or decimal number
        match = re.search(r"\d+(?:\.\d+)?", cleaned)
        if match:
            num = match.group()
            # return as float if it has a decimal
            return float(num) if "." in num else int(num)
        return 0



    def _extract_code(self, row: pd.Series) -> str:
        """
        Try to extract product code from known columns.
        Works with both numeric and string column names.
        """
        for col in row.index:
            col_name = str(col)  # 👈 ensure it's always string
            if any(keyword in col_name.lower() for keyword in ["code", "品番", "型番", "商品コード"]):
                value = str(row[col]).strip()
                if value:
                    return value
        return ""  # fallback


    def convert_to_component_list(self) -> NormalizedOrder:
        components = []
        mixed_cfg = self.detection_config.mixed
        qty_col = self.detection_config.quantity_col

        current_name = None
        current_quantity = None
        current_code = None

        group_context = None  # track current group name

        for idx, row in self.df.iterrows():
            # --- Build name normally ---
            if mixed_cfg.type == "single":
                external_name = str(row.iloc[mixed_cfg.cols[0]]).strip()
            elif mixed_cfg.type == "concat":
                parts = [str(row.iloc[c]).strip() for c in mixed_cfg.cols]
                external_name = mixed_cfg.sep.join(parts).strip()
            else:
                external_name = ""

            # --- Skip header rows ---
            if (not external_name 
                or any(keyword in external_name for keyword in ["名称", "規格", "数量", "単位", "金額", "備考"]) 
                or external_name.startswith("■")):
                continue

            # --- Quantity ---
            quantity = self._extract_quantity(row.iloc[qty_col])
            code = self._extract_code(row)

            if quantity > 0:
                # This is a product row
                if current_name:
                    # flush previous product
                    components.append(ConstructionComponent(
                        external_product_name=current_name,
                        external_product_code=current_code or "",
                        quantities=current_quantity or 0
                    ))
                # new product
                current_name = external_name
                current_quantity = quantity
                current_code = code

            else:
                # --- No quantity row ---

                # Detect blank/separator row → flush current product and reset
                if not external_name.strip() or row.isna().all():
                    if current_name:
                        components.append(ConstructionComponent(
                            external_product_name=current_name,
                            external_product_code=current_code or "",
                            quantities=current_quantity or 0
                        ))
                        current_name = None
                        current_quantity = None
                        current_code = None
                    continue

                # Skip obvious notes / disclaimers / headers
<<<<<<< HEAD
                            # Skip obvious notes / disclaimers / headers
                if (external_name.startswith("※")
                    or any(keyword in external_name for keyword in ["名称", "規格", "数量", "単位", "金額", "備考"])):
                    # Flush current product if one is open, then reset
                    if current_name:
                        components.append(ConstructionComponent(
                            external_product_name=current_name,
                            external_product_code=current_code or "",
                            quantities=current_quantity or 0
                        ))
                        current_name, current_quantity, current_code = None, None, None
                    continue

=======
                if (external_name.startswith("※")
                    or any(keyword in external_name for keyword in ["名称", "規格", "数量", "単位", "金額", "備考"])):
                    continue

                # Look ahead: is this a group header? (next row has quantity)
                next_qty = None
                if idx + 1 < len(self.df):
                    next_qty = self._extract_quantity(self.df.iloc[idx + 1, qty_col])
                if next_qty and next_qty > 0:
                    group_context = external_name
                    continue
>>>>>>> 052ef1b27b9a98155612271920865e406e74ae41

                # Otherwise, treat as continuation (only if no blank before)
                if current_name:
                    current_name += " " + external_name





        # --- After loop, flush last product safely ---
        if current_name:
            # If the last name contains disclaimers/headers, clean them out
            if ("※" in current_name 
                or any(keyword in current_name for keyword in ["名称", "規格", "数量", "単位", "金額", "備考"])):
                # cut off everything after the first keyword/disclaimer
                for marker in ["※", "名称", "規格", "数量", "単位", "金額", "備考"]:
                    if marker in current_name:
                        current_name = current_name.split(marker)[0].strip()
                        break

            components.append(ConstructionComponent(
                external_product_name=current_name,
                external_product_code=current_code or "",
                quantities=current_quantity or 0
            ))


        return NormalizedOrder(components=components)

