from astrapy import DataAPIClient
import os
import datetime
from dotenv import load_dotenv

load_dotenv()


INDEXED_PREVIEW_BYTES = 3000   
MAX_ANALYSIS_BYTES    = 7500   


def _truncate_bytes(text: str, max_bytes: int) -> str:
    """Safely truncate a string to max_bytes without splitting a UTF-8 char."""
    if not text:
        return ""
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    return encoded[:max_bytes].decode("utf-8", errors="ignore").strip()


def _sanitise_full_result(full_result: dict) -> dict:
   
    if not isinstance(full_result, dict):
        return {}

    raw_analysis = full_result.get("analysis", "") or ""
    web_sources  = full_result.get("web_sources", [])

    
    if isinstance(web_sources, str):
        web_sources = _truncate_bytes(web_sources, 2000)

    return {
        
        "analysis_preview": _truncate_bytes(raw_analysis, INDEXED_PREVIEW_BYTES),
        "analysis":         _truncate_bytes(raw_analysis, MAX_ANALYSIS_BYTES),
        "market_size":      full_result.get("market_size"),
        "web_sources":      web_sources,
    }


class DBService:
    def __init__(self):
        token    = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        keyspace = os.getenv("ASTRA_DB_KEYSPACE")
        print("TOKEN:",    token)
        print("ENDPOINT:", endpoint)
        print("KEYSPACE:", keyspace)
        client   = DataAPIClient(token)
        self.db  = client.get_database_by_api_endpoint(endpoint, keyspace=keyspace)

        self.history_col = self.db.get_collection("chat_history")

        if "usage_metrics" not in self.db.list_collection_names():
            self.metrics_col = self.db.create_collection("usage_metrics")
        else:
            self.metrics_col = self.db.get_collection("usage_metrics")

    
    def save_message(self, user_id: str, message: str, full_result: dict):
        ts = datetime.datetime.now().isoformat()

        
        safe_result = _sanitise_full_result(full_result)

        document = {
            "user_id":     user_id,
            "user_query":  _truncate_bytes(str(message), 1000),  # queries can be long too
            "full_result": safe_result,
            "timestamp":   ts,
        }

        try:
            self.history_col.insert_one(document)
            self.metrics_col.insert_one({
                "user_id":  user_id,
                "event":    "success_analysis",
                "timestamp": ts,
            })

        except Exception as e:
            
            print(f"DB insert failed even after sanitise: {e}")
            document["full_result"]["analysis"]         = "[Analysis too large — download PDF]"
            document["full_result"]["analysis_preview"] = "[Analysis too large — download PDF]"
            try:
                self.history_col.insert_one(document)
            except Exception as e2:
                
                print(f"DB fallback also failed: {e2}")

   
    def delete_user_history(self, user_id: str):
        self.history_col.delete_many({"user_id": user_id})
        self.metrics_col.delete_many({"user_id": user_id})
        return True

    # ── Fetch ────────────────────────────────────────────────────────────
    def get_history(self, user_id: str) -> list:
        return list(self.history_col.find(
            filter={"user_id": user_id},
            sort={"timestamp": -1},
        ))