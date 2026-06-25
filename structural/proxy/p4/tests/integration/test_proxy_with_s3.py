"""Integration test: RemoteFileProxy wired to a real RealS3File against
moto's simulated S3 bucket -- the full Proxy -> RealSubject -> S3 chain."""

from __future__ import annotations

from src.remote_files.infrastructure.real_s3_file import RealS3File
from src.remote_files.infrastructure.remote_file_proxy import RemoteFileProxy
from tests.conftest import TEST_BUCKET, TEST_CONTENT, TEST_KEY


class TestProxyEndToEndWithMotoS3:
    def test_lazy_load_then_cache_against_real_s3_client(
        self, populated_moto_s3: object
    ) -> None:
        real_subject = RealS3File(
            bucket=TEST_BUCKET, key=TEST_KEY, s3_client=populated_moto_s3
        )
        proxy = RemoteFileProxy(real_subject=real_subject)

        assert proxy.is_cached() is False

        first = proxy.read()
        assert first == TEST_CONTENT
        assert proxy.is_cached() is True

        # Delete the object from the simulated bucket: if the proxy were to
        # call S3 again, this read would now fail. It must not.
        populated_moto_s3.delete_object(Bucket=TEST_BUCKET, Key=TEST_KEY)  # type: ignore[attr-defined]

        second = proxy.read()
        assert second == TEST_CONTENT

        stats = proxy.cache_stats()
        assert stats.cache_misses == 1
        assert stats.cache_hits == 1

    def test_exists_and_size_reflect_real_bucket_state(
        self, populated_moto_s3: object
    ) -> None:
        real_subject = RealS3File(
            bucket=TEST_BUCKET, key=TEST_KEY, s3_client=populated_moto_s3
        )
        proxy = RemoteFileProxy(real_subject=real_subject)

        assert proxy.exists() is True
        assert proxy.size == len(TEST_CONTENT)

    def test_invalidate_forces_real_redownload(self, populated_moto_s3: object) -> None:
        real_subject = RealS3File(
            bucket=TEST_BUCKET, key=TEST_KEY, s3_client=populated_moto_s3
        )
        proxy = RemoteFileProxy(real_subject=real_subject)

        proxy.read()
        proxy.invalidate()

        new_content = b"updated content"
        populated_moto_s3.put_object(  # type: ignore[attr-defined]
            Bucket=TEST_BUCKET, Key=TEST_KEY, Body=new_content
        )

        refreshed = proxy.read()
        assert refreshed == new_content
        assert proxy.cache_stats().cache_misses == 2
