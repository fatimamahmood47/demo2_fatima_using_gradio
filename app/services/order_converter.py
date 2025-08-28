# services/order_converter.py (MODIFIED)
# schemas
from app.schemas.normalized_order import NormalizedOrder 
from app.schemas.converted_order import ConvertedProduct, ConvertOrder, Candidate, PreConvert, Converted

# vector database  
from app.dependencies.vector_database import QueryProductNames 
# llm
from app.dependencies.llm import get_openai_client 

# json handling
import json
from typing import List 

class ConvertProduct: 
    def __init__(self, normalized_order: NormalizedOrder):
        # assign 
        self.product_list = normalized_order.components
        self.client = get_openai_client() 
        self.vdatabase = QueryProductNames()  

    def _query_similar_products(self, product_name: str): 
        pinecone_result = self.vdatabase.query_product_names(product_name) 
        return pinecone_result 
    
    def _convert(self, product_name: str, product_code: str, similar_products: str) -> List[Candidate]:
        prompt = (
            "🎯 Task: Given a `target_product_name` and a list of top vector similarity matches, return multiple candidate matches "
            "with their details. Input includes target name and a list of matches (each with external_product_name, "
            "internal_product_name, internal_product_id, and score). "
            "Rules: "
            "1. Use ONLY the provided matches from the similarity search results "
            "2. ALWAYS return at least 1-3 candidates, even if scores are low "
            "3. Generate sequential master_id numbers starting from 10001 "
            "4. Use the internal_product_name as 'product-name' and internal_product_id as 'product-code' "
            "5. Keep the original similarity scores "
            "6. If no good matches exist, still return the top available matches "
            "Output JSON format: {\"candidates\": [{\"master_id\": 10001, \"product-name\": \"...\", \"product-code\": \"...\", \"score\": 0.96}, ...]}"
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": f"Target product name: {product_name}\nTarget product code: {product_code}\n\nSimilarity matches:\n{similar_products}",
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Lower temperature for more consistent results
            )
            
            # Parse the JSON response
            result_json = json.loads(response.choices[0].message.content)
            
            # Handle different response formats
            if 'candidates' in result_json:
                candidates_data = result_json['candidates']
            elif isinstance(result_json, list):
                candidates_data = result_json
            else:
                # Fallback: try to find any array in the response
                candidates_data = []
                for key, value in result_json.items():
                    if isinstance(value, list) and len(value) > 0:
                        candidates_data = value
                        break
            
            # Convert to Candidate objects
            candidates = []
            for i, candidate in enumerate(candidates_data):
                try:
                    # Handle different key formats
                    master_id = candidate.get('master_id', 10001 + i)
                    product_name_key = candidate.get('product-name') or candidate.get('product_name') or candidate.get('name', f"Unknown Product {i+1}")
                    product_code_key = candidate.get('product-code') or candidate.get('product_code') or candidate.get('code', f"UNK{i+1}")
                    score = float(candidate.get('score', 0.5))
                    
                    candidates.append(Candidate(
                        master_id=master_id,
                        product_name=product_name_key,
                        product_code=product_code_key,
                        score=score
                    ))
                except Exception as e:
                    print(f"Error parsing candidate {i}: {e}")
                    # Add a fallback candidate
                    candidates.append(Candidate(
                        master_id=10001 + i,
                        product_name=f"Fallback Product {i+1}",
                        product_code=f"FB{i+1}",
                        score=0.1
                    ))
            
            # Ensure we always return at least one candidate
            if not candidates:
                candidates.append(Candidate(
                    master_id=10001,
                    product_name="No Match Found",
                    product_code="NOMATCH",
                    score=0.0
                ))
            
            return candidates
            
        except Exception as e:
            print(f"Error in _convert method: {e}")
            # Return a fallback candidate in case of complete failure
            return [Candidate(
                master_id=10001,
                product_name="Error Processing",
                product_code="ERROR",
                score=0.0
            )]

    def _convert_single_product(self, single_product: dict, product_index: int) -> ConvertedProduct: 
        # Extract data from the product
        external_name = single_product.external_product_name
        external_code = single_product.external_product_code
        quantity = single_product.quantities
        
        # Get similar products
        similar_products = str(self._query_similar_products(external_name))
        
        # Convert and get candidates
        candidates = self._convert(external_name, external_code, similar_products)
        


            # --- DEBUG: print to terminal ---
        print(f"\n[DEBUG] Product #{product_index}")
        print(f"[DEBUG] external_name: {external_name}")
        print(f"[DEBUG] external_code: {external_code}")
        print(f"[DEBUG] similar_products: {similar_products}")
        print("[DEBUG] candidates:")
        for c in candidates:
            try:
                payload = c.model_dump() if hasattr(c, "model_dump") else (
                        c.dict() if hasattr(c, "dict") else vars(c))
            except Exception:
                payload = str(c)
            print("   ", payload)
        # --- end DEBUG ---





        # Create the new structure
        pre_convert = PreConvert(
            id=product_index,
            mixed=f"{external_name} | {external_code}",
            quantity=quantity
        )
        
        converted = Converted(
            candidates=candidates,
            quantity=quantity
        )
        
        return ConvertedProduct(
            pre_convert=pre_convert,
            converted=converted
        )
    
    def convert_single_order(self):
        converted_list = []
        for index, product in enumerate(self.product_list):   
            converted_list.append(self._convert_single_product(product, index))
        
        # Return as a list directly (not wrapped in ConvertOrder)
        return converted_list