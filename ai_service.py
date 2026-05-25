import os
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate


class AIService:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.0,
            max_tokens=2000,
            model="llama-3.3-70b-versatile"   # Valid Groq model with 128k context
        )
        self.search = TavilySearchResults(max_results=3)  # 3 results keeps tokens lean

   

    def _trim(self, text: str, max_chars: int) -> str:
        """Hard-truncate a string and signal the cut."""
        if not text:
            return "N/A"
        text = str(text)
        return text[:max_chars] + " [trimmed]" if len(text) > max_chars else text

    def _build_prompt(self) -> ChatPromptTemplate:
        template = """\
You are a senior market-intelligence consultant at a top-tier strategy firm.
Produce a structured, data-driven Strategic Intelligence Report.
Be specific, cite real numbers, and name real companies from the web research only.
Never stop mid-sentence. Complete every section fully.

STRICT FORMATTING RULES:
- Section headings: write them as "SECTION N — TITLE" in ALL CAPS (the frontend will bold and color these)

- No markdown symbols (* # ** --- ~~)
- No bullet points — write in flowing prose paragraphs only
- Every section must contain at least 2 numeric metrics or benchmarks
- 3 to 4 sentences per section minimum

PRODUCT CONCEPT:
{desc}

INTERNAL DATABASE INSIGHTS:
{internal}

MARKET SIZE DATA (TAM / SAM / SOM):
{math}

LIVE WEB RESEARCH (competitors, pricing, trends — use only names found here):
{web}

---

SECTION 1 — EXECUTIVE SUMMARY
State the core market opportunity with dollar value, the single biggest strategic advantage,
expected market capture percentage by 2028, and the CAGR.
Write each as "Label: sentence." on its own line.

SECTION 2 — MARKET ANALYSIS
Quantify TAM, SAM, and SOM using the MARKET SIZE DATA.
State CAGR, projected market value by 2028, primary demand driver, and top geographic region.
Write each as "Label: sentence." on its own line.

SECTION 3 — COMPETITOR LANDSCAPE
List exactly 4 to 5 real competitors from WEB RESEARCH only.
For each write: "CompanyName: pricing range, one key differentiator, growth signal."
Do not invent company names.
Write each as "Label: sentence." on its own line.

SECTION 4 — COMPETITIVE GAP ANALYSIS
For each competitor named in Section 3, write one sentence identifying a measurable shortfall.
Format each as: "CompanyName Gap: describe the specific weakness with a metric."
Write each as "Label: sentence." on its own line.

SECTION 5 — SWOT MATRIX
Strengths: two internal advantages with supporting metrics.
Weaknesses: two internal limitations with estimated cost or risk percentage.
Opportunities: two external tailwinds with market size or growth rate.
Threats: two external risks with probability or impact estimate.
Write each as "Label: sentence." on its own line.

SECTION 6 — REVENUE CAPTURE LOGIC
State the primary monetization model, Year 1 projected revenue, Year 3 milestone,
Year 5 target, and the top two growth levers with expected percentage contribution each.
Write each as "Label: sentence." on its own line.

SECTION 7 — TARGET CUSTOMER PROFILE
Demographic: age range, income bracket, job role or lifestyle segment, estimated segment size.
Psychographic: core motivation, buying trigger, and willingness-to-pay range.
Write as "Demographic:" and "Psychographic:" sub-headings.

SECTION 8 — CONSUMER SENTIMENT AND EARLY ADOPTERS
Identify the earliest-adopter archetype by name and trait.
Cite at least one demand signal such as search volume trend, social mentions, or survey stat.
Predict the adoption S-curve inflection point in months from launch.
Write each as "Label: sentence." on its own line.

SECTION 9 — PRICING AND MONETIZATION RECOMMENDATIONS
Recommend a specific tier structure with price points benchmarked against Section 3 competitors.
State expected gross margin percentage and projected conversion rate from free to paid tier.
Format tiers as "TierName: $price — feature summary."
Write each as "Label: sentence." on its own line.

SECTION 10 — STRATEGIC ROADMAP
Phase 1 (Months 1 to 2): Beta goal, target user count, and primary KPI.
Phase 2 (Months 3 to 4): Launch channel, MRR milestone in dollars, and NPS target above 50.
Phase 3 (Months 5 plus): Scale lever, churn-rate target below 5 percent monthly, and LTV goal.
Write each as "Phase 1:", "Phase 2:", "Phase 3:" sub-headings.
"""
        return ChatPromptTemplate.from_template(template)

    def generate_strategy(
        self,
        product_desc: str,
        internal_data: str,
        market_data: str,
    ) -> tuple[str, str]:

        print(f"Step: Browsing web for {product_desc}...")
        try:
            query = f"competitors pricing trends {product_desc} 2025"
            raw_results = self.search.run(query)
            web_results = raw_results if raw_results else "No web data found."
        except Exception as e:
            print(f"Search error: {e}")
            web_results = "Web research unavailable."

        trimmed_desc     = self._trim(product_desc, 800)
        trimmed_internal = self._trim(internal_data, 1600)
        trimmed_math     = self._trim(market_data,   800)
        trimmed_web      = self._trim(web_results,  2000)

       
        chain = self._build_prompt() | self.llm

        response = chain.invoke({
            "desc":     trimmed_desc,
            "internal": trimmed_internal,
            "math":     trimmed_math,
            "web":      trimmed_web,
        })

        return response.content, web_results