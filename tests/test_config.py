from goldscope.core.config import get_settings


def test_postgresql_url_is_normalized_for_psycopg(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://user:password@render-host:5432/goldscope",
    )
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_url == "postgresql+psycopg://user:password@render-host:5432/goldscope"

    get_settings.cache_clear()


def test_legacy_postgres_url_is_normalized_for_psycopg(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgres://user:password@render-host:5432/goldscope",
    )
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_url == "postgresql+psycopg://user:password@render-host:5432/goldscope"

    get_settings.cache_clear()
