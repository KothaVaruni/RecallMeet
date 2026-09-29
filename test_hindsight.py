import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv(override=True)

client = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

bank_id = os.getenv("HINDSIGHT_BANK_ID")

client.retain(
    bank_id=bank_id,
    content="Acme Corp has a budget of ₹5 lakh and wants the project delivered within 3 months.",
    context="client meeting"
)

response = client.recall(
    bank_id=bank_id,
    query="What are Acme Corp's budget and delivery timeline?"
)

print("RecallMeet remembered:")

for result in response.results:
    print("-", result.text)