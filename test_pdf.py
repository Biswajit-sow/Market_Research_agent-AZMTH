import requests
import json
import time

# --- CONFIGURATION ---
BASE_URL = "http://127.0.0.1:5000"
USER_ID = "startup_founder_01"  # Matches current frontend ID
SAMPLE_PRODUCT = "A foldable electric bike specifically engineered for 'last-mile' delivery drivers in New York, priced under $1200"

def test_full_pipeline():
    print(f"\n{'='*60}")
    print(f"🚀 STARTING HYBRID PIPELINE TEST")
    print(f"{'='*60}\n")

    # 1. TEST ANALYZE (Hybrid RAG: Internal Pinecone + Live Tavily)
    print("STEP 1: Requesting Hybrid Market Intelligence...")
    analyze_payload = {
        "user_id": USER_ID,
        "description": SAMPLE_PRODUCT
    }
    
    try:
        analyze_res = requests.post(f"{BASE_URL}/analyze", json=analyze_payload)
        if analyze_res.status_code != 200:
            print(f"❌ Analysis Failed! Status: {analyze_res.status_code}")
            print(analyze_res.text)
            return

        data = analyze_res.json()
        print("✅ Analysis Complete!\n")

        # Verify Math
        print("📊 [PRD 4.3] DYNAMIC MARKET MATH (NumPy):")
        print(json.dumps(data.get('market_size'), indent=2))
        
        # Verify Hybrid Storage Search
        print("\n🧠 [PRD 4.2] INTERNAL PINECOCE KNOWLEDGE FOUND:")
        print(data.get('internal_knowledge_found', "No DB records matched."))

        # Verify Live Search
        print("\n🌐 [PRD 4.2] LIVE WEB SOURCES CAPTURED (Tavily):")
        sources = data.get('web_sources', [])
        print(f"Retrieved {len(sources)} verified links.")
        if sources:
            print(f"Example Snippet: {str(sources[0])[:150]}...")

        # Verify AI Strategy Text
        print("\n🤖 [PRD 4.4/4.5] AI STRATEGIC NARRATIVE PREVIEW:")
        full_analysis = data.get('analysis', "")
        print(f"{full_analysis[:400]}...")

        # 2. TEST HISTORY (Astra DB Retrieval)
        print(f"\n{'-'*60}")
        print("STEP 2: Checking Astra DB Persistence (History)...")
        history_res = requests.get(f"{BASE_URL}/history/{USER_ID}")
        if history_res.status_code == 200:
            history_data = history_res.json()
            print(f"✅ Success! Astra DB returned {len(history_data)} past interactions.")
        else:
            print("❌ Failed to retrieve history from Astra DB.")

        # 3. TEST PDF GENERATION (FPDF2 Service)
        print(f"\n{'-'*60}")
        print("STEP 3: Testing Professional PDF Generation Engine...")
        pdf_payload = {"analysis": full_analysis}
        pdf_res = requests.post(f"{BASE_URL}/download-report", json=pdf_payload)
        
        if pdf_res.status_code == 200:
            filename = f"API_Test_Report_{int(time.time())}.pdf"
            with open(filename, "wb") as f:
                f.write(pdf_res.content)
            print(f"✅ Success! Generated High-Fidelity Report: {filename}")
        else:
            print(f"❌ PDF Engine Crash: {pdf_res.status_code}")

        # 4. TEST PERMANENT CLEAR (Database wipe)
        # Uncomment below if you want to test the full clear logic as well
        # print(f"\n{'-'*60}")
        # print("STEP 4: Testing Permanent History Deletion...")
        # clear_res = requests.delete(f"{BASE_URL}/clear-history/{USER_ID}")
        # print(f"✅ Result: {clear_res.json().get('message')}")

    except Exception as e:
        print(f"💥 Connection Error: Ensure Flask (app.py) is running on port 5000.")
        print(f"Details: {e}")

if __name__ == "__main__":
    test_full_pipeline()