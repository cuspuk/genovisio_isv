from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from isv.src.cnv_region import CNVRegion


def get_mongo_database(uri: str, db_name: str) -> Database[dict[str, Any]]:
    client: MongoClient[dict[str, Any]] = MongoClient(uri)
    return client[db_name]


def find_intersections(
    collection: Collection[dict[str, Any]], search_params: CNVRegion, check_type: bool = False
) -> list[dict[str, Any]]:
    query = {
        "chromosome": search_params.chr,
        "start": {"$lte": search_params.end},  # search_params.start <= other.end
        "end": {"$gte": search_params.start},  # search_params.end >= other.start
    }
    if check_type:
        query["cnv_type"] = search_params.cnv_type

    with collection.find(query) as cursor:
        results = list(cursor)

    return results


class IntersectionCollectionsParser:
    db: Database[dict[str, Any]]

    def __init__(self, uri: str, db_name: str, collection_names: list[str], check_type_names: list[str]):
        self.db = get_mongo_database(uri, db_name)
        self.collection_names = collection_names
        self.check_type_names = check_type_names

    def get_for_region(self, region: CNVRegion) -> dict[str, list[dict[str, Any]]]:
        return {
            collection_name: find_intersections(
                self.db[collection_name], region, collection_name in self.check_type_names
            )
            for collection_name in self.collection_names
        }
