from firstlight.config import UserConfig, config_path, load_config, save_config


def test_load_missing_returns_defaults() -> None:
    config = load_config()
    assert config == UserConfig()


def test_save_and_load_roundtrip() -> None:
    original = UserConfig(author="Ada", email="ada@example.com", default_stack="python")
    save_config(original)
    assert load_config() == original


def test_empty_values_not_written() -> None:
    save_config(UserConfig(author="Ada"))
    text = config_path().read_text()
    assert "author" in text
    assert "email" not in text


def test_unknown_keys_ignored() -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('author = "Ada"\nfuture_option = "x"\n')
    assert load_config().author == "Ada"
