"""Tests des deux StorageAdapter (Local + Cloud) avec contrat commun."""

from __future__ import annotations

import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------- Local


@pytest_asyncio.fixture
async def local_adapter(tmp_path):
    from pli.adapters.local import LocalStorageAdapter

    return LocalStorageAdapter(root=tmp_path)


async def test_local_put_get_roundtrip(local_adapter):
    obj = await local_adapter.put(
        tenant_id="local",
        key="ignored",
        data=b"hello world",
    )
    assert obj.size_bytes == 11
    data = await local_adapter.get(tenant_id="local", key=obj.sha256)
    assert data == b"hello world"


async def test_local_dedup_by_content(local_adapter):
    o1 = await local_adapter.put(tenant_id="local", key="a", data=b"same")
    o2 = await local_adapter.put(tenant_id="local", key="b", data=b"same")
    assert o1.sha256 == o2.sha256


async def test_local_refuses_other_tenant(local_adapter):
    from pli.adapters.base import TenantIsolationError

    with pytest.raises(TenantIsolationError):
        await local_adapter.put(tenant_id="alice", key="x", data=b"x")


async def test_local_get_missing(local_adapter):
    from pli.adapters.base import StorageNotFound

    with pytest.raises(StorageNotFound):
        await local_adapter.get(tenant_id="local", key="deadbeef" * 8)


# ---------------------------------------------------------------- Cloud (moto)


@pytest.fixture
def s3_mock():
    """Bucket S3 mocké avec moto. Skip si moto non installé."""
    try:
        from moto import mock_aws
    except ImportError:
        pytest.skip("moto non installé — skip tests S3")
    import boto3

    with mock_aws():
        client = boto3.client("s3", region_name="eu-west-3")
        client.create_bucket(
            Bucket="pli-test",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-3"},
        )
        yield client


async def test_cloud_put_get_with_tenant_prefix(s3_mock, monkeypatch):
    monkeypatch.setenv("PLI_S3_BUCKET", "pli-test")
    from pli.adapters.cloud import CloudStorageAdapter

    adapter = CloudStorageAdapter(bucket="pli-test")

    await adapter.put(tenant_id="alice", key="att/1.pdf", data=b"alice-data")
    await adapter.put(tenant_id="bob", key="att/1.pdf", data=b"bob-data")

    # Chaque tenant ne voit que son fichier
    assert await adapter.get(tenant_id="alice", key="att/1.pdf") == b"alice-data"
    assert await adapter.get(tenant_id="bob", key="att/1.pdf") == b"bob-data"

    # Vérification du préfixe physique en S3
    keys = [o["Key"] for o in s3_mock.list_objects_v2(Bucket="pli-test")["Contents"]]
    assert sorted(keys) == ["t/alice/att/1.pdf", "t/bob/att/1.pdf"]


async def test_cloud_refuses_pre_prefixed_key(s3_mock, monkeypatch):
    monkeypatch.setenv("PLI_S3_BUCKET", "pli-test")
    from pli.adapters.base import TenantIsolationError
    from pli.adapters.cloud import CloudStorageAdapter

    adapter = CloudStorageAdapter(bucket="pli-test")
    with pytest.raises(TenantIsolationError):
        await adapter.put(tenant_id="alice", key="t/bob/att/x", data=b"x")


async def test_cloud_iter_tenant_isolation(s3_mock, monkeypatch):
    monkeypatch.setenv("PLI_S3_BUCKET", "pli-test")
    from pli.adapters.cloud import CloudStorageAdapter

    adapter = CloudStorageAdapter(bucket="pli-test")
    await adapter.put(tenant_id="alice", key="a", data=b"1")
    await adapter.put(tenant_id="alice", key="b", data=b"2")
    await adapter.put(tenant_id="bob", key="c", data=b"3")
    keys_alice = [o.key async for o in adapter.iter_tenant(tenant_id="alice")]
    keys_bob = [o.key async for o in adapter.iter_tenant(tenant_id="bob")]
    assert sorted(keys_alice) == ["a", "b"]
    assert keys_bob == ["c"]
