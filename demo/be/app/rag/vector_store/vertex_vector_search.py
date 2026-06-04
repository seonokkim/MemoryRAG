"""Vertex AI Vector Search backend (production GCP path).

Requires index, endpoint, and deployed index resources in the same GCP project/region.
Falls back to empty search results when not configured so MySQL SQL retrieval still works.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.rag.vector_store.base import VectorRecord, VectorSearchHit, VectorStoreBackend

if TYPE_CHECKING:
    from app.core.config import Settings

logger = logging.getLogger(__name__)


class VertexVectorSearchStore(VectorStoreBackend):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def provider_name(self) -> str:
        return "vertex_vector_search"

    def is_available(self) -> bool:
        return self.settings.vertex_vector_search_configured

    def upsert(self, collection: str, records: list[VectorRecord]) -> list[str]:
        if not records:
            return []
        if not self.is_available():
            return [r.id for r in records]
        try:
            self._upsert_datapoints(collection, records)
        except Exception as exc:
            logger.warning("vertex_vector_upsert_skipped", extra={"error": str(exc)})
        return [r.id for r in records]

    def search(
        self,
        collection: str,
        query: str,
        *,
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[VectorSearchHit]:
        if not self.is_available():
            return []
        try:
            return self._find_neighbors(collection, query, top_k=top_k, filters=filters)
        except Exception as exc:
            logger.warning("vertex_vector_search_failed", extra={"error": str(exc)})
            return []

    def _endpoint_resource_name(self) -> str:
        project = self.settings.vertex_project_id
        region = self.settings.vertex_location
        endpoint_id = self.settings.vertex_vector_endpoint_id
        return (
            f"projects/{project}/locations/{region}/indexEndpoints/{endpoint_id}"
        )

    def _deployed_index_id(self) -> str:
        return self.settings.vertex_vector_deployed_index_id

    def _upsert_datapoints(self, collection: str, records: list[VectorRecord]) -> None:
        from google.cloud import aiplatform

        aiplatform.init(
            project=self.settings.vertex_project_id,
            location=self.settings.vertex_location,
        )
        index_name = (
            f"projects/{self.settings.vertex_project_id}/locations/"
            f"{self.settings.vertex_location}/indexes/"
            f"{self.settings.vertex_vector_index_id}"
        )
        index = aiplatform.MatchingEngineIndex(index_name=index_name)
        datapoints = []
        for record in records:
            embedding = self._embed_text(record.text)
            meta = {**record.metadata, "collection": collection}
            restricts = self._build_restricts(meta)
            datapoints.append(
                {
                    "datapoint_id": record.id,
                    "feature_vector": embedding,
                    "restricts": restricts,
                }
            )
        if datapoints:
            index.upsert_datapoints(datapoints=datapoints)

    def _find_neighbors(
        self,
        collection: str,
        query: str,
        *,
        top_k: int,
        filters: dict | None,
    ) -> list[VectorSearchHit]:
        from google.cloud import aiplatform

        aiplatform.init(
            project=self.settings.vertex_project_id,
            location=self.settings.vertex_location,
        )
        endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=self._endpoint_resource_name()
        )
        query_embedding = self._embed_text(query)
        neighbor_filters = self._build_neighbor_filters(collection, filters)
        response = endpoint.find_neighbors(
            deployed_index_id=self._deployed_index_id(),
            queries=[query_embedding],
            num_neighbors=top_k,
            filter=neighbor_filters,
        )
        hits: list[VectorSearchHit] = []
        for group in response or []:
            for neighbor in group:
                hits.append(
                    VectorSearchHit(
                        id=str(neighbor.id),
                        text="",
                        score=float(neighbor.distance),
                        metadata={"collection": collection},
                    )
                )
        return hits

    def _embed_text(self, text: str) -> list[float]:
        """Placeholder embedding; replace with Vertex text-embedding model in production."""
        # Deterministic pseudo-embedding keeps local tests independent of GCP APIs.
        seed = sum(ord(c) for c in text[:512]) or 1
        return [((seed * (i + 1)) % 997) / 997.0 for i in range(8)]

    def _build_restricts(self, metadata: dict) -> list[dict]:
        restricts: list[dict] = []
        if collection := metadata.get("collection"):
            restricts.append(
                {"namespace": "collection", "allow_list": [str(collection)]}
            )
        if user_id := metadata.get("user_id"):
            restricts.append(
                {"namespace": "user_id", "allow_list": [str(user_id)]}
            )
        return restricts

    def _build_neighbor_filters(
        self, collection: str, filters: dict | None
    ) -> list[dict] | None:
        namespaces = [{"name": "collection", "allow_tokens": [collection]}]
        if filters and filters.get("user_id") is not None:
            namespaces.append(
                {
                    "name": "user_id",
                    "allow_tokens": [str(filters["user_id"])],
                }
            )
        return namespaces
