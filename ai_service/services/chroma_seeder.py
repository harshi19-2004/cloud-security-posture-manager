"""
chroma_seeder.py
Day 12 — AI Developer 1

Seeds ChromaDB with 10 cloud security domain knowledge documents.
These documents help AI give better answers about cloud security.
"""

import logging
import os

logger = logging.getLogger(__name__)

# ── 10 domain knowledge documents ────────────────────────────────────────────
SECURITY_DOCUMENTS = [
    {
        "id":      "doc_001",
        "content": "AWS S3 bucket security: Always enable Block Public Access, server-side encryption (SSE-S3 or SSE-KMS), versioning, and access logging. Never use public ACLs for production data.",
        "topic":   "AWS S3 Security"
    },
    {
        "id":      "doc_002",
        "content": "AWS IAM best practices: Follow least privilege principle. Never attach AdministratorAccess to users or roles. Enable MFA for all users. Rotate access keys every 90 days. Use IAM roles instead of long-term credentials.",
        "topic":   "AWS IAM Security"
    },
    {
        "id":      "doc_003",
        "content": "Network security groups: Always restrict inbound rules to specific IP ranges. Never open port 22 (SSH) or port 3389 (RDP) to 0.0.0.0/0. Use VPN or bastion hosts for remote access.",
        "topic":   "Network Security"
    },
    {
        "id":      "doc_004",
        "content": "Database security: Never expose database ports to public internet. Use VPC endpoints or private subnets. Enable encryption at rest and in transit. Use strong passwords and rotate regularly.",
        "topic":   "Database Security"
    },
    {
        "id":      "doc_005",
        "content": "Container security: Never run containers as root. Use read-only file systems. Scan images for vulnerabilities regularly. Never use --privileged flag in production. Keep base images updated.",
        "topic":   "Container Security"
    },
    {
        "id":      "doc_006",
        "content": "Kubernetes security: Always enable RBAC. Never expose dashboard publicly. Use network policies to restrict pod communication. Encrypt etcd at rest. Use PodSecurityPolicies or OPA.",
        "topic":   "Kubernetes Security"
    },
    {
        "id":      "doc_007",
        "content": "Logging and monitoring: Always enable CloudTrail in AWS. Use centralized logging with retention policies. Set up alerts for suspicious activity. Never disable audit logging in production.",
        "topic":   "Logging and Monitoring"
    },
    {
        "id":      "doc_008",
        "content": "Encryption best practices: Encrypt data at rest using AES-256. Encrypt data in transit using TLS 1.2 or higher. Use managed key services like AWS KMS or Azure Key Vault. Never hardcode encryption keys.",
        "topic":   "Encryption"
    },
    {
        "id":      "doc_009",
        "content": "Secrets management: Never hardcode secrets in code or config files. Use environment variables or secrets managers like AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault. Rotate secrets regularly.",
        "topic":   "Secrets Management"
    },
    {
        "id":      "doc_010",
        "content": "Zero trust security: Never trust network location alone. Verify every request. Use identity-based access controls. Implement micro-segmentation. Monitor all traffic between services.",
        "topic":   "Zero Trust Security"
    },
]


def seed_chromadb() -> bool:
    """
    Seeds ChromaDB with 10 security knowledge documents.

    Returns:
        True  — if seeding successful
        False — if ChromaDB not available
    """
    try:
        import chromadb

        # ── Connect to ChromaDB ───────────────────────────────────────────────
        chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
        client      = chromadb.PersistentClient(path=chroma_path)

        # ── Get or create collection ──────────────────────────────────────────
        collection = client.get_or_create_collection(
            name="security_knowledge",
            metadata={"description": "Cloud security domain knowledge"}
        )

        # ── Check if already seeded ───────────────────────────────────────────
        existing = collection.count()
        if existing >= len(SECURITY_DOCUMENTS):
            logger.info(f"ChromaDB already seeded with {existing} documents")
            return True

        # ── Add documents ─────────────────────────────────────────────────────
        collection.add(
            ids       = [doc["id"]      for doc in SECURITY_DOCUMENTS],
            documents = [doc["content"] for doc in SECURITY_DOCUMENTS],
            metadatas = [{"topic": doc["topic"]} for doc in SECURITY_DOCUMENTS],
        )

        logger.info(f"ChromaDB seeded with {len(SECURITY_DOCUMENTS)} documents!")
        return True

    except Exception as e:
        logger.warning(f"ChromaDB seeding failed (not critical): {e}")
        return False


def query_knowledge(query: str, n_results: int = 3) -> list:
    """
    Query ChromaDB for relevant security knowledge.

    Returns:
        list of relevant document strings
        empty list if ChromaDB not available
    """
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
        client      = chromadb.PersistentClient(path=chroma_path)
        collection  = client.get_or_create_collection("security_knowledge")

        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count())
        )

        documents = results.get("documents", [[]])[0]
        logger.info(f"ChromaDB query returned {len(documents)} results")
        return documents

    except Exception as e:
        logger.warning(f"ChromaDB query failed: {e}")
        return []


def get_seeded_count() -> int:
    """Returns number of documents in ChromaDB."""
    try:
        import chromadb
        chroma_path = os.getenv("CHROMA_PATH", "./chroma_data")
        client      = chromadb.PersistentClient(path=chroma_path)
        collection  = client.get_or_create_collection("security_knowledge")
        return collection.count()
    except Exception:
        return 0