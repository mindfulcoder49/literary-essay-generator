from __future__ import annotations

from typing import Iterable

from pinecone import Pinecone, ServerlessSpec

from app.config import get_settings
from app.logging_config import configure_logging


class PineconeClient:
    def __init__(self):
        settings = get_settings()
        if not settings.pinecone_api_key:
            raise RuntimeError("PINECONE_API_KEY is required")
        self._pc = Pinecone(api_key=settings.pinecone_api_key)
        self._index_name = settings.pinecone_index
        self._cloud = settings.pinecone_cloud
        self._region = settings.pinecone_region
        self._logger = configure_logging("pinecone", "worker.log")

    def ensure_index(self, dimension: int):
        if self._index_name not in self._pc.list_indexes().names():
            self._pc.create_index(
                name=self._index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud=self._cloud, region=self._region),
            )
            self._logger.info(
                "pinecone index created name=%s dim=%s cloud=%s region=%s",
                self._index_name,
                dimension,
                self._cloud,
                self._region,
            )

    def index(self):
        return self._pc.Index(self._index_name)


UPSERT_BATCH_SIZE = 100


def upsert_embeddings(
    pc: PineconeClient,
    namespace: str,
    vectors: Iterable[tuple[str, list[float], dict]],
):
    index = pc.index()
    payload = [{"id": vid, "values": values, "metadata": metadata} for vid, values, metadata in vectors]
    for i in range(0, len(payload), UPSERT_BATCH_SIZE):
        batch = payload[i : i + UPSERT_BATCH_SIZE]
        index.upsert(vectors=batch, namespace=namespace)
        pc._logger.info("pinecone upsert namespace=%s batch=%s/%s", namespace, i + len(batch), len(payload))


def query_similar(
    pc: PineconeClient,
    namespace: str,
    query_vector: list[float],
    top_k: int,
):
    index = pc.index()
    result = index.query(
        vector=query_vector,
        namespace=namespace,
        top_k=top_k,
        include_metadata=True,
    )
    pc._logger.info("pinecone query namespace=%s top_k=%s matches=%s", namespace, top_k, len(result.get("matches", [])))
    return result
