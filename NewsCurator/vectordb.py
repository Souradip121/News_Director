from pinecone import Pinecone
import os
from dotenv import load_dotenv
load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# To get the unique host for an index, 
# see https://docs.pinecone.io/guides/manage-data/target-an-index
index = pc.Index(host="https://thrillernews-yuhz74v.svc.aped-4627-b74a.pinecone.io")


# Upsert records into a namespace
# `chunk_text` fields are converted to dense vectors
# `category` fields are stored as metadata
index.upsert_records(
    "example-namespace",
    [
        { 
            "_id": "vec1", 
            "text": "AAPL reported a year-over-year revenue increase, expecting stronger Q3 demand for its flagship phones.", 
            "category": "technology",
            "quarter": "Q3"
        },
        { 
            "_id": "vec2", 
            "text": "Analysts suggest that AAPL'\''s upcoming Q4 product launch event might solidify its position in the premium smartphone market.", 
            "category": "technology",
            "quarter": "Q4"
        },
        { 
            "_id": "vec3", 
            "text": "AAPL'\''s strategic Q3 partnerships with semiconductor suppliers could mitigate component risks and stabilize iPhone production.",
            "category": "technology",
            "quarter": "Q3"
        },
        { 
            "_id": "vec4", 
            "text": "AAPL may consider healthcare integrations in Q4 to compete with tech rivals entering the consumer wellness space.", 
            "category": "technology",
            "quarter": "Q4"
        }
    ]
)